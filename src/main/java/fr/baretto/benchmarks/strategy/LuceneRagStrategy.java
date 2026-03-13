package fr.baretto.benchmarks.strategy;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.TypeDeclaration;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.KnnFloatVectorField;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.KnnFloatVectorQuery;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.index.VectorSimilarityFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class LuceneRagStrategy implements RagStrategy {

    private static final Logger logger = LoggerFactory.getLogger(LuceneRagStrategy.class);
    private static final String DEFAULT_INDEX_PATH = "./lucene-db";
    private static final int TOP_K = 5;
    private static final int VECTOR_DIMENSIONS = 384;
    private static final String FIELD_CONTENT = "content";
    private static final String FIELD_EMBEDDING = "embedding";

    private final Path indexPath;
    private final EmbeddingModel embeddingModel;
    private FSDirectory directory;

    public LuceneRagStrategy() {
        this(Path.of(DEFAULT_INDEX_PATH));
    }

    public LuceneRagStrategy(Path indexPath) {
        this.indexPath = indexPath;
        this.embeddingModel = new AllMiniLmL6V2EmbeddingModel();
        logger.info("Initialisation de la stratégie Lucene RAG");
    }

    @Override
    public void indexDirectory(Path directoryPath) throws Exception {
        logger.info("Indexation du répertoire avec Lucene: {}", directoryPath);

        if (Files.exists(indexPath)) {
            deleteDirectory(indexPath);
        }
        Files.createDirectories(indexPath);

        directory = FSDirectory.open(indexPath);
        try (IndexWriter writer = new IndexWriter(directory, new IndexWriterConfig())) {
            Files.walk(directoryPath)
                    .filter(p -> p.toString().endsWith(".java"))
                    .forEach(javaFile -> indexFile(writer, javaFile));
            writer.commit();
        }

        logger.info("Indexation Lucene terminée");
    }

    private void indexFile(IndexWriter writer, Path filePath) {
        try {
            String source = Files.readString(filePath);
            List<String> chunks = extractChunks(filePath, source);
            for (String chunk : chunks) {
                float[] embedding = embeddingModel.embed(chunk).content().vector();
                Document doc = new Document();
                doc.add(new StoredField(FIELD_CONTENT, chunk));
                doc.add(new KnnFloatVectorField(FIELD_EMBEDDING, embedding, VectorSimilarityFunction.COSINE));
                writer.addDocument(doc);
            }
        } catch (Exception e) {
            logger.warn("Erreur lors de l'indexation de {}: {}", filePath, e.getMessage());
        }
    }

    /**
     * Extrait des chunks au niveau classe et méthode, comme Neo4j indexe ses nœuds.
     * Un chunk par classe (nom + champs + signatures) + un chunk par méthode (signature + corps).
     */
    private List<String> extractChunks(Path filePath, String source) {
        List<String> chunks = new ArrayList<>();
        try {
            CompilationUnit cu = StaticJavaParser.parse(source);
            String packageName = cu.getPackageDeclaration()
                    .map(pd -> pd.getNameAsString())
                    .orElse("");

            cu.findAll(TypeDeclaration.class).forEach(typeRaw -> {
                @SuppressWarnings("unchecked")
                TypeDeclaration<?> type = (TypeDeclaration<?>) typeRaw;
                String fqn = packageName.isEmpty()
                        ? type.getNameAsString()
                        : packageName + "." + type.getNameAsString();

                // Chunk classe : résumé structurel
                StringBuilder classChunk = new StringBuilder();
                classChunk.append("Type: ").append(fqn).append("\n");
                type.getComment().ifPresent(c -> classChunk.append("Doc: ").append(c.getContent().strip()).append("\n"));
                type.getFields().forEach(f -> classChunk.append("Field: ").append(f.toString().strip()).append("\n"));
                type.getMethods().forEach(m -> {
                    MethodDeclaration method = (MethodDeclaration) m;
                    classChunk.append("Method: ").append(method.getDeclarationAsString()).append("\n");
                });
                chunks.add(classChunk.toString());

                // Chunk méthode : signature + corps
                type.getMethods().forEach(m -> {
                    MethodDeclaration method = (MethodDeclaration) m;
                    StringBuilder methodChunk = new StringBuilder();
                    methodChunk.append("Method: ").append(fqn).append("#").append(method.getNameAsString()).append("\n");
                    method.getComment().ifPresent(c -> methodChunk.append("Doc: ").append(c.getContent().strip()).append("\n"));
                    methodChunk.append("Signature: ").append(method.getDeclarationAsString()).append("\n");
                    method.getBody().ifPresent(b -> methodChunk.append("Body: ").append(b.toString()).append("\n"));
                    chunks.add(methodChunk.toString());
                });
            });

            if (chunks.isEmpty()) {
                chunks.add(filePath.getFileName().toString() + "\n" + source);
            }
        } catch (Exception e) {
            logger.debug("JavaParser failed for {}, fallback raw content", filePath);
            chunks.add(filePath.getFileName().toString() + "\n" + source);
        }
        return chunks;
    }

    @Override
    public List<String> retrieveContext(String query) throws Exception {
        logger.info("Recherche de contexte avec Lucene pour la requête: {}", query);

        if (directory == null) {
            directory = FSDirectory.open(indexPath);
        }

        float[] queryEmbedding = embeddingModel.embed(query).content().vector();

        try (DirectoryReader reader = DirectoryReader.open(directory)) {
            IndexSearcher searcher = new IndexSearcher(reader);
            KnnFloatVectorQuery vectorQuery = new KnnFloatVectorQuery(FIELD_EMBEDDING, queryEmbedding, TOP_K);
            TopDocs topDocs = searcher.search(vectorQuery, TOP_K);

            List<String> results = new ArrayList<>();
            for (ScoreDoc scoreDoc : topDocs.scoreDocs) {
                String content = searcher.storedFields().document(scoreDoc.doc).get(FIELD_CONTENT);
                if (content != null) {
                    results.add(content);
                }
            }
            return results;
        }
    }

    @Override
    public String getStrategyName() {
        return "Vectoriel (Lucene)";
    }

    @Override
    public void close() throws Exception {
        if (directory != null) {
            directory.close();
            directory = null;
        }
        logger.info("Ressources Lucene fermées");
    }

    private void deleteDirectory(Path path) throws IOException {
        Files.walk(path)
                .sorted(Comparator.reverseOrder())
                .forEach(p -> {
                    try {
                        Files.delete(p);
                    } catch (IOException ignored) {
                    }
                });
    }
}
