package fr.baretto.benchmarks.strategy;

import org.neo4j.configuration.GraphDatabaseSettings;
import org.neo4j.configuration.connectors.BoltConnector;
import org.neo4j.configuration.helpers.SocketAddress;
import org.neo4j.dbms.api.DatabaseManagementService;
import org.neo4j.dbms.api.DatabaseManagementServiceBuilder;
import org.neo4j.driver.AuthTokens;
import org.neo4j.driver.Driver;
import org.neo4j.driver.GraphDatabase;
import org.neo4j.driver.Session;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.graphdb.ResourceIterator;
import org.neo4j.graphdb.Transaction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import fr.baretto.benchmarks.search.AdvancedSearchService;
import fr.baretto.benchmarks.search.EntryPoint;
import fr.baretto.benchmarks.search.SearchException;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.nodeTypes.NodeWithSimpleName;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.CombinedTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.ReflectionTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.JavaParserTypeSolver;

import fr.baretto.benchmarks.strategy.model.*;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.body.VariableDeclarator;

/**
 * Implémentation de la stratégie GraphRAG utilisant Neo4j Embedded.
 * Crée un graphe de connaissances à partir de la codebase et utilise
 * les relations entre entités pour améliorer la recherche.
 */
public class Neo4jGraphRagStrategy implements RagStrategy {

    private static final Logger logger = LoggerFactory.getLogger(Neo4jGraphRagStrategy.class);
    private static final String DB_PATH = "./neo4j-db";
    private static final String DEFAULT_DATABASE = "neo4j";

    private DatabaseManagementService managementService;
    private GraphDatabaseService graphDb;
    private boolean initialized = false;
    private final String dbPath;

    // Pipeline de recherche hybride (bolt + embeddings)
    private Driver boltDriver;
    private EmbeddingModel embeddingModel;
    private AdvancedSearchService advancedSearchService;
    private int boltPort = -1;

    // Types de relations dans le graphe
    private enum RelationType implements RelationshipType {
        CONTAINS,       // File contient Class/Function, Package contient Package/Class
        IMPORTS,        // File importe un autre File/Module
        EXTENDS,        // Class hérite d'une autre Class
        IMPLEMENTS,     // Class implémente une Interface
        HAS_METHOD,     // Class a une Method (deprecated, utiliser DECLARES)
        DECLARES,       // Class déclare Function/Constructor/Property
        CALLS,          // Function appelle une autre Function
        USES,           // Function utilise une Variable/Type
        RETURNS,        // Function retourne un Type
        HAS_PARAMETER,  // Function a un Parameter
        ANNOTATED_WITH  // Element est annoté avec Annotation
    }

    // Labels pour les noeuds (alignés avec CodeGraph)
    private static final String LABEL_FILE = "File";
    private static final String LABEL_CLASS = "Class";
    private static final String LABEL_INTERFACE = "Interface";
    private static final String LABEL_ENUM = "Enum";
    private static final String LABEL_RECORD = "Record";
    private static final String LABEL_ANNOTATION_TYPE = "AnnotationType";
    private static final String LABEL_FUNCTION = "Function";
    private static final String LABEL_CONSTRUCTOR = "Constructor";
    private static final String LABEL_PROPERTY = "Property";
    private static final String LABEL_PARAMETER = "Parameter";
    private static final String LABEL_ANNOTATION = "Annotation";
    private static final String LABEL_IMPORT = "Import";
    private static final String LABEL_PACKAGE = "Package";
    private static final String LABEL_PROJECT = "Project";

    public Neo4jGraphRagStrategy() {
        this(DB_PATH);
    }

    /**
     * Constructeur avec chemin de base de données personnalisé (utile pour les tests).
     */
    public Neo4jGraphRagStrategy(String customDbPath) {
        this.dbPath = customDbPath;
        logger.info("Stratégie Neo4j GraphRAG créée avec chemin: {} (initialisation lazy)", dbPath);
    }

    /**
     * Initialise la base de données Neo4j Embedded (lazy initialization).
     */
    private void ensureInitialized() {
        if (initialized) {
            return;
        }
        initializeNeo4j();
        initialized = true;
    }

    /**
     * Initialise la base de données Neo4j Embedded.
     */
    private void initializeNeo4j() {
        try {
            // Normaliser et rendre le chemin absolu pour Neo4j
            Path dbPath = Paths.get(this.dbPath).toAbsolutePath().normalize();

            // Créer le répertoire si nécessaire
            if (!Files.exists(dbPath)) {
                Files.createDirectories(dbPath);
            }

            // Trouver un port bolt libre
            boltPort = findFreePort();

            // Initialiser Neo4j Embedded avec bolt activé
            managementService = new DatabaseManagementServiceBuilder(dbPath)
                    .setConfig(BoltConnector.enabled, true)
                    .setConfig(BoltConnector.listen_address, new SocketAddress("localhost", boltPort))
                    .setConfig(GraphDatabaseSettings.auth_enabled, false)
                    .build();

            graphDb = managementService.database(DEFAULT_DATABASE);

            // Créer les index pour optimiser les recherches
            createIndexes();

            // Enregistrer un shutdown hook pour fermer proprement Neo4j
            registerShutdownHook(managementService);

            // Initialiser le pipeline de recherche hybride (bolt + embeddings)
            initSearchPipeline();

            logger.info("Neo4j Embedded initialisé avec succès à: {} (bolt port: {})", dbPath.toAbsolutePath(), boltPort);

        } catch (Exception e) {
            logger.error("Erreur lors de l'initialisation de Neo4j", e);
            throw new RuntimeException("Impossible d'initialiser Neo4j", e);
        }
    }

    /**
     * Enregistre un shutdown hook pour fermer proprement Neo4j.
     */
    private void registerShutdownHook(DatabaseManagementService service) {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("Arrêt de Neo4j...");
            service.shutdown();
        }));
    }

    /**
     * Trouve un port TCP libre sur localhost.
     */
    private int findFreePort() {
        try (java.net.ServerSocket s = new java.net.ServerSocket(0)) {
            s.setReuseAddress(true);
            return s.getLocalPort();
        } catch (java.io.IOException e) {
            return 7689;
        }
    }

    /**
     * Initialise le driver bolt et les services de recherche hybride.
     */
    private void initSearchPipeline() {
        try {
            // Petit délai pour que le connector bolt soit prêt
            Thread.sleep(500);

            boltDriver = GraphDatabase.driver(
                "bolt://localhost:" + boltPort,
                AuthTokens.none()
            );
            boltDriver.verifyConnectivity();

            embeddingModel = new AllMiniLmL6V2EmbeddingModel();
            advancedSearchService = new AdvancedSearchService(boltDriver, embeddingModel);

            logger.info("Pipeline de recherche hybride initialisé (bolt://localhost:{})", boltPort);
        } catch (Exception e) {
            logger.warn("Pipeline hybride non disponible (bolt inaccessible): {}", e.getMessage());
            // Pas fatal : retrieveContext basculera sur la recherche par mots-clés
        }
    }

    /**
     * Crée les index fulltext et vecteur (appelé après l'indexation).
     * Un index par label car Neo4j ne supporte pas le pipe dans FULLTEXT/VECTOR.
     */
    private void createSearchIndexes() {
        if (boltDriver == null) return;
        try (Session session = boltDriver.session()) {
            runIgnoreError(session, "CREATE FULLTEXT INDEX codeFullText IF NOT EXISTS FOR (n:Class) ON EACH [n.name, n.javaDoc]");
            runIgnoreError(session, "CREATE FULLTEXT INDEX codeFullTextFunction IF NOT EXISTS FOR (n:Function) ON EACH [n.name, n.javaDoc]");
            runIgnoreError(session, "CREATE FULLTEXT INDEX codeFullTextInterface IF NOT EXISTS FOR (n:Interface) ON EACH [n.name, n.javaDoc]");

            runIgnoreError(session, """
                CREATE VECTOR INDEX codeVector IF NOT EXISTS
                FOR (n:Class) ON n.embedding
                OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
                """);
            runIgnoreError(session, """
                CREATE VECTOR INDEX codeVectorFunction IF NOT EXISTS
                FOR (n:Function) ON n.embedding
                OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
                """);
            runIgnoreError(session, """
                CREATE VECTOR INDEX codeVectorInterface IF NOT EXISTS
                FOR (n:Interface) ON n.embedding
                OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
                """);

            Thread.sleep(2000);
            logger.info("Index fulltext et vecteur créés");
        } catch (Exception e) {
            logger.warn("Erreur création index de recherche: {}", e.getMessage());
        }
    }

    private void runIgnoreError(Session session, String cypher) {
        try {
            session.run(cypher);
        } catch (Exception e) {
            logger.debug("Index creation warning: {}", e.getMessage());
        }
    }

    /**
     * Génère et stocke les embeddings pour tous les nœuds Class/Function/Interface.
     */
    private void indexEmbeddings() {
        if (boltDriver == null || embeddingModel == null) return;
        logger.info("=== PHASE 5: EMBEDDING ===");

        try (Session session = boltDriver.session()) {
            var result = session.run(
                "MATCH (n) WHERE n:Class OR n:Function OR n:Interface " +
                "RETURN id(n) as nodeId, n.name as name, coalesce(n.javaDoc, '') as javaDoc"
            );

            int count = 0;
            while (result.hasNext()) {
                var record = result.next();
                long nodeId = record.get("nodeId").asLong();
                String text = record.get("name").asString("") + " " + record.get("javaDoc").asString("");

                float[] vector = embeddingModel.embed(text).content().vector();

                session.run(
                    "MATCH (n) WHERE id(n) = $id SET n.embedding = $embedding",
                    Map.of("id", nodeId, "embedding", vector)
                );
                count++;
            }
            logger.info("✅ {} embeddings générés et stockés", count);
        } catch (Exception e) {
            logger.warn("Erreur lors de l'indexation des embeddings: {}", e.getMessage());
        }
    }

    /**
     * Crée les index Neo4j pour optimiser les recherches.
     */
    private void createIndexes() {
        try (Transaction tx = graphDb.beginTx()) {
            // Index sur le nom des fichiers pour recherche rapide par chemin
            try {
                tx.execute("CREATE INDEX file_path_index IF NOT EXISTS FOR (f:File) ON (f.path)");
                tx.execute("CREATE INDEX file_name_index IF NOT EXISTS FOR (f:File) ON (f.name)");
            } catch (Exception e) {
                logger.debug("Index file_path déjà existant ou erreur: {}", e.getMessage());
            }

            // Index sur le nom des classes
            try {
                tx.execute("CREATE INDEX class_name_index IF NOT EXISTS FOR (c:Class) ON (c.name)");
                tx.execute("CREATE INDEX class_type_index IF NOT EXISTS FOR (c:Class) ON (c.type)");
            } catch (Exception e) {
                logger.debug("Index class_name déjà existant ou erreur: {}", e.getMessage());
            }

            // Index sur le nom des fonctions
            try {
                tx.execute("CREATE INDEX function_name_index IF NOT EXISTS FOR (f:Function) ON (f.name)");
            } catch (Exception e) {
                logger.debug("Index function_name déjà existant ou erreur: {}", e.getMessage());
            }

            // Index sur le nom des imports
            try {
                tx.execute("CREATE INDEX import_name_index IF NOT EXISTS FOR (i:Import) ON (i.name)");
            } catch (Exception e) {
                logger.debug("Index import_name déjà existant ou erreur: {}", e.getMessage());
            }

            // Index sur le nom des packages (Phase 4)
            try {
                tx.execute("CREATE INDEX package_name_index IF NOT EXISTS FOR (p:Package) ON (p.name)");
                logger.info("✓ Index sur Package.name créé");
            } catch (Exception e) {
                logger.debug("Index package_name déjà existant ou erreur: {}", e.getMessage());
            }

            // Index sur le nom des projets
            try {
                tx.execute("CREATE INDEX IF NOT EXISTS FOR (p:Project) ON (p.name)");
                logger.info("✓ Index sur Project.name créé");
            } catch (Exception e) {
                logger.debug("Index project_name déjà existant ou erreur: {}", e.getMessage());
            }

            // =========================================================================
            // CONTRAINTES ET INDEX SUR LES FQN (Fully Qualified Names)
            // =========================================================================

            // Contrainte d'unicité sur FQN des classes
            try {
                tx.execute("CREATE CONSTRAINT class_fqn_unique IF NOT EXISTS FOR (c:Class) REQUIRE c.fqn IS UNIQUE");
                logger.info("✓ Contrainte d'unicité sur Class.fqn créée");
            } catch (Exception e) {
                logger.debug("Contrainte class_fqn_unique déjà existante ou erreur: {}", e.getMessage());
            }

            // Contrainte d'unicité sur FQN des fonctions
            try {
                tx.execute("CREATE CONSTRAINT function_fqn_unique IF NOT EXISTS FOR (f:Function) REQUIRE f.fqn IS UNIQUE");
                logger.info("✓ Contrainte d'unicité sur Function.fqn créée");
            } catch (Exception e) {
                logger.debug("Contrainte function_fqn_unique déjà existante ou erreur: {}", e.getMessage());
            }

            // Index sur les FQN pour recherche rapide
            try {
                tx.execute("CREATE INDEX class_fqn_index IF NOT EXISTS FOR (c:Class) ON (c.fqn)");
                tx.execute("CREATE INDEX function_fqn_index IF NOT EXISTS FOR (f:Function) ON (f.fqn)");
                tx.execute("CREATE INDEX import_fqn_index IF NOT EXISTS FOR (i:Import) ON (i.fqn)");
                logger.info("✓ Index sur FQN créés");
            } catch (Exception e) {
                logger.debug("Index FQN déjà existants ou erreur: {}", e.getMessage());
            }

            // Index sur packageName pour recherche par package
            try {
                tx.execute("CREATE INDEX class_package_index IF NOT EXISTS FOR (c:Class) ON (c.packageName)");
                tx.execute("CREATE INDEX file_package_index IF NOT EXISTS FOR (f:File) ON (f.packageName)");
                logger.info("✓ Index sur packageName créés");
            } catch (Exception e) {
                logger.debug("Index packageName déjà existants ou erreur: {}", e.getMessage());
            }

            // NOTE: Les index full-text Lucene sont désactivés pour éviter les conflits de version
            // La recherche utilisera CONTAINS qui est plus lent mais fonctionne sans index Lucene
            /*
            // Index full-text sur le contenu des fichiers pour recherche textuelle
            try {
                tx.execute(
                    "CREATE FULLTEXT INDEX file_content_fulltext IF NOT EXISTS " +
                    "FOR (f:File) ON EACH [f.content]"
                );
            } catch (Exception e) {
                logger.debug("Index fulltext déjà existant ou erreur: {}", e.getMessage());
            }

            // Index full-text sur les noms d'entités (classes, fonctions)
            try {
                tx.execute(
                    "CREATE FULLTEXT INDEX entity_name_fulltext IF NOT EXISTS " +
                    "FOR (n:Class|Function|Import) ON EACH [n.name]"
                );
            } catch (Exception e) {
                logger.debug("Index entity fulltext déjà existant ou erreur: {}", e.getMessage());
            }
            */

            tx.commit();
            logger.info("Index Neo4j créés avec succès");

        } catch (Exception e) {
            logger.error("Erreur lors de la création des index", e);
        }
    }

    @Override
    public void indexDirectory(Path directoryPath) throws Exception {
        ensureInitialized();
        logger.info("=== INDEXATION AVEC PIPELINE 4 PHASES ===");
        logger.info("Répertoire: {}", directoryPath);

        if (!Files.exists(directoryPath) || !Files.isDirectory(directoryPath)) {
            throw new IllegalArgumentException("Le chemin spécifié n'est pas un répertoire valide: " + directoryPath);
        }

        long startTime = System.currentTimeMillis();

        // === PHASE 1: PARSING ===
        logger.info("\n=== PHASE 1: PARSING ===");
        List<ParsedFile> parsedFiles = parsePhase(directoryPath);
        logger.info("✅ Phase 1 terminée: {} fichiers parsés", parsedFiles.size());

        // === PHASE 2: SYMBOL RESOLUTION ===
        logger.info("\n=== PHASE 2: SYMBOL RESOLUTION ===");
        SymbolTable symbolTable = buildSymbolTable(parsedFiles);
        logger.info("✅ Symbol Table construite: {} classes", symbolTable.size());

        List<ParsedFile> resolvedFiles = resolvePhase(parsedFiles, symbolTable);
        logger.info("✅ Phase 2 terminée: Symboles résolus");

        // === PHASE 3: NEO4J WRITE ===
        logger.info("\n=== PHASE 3: NEO4J WRITE ===");
        writePhase(resolvedFiles);
        logger.info("✅ Phase 3 terminée: Graph écrit dans Neo4j");

        // === PHASE 4: POST-PROCESSING ===
        logger.info("\n=== PHASE 4: POST-PROCESSING ===");
        postProcessPhase();
        logger.info("✅ Phase 4 terminée");

        // === PHASE 5: INDEX FULLTEXT/VECTOR + EMBEDDINGS ===
        createSearchIndexes();
        indexEmbeddings();
        logger.info("✅ Phase 5 terminée");

        long duration = System.currentTimeMillis() - startTime;
        logger.info("\n✅ INDEXATION TERMINÉE en {}ms", duration);
    }

    /**
     * ANCIENNE MÉTHODE (conservée pour référence, à supprimer plus tard)
     */
    private void indexDirectoryOld(Path directoryPath) throws Exception {
        // Compter les fichiers à indexer
        final int[] fileCount = {0};

        try (Transaction tx = graphDb.beginTx()) {
            // Parcourir récursivement les fichiers
            Files.walkFileTree(directoryPath, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    try {
                        // Filtrer les fichiers pertinents (code source)
                        if (isSourceFile(file)) {
                            indexFile(file, tx);
                            fileCount[0]++;
                        }
                    } catch (Exception e) {
                        logger.warn("Erreur lors de l'indexation du fichier: {}", file, e);
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
                    // Ignorer les répertoires cachés et node_modules, .git, etc.
                    String dirName = dir.getFileName().toString();
                    if (dirName.startsWith(".") || dirName.equals("node_modules") ||
                        dirName.equals("target") || dirName.equals("build")) {
                        return FileVisitResult.SKIP_SUBTREE;
                    }
                    return FileVisitResult.CONTINUE;
                }
            });

            tx.commit();
            logger.info("Indexation terminée: {} fichiers indexés", fileCount[0]);
        }

        // Afficher les statistiques après l'indexation
        printDatabaseStats();
    }

    /**
     * Vérifie si un fichier est un fichier source à indexer.
     */
    private boolean isSourceFile(Path file) {
        String fileName = file.getFileName().toString().toLowerCase();
        return fileName.endsWith(".java") ||
               fileName.endsWith(".js") ||
               fileName.endsWith(".ts") ||
               fileName.endsWith(".py") ||
               fileName.endsWith(".md") ||
               fileName.endsWith(".txt");
    }

    /**
     * Indexe un fichier individuel dans Neo4j.
     * Crée des noeuds pour le fichier, les classes, fonctions, etc.
     * et des relations entre eux.
     */
    private void indexFile(Path file, Transaction tx) throws IOException {
        String content = Files.readString(file);
        String fileName = file.getFileName().toString();
        String relativePath = file.toString();

        // 1. Créer le noeud File dans Neo4j (INSERTION)
        Node fileNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FILE));
        fileNode.setProperty("path", relativePath);
        fileNode.setProperty("name", fileName);
        fileNode.setProperty("content", content);
        fileNode.setProperty("size", content.length());

        logger.info("✓ Nœud File créé dans Neo4j: {}", fileName);

        // 2. Détecter le type de fichier et extraire les entités
        String extension = getFileExtension(fileName);

        int entitiesCount = 0;
        switch (extension) {
            case "java":
                entitiesCount = extractJavaEntities(fileNode, content, tx);
                break;
            case "js":
            case "ts":
                entitiesCount = extractJavaScriptEntities(fileNode, content, tx);
                break;
            case "py":
                entitiesCount = extractPythonEntities(fileNode, content, tx);
                break;
            default:
                // Pour les autres fichiers (md, txt), juste stocker le contenu
                break;
        }

        logger.info("✓ Fichier indexé: {} → {} entités extraites", fileName, entitiesCount);
    }

    /**
     * Extrait l'extension d'un fichier.
     */
    private String getFileExtension(String fileName) {
        int lastDot = fileName.lastIndexOf('.');
        return lastDot > 0 ? fileName.substring(lastDot + 1).toLowerCase() : "";
    }

    /**
     * Extrait le nom du package depuis le contenu d'un fichier Java.
     * @return le nom du package ou une chaîne vide si non trouvé
     */
    private String extractPackageName(String content) {
        Pattern packagePattern = Pattern.compile("^\\s*package\\s+([\\w.]+)\\s*;", Pattern.MULTILINE);
        Matcher matcher = packagePattern.matcher(content);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return "";
    }

    /**
     * Construit le Fully Qualified Name (FQN) d'une classe.
     * @param packageName le nom du package
     * @param className le nom de la classe
     * @return le FQN complet (ex: "com.example.MyClass")
     */
    private String buildClassFqn(String packageName, String className) {
        if (packageName == null || packageName.isEmpty()) {
            return className;
        }
        return packageName + "." + className;
    }

    /**
     * Construit le Fully Qualified Name (FQN) d'une méthode.
     * @param classFqn le FQN de la classe
     * @param methodName le nom de la méthode
     * @param parameters les paramètres (pour gérer les overloads)
     * @return le FQN complet (ex: "com.example.MyClass.myMethod(String,int)")
     */
    private String buildMethodFqn(String classFqn, String methodName, String parameters) {
        // Simplifier les paramètres pour le FQN (juste les types, sans noms de variables)
        String simplifiedParams = simplifyParameters(parameters);
        return classFqn + "." + methodName + "(" + simplifiedParams + ")";
    }

    /**
     * Simplifie une chaîne de paramètres pour le FQN.
     * Exemple: "String name, int age" -> "String,int"
     */
    private String simplifyParameters(String parameters) {
        if (parameters == null || parameters.trim().isEmpty()) {
            return "";
        }

        String[] params = parameters.split(",");
        List<String> types = new ArrayList<>();

        for (String param : params) {
            param = param.trim();
            // Extraire juste le type (premier mot avant le nom de variable)
            String[] parts = param.split("\\s+");
            if (parts.length > 0) {
                types.add(parts[0]);
            }
        }

        return String.join(",", types);
    }

    /**
     * Extrait les entités d'un fichier Java (classes, méthodes, imports).
     * @return le nombre d'entités extraites
     */
    private int extractJavaEntities(Node fileNode, String content, Transaction tx) {
        int entityCount = 0;

        // Extraire le package name
        String packageName = extractPackageName(content);
        if (!packageName.isEmpty()) {
            fileNode.setProperty("packageName", packageName);
            logger.debug("  → Package: {}", packageName);
        }

        // Extraire toutes les entités avec JavaParser (AST)
        try {
            CompilationUnit cu = StaticJavaParser.parse(content);

            // Extraire les imports (avec JavaParser, plus de regex!)
            for (com.github.javaparser.ast.ImportDeclaration imp : cu.getImports()) {
                String importFqn = imp.getNameAsString();
                boolean isStatic = imp.isStatic();
                boolean isAsterisk = imp.isAsterisk();

                Node importNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_IMPORT));
                importNode.setProperty("name", importFqn);
                importNode.setProperty("fqn", importFqn);
                importNode.setProperty("isStatic", isStatic);
                importNode.setProperty("isWildcard", isAsterisk);

                fileNode.createRelationshipTo(importNode, RelationType.IMPORTS);
                entityCount++;
                logger.debug("  → Import créé: {} (static={}, wildcard={})", importFqn, isStatic, isAsterisk);
            }

            // Extraire les classes et interfaces
            for (ClassOrInterfaceDeclaration cls : cu.findAll(ClassOrInterfaceDeclaration.class)) {
                String className = cls.getNameAsString();
                String classFqn = buildClassFqn(packageName, className);

                // Déterminer le type (class ou interface)
                String classType = cls.isInterface() ? "interface" : "class";

                // Extraire les modificateurs
                String modifier = "";
                if (cls.isAbstract()) {
                    modifier = "abstract";
                } else if (cls.isFinal()) {
                    modifier = "final";
                }

                Node classNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
                classNode.setProperty("name", className);
                classNode.setProperty("fqn", classFqn);
                classNode.setProperty("type", classType);

                if (!packageName.isEmpty()) {
                    classNode.setProperty("packageName", packageName);
                }

                if (!modifier.isEmpty()) {
                    classNode.setProperty("modifier", modifier);
                }

                fileNode.createRelationshipTo(classNode, RelationType.CONTAINS);
                entityCount++;
                logger.debug("  → Classe créée: {} (FQN: {})", className, classFqn);

                // Créer les relations d'héritage (extends)
                for (ClassOrInterfaceType extendedType : cls.getExtendedTypes()) {
                    String parentName = extendedType.getNameAsString();
                    Node parentNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
                    parentNode.setProperty("name", parentName);
                    classNode.createRelationshipTo(parentNode, RelationType.EXTENDS);
                    logger.debug("    → EXTENDS: {}", parentName);
                }

                // Créer les relations d'implémentation (implements)
                for (ClassOrInterfaceType implementedType : cls.getImplementedTypes()) {
                    String ifaceName = implementedType.getNameAsString();
                    Node interfaceNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
                    interfaceNode.setProperty("name", ifaceName);
                    interfaceNode.setProperty("type", "interface");
                    classNode.createRelationshipTo(interfaceNode, RelationType.IMPLEMENTS);
                    logger.debug("    → IMPLEMENTS: {}", ifaceName);
                }

                // Extraire les méthodes, constructeurs, fields avec JavaParser
                int methodCount = extractMethodsWithParser(classNode, cls, classFqn, tx);
                int constructorCount = extractConstructorsWithParser(classNode, cls, classFqn, tx);
                int fieldCount = extractFieldsWithParser(classNode, cls, classFqn, tx);
                entityCount += methodCount + constructorCount + fieldCount;
            }

            // Extraire les enums
            for (EnumDeclaration enumDecl : cu.findAll(EnumDeclaration.class)) {
                String enumName = enumDecl.getNameAsString();
                String enumFqn = buildClassFqn(packageName, enumName);

                Node enumNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
                enumNode.setProperty("name", enumName);
                enumNode.setProperty("fqn", enumFqn);
                enumNode.setProperty("type", "enum");

                if (!packageName.isEmpty()) {
                    enumNode.setProperty("packageName", packageName);
                }

                fileNode.createRelationshipTo(enumNode, RelationType.CONTAINS);
                entityCount++;
                logger.debug("  → Enum créé: {} (FQN: {})", enumName, enumFqn);

                // Extraire les méthodes et fields de cet enum
                int methodCount = extractEnumMethodsWithParser(enumNode, enumDecl, enumFqn, tx);
                int fieldCount = extractEnumFieldsWithParser(enumNode, enumDecl, enumFqn, tx);
                entityCount += methodCount + fieldCount;
            }

            // Extraire les records (Java 14+)
            for (RecordDeclaration recordDecl : cu.findAll(RecordDeclaration.class)) {
                String recordName = recordDecl.getNameAsString();
                String recordFqn = buildClassFqn(packageName, recordName);

                Node recordNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
                recordNode.setProperty("name", recordName);
                recordNode.setProperty("fqn", recordFqn);
                recordNode.setProperty("type", "record");

                if (!packageName.isEmpty()) {
                    recordNode.setProperty("packageName", packageName);
                }

                fileNode.createRelationshipTo(recordNode, RelationType.CONTAINS);
                entityCount++;
                logger.debug("  → Record créé: {} (FQN: {})", recordName, recordFqn);

                // Créer les relations d'implémentation (implements)
                for (ClassOrInterfaceType implementedType : recordDecl.getImplementedTypes()) {
                    String ifaceName = implementedType.getNameAsString();
                    Node interfaceNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
                    interfaceNode.setProperty("name", ifaceName);
                    interfaceNode.setProperty("type", "interface");
                    recordNode.createRelationshipTo(interfaceNode, RelationType.IMPLEMENTS);
                    logger.debug("    → IMPLEMENTS: {}", ifaceName);
                }

                // Extraire les méthodes de ce record
                int methodCount = extractRecordMethodsWithParser(recordNode, recordDecl, recordFqn, tx);
                entityCount += methodCount;
            }

            // Extraire les annotations (@interface)
            for (AnnotationDeclaration annotationDecl : cu.findAll(AnnotationDeclaration.class)) {
                String annotationName = annotationDecl.getNameAsString();
                String annotationFqn = buildClassFqn(packageName, annotationName);

                Node annotationNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
                annotationNode.setProperty("name", annotationName);
                annotationNode.setProperty("fqn", annotationFqn);
                annotationNode.setProperty("type", "@interface");

                if (!packageName.isEmpty()) {
                    annotationNode.setProperty("packageName", packageName);
                }

                fileNode.createRelationshipTo(annotationNode, RelationType.CONTAINS);
                entityCount++;
                logger.debug("  → Annotation créée: {} (FQN: {})", annotationName, annotationFqn);
            }

        } catch (Exception e) {
            logger.error("Erreur lors du parsing JavaParser pour le fichier", e);
            // En cas d'erreur de parsing, on continue sans les classes
        }

        // PHASE 2: Détecter les appels de méthodes (CALLS)
        // On fait ça après avoir créé toutes les méthodes
        extractMethodCalls(content, tx);

        return entityCount;
    }

    /**
     * Extrait les appels de méthodes dans le code pour créer les relations CALLS.
     * Cette méthode détecte les patterns comme: variable.method(), Class.method(), this.method()
     * @param content le contenu du fichier
     * @param tx la transaction Neo4j
     */
    private void extractMethodCalls(String content, Transaction tx) {
        // Pattern pour détecter les appels de méthodes
        // Capture: nom_appelant.nom_méthode(...)
        Pattern callPattern = Pattern.compile("([\\w.]+)\\.([\\w]+)\\s*\\(");
        Matcher callMatcher = callPattern.matcher(content);

        while (callMatcher.find()) {
            String caller = callMatcher.group(1); // peut être une variable, une classe, "this", "super"
            String calledMethod = callMatcher.group(2);

            // Ignorer certains patterns courants qui ne sont pas des appels de méthodes
            if (isJavaKeyword(calledMethod) || isJavaKeyword(caller)) {
                continue;
            }

            // Essayer de créer une relation CALLS
            // Note: On ne peut pas toujours résoudre précisément quel nœud Function appelle quel autre
            // On va créer une relation basique pour commencer
            createCallRelation(caller, calledMethod, tx);
        }
    }

    /**
     * Crée une relation CALLS entre deux méthodes (si elles existent).
     * @param caller le nom de l'appelant (peut être une variable, classe, this, super)
     * @param calledMethod le nom de la méthode appelée
     * @param tx la transaction Neo4j
     */
    private void createCallRelation(String caller, String calledMethod, Transaction tx) {
        try {
            // Rechercher la méthode appelée par nom
            // Note: C'est une approximation simple, dans un vrai resolver on devrait
            // résoudre le type de 'caller' pour trouver la méthode exacte
            var result = tx.execute(
                "MATCH (called:Function) WHERE called.name = $methodName " +
                "RETURN called LIMIT 1",
                java.util.Map.of("methodName", calledMethod)
            );

            if (result.hasNext()) {
                Node calledNode = (Node) result.next().get("called");

                // Pour l'instant, on ne crée pas de relation car on ne sait pas
                // exactement quelle méthode fait l'appel
                // On pourrait améliorer ça en analysant le contexte (dans quelle méthode se trouve cet appel)

                logger.debug("      → Appel détecté: {}.{}()", caller, calledMethod);
            }
        } catch (Exception e) {
            // Ignorer les erreurs de résolution
            logger.trace("Impossible de résoudre l'appel: {}.{}", caller, calledMethod);
        }
    }

    /**
     * Extrait les méthodes d'une classe Java.
     * @param classNode le nœud de la classe
     * @param classFqn le FQN de la classe
     * @param content le contenu du fichier
     * @param tx la transaction Neo4j
     * @return le nombre de méthodes extraites
     */
    private int extractJavaMethods(Node classNode, String classFqn, String content, Transaction tx) {
        int methodCount = 0;
        // Pattern amélioré pour détecter les méthodes avec annotations
        Pattern methodPattern = Pattern.compile(
            "(?:@\\w+(?:\\([^)]*\\))?\\s*)?" +  // annotation optionnelle
            "(public|private|protected)?\\s*" +  // visibilité
            "(static\\s+)?" +                    // static optionnel
            "(final\\s+)?" +                     // final optionnel
            "(synchronized\\s+)?" +              // synchronized optionnel
            "([\\w<>\\[\\].,\\s]+)\\s+" +       // type de retour
            "(\\w+)\\s*" +                       // nom de la méthode
            "\\(([^)]*)\\)"                      // paramètres
        );
        Matcher methodMatcher = methodPattern.matcher(content);

        while (methodMatcher.find()) {
            String visibility = methodMatcher.group(1);
            String isStatic = methodMatcher.group(2);
            String returnType = methodMatcher.group(5);
            String methodName = methodMatcher.group(6);
            String parameters = methodMatcher.group(7);

            // Filtrer les faux positifs (mots-clés Java qui ressemblent à des méthodes)
            if (isJavaKeyword(methodName) || isControlStructure(returnType)) {
                continue;
            }

            // Vérifier que c'est bien une méthode (pas une déclaration de variable)
            if (returnType != null && !returnType.trim().isEmpty()) {
                // Calculer le FQN de la méthode
                String methodFqn = buildMethodFqn(classFqn, methodName, parameters);

                Node methodNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FUNCTION));
                methodNode.setProperty("name", methodName);
                methodNode.setProperty("fqn", methodFqn);  // FQN complet
                methodNode.setProperty("returnType", returnType.trim());

                if (visibility != null) {
                    methodNode.setProperty("visibility", visibility);
                }

                if (isStatic != null) {
                    methodNode.setProperty("static", true);
                }

                if (parameters != null && !parameters.trim().isEmpty()) {
                    methodNode.setProperty("parameters", parameters.trim());

                    // Créer des nœuds Parameter et relations USES
                    createParametersAndRelations(methodNode, parameters, tx);
                }

                // Créer une relation RETURNS pour le type de retour
                if (!returnType.trim().equals("void")) {
                    createReturnsRelation(methodNode, returnType.trim(), tx);
                }

                classNode.createRelationshipTo(methodNode, RelationType.HAS_METHOD);
                methodCount++;
                logger.debug("    → Méthode créée: {} (FQN: {})", methodName, methodFqn);
            }
        }

        return methodCount;
    }

    /**
     * Extrait les méthodes d'une classe avec JavaParser (remplace la version regex).
     * @param classNode le nœud de la classe
     * @param cls la déclaration de classe JavaParser
     * @param classFqn le FQN de la classe
     * @param tx la transaction Neo4j
     * @return le nombre de méthodes extraites
     */
    private int extractMethodsWithParser(
            Node classNode,
            ClassOrInterfaceDeclaration cls,
            String classFqn,
            Transaction tx) {
        int methodCount = 0;

        for (MethodDeclaration method : cls.getMethods()) {
            String methodName = method.getNameAsString();
            String returnType = method.getType().asString();
            String visibility = method.getAccessSpecifier().asString();

            // Construire signature pour FQN
            String signature = buildMethodSignatureFromParser(method.getParameters());
            String methodFqn = classFqn + "." + methodName + "(" + signature + ")";

            Node methodNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FUNCTION));
            methodNode.setProperty("name", methodName);
            methodNode.setProperty("fqn", methodFqn);
            methodNode.setProperty("returnType", returnType);
            methodNode.setProperty("visibility", visibility);
            methodNode.setProperty("isStatic", method.isStatic());
            methodNode.setProperty("isAbstract", method.isAbstract());
            methodNode.setProperty("isFinal", method.isFinal());

            classNode.createRelationshipTo(methodNode, RelationType.DECLARES);

            // Extraire paramètres avec JavaParser
            extractParametersWithParser(methodNode, method.getParameters(), tx);

            // Extraire annotations
            extractAnnotationsWithParser(methodNode, method, tx);

            // Créer relation RETURNS si non-void
            if (!returnType.equals("void")) {
                createReturnsRelation(methodNode, returnType, tx);
            }

            methodCount++;
            logger.debug("    → Méthode créée: {} (FQN: {})", methodName, methodFqn);
        }

        return methodCount;
    }

    /**
     * Extrait les constructeurs d'une classe avec JavaParser.
     */
    private int extractConstructorsWithParser(
            Node classNode,
            ClassOrInterfaceDeclaration cls,
            String classFqn,
            Transaction tx) {
        int count = 0;

        for (ConstructorDeclaration constructor : cls.getConstructors()) {
            String visibility = constructor.getAccessSpecifier().asString();
            String signature = buildMethodSignatureFromParser(constructor.getParameters());
            String constructorFqn = classFqn + ".<init>(" + signature + ")";

            Node constructorNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CONSTRUCTOR));
            constructorNode.setProperty("name", cls.getNameAsString());
            constructorNode.setProperty("fqn", constructorFqn);
            constructorNode.setProperty("visibility", visibility);

            classNode.createRelationshipTo(constructorNode, RelationType.DECLARES);

            // Extraire paramètres
            extractParametersWithParser(constructorNode, constructor.getParameters(), tx);

            // Extraire annotations
            extractAnnotationsWithParser(constructorNode, constructor, tx);

            count++;
            logger.debug("    → Constructeur créé: {} (FQN: {})", cls.getNameAsString(), constructorFqn);
        }

        return count;
    }

    /**
     * Extrait les fields/propriétés d'une classe avec JavaParser.
     */
    private int extractFieldsWithParser(
            Node classNode,
            ClassOrInterfaceDeclaration cls,
            String classFqn,
            Transaction tx) {
        int count = 0;

        for (FieldDeclaration field : cls.getFields()) {
            String type = field.getCommonType().asString();
            String visibility = field.getAccessSpecifier().asString();

            for (com.github.javaparser.ast.body.VariableDeclarator var : field.getVariables()) {
                String fieldName = var.getNameAsString();
                String fieldFqn = classFqn + "." + fieldName;

                Node propertyNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_PROPERTY));
                propertyNode.setProperty("name", fieldName);
                propertyNode.setProperty("fqn", fieldFqn);
                propertyNode.setProperty("type", type);
                propertyNode.setProperty("visibility", visibility);
                propertyNode.setProperty("isStatic", field.isStatic());
                propertyNode.setProperty("isFinal", field.isFinal());

                classNode.createRelationshipTo(propertyNode, RelationType.DECLARES);

                // Extraire annotations
                extractAnnotationsWithParser(propertyNode, field, tx);

                count++;
                logger.debug("    → Field créé: {} (type: {})", fieldName, type);
            }
        }

        return count;
    }

    /**
     * Extrait les méthodes d'un enum avec JavaParser.
     */
    private int extractEnumMethodsWithParser(
            Node enumNode,
            EnumDeclaration enumDecl,
            String enumFqn,
            Transaction tx) {
        int count = 0;

        for (MethodDeclaration method : enumDecl.getMethods()) {
            String methodName = method.getNameAsString();
            String returnType = method.getType().asString();
            String visibility = method.getAccessSpecifier().asString();
            String signature = buildMethodSignatureFromParser(method.getParameters());
            String methodFqn = enumFqn + "." + methodName + "(" + signature + ")";

            Node methodNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FUNCTION));
            methodNode.setProperty("name", methodName);
            methodNode.setProperty("fqn", methodFqn);
            methodNode.setProperty("returnType", returnType);
            methodNode.setProperty("visibility", visibility);
            methodNode.setProperty("isStatic", method.isStatic());

            enumNode.createRelationshipTo(methodNode, RelationType.DECLARES);

            extractParametersWithParser(methodNode, method.getParameters(), tx);
            extractAnnotationsWithParser(methodNode, method, tx);

            count++;
        }

        return count;
    }

    /**
     * Extrait les fields d'un enum avec JavaParser.
     */
    private int extractEnumFieldsWithParser(
            Node enumNode,
            EnumDeclaration enumDecl,
            String enumFqn,
            Transaction tx) {
        int count = 0;

        for (FieldDeclaration field : enumDecl.getFields()) {
            String type = field.getCommonType().asString();
            String visibility = field.getAccessSpecifier().asString();

            for (com.github.javaparser.ast.body.VariableDeclarator var : field.getVariables()) {
                String fieldName = var.getNameAsString();
                String fieldFqn = enumFqn + "." + fieldName;

                Node propertyNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_PROPERTY));
                propertyNode.setProperty("name", fieldName);
                propertyNode.setProperty("fqn", fieldFqn);
                propertyNode.setProperty("type", type);
                propertyNode.setProperty("visibility", visibility);
                propertyNode.setProperty("isStatic", field.isStatic());

                enumNode.createRelationshipTo(propertyNode, RelationType.DECLARES);

                extractAnnotationsWithParser(propertyNode, field, tx);

                count++;
            }
        }

        return count;
    }

    /**
     * Extrait les méthodes d'un record avec JavaParser.
     */
    private int extractRecordMethodsWithParser(
            Node recordNode,
            RecordDeclaration recordDecl,
            String recordFqn,
            Transaction tx) {
        int count = 0;

        for (MethodDeclaration method : recordDecl.getMethods()) {
            String methodName = method.getNameAsString();
            String returnType = method.getType().asString();
            String visibility = method.getAccessSpecifier().asString();
            String signature = buildMethodSignatureFromParser(method.getParameters());
            String methodFqn = recordFqn + "." + methodName + "(" + signature + ")";

            Node methodNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FUNCTION));
            methodNode.setProperty("name", methodName);
            methodNode.setProperty("fqn", methodFqn);
            methodNode.setProperty("returnType", returnType);
            methodNode.setProperty("visibility", visibility);
            methodNode.setProperty("isStatic", method.isStatic());

            recordNode.createRelationshipTo(methodNode, RelationType.DECLARES);

            extractParametersWithParser(methodNode, method.getParameters(), tx);
            extractAnnotationsWithParser(methodNode, method, tx);

            count++;
        }

        return count;
    }

    /**
     * Construit une signature de méthode à partir des paramètres JavaParser.
     */
    private String buildMethodSignatureFromParser(com.github.javaparser.ast.NodeList<com.github.javaparser.ast.body.Parameter> parameters) {
        return parameters.stream()
                .map(p -> p.getType().asString())
                .collect(java.util.stream.Collectors.joining(","));
    }

    /**
     * Extrait les paramètres d'une méthode/constructeur avec JavaParser.
     */
    private void extractParametersWithParser(
            Node methodNode,
            com.github.javaparser.ast.NodeList<com.github.javaparser.ast.body.Parameter> parameters,
            Transaction tx) {
        for (int i = 0; i < parameters.size(); i++) {
            com.github.javaparser.ast.body.Parameter param = parameters.get(i);

            Node paramNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_PARAMETER));
            paramNode.setProperty("name", param.getNameAsString());
            paramNode.setProperty("type", param.getType().asString());
            paramNode.setProperty("position", i);
            paramNode.setProperty("isVarArgs", param.isVarArgs());

            methodNode.createRelationshipTo(paramNode, RelationType.HAS_PARAMETER);

            // Créer relation USES vers le type si custom
            String paramType = param.getType().asString();
            if (isCustomType(cleanType(paramType))) {
                createUsesRelation(methodNode, paramType, tx);
            }
        }
    }

    /**
     * Extrait les annotations d'un élément avec JavaParser.
     */
    private void extractAnnotationsWithParser(
            Node targetNode,
            com.github.javaparser.ast.nodeTypes.NodeWithAnnotations<?> annotated,
            Transaction tx) {
        for (com.github.javaparser.ast.expr.AnnotationExpr annotation : annotated.getAnnotations()) {
            String annotationName = annotation.getNameAsString();

            Node annotationNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_ANNOTATION));
            annotationNode.setProperty("name", annotationName);

            targetNode.createRelationshipTo(annotationNode, RelationType.ANNOTATED_WITH);

            logger.trace("      → Annotation: @{}", annotationName);
        }
    }

    /**
     * Crée des nœuds Parameter pour une méthode et des relations USES vers les types.
     * @param methodNode le nœud de la méthode
     * @param parameters la chaîne de paramètres (ex: "String name, int age")
     * @param tx la transaction Neo4j
     * @deprecated Utiliser extractParametersWithParser() à la place
     */
    private void createParametersAndRelations(Node methodNode, String parameters, Transaction tx) {
        if (parameters == null || parameters.trim().isEmpty()) {
            return;
        }

        String[] params = parameters.split(",");
        for (int i = 0; i < params.length; i++) {
            String param = params[i].trim();
            if (param.isEmpty()) continue;

            // Parser le paramètre: "Type name" ou "Type... name" ou "@Annotation Type name"
            String[] parts = param.split("\\s+");
            if (parts.length < 2) continue;

            // Le type est le premier mot non-annotation
            String paramType = null;
            String paramName = null;

            for (int j = 0; j < parts.length; j++) {
                if (!parts[j].startsWith("@")) {
                    if (paramType == null) {
                        paramType = parts[j].replace("...", ""); // Enlever varargs
                        paramType = paramType.replace("final", "").trim(); // Enlever final
                    } else {
                        paramName = parts[j];
                        break;
                    }
                }
            }

            if (paramType != null && !paramType.isEmpty()) {
                // Créer le nœud Parameter
                Node paramNode = tx.createNode(org.neo4j.graphdb.Label.label("Parameter"));
                if (paramName != null) {
                    paramNode.setProperty("name", paramName);
                }
                paramNode.setProperty("type", paramType);
                paramNode.setProperty("position", i);

                // Relation de la méthode vers le paramètre
                methodNode.createRelationshipTo(paramNode, org.neo4j.graphdb.RelationshipType.withName("HAS_PARAMETER"));

                // Créer une relation USES vers le type (si c'est un type custom)
                if (isCustomType(paramType)) {
                    createUsesRelation(methodNode, paramType, tx);
                }

                logger.debug("      → Paramètre créé: {} (type: {})", paramName, paramType);
            }
        }
    }

    /**
     * Crée une relation RETURNS d'une méthode vers un type.
     * @param methodNode le nœud de la méthode
     * @param returnType le type de retour
     * @param tx la transaction Neo4j
     */
    private void createReturnsRelation(Node methodNode, String returnType, Transaction tx) {
        if (returnType == null || returnType.isEmpty() || returnType.equals("void")) {
            return;
        }

        // Nettoyer le type de retour (enlever les génériques, arrays, etc.)
        String cleanType = cleanType(returnType);

        // Créer une relation RETURNS vers le type (si c'est un type custom)
        if (isCustomType(cleanType)) {
            // Trouver ou créer un nœud pour ce type
            Node typeNode = findOrCreateTypeNode(cleanType, tx);
            methodNode.createRelationshipTo(typeNode, org.neo4j.graphdb.RelationshipType.withName("RETURNS"));
            logger.debug("      → Relation RETURNS créée vers: {}", cleanType);
        }
    }

    /**
     * Crée une relation USES d'une méthode vers un type.
     * @param methodNode le nœud de la méthode
     * @param type le type utilisé
     * @param tx la transaction Neo4j
     */
    private void createUsesRelation(Node methodNode, String type, Transaction tx) {
        String cleanType = cleanType(type);
        if (isCustomType(cleanType)) {
            Node typeNode = findOrCreateTypeNode(cleanType, tx);
            methodNode.createRelationshipTo(typeNode, org.neo4j.graphdb.RelationshipType.withName("USES"));
            logger.debug("      → Relation USES créée vers: {}", cleanType);
        }
    }

    /**
     * Nettoie un type en enlevant les génériques et les arrays.
     * Exemple: "List<String>" -> "List", "String[]" -> "String"
     */
    private String cleanType(String type) {
        if (type == null) return "";

        // Enlever les génériques
        int genericStart = type.indexOf('<');
        if (genericStart > 0) {
            type = type.substring(0, genericStart);
        }

        // Enlever les arrays
        type = type.replace("[]", "");

        // Enlever les espaces
        return type.trim();
    }

    /**
     * Vérifie si un type est un type custom (pas un type primitif Java).
     */
    private boolean isCustomType(String type) {
        if (type == null || type.isEmpty()) return false;

        // Types primitifs Java
        String[] primitives = {"void", "boolean", "byte", "short", "int", "long", "float", "double", "char",
                              "Boolean", "Byte", "Short", "Integer", "Long", "Float", "Double", "Character",
                              "String", "Object", "List", "Map", "Set", "Collection", "ArrayList", "HashMap"};

        for (String primitive : primitives) {
            if (type.equals(primitive)) {
                return false;
            }
        }

        return true;
    }

    /**
     * Trouve ou crée un nœud pour un type donné.
     * Recherche d'abord par nom, sinon crée un nouveau nœud Class.
     */
    private Node findOrCreateTypeNode(String typeName, Transaction tx) {
        // Chercher d'abord si le type existe déjà
        var result = tx.execute(
            "MATCH (c:Class {name: $name}) RETURN c LIMIT 1",
            java.util.Map.of("name", typeName)
        );

        if (result.hasNext()) {
            return (Node) result.next().get("c");
        }

        // Sinon créer un nouveau nœud
        Node typeNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
        typeNode.setProperty("name", typeName);
        typeNode.setProperty("fqn", typeName); // On ne connaît pas le package, utiliser le nom simple
        return typeNode;
    }

    /**
     * Vérifie si un mot est un mot-clé Java.
     */
    private boolean isJavaKeyword(String word) {
        String[] keywords = {"if", "for", "while", "switch", "try", "catch", "finally",
                            "return", "throw", "new", "super", "this", "void"};
        for (String keyword : keywords) {
            if (word.equals(keyword)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Vérifie si un type ressemble à une structure de contrôle.
     */
    private boolean isControlStructure(String type) {
        if (type == null) return false;
        String trimmed = type.trim();
        return trimmed.equals("if") || trimmed.equals("for") || trimmed.equals("while") ||
               trimmed.equals("switch") || trimmed.equals("try") || trimmed.equals("catch");
    }

    /**
     * Extrait les entités d'un fichier JavaScript/TypeScript.
     * @return le nombre d'entités extraites
     */
    private int extractJavaScriptEntities(Node fileNode, String content, Transaction tx) {
        int entityCount = 0;
        // Extraire les imports ES6
        Pattern importPattern = Pattern.compile("import\\s+.*?from\\s+['\"]([^'\"]+)['\"]");
        Matcher importMatcher = importPattern.matcher(content);
        while (importMatcher.find()) {
            String importName = importMatcher.group(1);
            Node importNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_IMPORT));
            importNode.setProperty("name", importName);
            fileNode.createRelationshipTo(importNode, RelationType.IMPORTS);
            entityCount++;
        }

        // Extraire les classes
        Pattern classPattern = Pattern.compile("class\\s+(\\w+)");
        Matcher classMatcher = classPattern.matcher(content);
        while (classMatcher.find()) {
            String className = classMatcher.group(1);
            Node classNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
            classNode.setProperty("name", className);
            classNode.setProperty("type", "class");
            fileNode.createRelationshipTo(classNode, RelationType.CONTAINS);
            entityCount++;
        }

        // Extraire les fonctions
        Pattern functionPattern = Pattern.compile("function\\s+(\\w+)\\s*\\(|const\\s+(\\w+)\\s*=\\s*\\(");
        Matcher functionMatcher = functionPattern.matcher(content);
        while (functionMatcher.find()) {
            String functionName = functionMatcher.group(1) != null ?
                                functionMatcher.group(1) : functionMatcher.group(2);
            Node functionNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FUNCTION));
            functionNode.setProperty("name", functionName);
            fileNode.createRelationshipTo(functionNode, RelationType.CONTAINS);
            entityCount++;
        }

        return entityCount;
    }

    /**
     * Extrait les entités d'un fichier Python.
     * @return le nombre d'entités extraites
     */
    private int extractPythonEntities(Node fileNode, String content, Transaction tx) {
        int entityCount = 0;
        // Extraire les imports
        Pattern importPattern = Pattern.compile("(?:from\\s+([\\w.]+)\\s+)?import\\s+([\\w., ]+)");
        Matcher importMatcher = importPattern.matcher(content);
        while (importMatcher.find()) {
            String importName = importMatcher.group(1) != null ?
                              importMatcher.group(1) : importMatcher.group(2);
            Node importNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_IMPORT));
            importNode.setProperty("name", importName);
            fileNode.createRelationshipTo(importNode, RelationType.IMPORTS);
            entityCount++;
        }

        // Extraire les classes
        Pattern classPattern = Pattern.compile("class\\s+(\\w+)");
        Matcher classMatcher = classPattern.matcher(content);
        while (classMatcher.find()) {
            String className = classMatcher.group(1);
            Node classNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
            classNode.setProperty("name", className);
            classNode.setProperty("type", "class");
            fileNode.createRelationshipTo(classNode, RelationType.CONTAINS);
            entityCount++;
        }

        // Extraire les fonctions
        Pattern functionPattern = Pattern.compile("def\\s+(\\w+)\\s*\\(");
        Matcher functionMatcher = functionPattern.matcher(content);
        while (functionMatcher.find()) {
            String functionName = functionMatcher.group(1);
            Node functionNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FUNCTION));
            functionNode.setProperty("name", functionName);
            fileNode.createRelationshipTo(functionNode, RelationType.CONTAINS);
            entityCount++;
        }

        return entityCount;
    }

    @Override
    public List<String> retrieveContext(String query) throws Exception {
        ensureInitialized();
        logger.info("Recherche de contexte hybride (BM25 + vecteur) pour: {}", query);

        // Recherche hybride via AdvancedSearchService si disponible
        if (advancedSearchService != null) {
            try {
                return retrieveContextHybrid(query);
            } catch (SearchException e) {
                logger.warn("Recherche hybride échouée, fallback sur mots-clés: {}", e.getMessage());
            }
        }

        // Fallback : recherche par mots-clés
        return retrieveContextKeywords(query);
    }

    /**
     * Recherche hybride : BM25 fulltext + vecteur + expansion graphe K-hop.
     */
    private List<String> retrieveContextHybrid(String query) throws SearchException {
        List<EntryPoint> entryPoints = advancedSearchService.findEntryPoints(query, 5);
        logger.info("Recherche hybride : {} points d'entrée trouvés", entryPoints.size());

        return entryPoints.stream()
            .map(ep -> formatEntryPointAsContext(ep))
            .collect(Collectors.toList());
    }

    /**
     * Formate un EntryPoint comme chunk de contexte pour le LLM.
     * Enrichit avec le contenu du fichier source si disponible.
     */
    private String formatEntryPointAsContext(EntryPoint ep) {
        StringBuilder ctx = new StringBuilder();
        ctx.append(String.format("=== %s [%s] ===\n", ep.fqn(), ep.nodeType()));

        String javaDoc = (String) ep.properties().get("javaDoc");
        String signature = (String) ep.properties().get("signature");

        if (signature != null && !signature.isBlank()) {
            ctx.append("Signature: ").append(signature).append("\n");
        }
        if (javaDoc != null && !javaDoc.isBlank()) {
            ctx.append("Documentation: ").append(javaDoc).append("\n");
        }

        // Récupérer le contenu du fichier source via le graphe
        try (Session session = boltDriver.session()) {
            var result = session.run("""
                MATCH (n)-[:CONTAINS|DECLARES*1..2]-(f:File)
                WHERE id(n) = $id
                RETURN f.content as content, f.path as path
                LIMIT 1
                """, Map.of("id", ep.nodeId()));
            if (result.hasNext()) {
                var record = result.next();
                String path = record.get("path").asString("");
                String content = record.get("content").asString("");
                if (!content.isBlank()) {
                    // Inclure seulement les 50 premières lignes pour ne pas surcharger le LLM
                    String[] lines = content.split("\n");
                    int limit = Math.min(lines.length, 50);
                    ctx.append("Source (").append(path).append("):\n");
                    for (int i = 0; i < limit; i++) {
                        ctx.append(lines[i]).append("\n");
                    }
                }
            }
        } catch (Exception e) {
            logger.debug("Impossible de récupérer le fichier source pour {}: {}", ep.fqn(), e.getMessage());
        }

        return ctx.toString();
    }

    /**
     * Fallback : recherche par mots-clés Cypher (comportement original).
     */
    private List<String> retrieveContextKeywords(String query) {
        logger.info("Recherche par mots-clés pour: {}", query);
        List<String> results = new ArrayList<>();

        try (Transaction tx = graphDb.beginTx()) {
            List<String> keywords = extractKeywords(query);
            String cypher = buildSearchQuery(keywords);
            var result = tx.execute(cypher);

            while (result.hasNext()) {
                var row = result.next();
                Node fileNode = (Node) row.get("file");
                String filePath = (String) fileNode.getProperty("path");
                String content = (String) fileNode.getProperty("content");
                Object scoreObj = row.get("score");
                double score = scoreObj instanceof Long ?
                    ((Long) scoreObj).doubleValue() : ((Number) scoreObj).doubleValue();

                results.add(String.format("=== %s (score: %.2f) ===\n%s\n", filePath, score, content));
            }
            tx.commit();

            if (results.size() > 5) results = results.subList(0, 5);
            logger.info("Trouvé {} fichiers pertinents (mots-clés)", results.size());
        } catch (Exception e) {
            logger.error("Erreur recherche mots-clés", e);
        }

        return results;
    }

    /**
     * Extrait les mots-clés pertinents de la requête.
     */
    private List<String> extractKeywords(String query) {
        List<String> keywords = new ArrayList<>();

        // Extraire les mots commençant par une majuscule (probablement des noms de classes)
        Pattern classNamePattern = Pattern.compile("\\b([A-Z][a-zA-Z0-9_]*)\\b");
        Matcher matcher = classNamePattern.matcher(query);
        while (matcher.find()) {
            keywords.add(matcher.group(1));
        }

        // Nettoyer et extraire les mots-clés techniques
        String[] technicalKeywords = query.toLowerCase()
            .split("\\s+");

        for (String word : technicalKeywords) {
            // Nettoyer les articles et prépositions français avec apostrophes
            word = cleanFrenchWord(word);

            // Garder seulement les mots significatifs (> 3 caractères et pas des stopwords)
            if (word.length() > 3 && !isStopWord(word)) {
                keywords.add(word);
            }
        }

        logger.debug("Mots-clés extraits: {}", keywords);
        return keywords;
    }

    /**
     * Nettoie un mot français en retirant les articles et prépositions avec apostrophe.
     * Ex: "l'application" -> "application", "d'indexation" -> "indexation"
     */
    private String cleanFrenchWord(String word) {
        // Enlever l', d', qu', s', c', j', m', t', n' (apostrophe droite)
        word = word.replaceAll("^[ldqscjmtn]'", "");

        // Enlever l', d', qu', s', c', j', m', t', n' (apostrophe courbe Unicode)
        word = word.replaceAll("^[ldqscjmtn]'", "");

        // Enlever toutes les apostrophes restantes
        word = word.replace("'", "").replace("'", "");

        // Enlever la ponctuation en fin de mot
        word = word.replaceAll("[,;:.!?]+$", "");

        return word.trim();
    }

    /**
     * Vérifie si un mot est un mot vide (stop word).
     */
    private boolean isStopWord(String word) {
        String[] stopWords = {
            // Français
            "comment", "quelle", "quel", "quels", "quelles", "dans", "pour", "avec",
            "mais", "ou", "donc", "car", "ni", "sur", "sous", "entre", "vers",
            "chez", "sans", "des", "les", "une", "cette", "sont", "sera",
            "fait", "peut", "dois", "dois", "avoir", "être", "faire",
            // Anglais
            "what", "how", "where", "when", "which", "that", "this", "these",
            "those", "from", "with", "about", "into", "through", "during"
        };

        for (String stopWord : stopWords) {
            if (word.equals(stopWord)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Construit la requête Cypher pour rechercher dans le graphe.
     * Utilise CONTAINS pour rechercher dans le contenu et les noms d'entités.
     */
    private String buildSearchQuery(List<String> keywords) {
        if (keywords.isEmpty()) {
            // Si pas de mots-clés, retourner tous les fichiers (limité)
            return "MATCH (file:File) RETURN file, 1.0 as score LIMIT 5";
        }

        // Construire les conditions de recherche
        StringBuilder cypher = new StringBuilder();
        cypher.append("MATCH (file:File) ");
        cypher.append("OPTIONAL MATCH (file)-[:CONTAINS]->(entity) ");
        cypher.append("WHERE ");

        List<String> conditions = new ArrayList<>();
        for (String keyword : keywords) {
            if (keyword.length() >= 3) {  // Ignorer les mots trop courts
                // Recherche dans le contenu du fichier
                conditions.add("toLower(file.content) CONTAINS toLower('" + escapeCypher(keyword) + "')");
                conditions.add("toLower(file.name) CONTAINS toLower('" + escapeCypher(keyword) + "')");
                // Recherche dans les noms d'entités
                conditions.add("toLower(entity.name) CONTAINS toLower('" + escapeCypher(keyword) + "')");
            }
        }

        if (conditions.isEmpty()) {
            return "MATCH (file:File) RETURN file, 1.0 as score LIMIT 5";
        }

        cypher.append(String.join(" OR ", conditions));
        cypher.append(" RETURN DISTINCT file, COUNT(entity) + 1 as score ");
        cypher.append("ORDER BY score DESC LIMIT 10");

        String finalQuery = cypher.toString();
        logger.debug("Requête Cypher générée: {}", finalQuery);

        return finalQuery;
    }

    /**
     * Échappe les apostrophes pour Cypher.
     */
    private String escapeCypher(String value) {
        return value.replace("'", "\\'");
    }



    @Override
    public String getStrategyName() {
        return "GraphRAG (Neo4j Embedded)";
    }

    @Override
    public void close() throws Exception {
        logger.info("Fermeture de Neo4j GraphRAG");
        // Fermer le driver bolt avant Neo4j
        if (boltDriver != null) {
            try { boltDriver.close(); } catch (Exception e) { logger.debug("Erreur fermeture bolt driver: {}", e.getMessage()); }
        }
        if (managementService != null) {
            managementService.shutdown();
        }
    }

    /**
     * Alias pour close() - ferme Neo4j proprement.
     */
    public void shutdown() {
        try {
            close();
        } catch (Exception e) {
            logger.error("Erreur lors du shutdown: {}", e.getMessage());
        }
    }

    /**
     * Nettoie complètement la base de données (supprime tous les nœuds et relations).
     * Utile avant une réindexation pour éviter les doublons.
     */
    public void clearDatabase() {
        ensureInitialized();

        logger.info("🗑️  Nettoyage de la base de données Neo4j...");

        try (Transaction tx = graphDb.beginTx()) {
            // Supprimer tous les nœuds et relations
            long deletedNodes = 0;
            long deletedRelationships = 0;

            // Compter d'abord
            var countResult = tx.execute("MATCH (n) RETURN count(n) as nodeCount");
            if (countResult.hasNext()) {
                deletedNodes = (Long) countResult.next().get("nodeCount");
            }

            var relCountResult = tx.execute("MATCH ()-[r]->() RETURN count(r) as relCount");
            if (relCountResult.hasNext()) {
                deletedRelationships = (Long) relCountResult.next().get("relCount");
            }

            // Supprimer tout (DETACH DELETE supprime aussi les relations)
            tx.execute("MATCH (n) DETACH DELETE n");

            tx.commit();

            logger.info("✅ Base de données nettoyée:");
            logger.info("   - {} nœuds supprimés", deletedNodes);
            logger.info("   - {} relations supprimées", deletedRelationships);

        } catch (Exception e) {
            logger.error("❌ Erreur lors du nettoyage de la base de données", e);
            throw new RuntimeException("Impossible de nettoyer la base de données", e);
        }
    }

    /**
     * Retourne la base de données Neo4j (pour tests uniquement).
     */
    public GraphDatabaseService getGraphDb() {
        ensureInitialized();
        return graphDb;
    }

    /**
     * Affiche des statistiques sur le graphe pour debug.
     */
    public void printDatabaseStats() {
        if (!initialized) {
            logger.warn("Neo4j n'est pas initialisé");
            return;
        }

        try (Transaction tx = graphDb.beginTx()) {
            // Compter les différents types de nœuds
            long fileCount = (Long) tx.execute("MATCH (f:File) RETURN COUNT(f) as count")
                    .next().get("count");
            long classCount = (Long) tx.execute("MATCH (c:Class) RETURN COUNT(c) as count")
                    .next().get("count");
            long functionCount = (Long) tx.execute("MATCH (f:Function) RETURN COUNT(f) as count")
                    .next().get("count");
            long importCount = (Long) tx.execute("MATCH (i:Import) RETURN COUNT(i) as count")
                    .next().get("count");

            // Compter les relations
            long containsCount = (Long) tx.execute("MATCH ()-[r:CONTAINS]->() RETURN COUNT(r) as count")
                    .next().get("count");
            long importsCount = (Long) tx.execute("MATCH ()-[r:IMPORTS]->() RETURN COUNT(r) as count")
                    .next().get("count");

            logger.info("=== Statistiques Neo4j ===");
            logger.info("Fichiers: {}", fileCount);
            logger.info("Classes: {}", classCount);
            logger.info("Fonctions: {}", functionCount);
            logger.info("Imports: {}", importCount);
            logger.info("Relations CONTAINS: {}", containsCount);
            logger.info("Relations IMPORTS: {}", importsCount);

            // Afficher quelques exemples de fichiers
            logger.info("=== Exemples de fichiers indexés ===");
            var files = tx.execute("MATCH (f:File) RETURN f.name as name, f.size as size LIMIT 5");
            while (files.hasNext()) {
                var file = files.next();
                logger.info("  - {} ({} bytes)", file.get("name"), file.get("size"));
            }

            // Afficher quelques exemples de classes
            logger.info("=== Exemples de classes ===");
            var classes = tx.execute("MATCH (c:Class) RETURN c.name as name, c.type as type LIMIT 5");
            while (classes.hasNext()) {
                var cls = classes.next();
                logger.info("  - {} ({})", cls.get("name"), cls.get("type"));
            }

            tx.commit();
        } catch (Exception e) {
            logger.error("Erreur lors de l'affichage des stats", e);
        }
    }

    /**
     * Exécute une requête Cypher personnalisée pour debug.
     */
    public void executeDebugQuery(String cypherQuery) {
        if (!initialized) {
            ensureInitialized();
        }

        try (Transaction tx = graphDb.beginTx()) {
            logger.info("=== Exécution requête Cypher ===");
            logger.info("Query: {}", cypherQuery);

            var result = tx.execute(cypherQuery);

            int count = 0;
            while (result.hasNext() && count < 10) {  // Limiter à 10 résultats
                var row = result.next();
                logger.info("Résultat {}: {}", count + 1, row);
                count++;
            }

            if (count == 0) {
                logger.warn("Aucun résultat trouvé pour cette requête");
            } else {
                logger.info("Total: {} résultats affichés", count);
            }

            tx.commit();
        } catch (Exception e) {
            logger.error("Erreur lors de l'exécution de la requête: {}", cypherQuery, e);
        }
    }

    /**
     * Exécute une requête Cypher et retourne les résultats formatés.
     * Utilisé par la console de debug.
     */
    public void executeDebugQueryWithResult(String cypherQuery, StringBuilder output) {
        if (!initialized) {
            ensureInitialized();
        }

        try (Transaction tx = graphDb.beginTx()) {
            var result = tx.execute(cypherQuery);

            // Récupérer les colonnes
            var columns = result.columns();
            if (columns.isEmpty()) {
                output.append("Aucune colonne retournée.\n");
                tx.commit();
                return;
            }

            // Afficher l'en-tête
            output.append(String.join(" | ", columns)).append("\n");
            output.append("-".repeat(80)).append("\n");

            int count = 0;
            int maxResults = 100; // Limiter pour ne pas surcharger l'UI

            while (result.hasNext() && count < maxResults) {
                var row = result.next();
                StringBuilder line = new StringBuilder();

                for (String column : columns) {
                    Object value = row.get(column);
                    String strValue = formatValue(value);
                    line.append(strValue).append(" | ");
                }

                output.append(line.toString()).append("\n");
                count++;
            }

            if (count == 0) {
                output.append("\n(Aucun résultat)\n");
            } else {
                output.append("\n").append(count).append(" résultat(s) trouvé(s)");
                if (result.hasNext()) {
                    output.append(" (limité à ").append(maxResults).append(" premiers)");
                }
                output.append(".\n");
            }

            tx.commit();

        } catch (Exception e) {
            output.append("\nERREUR lors de l'exécution:\n");
            output.append(e.getClass().getSimpleName()).append(": ").append(e.getMessage()).append("\n");
            logger.error("Erreur lors de l'exécution de la requête debug", e);
        }
    }

    /**
     * Formate une valeur pour l'affichage (tronque les longs textes).
     */
    private String formatValue(Object value) {
        if (value == null) {
            return "null";
        }

        if (value instanceof Node) {
            Node node = (Node) value;
            StringBuilder sb = new StringBuilder("(");
            node.getLabels().forEach(label -> sb.append(":").append(label.name()));
            sb.append(" {");
            node.getAllProperties().forEach((key, val) -> {
                String strVal = val.toString();
                if (strVal.length() > 50) {
                    strVal = strVal.substring(0, 47) + "...";
                }
                sb.append(key).append(": ").append(strVal).append(", ");
            });
            if (sb.length() > 2) {
                sb.setLength(sb.length() - 2); // Enlever la dernière virgule
            }
            sb.append("})");
            return sb.toString();
        }

        String str = value.toString();
        if (str.length() > 100) {
            return str.substring(0, 97) + "...";
        }
        return str;
    }

    /**
     * Exporte le graphe Neo4j vers un fichier Cypher pour Neo4j Desktop.
     *
     * @param outputPath chemin du fichier de sortie
     * @throws Exception si une erreur survient
     */
    public void exportToCypherScript(Path outputPath) throws Exception {
        if (!initialized) {
            ensureInitialized();
        }

        logger.info("Début de l'export vers: {}", outputPath);

        try (Transaction tx = graphDb.beginTx();
             java.io.PrintWriter writer = new java.io.PrintWriter(
                     new java.io.BufferedWriter(
                             new java.io.FileWriter(outputPath.toFile())))) {

            // En-tête du script
            writer.println("// Export Neo4j GraphRAG - " + java.time.LocalDateTime.now());
            writer.println("// Généré automatiquement");
            writer.println();
            writer.println("// Nettoyer la base avant import (ATTENTION: supprime tout!)");
            writer.println("// MATCH (n) DETACH DELETE n;");
            writer.println();
            writer.println("// Créer les contraintes et index");
            writer.println("CREATE CONSTRAINT file_path_unique IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE;");
            writer.println("CREATE INDEX file_name_idx IF NOT EXISTS FOR (f:File) ON (f.name);");
            writer.println("CREATE INDEX class_name_idx IF NOT EXISTS FOR (c:Class) ON (c.name);");
            writer.println("CREATE INDEX function_name_idx IF NOT EXISTS FOR (fn:Function) ON (fn.name);");
            writer.println();

            // Map pour stocker les IDs internes et générer des variables
            java.util.Map<Long, String> nodeVars = new java.util.HashMap<>();
            int varCounter = 0;

            // 1. Exporter tous les nœuds
            writer.println("// ========== CRÉATION DES NŒUDS ==========");
            writer.println();

            var allNodes = tx.execute("MATCH (n) RETURN n, id(n) as nodeId ORDER BY id(n)");
            while (allNodes.hasNext()) {
                var row = allNodes.next();
                Node node = (Node) row.get("n");
                Long nodeId = (Long) row.get("nodeId");

                String varName = "n" + varCounter++;
                nodeVars.put(nodeId, varName);

                writer.print("CREATE (" + varName);

                // Labels
                node.getLabels().forEach(label -> writer.print(":" + label.name()));

                // Propriétés
                writer.print(" {");
                boolean first = true;
                for (var entry : node.getAllProperties().entrySet()) {
                    if (!first) writer.print(", ");
                    first = false;

                    String key = entry.getKey();
                    Object value = entry.getValue();

                    writer.print(key + ": ");
                    writer.print(escapeCypherValue(value));
                }
                writer.println("});");
            }

            writer.println();
            writer.println("// ========== CRÉATION DES RELATIONS ==========");
            writer.println();

            // 2. Exporter toutes les relations
            var allRels = tx.execute(
                "MATCH (a)-[r]->(b) " +
                "RETURN id(a) as startId, type(r) as relType, id(b) as endId, properties(r) as props"
            );

            while (allRels.hasNext()) {
                var row = allRels.next();
                Long startId = (Long) row.get("startId");
                Long endId = (Long) row.get("endId");
                String relType = (String) row.get("relType");
                @SuppressWarnings("unchecked")
                java.util.Map<String, Object> props = (java.util.Map<String, Object>) row.get("props");

                String startVar = nodeVars.get(startId);
                String endVar = nodeVars.get(endId);

                if (startVar != null && endVar != null) {
                    writer.print("CREATE (" + startVar + ")-[:" + relType);

                    if (props != null && !props.isEmpty()) {
                        writer.print(" {");
                        boolean first = true;
                        for (var entry : props.entrySet()) {
                            if (!first) writer.print(", ");
                            first = false;
                            writer.print(entry.getKey() + ": ");
                            writer.print(escapeCypherValue(entry.getValue()));
                        }
                        writer.print("}");
                    }

                    writer.println("]->(" + endVar + ");");
                }
            }

            writer.println();
            writer.println("// ========== FIN DE L'EXPORT ==========");
            writer.println("// Total de nœuds: " + nodeVars.size());

            tx.commit();
            logger.info("Export terminé: {} nœuds exportés vers {}", nodeVars.size(), outputPath);

        } catch (Exception e) {
            logger.error("Erreur lors de l'export", e);
            throw e;
        }
    }

    /**
     * Échappe une valeur pour l'insertion dans Cypher.
     */
    private String escapeCypherValue(Object value) {
        if (value == null) {
            return "null";
        }

        if (value instanceof String) {
            String str = (String) value;
            // Échapper les caractères spéciaux
            str = str.replace("\\", "\\\\")
                     .replace("\"", "\\\"")
                     .replace("\n", "\\n")
                     .replace("\r", "\\r")
                     .replace("\t", "\\t");
            return "\"" + str + "\"";
        }

        if (value instanceof Number || value instanceof Boolean) {
            return value.toString();
        }

        if (value instanceof java.util.List) {
            @SuppressWarnings("unchecked")
            java.util.List<Object> list = (java.util.List<Object>) value;
            return "[" + list.stream()
                    .map(this::escapeCypherValue)
                    .collect(java.util.stream.Collectors.joining(", ")) + "]";
        }

        // Pour les autres types, convertir en string
        return escapeCypherValue(value.toString());
    }

    /**
     * Exporte le graphe Neo4j vers un fichier Cypher unique.
     * Génère le fichier import_complet.cypher prêt à être importé dans Neo4j Desktop.
     *
     * @param outputDir répertoire de sortie pour le fichier Cypher
     * @throws Exception si une erreur survient
     */
    public void exportToCSV(Path outputDir) throws Exception {
        if (!initialized) {
            ensureInitialized();
        }

        logger.info("Export du graphe Neo4j vers fichier Cypher unique...");

        // Créer le répertoire si nécessaire
        if (!Files.exists(outputDir)) {
            Files.createDirectories(outputDir);
        }

        // Générer le fichier Cypher unique
        Path cypherFile = outputDir.resolve("import_complet.cypher");
        exportToCypherScript(cypherFile);

        logger.info("✅ Export terminé: {}", cypherFile.toAbsolutePath());
        logger.info("📌 Pour importer dans Neo4j Desktop:");
        logger.info("   1. Ouvrez Neo4j Browser");
        logger.info("   2. Copiez-collez le contenu du fichier");
        logger.info("   3. Ou utilisez: cat {} | cypher-shell -u neo4j -p password", cypherFile.getFileName());
    }

    // =========================================================================
    // PIPELINE EN 4 PHASES (Phase 2 de l'alignement CodeGraph)
    // =========================================================================

    /**
     * PHASE 1: Parse tous les fichiers Java et extrait les entités.
     */
    private List<ParsedFile> parsePhase(Path directoryPath) throws IOException {
        // Setup Symbol Solver pour résolution précise des types
        setupSymbolSolver(directoryPath);

        List<ParsedFile> parsedFiles = new ArrayList<>();

        Files.walkFileTree(directoryPath, new SimpleFileVisitor<Path>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                if (file.toString().endsWith(".java")) {
                    try {
                        String content = Files.readString(file);
                        ParsedFile parsedFile = parseJavaFile(file, content);
                        parsedFiles.add(parsedFile);
                        logger.debug("  ✓ Parsé: {}", file.getFileName());
                    } catch (Exception e) {
                        logger.error("Erreur parsing {}: {}", file, e.getMessage());
                    }
                }
                return FileVisitResult.CONTINUE;
            }
        });

        return parsedFiles;
    }

    /**
     * Parse un fichier Java individuel et retourne un ParsedFile.
     */
    private ParsedFile parseJavaFile(Path filePath, String content) {
        ParsedFile file = new ParsedFile(filePath.toString());

        try {
            CompilationUnit cu = StaticJavaParser.parse(content);

            // Extraire package name
            file.packageName = cu.getPackageDeclaration()
                    .map(pd -> pd.getNameAsString())
                    .orElse("");

            // Extraire imports
            for (com.github.javaparser.ast.ImportDeclaration imp : cu.getImports()) {
                ParsedImport parsedImport = new ParsedImport(
                    imp.getNameAsString(),
                    imp.isStatic(),
                    imp.isAsterisk()
                );
                file.imports.add(parsedImport);
            }

            // Extraire classes
            for (ClassOrInterfaceDeclaration cls : cu.findAll(ClassOrInterfaceDeclaration.class)) {
                ParsedClass parsedClass = parseClassDeclaration(cls, file.packageName);
                file.classes.add(parsedClass);
            }

            // Extraire enums
            for (EnumDeclaration enumDecl : cu.findAll(EnumDeclaration.class)) {
                ParsedClass parsedEnum = parseEnumDeclaration(enumDecl, file.packageName);
                file.classes.add(parsedEnum);
            }

            // Extraire records
            for (RecordDeclaration recordDecl : cu.findAll(RecordDeclaration.class)) {
                ParsedClass parsedRecord = parseRecordDeclaration(recordDecl, file.packageName);
                file.classes.add(parsedRecord);
            }

            // Extraire annotations
            for (AnnotationDeclaration annotationDecl : cu.findAll(AnnotationDeclaration.class)) {
                ParsedClass parsedAnnotation = parseAnnotationDeclaration(annotationDecl, file.packageName);
                file.classes.add(parsedAnnotation);
            }

            // Passer le contexte d'imports aux classes
            for (ParsedClass cls : file.classes) {
                cls.fileImports = file.imports.stream()
                    .map(imp -> imp.fqn)
                    .collect(Collectors.toList());
                cls.packageName = file.packageName;
            }

        } catch (Exception e) {
            logger.warn("Erreur parsing JavaParser pour {}: {}", filePath, e.getMessage());
        }

        return file;
    }

    /**
     * Parse une déclaration de classe/interface.
     */
    private ParsedClass parseClassDeclaration(ClassOrInterfaceDeclaration cls, String packageName) {
        String className = cls.getNameAsString();
        String classFqn = buildClassFqn(packageName, className);
        String type = cls.isInterface() ? "interface" : "class";

        ParsedClass parsedClass = new ParsedClass(className, classFqn, type);
        parsedClass.visibility = cls.getAccessSpecifier().asString();

        // Modificateurs
        if (cls.isAbstract()) parsedClass.modifiers.add("abstract");
        if (cls.isFinal()) parsedClass.modifiers.add("final");
        if (cls.isStatic()) parsedClass.modifiers.add("static");

        // Extends - avec résolution de types
        for (ClassOrInterfaceType extendedType : cls.getExtendedTypes()) {
            String resolvedExtends = resolveTypeToFqn(extendedType);
            parsedClass.extendsTypes.add(extendedType.getNameAsString()); // Nom simple pour signature
            parsedClass.resolvedExtends.add(resolvedExtends); // FQN résolu
        }

        // Implements - avec résolution de types
        for (ClassOrInterfaceType implementedType : cls.getImplementedTypes()) {
            String resolvedImplements = resolveTypeToFqn(implementedType);
            parsedClass.implementsTypes.add(implementedType.getNameAsString()); // Nom simple pour signature
            parsedClass.resolvedImplements.add(resolvedImplements); // FQN résolu
        }

        // Annotations
        cls.getAnnotations().forEach(ann ->
            parsedClass.annotations.add(ann.getNameAsString())
        );

        // Méthodes
        for (MethodDeclaration method : cls.getMethods()) {
            ParsedMethod parsedMethod = parseMethodDeclaration(method, classFqn);
            parsedClass.methods.add(parsedMethod);
        }

        // Constructeurs
        for (ConstructorDeclaration constructor : cls.getConstructors()) {
            ParsedConstructor parsedConstructor = parseConstructorDeclaration(constructor, className, classFqn);
            parsedClass.constructors.add(parsedConstructor);
        }

        // Fields
        for (FieldDeclaration field : cls.getFields()) {
            List<ParsedField> parsedFields = parseFieldDeclaration(field, classFqn);
            parsedClass.fields.addAll(parsedFields);
        }

        return parsedClass;
    }

    /**
     * Parse une déclaration d'enum.
     */
    private ParsedClass parseEnumDeclaration(EnumDeclaration enumDecl, String packageName) {
        String enumName = enumDecl.getNameAsString();
        String enumFqn = buildClassFqn(packageName, enumName);

        ParsedClass parsedEnum = new ParsedClass(enumName, enumFqn, "enum");
        parsedEnum.visibility = enumDecl.getAccessSpecifier().asString();

        // Méthodes
        for (MethodDeclaration method : enumDecl.getMethods()) {
            ParsedMethod parsedMethod = parseMethodDeclaration(method, enumFqn);
            parsedEnum.methods.add(parsedMethod);
        }

        // Fields
        for (FieldDeclaration field : enumDecl.getFields()) {
            List<ParsedField> parsedFields = parseFieldDeclaration(field, enumFqn);
            parsedEnum.fields.addAll(parsedFields);
        }

        return parsedEnum;
    }

    /**
     * Parse une déclaration de record.
     */
    private ParsedClass parseRecordDeclaration(RecordDeclaration recordDecl, String packageName) {
        String recordName = recordDecl.getNameAsString();
        String recordFqn = buildClassFqn(packageName, recordName);

        ParsedClass parsedRecord = new ParsedClass(recordName, recordFqn, "record");
        parsedRecord.visibility = recordDecl.getAccessSpecifier().asString();

        // Implements - avec résolution de types
        for (ClassOrInterfaceType implementedType : recordDecl.getImplementedTypes()) {
            String resolvedImplements = resolveTypeToFqn(implementedType);
            parsedRecord.implementsTypes.add(implementedType.getNameAsString()); // Nom simple
            parsedRecord.resolvedImplements.add(resolvedImplements); // FQN résolu
        }

        // Méthodes
        for (MethodDeclaration method : recordDecl.getMethods()) {
            ParsedMethod parsedMethod = parseMethodDeclaration(method, recordFqn);
            parsedRecord.methods.add(parsedMethod);
        }

        return parsedRecord;
    }

    /**
     * Parse une déclaration d'annotation.
     */
    private ParsedClass parseAnnotationDeclaration(AnnotationDeclaration annotationDecl, String packageName) {
        String annotationName = annotationDecl.getNameAsString();
        String annotationFqn = buildClassFqn(packageName, annotationName);

        ParsedClass parsedAnnotation = new ParsedClass(annotationName, annotationFqn, "@interface");
        parsedAnnotation.visibility = annotationDecl.getAccessSpecifier().asString();

        return parsedAnnotation;
    }

    /**
     * Extrait le nom du receiver à partir d'une Expression.
     * Gère: NameExpr (variable, field), FieldAccessExpr, ThisExpr, etc.
     */
    private String extractReceiverName(com.github.javaparser.ast.expr.Expression expr) {
        if (expr.isNameExpr()) {
            // Variable simple: repository, user, etc.
            return expr.asNameExpr().getNameAsString();
        } else if (expr.isFieldAccessExpr()) {
            // Champ: this.repository, obj.field, etc.
            return expr.asFieldAccessExpr().getNameAsString();
        } else if (expr.isThisExpr()) {
            return "this";
        } else if (expr.isSuperExpr()) {
            return "super";
        } else if (expr.isMethodCallExpr()) {
            // Appel chaîné: getRepository().save() -> garder l'appel complet
            return expr.toString();
        } else {
            // Autres cas: retourner la représentation string
            return expr.toString();
        }
    }

    /**
     * Parse une déclaration de méthode.
     */
    private ParsedMethod parseMethodDeclaration(MethodDeclaration method, String classFqn) {
        String methodName = method.getNameAsString();
        String signature = buildMethodSignatureFromParser(method.getParameters());
        String methodFqn = classFqn + "." + methodName + "(" + signature + ")";

        ParsedMethod parsedMethod = new ParsedMethod(methodName, methodFqn);

        // Résoudre le type de retour avec Symbol Solver
        parsedMethod.returnType = resolveTypeToFqn(method.getType());
        parsedMethod.resolvedReturnType = parsedMethod.returnType; // Déjà résolu ici

        parsedMethod.visibility = method.getAccessSpecifier().asString();
        parsedMethod.isStatic = method.isStatic();
        parsedMethod.isAbstract = method.isAbstract();
        parsedMethod.isFinal = method.isFinal();

        // Paramètres avec résolution de types
        for (int i = 0; i < method.getParameters().size(); i++) {
            com.github.javaparser.ast.body.Parameter param = method.getParameters().get(i);

            // Résoudre le type du paramètre avec Symbol Solver
            String paramType = resolveTypeToFqn(param.getType());

            ParsedParameter parsedParam = new ParsedParameter(
                param.getNameAsString(),
                paramType,
                i
            );
            parsedParam.isVarArgs = param.isVarArgs();
            parsedParam.resolvedType = paramType; // Déjà résolu ici
            parsedMethod.parameters.add(parsedParam);
        }

        // Construire le scope avec les paramètres
        for (ParsedParameter param : parsedMethod.parameters) {
            parsedMethod.variableScope.addVariable(param.name, param.resolvedType);
        }

        // Extraire les variables locales du corps de la méthode
        if (method.getBody().isPresent()) {
            BlockStmt body = method.getBody().get();

            // Trouver toutes les déclarations de variables
            for (VariableDeclarationExpr varDecl : body.findAll(VariableDeclarationExpr.class)) {
                String varType = resolveTypeToFqn(varDecl.getCommonType());

                for (VariableDeclarator var : varDecl.getVariables()) {
                    String varName = var.getNameAsString();

                    // Créer ParsedLocalVariable
                    ParsedLocalVariable localVar = new ParsedLocalVariable(
                        varName,
                        varDecl.getCommonType().asString()
                    );
                    localVar.resolvedType = varType;
                    localVar.declarationLine = var.getBegin().map(pos -> pos.line).orElse(-1);

                    parsedMethod.localVariables.add(localVar);
                    parsedMethod.variableScope.addVariable(varName, varType);
                }
            }

            logger.debug("Méthode {}: {} variables locales détectées",
                         parsedMethod.name, parsedMethod.localVariables.size());
        }

        // Annotations
        method.getAnnotations().forEach(ann ->
            parsedMethod.annotations.add(ann.getNameAsString())
        );

        // Appels de méthodes avec résolution Symbol Solver
        for (MethodCallExpr call : method.findAll(MethodCallExpr.class)) {
            ParsedMethodCall parsedCall = new ParsedMethodCall(
                call.getScope().map(this::extractReceiverName).orElse(null),
                call.getNameAsString()
            );

            // Tenter de résoudre avec Symbol Solver
            try {
                if (call.getScope().isPresent()) {
                    // Résoudre le type du receiver
                    com.github.javaparser.resolution.types.ResolvedType receiverType =
                        call.getScope().get().calculateResolvedType();
                    parsedCall.receiverType = receiverType.describe();
                }

                // Résoudre la méthode appelée
                com.github.javaparser.resolution.declarations.ResolvedMethodDeclaration resolvedMethod =
                    call.resolve();
                parsedCall.targetFqn = resolvedMethod.getQualifiedName();

            } catch (Exception e) {
                // Impossible de résoudre avec Symbol Solver (méthode externe, etc.)
                logger.debug("Impossible de résoudre l'appel '{}': {}",
                    call, e.getMessage());
            }

            parsedMethod.calls.add(parsedCall);
        }

        return parsedMethod;
    }

    /**
     * Parse une déclaration de constructeur.
     */
    private ParsedConstructor parseConstructorDeclaration(
            ConstructorDeclaration constructor,
            String className,
            String classFqn) {
        String signature = buildMethodSignatureFromParser(constructor.getParameters());
        String constructorFqn = classFqn + ".<init>(" + signature + ")";

        ParsedConstructor parsedConstructor = new ParsedConstructor(className, constructorFqn);
        parsedConstructor.visibility = constructor.getAccessSpecifier().asString();

        // Paramètres avec résolution de types
        for (int i = 0; i < constructor.getParameters().size(); i++) {
            com.github.javaparser.ast.body.Parameter param = constructor.getParameters().get(i);

            // Résoudre le type du paramètre avec Symbol Solver
            String paramType = resolveTypeToFqn(param.getType());

            ParsedParameter parsedParam = new ParsedParameter(
                param.getNameAsString(),
                paramType,
                i
            );
            parsedParam.isVarArgs = param.isVarArgs();
            parsedParam.resolvedType = paramType; // Déjà résolu ici
            parsedConstructor.parameters.add(parsedParam);
        }

        // Annotations
        constructor.getAnnotations().forEach(ann ->
            parsedConstructor.annotations.add(ann.getNameAsString())
        );

        return parsedConstructor;
    }

    /**
     * Parse une déclaration de field (peut contenir plusieurs variables).
     */
    private List<ParsedField> parseFieldDeclaration(FieldDeclaration field, String classFqn) {
        List<ParsedField> fields = new ArrayList<>();

        // Résoudre le type avec Symbol Solver
        String type = resolveTypeToFqn(field.getCommonType());
        String visibility = field.getAccessSpecifier().asString();

        for (com.github.javaparser.ast.body.VariableDeclarator var : field.getVariables()) {
            String fieldName = var.getNameAsString();
            String fieldFqn = classFqn + "." + fieldName;

            ParsedField parsedField = new ParsedField(fieldName, fieldFqn, type);
            parsedField.visibility = visibility;
            parsedField.isStatic = field.isStatic();
            parsedField.isFinal = field.isFinal();
            parsedField.resolvedType = type; // Déjà résolu ici

            // Annotations
            field.getAnnotations().forEach(ann ->
                parsedField.annotations.add(ann.getNameAsString())
            );

            fields.add(parsedField);
        }

        return fields;
    }

    /**
     * PHASE 2: Construit la Symbol Table à partir des fichiers parsés.
     */
    private SymbolTable buildSymbolTable(List<ParsedFile> parsedFiles) {
        SymbolTable symbolTable = new SymbolTable();

        // Ajouter toutes les classes du projet
        for (ParsedFile file : parsedFiles) {
            for (ParsedClass cls : file.classes) {
                ClassInfo classInfo = new ClassInfo(cls.fqn, cls.name, file.packageName);
                classInfo.filePath = file.path;

                // Ajouter méthodes
                for (ParsedMethod method : cls.methods) {
                    MethodInfo methodInfo = new MethodInfo(method.fqn, method.name);
                    methodInfo.returnType = method.returnType;
                    methodInfo.parameterTypes = method.parameters.stream()
                            .map(p -> p.type)
                            .collect(Collectors.toList());
                    classInfo.addMethod(methodInfo);
                }

                symbolTable.addClass(classInfo);
            }
        }

        // Ajouter classes stdlib Java courantes
        addJavaStdlibToSymbolTable(symbolTable);

        logger.debug("Symbol Table: {} classes indexées", symbolTable.size());
        return symbolTable;
    }

    /**
     * Ajoute les classes stdlib Java courantes à la Symbol Table.
     */
    private void addJavaStdlibToSymbolTable(SymbolTable symbolTable) {
        String[] stdlibClasses = {
            "java.lang.String",
            "java.lang.Integer", "java.lang.Long", "java.lang.Double", "java.lang.Float",
            "java.lang.Boolean", "java.lang.Character", "java.lang.Byte", "java.lang.Short",
            "java.lang.Object", "java.lang.Class", "java.lang.System",
            "java.util.List", "java.util.ArrayList", "java.util.LinkedList",
            "java.util.Map", "java.util.HashMap", "java.util.TreeMap",
            "java.util.Set", "java.util.HashSet", "java.util.TreeSet",
            "java.util.Collection", "java.util.Optional",
            "java.io.File", "java.io.InputStream", "java.io.OutputStream",
            "java.nio.file.Path", "java.nio.file.Files"
        };

        for (String fqn : stdlibClasses) {
            String simpleName = fqn.substring(fqn.lastIndexOf('.') + 1);
            String packageName = fqn.substring(0, fqn.lastIndexOf('.'));
            ClassInfo classInfo = new ClassInfo(fqn, simpleName, packageName);
            symbolTable.addClass(classInfo);
        }
    }

    /**
     * PHASE 2 (suite): Résout les appels de méthodes avec la Symbol Table.
     * Note: Les types (extends, implements, returnType, paramètres, fields) sont déjà
     * résolus dans parsePhase() grâce au Symbol Solver.
     */
    private List<ParsedFile> resolvePhase(List<ParsedFile> parsedFiles, SymbolTable symbolTable) {
        logger.info("Résolution des appels de méthodes avec Symbol Table...");

        int totalCalls = 0;
        int resolvedCalls = 0;

        for (ParsedFile file : parsedFiles) {
            for (ParsedClass cls : file.classes) {
                for (ParsedMethod method : cls.methods) {
                    // Résoudre les appels de méthodes
                    for (ParsedMethodCall call : method.calls) {
                        totalCalls++;

                        // Utiliser la résolution avec scope de variables
                        if (resolveMethodCallWithScope(call, method, cls, symbolTable)) {
                            resolvedCalls++;
                        }
                    }
                }
            }
        }

        logger.info("Résolution des appels: {}/{} résolus ({} %)",
            resolvedCalls, totalCalls,
            totalCalls > 0 ? (resolvedCalls * 100 / totalCalls) : 0);

        return parsedFiles;
    }

    /**
     * Résout un appel de méthode en utilisant le scope de variables.
     * Gère: this, variables locales, paramètres, fields, classes statiques.
     *
     * @param call Appel de méthode à résoudre
     * @param method Méthode contenant l'appel
     * @param currentClass Classe courante
     * @param symbolTable Table des symboles
     * @return true si l'appel a été résolu
     */
    private boolean resolveMethodCallWithScope(ParsedMethodCall call, ParsedMethod method,
                                              ParsedClass currentClass, SymbolTable symbolTable) {
        // Cas 1: receiver null ou "this" → méthode de la classe courante
        if (call.receiver == null || call.receiver.equals("this")) {
            call.receiverType = currentClass.fqn;
            ClassInfo classInfo = symbolTable.getClassByFqn(currentClass.fqn);
            if (classInfo != null) {
                MethodInfo methodInfo = classInfo.getMethod(call.methodName);
                if (methodInfo != null) {
                    call.targetFqn = methodInfo.fqn;
                    return true;
                }
            }
            return false;
        }

        // Cas 2: Variable locale ou paramètre
        if (method.variableScope.hasVariable(call.receiver)) {
            String receiverType = method.variableScope.getVariableType(call.receiver);
            call.receiverType = receiverType;

            ClassInfo receiverClass = symbolTable.getClassByFqn(receiverType);
            if (receiverClass != null) {
                MethodInfo methodInfo = receiverClass.getMethod(call.methodName);
                if (methodInfo != null) {
                    call.targetFqn = methodInfo.fqn;
                    return true;
                }
            }
            return true; // Type résolu, méthode peut être externe
        }

        // Cas 3: Field de la classe
        for (ParsedField field : currentClass.fields) {
            if (field.name.equals(call.receiver)) {
                call.receiverType = field.resolvedType;
                ClassInfo receiverClass = symbolTable.getClassByFqn(field.resolvedType);
                if (receiverClass != null) {
                    MethodInfo methodInfo = receiverClass.getMethod(call.methodName);
                    if (methodInfo != null) {
                        call.targetFqn = methodInfo.fqn;
                        return true;
                    }
                }
                return true;
            }
        }

        // Cas 4: Référence statique (ex: Math, UserRepository)
        ClassInfo staticClass = symbolTable.resolveType(
            call.receiver,
            currentClass.packageName,
            currentClass.fileImports
        );
        if (staticClass != null) {
            call.receiverType = staticClass.fqn;
            MethodInfo methodInfo = staticClass.getMethod(call.methodName);
            if (methodInfo != null) {
                call.targetFqn = methodInfo.fqn;
                return true;
            }
            return true;
        }

        return false;
    }

    /**
     * Crée la hiérarchie de packages dans Neo4j.
     * Extrait tous les packages des fichiers et crée une structure hiérarchique :
     * com → com.example → com.example.service → com.example.service.impl
     *
     * @param parsedFiles Liste des fichiers parsés
     * @param tx Transaction Neo4j
     * @return Map packageName → Package Node
     */
    private Map<String, Node> createPackageHierarchy(List<ParsedFile> parsedFiles, Transaction tx) {
        logger.debug("Création de la hiérarchie de packages...");

        // Extraire tous les packages uniques (non vides)
        java.util.Set<String> allPackages = parsedFiles.stream()
            .map(f -> f.packageName)
            .filter(p -> p != null && !p.isEmpty())
            .collect(java.util.stream.Collectors.toSet());

        logger.debug("Packages trouvés: {}", allPackages.size());

        // Générer tous les packages intermédiaires (parents)
        // Ex: com.example.service → ajouter "com" et "com.example"
        java.util.Set<String> allPackagesWithParents = new java.util.HashSet<>();
        for (String pkg : allPackages) {
            String[] parts = pkg.split("\\.");
            StringBuilder current = new StringBuilder();

            for (int i = 0; i < parts.length; i++) {
                if (i > 0) current.append(".");
                current.append(parts[i]);
                allPackagesWithParents.add(current.toString());
            }
        }

        logger.debug("Packages avec parents: {}", allPackagesWithParents.size());

        // Créer les nœuds Package
        Map<String, Node> packageNodes = new HashMap<>();
        for (String pkg : allPackagesWithParents) {
            Node pkgNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_PACKAGE));
            pkgNode.setProperty("name", pkg);

            // Extraire le nom simple (dernier segment)
            String simpleName = pkg.contains(".")
                ? pkg.substring(pkg.lastIndexOf('.') + 1)
                : pkg;
            pkgNode.setProperty("simpleName", simpleName);

            packageNodes.put(pkg, pkgNode);
        }

        // Créer les relations CONTAINS entre packages (hiérarchie)
        int hierarchyRelations = 0;
        for (String pkg : allPackagesWithParents) {
            int lastDot = pkg.lastIndexOf('.');
            if (lastDot > 0) {
                String parentPkg = pkg.substring(0, lastDot);
                Node parentNode = packageNodes.get(parentPkg);
                Node childNode = packageNodes.get(pkg);

                if (parentNode != null && childNode != null) {
                    parentNode.createRelationshipTo(childNode, RelationType.CONTAINS);
                    hierarchyRelations++;
                }
            }
        }

        logger.info("✅ Hiérarchie de packages créée: {} packages, {} relations hiérarchiques",
                    packageNodes.size(), hierarchyRelations);

        return packageNodes;
    }

    /**
     * Crée le nœud Project (racine du graphe).
     * Lie le Project aux packages racines (sans parent).
     */
    private Node createProjectNode(String projectName, String projectPath,
                                   Map<String, Node> packageNodes, Transaction tx) {
        logger.debug("Création du nœud Project: {}", projectName);

        Node projectNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_PROJECT));
        projectNode.setProperty("name", projectName);
        projectNode.setProperty("path", projectPath);
        projectNode.setProperty("indexedAt", System.currentTimeMillis());

        // Lier aux packages racines (sans '.')
        int rootPackages = 0;
        for (Map.Entry<String, Node> entry : packageNodes.entrySet()) {
            String packageName = entry.getKey();
            if (!packageName.contains(".")) {
                Node packageNode = entry.getValue();
                projectNode.createRelationshipTo(packageNode, RelationType.CONTAINS);
                rootPackages++;
            }
        }

        logger.debug("Project lié à {} packages racines", rootPackages);
        return projectNode;
    }

    /**
     * Extrait le nom du projet depuis les fichiers parsés.
     * Remonte l'arborescence jusqu'à trouver le répertoire racine (contenant src/).
     */
    private String extractProjectName(List<ParsedFile> files) {
        if (files.isEmpty()) return "Unknown";
        Path firstFilePath = Paths.get(files.get(0).path);
        // Remonter jusqu'à trouver src/main/java
        Path current = firstFilePath.getParent();
        while (current != null && !current.endsWith("src")) {
            current = current.getParent();
        }
        if (current != null && current.getParent() != null) {
            return current.getParent().getFileName().toString();
        }
        return firstFilePath.getName(0).toString();
    }

    /**
     * Extrait le chemin du projet depuis les fichiers parsés.
     */
    private String extractProjectPath(List<ParsedFile> files) {
        if (files.isEmpty()) return "";
        Path firstFilePath = Paths.get(files.get(0).path);
        Path current = firstFilePath.getParent();
        while (current != null && !current.endsWith("src")) {
            current = current.getParent();
        }
        return current != null && current.getParent() != null
               ? current.getParent().toString()
               : firstFilePath.getParent().toString();
    }

    /**
     * PHASE 3: Écrit le graph dans Neo4j avec batch processing en 2 passes.
     * Passe 0: Créer la hiérarchie de packages
     * Passe 1: Créer tous les nœuds et les mettre en cache
     * Passe 2: Créer toutes les relations (dont CALLS)
     */
    private void writePhase(List<ParsedFile> resolvedFiles) {
        logger.info("Écriture de {} fichiers dans Neo4j (batch processing en 3 passes)...", resolvedFiles.size());

        // Cache FQN → Node pour les relations CALLS
        Map<String, Node> methodNodesByFqn = new HashMap<>();

        // Cache FQN → Node pour les classes (évite les doublons)
        Map<String, Node> classNodesByFqn = new HashMap<>();

        try (Transaction tx = graphDb.beginTx()) {
            // PASSE 0: Créer la hiérarchie de packages
            logger.debug("Passe 0: Création de la hiérarchie de packages...");
            Map<String, Node> packageNodes = createPackageHierarchy(resolvedFiles, tx);

            // PASSE 0b: Créer le nœud Project (racine du graphe)
            String projectName = extractProjectName(resolvedFiles);
            String projectPath = extractProjectPath(resolvedFiles);
            Node projectNode = createProjectNode(projectName, projectPath, packageNodes, tx);
            logger.info("Nœud Project créé: {}", projectName);

            // PASSE 1: Créer tous les nœuds
            logger.debug("Passe 1: Création des nœuds (fichiers, classes, méthodes)...");
            for (ParsedFile file : resolvedFiles) {
                writeFileToNeo4j(file, tx, methodNodesByFqn, packageNodes, classNodesByFqn);
            }

            // PASSE 2: Créer les relations CALLS
            logger.debug("Passe 2: Création des relations CALLS...");
            int callsCreated = 0;
            for (ParsedFile file : resolvedFiles) {
                for (ParsedClass cls : file.classes) {
                    for (ParsedMethod method : cls.methods) {
                        Node methodNode = methodNodesByFqn.get(method.fqn);
                        if (methodNode != null && method.calls != null) {
                            for (ParsedMethodCall call : method.calls) {
                                if (call.targetFqn != null) {
                                    Node targetNode = methodNodesByFqn.get(call.targetFqn);
                                    if (targetNode != null) {
                                        org.neo4j.graphdb.Relationship callRel = methodNode.createRelationshipTo(targetNode, RelationType.CALLS);
                                        // Ajouter les propriétés du call
                                        if (call.receiver != null) {
                                            callRel.setProperty("receiver", call.receiver);
                                        }
                                        if (call.receiverType != null) {
                                            callRel.setProperty("receiverType", call.receiverType);
                                        }
                                        callsCreated++;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            tx.commit();
            logger.info("✅ Graph écrit: {} relations CALLS créées", callsCreated);
        }
    }

    /**
     * Écrit un ParsedFile dans Neo4j.
     * @param file Fichier à écrire
     * @param tx Transaction Neo4j
     * @param methodNodesByFqn Cache FQN → Node pour les méthodes (rempli par cette méthode)
     * @param packageNodes Map packageName → Package Node
     * @param classNodesByFqn Cache FQN → Node pour les classes (évite les doublons)
     */
    private void writeFileToNeo4j(ParsedFile file, Transaction tx, Map<String, Node> methodNodesByFqn, Map<String, Node> packageNodes, Map<String, Node> classNodesByFqn) {
        // Créer nœud File
        Node fileNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FILE));
        fileNode.setProperty("name", Paths.get(file.path).getFileName().toString());
        fileNode.setProperty("path", file.path);

        if (!file.packageName.isEmpty()) {
            fileNode.setProperty("packageName", file.packageName);

            // Lier le fichier au package correspondant
            Node packageNode = packageNodes.get(file.packageName);
            if (packageNode != null) {
                packageNode.createRelationshipTo(fileNode, RelationType.CONTAINS);
            }
        }

        // Créer imports
        for (ParsedImport imp : file.imports) {
            Node importNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_IMPORT));
            importNode.setProperty("name", imp.fqn);
            importNode.setProperty("fqn", imp.fqn);
            importNode.setProperty("isStatic", imp.isStatic);
            importNode.setProperty("isWildcard", imp.isWildcard);
            fileNode.createRelationshipTo(importNode, RelationType.IMPORTS);
        }

        // Créer classes
        for (ParsedClass cls : file.classes) {
            writeClassToNeo4j(cls, file.packageName, fileNode, tx, methodNodesByFqn, packageNodes, classNodesByFqn);
        }
    }

    /**
     * Écrit une ParsedClass dans Neo4j.
     * @param cls Classe à écrire
     * @param packageName Nom du package (pour lier au package node)
     * @param fileNode Nœud du fichier parent
     * @param tx Transaction Neo4j
     * @param methodNodesByFqn Cache FQN → Node pour les méthodes
     * @param packageNodes Map packageName → Package Node
     * @param classNodesByFqn Cache FQN → Node pour les classes (évite les doublons)
     */
    private void writeClassToNeo4j(ParsedClass cls, String packageName, Node fileNode, Transaction tx,
                                    Map<String, Node> methodNodesByFqn, Map<String, Node> packageNodes, Map<String, Node> classNodesByFqn) {
        // Vérifier si la classe existe déjà dans le cache
        // (peut arriver si deux fichiers contiennent la même classe ou si elle a déjà été créée comme stub)
        Node classNode = classNodesByFqn.get(cls.fqn);

        if (classNode == null) {
            // La classe n'existe pas encore, on la crée
            // Déterminer le bon label
            String label = switch (cls.type) {
                case "interface" -> LABEL_INTERFACE;
                case "enum" -> LABEL_ENUM;
                case "record" -> LABEL_RECORD;
                case "@interface" -> LABEL_ANNOTATION_TYPE;
                default -> LABEL_CLASS;
            };

            classNode = tx.createNode(org.neo4j.graphdb.Label.label(label));
            classNode.setProperty("name", cls.name);
            classNode.setProperty("fqn", cls.fqn);
            classNode.setProperty("type", cls.type);
            classNode.setProperty("visibility", cls.visibility);

            // Ajouter les modifiers si présents
            if (cls.modifiers != null && !cls.modifiers.isEmpty()) {
                classNode.setProperty("modifiers", String.join(",", cls.modifiers));
            }

            // Ajouter au cache pour éviter les doublons
            classNodesByFqn.put(cls.fqn, classNode);

            // Relations intrinsèques à la classe (créées seulement lors de la création du nœud)

            // Relations EXTENDS (héritage)
            if (cls.resolvedExtends != null) {
                for (String extendsFqn : cls.resolvedExtends) {
                    Node parentNode = findOrCreateClassNode(extendsFqn, tx, classNodesByFqn);
                    classNode.createRelationshipTo(parentNode, RelationType.EXTENDS);
                }
            }

            // Relations IMPLEMENTS (interfaces)
            if (cls.resolvedImplements != null) {
                for (String implementsFqn : cls.resolvedImplements) {
                    Node interfaceNode = findOrCreateClassNode(implementsFqn, tx, classNodesByFqn);
                    classNode.createRelationshipTo(interfaceNode, RelationType.IMPLEMENTS);
                }
            }

            // Annotations de la classe
            if (cls.annotations != null) {
                for (String annotation : cls.annotations) {
                    Node annotationNode = findOrCreateAnnotationNode(annotation, tx);
                    classNode.createRelationshipTo(annotationNode, RelationType.ANNOTATED_WITH);
                }
            }
        } else {
            // La classe existe déjà (probablement créée comme stub), on met à jour ses propriétés
            logger.debug("Classe {} déjà existante (mise à jour des propriétés)", cls.fqn);

            // Mettre à jour les propriétés avec les vraies valeurs
            classNode.setProperty("name", cls.name);
            classNode.setProperty("type", cls.type);
            classNode.setProperty("visibility", cls.visibility);

            if (cls.modifiers != null && !cls.modifiers.isEmpty()) {
                classNode.setProperty("modifiers", String.join(",", cls.modifiers));
            }

            // Enlever le marqueur stub s'il existe
            if (classNode.hasProperty("stub")) {
                classNode.removeProperty("stub");
            }
        }

        // Relations CONTAINS depuis le fichier et package (toujours créées)
        // Une classe peut apparaître dans plusieurs fichiers (inner classes, etc.)
        fileNode.createRelationshipTo(classNode, RelationType.CONTAINS);

        // Relation CONTAINS depuis le package (si package existe)
        if (packageName != null && !packageName.isEmpty()) {
            Node packageNode = packageNodes.get(packageName);
            if (packageNode != null) {
                packageNode.createRelationshipTo(classNode, RelationType.CONTAINS);
            }
        }

        // Méthodes
        if (cls.methods != null) {
            for (ParsedMethod method : cls.methods) {
                writeMethodToNeo4j(method, classNode, tx, methodNodesByFqn, classNodesByFqn);
            }
        }

        // Constructeurs
        if (cls.constructors != null) {
            for (ParsedConstructor constructor : cls.constructors) {
                writeConstructorToNeo4j(constructor, classNode, tx, classNodesByFqn);
            }
        }

        // Fields (propriétés)
        if (cls.fields != null) {
            for (ParsedField field : cls.fields) {
                writeFieldToNeo4j(field, classNode, tx, classNodesByFqn);
            }
        }
    }

    /**
     * Écrit une méthode dans Neo4j.
     * @param method Méthode à écrire
     * @param classNode Nœud de la classe parente
     * @param tx Transaction Neo4j
     * @param methodNodesByFqn Cache FQN → Node (cette méthode y ajoute le nœud créé)
     * @param classNodesByFqn Cache FQN → Node pour les classes (évite les doublons)
     */
    private void writeMethodToNeo4j(ParsedMethod method, Node classNode, Transaction tx, Map<String, Node> methodNodesByFqn, Map<String, Node> classNodesByFqn) {
        // Vérifier si le nœud existe déjà dans le cache (évite les doublons)
        Node methodNode = methodNodesByFqn.get(method.fqn);

        if (methodNode == null) {
            // Créer le nœud seulement s'il n'existe pas
            methodNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_FUNCTION));

            methodNode.setProperty("name", method.name);
            methodNode.setProperty("fqn", method.fqn);
            methodNode.setProperty("visibility", method.visibility);
            methodNode.setProperty("isStatic", method.isStatic);
            methodNode.setProperty("isAbstract", method.isAbstract);
            methodNode.setProperty("isFinal", method.isFinal);

            if (method.returnType != null) {
                methodNode.setProperty("returnType", method.returnType);
            }

            // Ajouter au cache pour les relations CALLS (passe 2)
            methodNodesByFqn.put(method.fqn, methodNode);

            // Relation RETURNS si le type de retour est résolu (uniquement pour le nouveau nœud)
            if (method.resolvedReturnType != null) {
                Node returnTypeNode = findOrCreateClassNode(method.resolvedReturnType, tx, classNodesByFqn);
                methodNode.createRelationshipTo(returnTypeNode, RelationType.RETURNS);
            }

            // Paramètres (uniquement pour le nouveau nœud)
            if (method.parameters != null) {
                for (ParsedParameter param : method.parameters) {
                    writeParameterToNeo4j(param, methodNode, tx, classNodesByFqn);
                }
            }

            // Annotations (uniquement pour le nouveau nœud)
            if (method.annotations != null) {
                for (String annotation : method.annotations) {
                    Node annotationNode = findOrCreateAnnotationNode(annotation, tx);
                    methodNode.createRelationshipTo(annotationNode, RelationType.ANNOTATED_WITH);
                }
            }
        }

        // Relation DECLARES depuis la classe (toujours créée, même si nœud existait)
        // Permet à une méthode d'avoir plusieurs DECLARES (ex: interface + implémentation)
        classNode.createRelationshipTo(methodNode, RelationType.DECLARES);
    }

    /**
     * Écrit un constructeur dans Neo4j.
     */
    private void writeConstructorToNeo4j(ParsedConstructor constructor, Node classNode, Transaction tx, Map<String, Node> classNodesByFqn) {
        Node constructorNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CONSTRUCTOR));

        constructorNode.setProperty("name", constructor.name);
        constructorNode.setProperty("fqn", constructor.fqn);
        constructorNode.setProperty("visibility", constructor.visibility);

        // Relation DECLARES depuis la classe
        classNode.createRelationshipTo(constructorNode, RelationType.DECLARES);

        // Paramètres
        if (constructor.parameters != null) {
            for (ParsedParameter param : constructor.parameters) {
                writeParameterToNeo4j(param, constructorNode, tx, classNodesByFqn);
            }
        }

        // Annotations
        if (constructor.annotations != null) {
            for (String annotation : constructor.annotations) {
                Node annotationNode = findOrCreateAnnotationNode(annotation, tx);
                constructorNode.createRelationshipTo(annotationNode, RelationType.ANNOTATED_WITH);
            }
        }
    }

    /**
     * Écrit un field (propriété) dans Neo4j.
     */
    private void writeFieldToNeo4j(ParsedField field, Node classNode, Transaction tx, Map<String, Node> classNodesByFqn) {
        Node fieldNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_PROPERTY));

        fieldNode.setProperty("name", field.name);
        fieldNode.setProperty("fqn", field.fqn);
        fieldNode.setProperty("visibility", field.visibility);
        fieldNode.setProperty("isStatic", field.isStatic);
        fieldNode.setProperty("isFinal", field.isFinal);

        if (field.type != null) {
            fieldNode.setProperty("type", field.type);
        }

        // Relation DECLARES depuis la classe
        classNode.createRelationshipTo(fieldNode, RelationType.DECLARES);

        // Relation USES si le type est résolu
        if (field.resolvedType != null) {
            Node typeNode = findOrCreateClassNode(field.resolvedType, tx, classNodesByFqn);
            fieldNode.createRelationshipTo(typeNode, RelationType.USES);
        }

        // Annotations
        if (field.annotations != null) {
            for (String annotation : field.annotations) {
                Node annotationNode = findOrCreateAnnotationNode(annotation, tx);
                fieldNode.createRelationshipTo(annotationNode, RelationType.ANNOTATED_WITH);
            }
        }
    }

    /**
     * Écrit un paramètre dans Neo4j.
     */
    private void writeParameterToNeo4j(ParsedParameter param, Node methodOrConstructorNode, Transaction tx, Map<String, Node> classNodesByFqn) {
        Node paramNode = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_PARAMETER));

        paramNode.setProperty("name", param.name);

        if (param.type != null) {
            paramNode.setProperty("type", param.type);
        }

        // Relation HAS_PARAMETER
        methodOrConstructorNode.createRelationshipTo(paramNode, RelationType.HAS_PARAMETER);

        // Relation USES si le type est résolu
        if (param.resolvedType != null) {
            Node typeNode = findOrCreateClassNode(param.resolvedType, tx, classNodesByFqn);
            paramNode.createRelationshipTo(typeNode, RelationType.USES);
        }
    }

    /**
     * Trouve ou crée un nœud de classe par FQN.
     * Utilise un cache local pour éviter les doublons pendant la même transaction.
     */
    private Node findOrCreateClassNode(String fqn, Transaction tx, Map<String, Node> classNodesByFqn) {
        // Vérifier d'abord dans le cache local
        if (classNodesByFqn.containsKey(fqn)) {
            return classNodesByFqn.get(fqn);
        }

        // Chercher le nœud existant dans Neo4j
        ResourceIterator<Node> result = tx.execute(
            "MATCH (c) WHERE c.fqn = $fqn RETURN c",
            Map.of("fqn", fqn)
        ).columnAs("c");

        if (result.hasNext()) {
            Node node = result.next();
            // Ajouter au cache pour les prochains appels
            classNodesByFqn.put(fqn, node);
            return node;
        }

        // Créer un nouveau nœud (stub) si non trouvé
        Node node = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_CLASS));
        node.setProperty("fqn", fqn);
        node.setProperty("name", extractSimpleName(fqn));
        node.setProperty("stub", true); // Marqueur pour indiquer que c'est une référence externe

        // Ajouter au cache pour éviter les doublons
        classNodesByFqn.put(fqn, node);

        return node;
    }

    /**
     * Trouve ou crée un nœud d'annotation.
     */
    private Node findOrCreateAnnotationNode(String annotationName, Transaction tx) {
        // Chercher le nœud existant
        ResourceIterator<Node> result = tx.execute(
            "MATCH (a:Annotation) WHERE a.name = $name RETURN a",
            Map.of("name", annotationName)
        ).columnAs("a");

        if (result.hasNext()) {
            return result.next();
        }

        // Créer un nouveau nœud
        Node node = tx.createNode(org.neo4j.graphdb.Label.label(LABEL_ANNOTATION));
        node.setProperty("name", annotationName);

        return node;
    }

    /**
     * Extrait le nom simple d'un FQN.
     */
    private String extractSimpleName(String fqn) {
        int lastDot = fqn.lastIndexOf('.');
        return lastDot >= 0 ? fqn.substring(lastDot + 1) : fqn;
    }

    /**
     * PHASE 5: Post-processing (statistiques, validation).
     */
    /**
     * Résout un type avec le Symbol Solver et retourne son FQN complet.
     * Si la résolution échoue, retourne le nom simple.
     * @param type Type JavaParser à résoudre
     * @return FQN du type ou nom simple en fallback
     */
    private String resolveTypeToFqn(com.github.javaparser.ast.type.Type type) {
        try {
            // Tenter de résoudre avec Symbol Solver
            com.github.javaparser.resolution.types.ResolvedType resolvedType = type.resolve();
            return resolvedType.describe();
        } catch (Exception e) {
            // Fallback sur le nom simple si la résolution échoue
            logger.debug("Impossible de résoudre le type '{}': {} - utilisation du nom simple",
                type.asString(), e.getMessage());
            return type.asString();
        }
    }

    /**
     * Configure JavaParser Symbol Solver pour résoudre les types et symboles.
     * @param projectRoot Racine du projet à analyser
     */
    private void setupSymbolSolver(Path projectRoot) {
        try {
            logger.info("Configuration de JavaParser Symbol Solver...");

            CombinedTypeSolver combinedSolver = new CombinedTypeSolver();

            // 1. Résolution via réflexion (classes JDK: java.lang.*, java.util.*, etc.)
            combinedSolver.add(new ReflectionTypeSolver());

            // 2. Résolution via parsing (notre code source)
            combinedSolver.add(new JavaParserTypeSolver(projectRoot));

            // 3. Configurer JavaParser pour utiliser le Symbol Solver
            JavaSymbolSolver symbolSolver = new JavaSymbolSolver(combinedSolver);
            StaticJavaParser.getConfiguration().setSymbolResolver(symbolSolver);

            logger.info("✅ Symbol Solver configuré avec:");
            logger.info("   - ReflectionTypeSolver (JDK classes)");
            logger.info("   - JavaParserTypeSolver (source: {})", projectRoot);
        } catch (Exception e) {
            logger.warn("⚠️ Impossible de configurer Symbol Solver: {}", e.getMessage());
            logger.warn("   La résolution des types sera basique (sans Symbol Solver)");
        }
    }

    /**
     * PHASE 4: Post-traitement - Statistiques et validation du graphe
     */
    private void postProcessPhase() {
        logger.info("=== POST-PROCESSING ===");

        try (Transaction tx = graphDb.beginTx()) {
            // Statistiques sur les nœuds
            long packageCount = (Long) tx.execute("MATCH (p:Package) RETURN count(p) as count")
                    .next().get("count");
            long fileCount = (Long) tx.execute("MATCH (f:File) RETURN count(f) as count")
                    .next().get("count");
            long classCount = (Long) tx.execute("MATCH (c:Class) RETURN count(c) as count")
                    .next().get("count");
            long interfaceCount = (Long) tx.execute("MATCH (i:Interface) RETURN count(i) as count")
                    .next().get("count");
            long enumCount = (Long) tx.execute("MATCH (e:Enum) RETURN count(e) as count")
                    .next().get("count");
            long recordCount = (Long) tx.execute("MATCH (r:Record) RETURN count(r) as count")
                    .next().get("count");
            long functionCount = (Long) tx.execute("MATCH (f:Function) RETURN count(f) as count")
                    .next().get("count");
            long constructorCount = (Long) tx.execute("MATCH (c:Constructor) RETURN count(c) as count")
                    .next().get("count");
            long propertyCount = (Long) tx.execute("MATCH (p:Property) RETURN count(p) as count")
                    .next().get("count");
            long parameterCount = (Long) tx.execute("MATCH (p:Parameter) RETURN count(p) as count")
                    .next().get("count");
            long annotationCount = (Long) tx.execute("MATCH (a:Annotation) RETURN count(a) as count")
                    .next().get("count");
            long importCount = (Long) tx.execute("MATCH (i:Import) RETURN count(i) as count")
                    .next().get("count");

            // Statistiques sur les relations
            long containsCount = (Long) tx.execute("MATCH ()-[r:CONTAINS]->() RETURN count(r) as count")
                    .next().get("count");
            long declaresCount = (Long) tx.execute("MATCH ()-[r:DECLARES]->() RETURN count(r) as count")
                    .next().get("count");
            long extendsCount = (Long) tx.execute("MATCH ()-[r:EXTENDS]->() RETURN count(r) as count")
                    .next().get("count");
            long implementsCount = (Long) tx.execute("MATCH ()-[r:IMPLEMENTS]->() RETURN count(r) as count")
                    .next().get("count");
            long callsCount = (Long) tx.execute("MATCH ()-[r:CALLS]->() RETURN count(r) as count")
                    .next().get("count");
            long usesCount = (Long) tx.execute("MATCH ()-[r:USES]->() RETURN count(r) as count")
                    .next().get("count");
            long returnsCount = (Long) tx.execute("MATCH ()-[r:RETURNS]->() RETURN count(r) as count")
                    .next().get("count");
            long annotatedWithCount = (Long) tx.execute("MATCH ()-[r:ANNOTATED_WITH]->() RETURN count(r) as count")
                    .next().get("count");

            // Statistiques hiérarchie packages (Phase 4)
            long packageHierarchyDepth = 0;
            var depthResult = tx.execute(
                "MATCH path = (p:Package)-[:CONTAINS*]->(leaf:Package) " +
                "WHERE NOT (leaf)-[:CONTAINS]->(:Package) " +
                "RETURN max(length(path)) as maxDepth"
            );
            if (depthResult.hasNext()) {
                Object depth = depthResult.next().get("maxDepth");
                if (depth != null) {
                    packageHierarchyDepth = (Long) depth + 1; // +1 car length compte les relations
                }
            }

            // Statistiques Project
            var projectResult = tx.execute("MATCH (p:Project) RETURN count(p) as count");
            if (projectResult.hasNext()) {
                long projectCount = (Long) projectResult.next().get("count");
                if (projectCount > 0) {
                    var projectInfo = tx.execute(
                        "MATCH (p:Project) RETURN p.name as name, p.path as path"
                    );
                    if (projectInfo.hasNext()) {
                        var row = projectInfo.next();
                        logger.info("📦 Nœud Project: {}", projectCount);
                        logger.info("   • Nom: {}", row.get("name"));
                        logger.info("   • Chemin: {}", row.get("path"));
                        logger.info("");
                    }
                }
            }

            // Top 5 packages par nombre de classes
            var topPackages = tx.execute(
                "MATCH (p:Package)-[:CONTAINS]->(c:Class) " +
                "RETURN p.name as package, count(c) as classCount " +
                "ORDER BY classCount DESC LIMIT 5"
            );

            logger.info("📊 STATISTIQUES DU GRAPHE");
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            logger.info("📦 Nœuds:");
            logger.info("   • Packages: {}", packageCount);
            logger.info("   • Files: {}", fileCount);
            logger.info("   • Classes: {}", classCount);
            logger.info("   • Interfaces: {}", interfaceCount);
            logger.info("   • Enums: {}", enumCount);
            logger.info("   • Records: {}", recordCount);
            logger.info("   • Functions: {}", functionCount);
            logger.info("   • Constructors: {}", constructorCount);
            logger.info("   • Properties: {}", propertyCount);
            logger.info("   • Parameters: {}", parameterCount);
            logger.info("   • Annotations: {}", annotationCount);
            logger.info("   • Imports: {}", importCount);
            logger.info("");
            logger.info("🔗 Relations:");
            logger.info("   • CONTAINS: {}", containsCount);
            logger.info("   • DECLARES: {}", declaresCount);
            logger.info("   • EXTENDS: {}", extendsCount);
            logger.info("   • IMPLEMENTS: {}", implementsCount);
            logger.info("   • CALLS: {}", callsCount);
            logger.info("   • USES: {}", usesCount);
            logger.info("   • RETURNS: {}", returnsCount);
            logger.info("   • ANNOTATED_WITH: {}", annotatedWithCount);
            logger.info("");
            logger.info("📂 Hiérarchie Packages (Phase 4):");
            logger.info("   • Profondeur max: {}", packageHierarchyDepth);
            logger.info("   • Top 5 packages par classes:");
            while (topPackages.hasNext()) {
                var row = topPackages.next();
                logger.info("      - {}: {} classes", row.get("package"), row.get("classCount"));
            }
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            tx.commit();
        } catch (Exception e) {
            logger.error("Erreur lors du post-processing", e);
        }
    }
}
