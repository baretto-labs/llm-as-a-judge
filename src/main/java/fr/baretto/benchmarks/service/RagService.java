package fr.baretto.benchmarks.service;

import dev.langchain4j.model.ollama.OllamaChatModel;
import fr.baretto.benchmarks.strategy.RagStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Service principal gérant l'interaction entre les stratégies RAG et le modèle LLM (Ollama).
 * Suit le pattern MVC en séparant la logique métier de l'interface utilisateur.
 */
public class RagService {

    private static final Logger logger = LoggerFactory.getLogger(RagService.class);
    private static final String DEFAULT_OLLAMA_URL = "http://localhost:11434";
    private static final Duration DEFAULT_TIMEOUT = Duration.ofMinutes(5);

    private RagStrategy currentStrategy;
    private OllamaChatModel chatModel;
    private String currentModelName;

    /**
     * Initialise le service RAG.
     */
    public RagService() {
        logger.info("Initialisation du RagService");
    }

    /**
     * Définit la stratégie RAG à utiliser.
     *
     * @param strategy la stratégie RAG (Lucene ou Neo4j)
     */
    public void setStrategy(RagStrategy strategy) {
        // Fermer l'ancienne stratégie si elle existe
        if (this.currentStrategy != null) {
            try {
                this.currentStrategy.close();
            } catch (Exception e) {
                logger.error("Erreur lors de la fermeture de la stratégie précédente", e);
            }
        }

        this.currentStrategy = strategy;
        logger.info("Stratégie RAG changée pour: {}", strategy.getStrategyName());
    }

    /**
     * Configure le modèle Ollama à utiliser.
     *
     * @param modelName le nom du modèle (ex: "mistral", "llama3", "phi4")
     */
    public void setOllamaModel(String modelName) {
        try {
            logger.info("Configuration du modèle Ollama: {}", modelName);

            this.chatModel = OllamaChatModel.builder()
                    .baseUrl(DEFAULT_OLLAMA_URL)
                    .modelName(modelName)
                    .timeout(DEFAULT_TIMEOUT)
                    .build();

            this.currentModelName = modelName;
            logger.info("Modèle Ollama configuré avec succès: {}", modelName);

        } catch (Exception e) {
            logger.error("Erreur lors de la configuration du modèle Ollama", e);
            throw new RuntimeException("Impossible de configurer le modèle Ollama: " + modelName, e);
        }
    }

    /**
     * Indexe un répertoire avec la stratégie courante.
     *
     * @param directoryPath le chemin du répertoire à indexer
     * @throws Exception si une erreur survient pendant l'indexation
     */
    public void indexDirectory(Path directoryPath) throws Exception {
        if (currentStrategy == null) {
            throw new IllegalStateException("Aucune stratégie RAG n'est configurée");
        }

        logger.info("Démarrage de l'indexation du répertoire: {}", directoryPath);
        long startTime = System.currentTimeMillis();

        currentStrategy.indexDirectory(directoryPath);

        long duration = System.currentTimeMillis() - startTime;
        logger.info("Indexation terminée en {} ms", duration);
    }

    /**
     * Répond à une question en utilisant RAG (Retrieval-Augmented Generation).
     *
     * @param question la question de l'utilisateur
     * @return une réponse contenant le texte généré et le temps de réponse
     * @throws Exception si une erreur survient
     */
    public RagResponse askQuestion(String question) throws Exception {
        if (currentStrategy == null) {
            throw new IllegalStateException("Aucune stratégie RAG n'est configurée");
        }

        if (chatModel == null) {
            throw new IllegalStateException("Aucun modèle Ollama n'est configuré");
        }

        logger.info("Traitement de la question: {}", question);
        long startTime = System.currentTimeMillis();

        // 1. Récupérer le contexte pertinent via la stratégie RAG
        List<String> contextChunks = currentStrategy.retrieveContext(question);
        String context = String.join("\n\n", contextChunks);

        logger.debug("Contexte récupéré ({} chunks)", contextChunks.size());

        // 2. Construire le prompt augmenté avec le contexte
        String augmentedPrompt = buildPrompt(question, context);

        // 3. Envoyer au LLM via Ollama
        // Note: Dans LangChain4j 1.11.0+, utilisez chat() ou la méthode appropriée
        String response = chatModel.chat(augmentedPrompt);

        long duration = System.currentTimeMillis() - startTime;
        logger.info("Réponse générée en {} ms", duration);

        return new RagResponse(response, duration, contextChunks.size());
    }

    /**
     * Construit le prompt augmenté avec le contexte récupéré.
     */
    private String buildPrompt(String question, String context) {
        return """
                Tu es un assistant expert en analyse de code. Utilise le contexte fourni pour répondre à la question.

                CONTEXTE:
                %s

                QUESTION:
                %s

                RÉPONSE:
                """.formatted(context, question);
    }

    /**
     * Récupère la liste des modèles Ollama disponibles localement.
     * Appelle l'API Ollama REST à http://localhost:11434/api/tags
     *
     * @return une liste de noms de modèles
     */
    public List<String> getAvailableModels() {
        List<String> models = new ArrayList<>();

        try {
            // Créer un client HTTP
            HttpClient client = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(5))
                    .build();

            // Créer la requête vers l'API Ollama
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(DEFAULT_OLLAMA_URL + "/api/tags"))
                    .timeout(Duration.ofSeconds(5))
                    .GET()
                    .build();

            // Envoyer la requête
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() == 200) {
                // Parser le JSON manuellement (format: {"models":[{"name":"mistral:latest",...}]})
                String json = response.body();
                Pattern pattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
                Matcher matcher = pattern.matcher(json);

                while (matcher.find()) {
                    String fullName = matcher.group(1);
                    // Extraire juste le nom du modèle sans le tag (ex: "mistral:latest" -> "mistral")
                    String modelName = fullName.contains(":") ?
                            fullName.substring(0, fullName.indexOf(":")) : fullName;
                    if (!models.contains(modelName)) {
                        models.add(modelName);
                    }
                }

                logger.info("Modèles Ollama trouvés: {}", models);
            } else {
                logger.warn("Impossible de récupérer les modèles Ollama (status: {})", response.statusCode());
            }

        } catch (Exception e) {
            logger.error("Erreur lors de la récupération des modèles Ollama", e);
        }

        // Si aucun modèle trouvé, retourner une liste par défaut
        if (models.isEmpty()) {
            logger.warn("Aucun modèle Ollama trouvé. Assurez-vous qu'Ollama est installé et en cours d'exécution.");
            models.add("Aucun modèle disponible - Installer Ollama");
        }

        return models;
    }

    /**
     * Retourne le nom de la stratégie courante.
     */
    public String getCurrentStrategyName() {
        return currentStrategy != null ? currentStrategy.getStrategyName() : "Aucune";
    }

    /**
     * Retourne le nom du modèle courant.
     */
    public String getCurrentModelName() {
        return currentModelName != null ? currentModelName : "Aucun";
    }

    /**
     * Retourne la stratégie courante (pour debug).
     */
    public RagStrategy getCurrentStrategy() {
        return currentStrategy;
    }

    /**
     * Ferme les ressources utilisées par le service.
     */
    public void close() {
        if (currentStrategy != null) {
            try {
                currentStrategy.close();
            } catch (Exception e) {
                logger.error("Erreur lors de la fermeture de la stratégie", e);
            }
        }
    }

    /**
     * Classe représentant une réponse RAG avec métriques.
     */
    public static class RagResponse {
        private final String response;
        private final long responseTimeMs;
        private final int contextChunksCount;

        public RagResponse(String response, long responseTimeMs, int contextChunksCount) {
            this.response = response;
            this.responseTimeMs = responseTimeMs;
            this.contextChunksCount = contextChunksCount;
        }

        public String getResponse() {
            return response;
        }

        public long getResponseTimeMs() {
            return responseTimeMs;
        }

        public int getContextChunksCount() {
            return contextChunksCount;
        }
    }
}
