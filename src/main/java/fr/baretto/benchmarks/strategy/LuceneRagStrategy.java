package fr.baretto.benchmarks.strategy;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.EnumDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.TypeDeclaration;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.model.ollama.OllamaEmbeddingModel;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.KnnFloatVectorField;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.KnnFloatVectorQuery;
import org.apache.lucene.search.Query;
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
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class LuceneRagStrategy implements RagStrategy {

    private static final Logger logger = LoggerFactory.getLogger(LuceneRagStrategy.class);
    private static final String DEFAULT_INDEX_PATH = "./lucene-db";
    private static final String FIELD_CONTENT   = "content";
    private static final String FIELD_TEXT      = "text";      // champ BM25 (indexed, not stored)
    private static final String FIELD_EMBEDDING = "embedding";

    private static final String OLLAMA_BASE_URL      = System.getProperty("rag.ollama.url",       "http://localhost:11434");
    private static final String EMBEDDING_MODEL_NAME = System.getProperty("rag.embedding.model",  "nomic-embed-text");

    private final Path           indexPath;
    private final EmbeddingModel embeddingModel;
    private final int            vectorDimensions;
    private final FeatureFlags   flags;
    private FSDirectory          directory;

    public LuceneRagStrategy() {
        this(Path.of(DEFAULT_INDEX_PATH), FeatureFlags.hybrid());
    }

    public LuceneRagStrategy(Path indexPath) {
        this(indexPath, FeatureFlags.hybrid());
    }

    /** Constructeur principal avec feature flags explicites. */
    public LuceneRagStrategy(Path indexPath, FeatureFlags flags) {
        this.indexPath = indexPath;
        this.flags     = flags;
        EmbeddingModel model;
        int dims;
        try {
            model = OllamaEmbeddingModel.builder()
                .baseUrl(OLLAMA_BASE_URL)
                .modelName(EMBEDDING_MODEL_NAME)
                .build();
            dims = model.embed("probe").content().vector().length;
            logger.info("Lucene embedding model: {} ({}d)", EMBEDDING_MODEL_NAME, dims);
        } catch (Exception e) {
            logger.warn("Ollama indisponible, fallback AllMiniLmL6V2: {}", e.getMessage());
            model = new AllMiniLmL6V2EmbeddingModel();
            dims = 384;
        }
        this.embeddingModel   = model;
        this.vectorDimensions = dims;
        logger.info("Stratégie Lucene RAG initialisée (preset={})", flags.presetName());
    }

    /** Constructeur pour injection directe (tests). */
    public LuceneRagStrategy(Path indexPath, EmbeddingModel embeddingModel, int vectorDimensions) {
        this(indexPath, embeddingModel, vectorDimensions, FeatureFlags.hybrid());
    }

    /** Constructeur pour injection directe avec feature flags (tests, benchmark). */
    public LuceneRagStrategy(Path indexPath, EmbeddingModel embeddingModel, int vectorDimensions, FeatureFlags flags) {
        this.indexPath        = indexPath;
        this.embeddingModel   = embeddingModel;
        this.vectorDimensions = vectorDimensions;
        this.flags            = flags;
    }

    @Override
    public void indexDirectory(Path directoryPath) throws Exception {
        logger.info("Indexation du répertoire avec Lucene: {}", directoryPath);

        if (Files.exists(indexPath)) {
            deleteDirectory(indexPath);
        }
        Files.createDirectories(indexPath);

        directory = FSDirectory.open(indexPath);
        try (IndexWriter writer = new IndexWriter(directory, new IndexWriterConfig(new StandardAnalyzer()))) {
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
                doc.add(new TextField(FIELD_TEXT, chunk, Field.Store.NO));  // indexé pour BM25
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

                // Chunk classe : déclaration complète (kind + extends + implements) + champs + signatures
                StringBuilder classChunk = new StringBuilder();
                String kind = "class";
                String extendsStr = "";
                String implementsStr = "";
                if (type instanceof ClassOrInterfaceDeclaration coid) {
                    kind = coid.isInterface() ? "interface" : "class";
                    if (!coid.getExtendedTypes().isEmpty())
                        extendsStr = " extends " + coid.getExtendedTypes().stream()
                            .map(t -> t.getNameAsString()).collect(Collectors.joining(", "));
                    if (!coid.getImplementedTypes().isEmpty())
                        implementsStr = " implements " + coid.getImplementedTypes().stream()
                            .map(t -> t.getNameAsString()).collect(Collectors.joining(", "));
                } else if (type instanceof EnumDeclaration ed) {
                    kind = "enum";
                    if (!ed.getImplementedTypes().isEmpty())
                        implementsStr = " implements " + ed.getImplementedTypes().stream()
                            .map(t -> t.getNameAsString()).collect(Collectors.joining(", "));
                }
                classChunk.append("Type: ").append(kind).append(" ").append(fqn)
                          .append(extendsStr).append(implementsStr).append("\n");
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
        logger.info("Recherche Lucene [{}] pour: {}", flags.presetName(), query);

        if (directory == null) {
            directory = FSDirectory.open(indexPath);
        }

        int topK = flags.topK();
        float[] queryEmbedding = embeddingModel.embed(query).content().vector();

        try (DirectoryReader reader = DirectoryReader.open(directory)) {
            IndexSearcher searcher = new IndexSearcher(reader);

            if (!flags.bm25Enabled() || !flags.rrfEnabled()) {
                // knn-only : recherche vectorielle pure
                TopDocs knnDocs = searcher.search(
                    new KnnFloatVectorQuery(FIELD_EMBEDDING, queryEmbedding, topK), topK);
                List<String> results = new ArrayList<>();
                for (ScoreDoc sd : knnDocs.scoreDocs) {
                    String content = searcher.storedFields().document(sd.doc).get(FIELD_CONTENT);
                    if (content != null) results.add(content);
                }
                return results;
            }

            // hybrid : BM25 + KNN + RRF (k=60, identique à HybridSearchService Neo4j)
            List<Integer> bm25Results = searchBM25(searcher, query, topK);
            logger.debug("BM25: {} résultats", bm25Results.size());

            TopDocs knnDocs = searcher.search(
                new KnnFloatVectorQuery(FIELD_EMBEDDING, queryEmbedding, topK), topK);
            List<Integer> knnResults = Arrays.stream(knnDocs.scoreDocs)
                .map(sd -> sd.doc)
                .collect(Collectors.toList());
            logger.debug("KNN: {} résultats", knnResults.size());

            List<Integer> fusedDocIds = rrfFuse(List.of(bm25Results, knnResults), flags.rrfK(), topK);

            List<String> results = new ArrayList<>();
            for (int docId : fusedDocIds) {
                String content = searcher.storedFields().document(docId).get(FIELD_CONTENT);
                if (content != null) results.add(content);
            }
            return results;
        }
    }

    /**
     * Recherche BM25 via QueryParser (StandardAnalyzer — même tokenisation qu'à l'indexation).
     */
    private List<Integer> searchBM25(IndexSearcher searcher, String queryText, int topK) {
        try (StandardAnalyzer analyzer = new StandardAnalyzer()) {
            QueryParser parser = new QueryParser(FIELD_TEXT, analyzer);
            parser.setDefaultOperator(QueryParser.Operator.OR);
            Query bm25Query = parser.parse(QueryParser.escape(queryText));
            TopDocs bm25Docs = searcher.search(bm25Query, topK);
            return Arrays.stream(bm25Docs.scoreDocs)
                .map(sd -> sd.doc)
                .collect(Collectors.toList());
        } catch (Exception e) {
            logger.debug("BM25 search failed, skipping: {}", e.getMessage());
            return List.of();
        }
    }

    /**
     * Reciprocal Rank Fusion : fusionne plusieurs listes ordonnées de doc IDs.
     * Score RRF = Σ 1 / (k + rank_i + 1) pour chaque liste où le doc apparaît.
     */
    private List<Integer> rrfFuse(List<List<Integer>> rankedLists, int k, int topK) {
        Map<Integer, Double> scores = new HashMap<>();
        for (List<Integer> list : rankedLists) {
            for (int rank = 0; rank < list.size(); rank++) {
                scores.merge(list.get(rank), 1.0 / (k + rank + 1), Double::sum);
            }
        }
        return scores.entrySet().stream()
            .sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
            .limit(topK)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }

    @Override
    public String getStrategyName() {
        return "Lucene/" + flags.presetName();
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
