package fr.baretto.benchmarks.jmh;

import dev.langchain4j.model.ollama.OllamaChatModel;
import fr.baretto.benchmarks.service.RagService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.List;

/**
 * Génère la réponse finale à partir du contexte récupéré.
 *
 * <p><b>Pourquoi cette classe existe.</b> Jusqu'au 2026-10-17 le banc ne jugeait que le contexte
 * récupéré : aucune réponse n'était produite nulle part, et le champ {@code generated} des JSONL
 * contenait en réalité les extraits Java retournés par le moteur. L'exposé affirme qu'on évalue
 * aussi la réponse ; c'est cette classe qui rend l'affirmation vraie.</p>
 *
 * <p><b>Le générateur n'est pas le juge — mais depuis le 2026-10-18 il n'est plus d'une famille
 * disjointe, et c'est un choix déclaré.</b> Le défaut était {@code llama3.1} (4,9 Go), retenu
 * pour que le générateur ne partage aucune famille avec le juge : un modèle qui note sa propre
 * sortie la surévalue — biais d'auto-préférence. Le défaut est désormais {@code qwen3.8:27b}
 * (18 Go), nettement plus proche de ce qu'un produit servirait aujourd'hui. Il partage sa famille
 * avec le premier juge de la campagne, {@code 32B-baseline-conventions} (Qwen2.5-Coder-32B) —
 * génération et entraînement différents, famille commune.</p>
 *
 * <p><b>Ce qui remplace la disjonction : un second juge d'une autre famille.</b> La campagne du
 * talk juge les mêmes générations deux fois, la seconde par un modèle Gemma, disjoint du
 * générateur. Si les deux juges classent les bras dans le même ordre, la parenté de famille n'a
 * pas porté le résultat ; s'ils divergent, le désaccord est lui-même la mesure. Troquer une
 * précaution a priori contre un contrôle a posteriori est assumé et se dit à l'oral. Le juge, lui,
 * ne se choisit pas sur sa famille mais sur son accord mesuré avec l'étalon ; le générateur reste
 * une constante identique sur les trois bras.</p>
 *
 * <p><b>L'invite est celle du produit, pas une copie.</b> On appelle
 * {@link RagService#buildPrompt(String, String)} : si l'invite d'OllamAssist change, le banc change
 * avec elle. Une invite recopiée ici dériverait en silence et le banc mesurerait autre chose que le
 * produit.</p>
 *
 * <pre>
 *   -Drag.answer.model=qwen3.8:27b         (défaut depuis le 2026-10-18 ; llama3.1:latest avant)
 *   -Drag.answer.url=http://localhost:11434
 *   -Drag.answer.timeout=180               (secondes)
 * </pre>
 */
public class RagAnswerer {

    private static final Logger logger = LoggerFactory.getLogger(RagAnswerer.class);

    private static final String DEFAULT_URL   = "http://localhost:11434";
    private static final String DEFAULT_MODEL = "qwen3.8:27b";

    /**
     * Même plafond que {@link RagContextJudge} : le juge de fidélité doit voir exactement le
     * contexte que le générateur a vu, sans quoi « absence_invention » sanctionnerait une
     * affirmation puisée dans un extrait que le juge, lui, n'aurait pas reçu.
     */
    static final int MAX_CONTEXTE = 6000;

    private final OllamaChatModel model;
    private final String modelLabel;

    public RagAnswerer() {
        String baseUrl = prop("rag.answer.url", DEFAULT_URL);
        this.modelLabel = prop("rag.answer.model", DEFAULT_MODEL);
        long timeout = Long.parseLong(prop("rag.answer.timeout", "180"));
        this.model = OllamaChatModel.builder()
            .baseUrl(baseUrl)
            .modelName(modelLabel)
            // 0.0 et non le défaut du produit : un banc apparié doit pouvoir être rejoué.
            // L'écart avec le réglage de production est assumé et déclaré.
            .temperature(0.0)
            .timeout(Duration.ofSeconds(timeout))
            .build();
        logger.info("RagAnswerer initialisé : {} sur {}", modelLabel, baseUrl);
    }

    private static String prop(String cle, String defaut) {
        String v = System.getProperty(cle);
        return (v == null || v.isBlank()) ? defaut : v.trim();
    }

    public String getModelLabel() {
        return modelLabel;
    }

    /**
     * @param texte     la réponse rendue, ou le message d'échec
     * @param contexte  le contexte exact soumis au générateur — à transmettre tel quel au juge
     * @param millis    durée de l'appel
     * @param echec     vrai si l'appel a échoué ; la réponse ne doit alors pas être jugée PASS
     */
    public record Answer(String texte, String contexte, long millis, boolean echec) {}

    /** Ordre de récupération conservé : c'est celui que le produit soumettrait au modèle. */
    public Answer answer(String question, List<String> contexteRecupere) {
        String contexte = String.join("\n\n", contexteRecupere);
        if (contexte.length() > MAX_CONTEXTE) {
            contexte = contexte.substring(0, MAX_CONTEXTE) + "\n[... truncated ...]";
        }
        if (contexteRecupere.isEmpty()) {
            return new Answer("", "", 0L, false);
        }
        long t0 = System.currentTimeMillis();
        try {
            String reponse = model.chat(RagService.buildPrompt(question, contexte));
            return new Answer(reponse == null ? "" : reponse, contexte,
                System.currentTimeMillis() - t0, false);
        } catch (Exception e) {
            logger.warn("Génération en échec sur '{}' : {}", question, e.getMessage());
            return new Answer("Appel en échec : " + e.getMessage(), contexte,
                System.currentTimeMillis() - t0, true);
        }
    }
}
