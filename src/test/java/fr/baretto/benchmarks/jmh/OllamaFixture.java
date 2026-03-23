package fr.baretto.benchmarks.jmh;

import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.utility.DockerImageName;

import java.time.Duration;

/**
 * Fixture Testcontainers pour Ollama.
 *
 * Démarre un conteneur Ollama isolé et y télécharge un modèle léger (tinyllama).
 * Utilisé pour les benchmarks de la pipeline RAG complète (incluant appel LLM).
 *
 * Usage dans un benchmark @Fork(0) :
 * <pre>
 *   private static final OllamaFixture OLLAMA = new OllamaFixture("tinyllama");
 *
 *   @Setup(Level.Trial)
 *   public void setup() {
 *       OLLAMA.start();
 *       ragService.setOllamaModel(OLLAMA.getModel());
 *       // OllamaChatModel.builder().baseUrl(OLLAMA.getBaseUrl()) ...
 *   }
 *
 *   @TearDown(Level.Trial)
 *   public void teardown() {
 *       OLLAMA.stop();
 *   }
 * </pre>
 *
 * Note : le premier démarrage télécharge le modèle (~600 MB pour tinyllama).
 * Les exécutions suivantes utilisent le cache Docker.
 */
public class OllamaFixture {

    private static final String OLLAMA_IMAGE = "ollama/ollama:latest";
    private static final int    OLLAMA_PORT  = 11434;

    private final String model;
    private GenericContainer<?> container;

    /**
     * @param model nom du modèle Ollama à pré-charger (ex: "tinyllama", "phi3:mini")
     */
    public OllamaFixture(String model) {
        this.model = model;
    }

    public void start() {
        container = new GenericContainer<>(DockerImageName.parse(OLLAMA_IMAGE))
                .withExposedPorts(OLLAMA_PORT)
                .withStartupTimeout(Duration.ofMinutes(3))
                .waitingFor(Wait.forHttp("/api/tags")
                        .forPort(OLLAMA_PORT)
                        .forStatusCode(200)
                        .withStartupTimeout(Duration.ofMinutes(3)));

        container.start();

        pullModel();
    }

    public void stop() {
        if (container != null && container.isRunning()) {
            container.stop();
        }
    }

    /** URL de base Ollama accessible depuis le host. */
    public String getBaseUrl() {
        return "http://" + container.getHost() + ":" + container.getMappedPort(OLLAMA_PORT);
    }

    public String getModel() {
        return model;
    }

    private void pullModel() {
        try {
            var result = container.execInContainer("ollama", "pull", model);
            if (result.getExitCode() != 0) {
                throw new RuntimeException("ollama pull " + model + " failed:\n" + result.getStderr());
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to pull model " + model, e);
        }
    }
}
