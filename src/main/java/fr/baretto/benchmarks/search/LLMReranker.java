package fr.baretto.benchmarks.search;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.input.Prompt;
import dev.langchain4j.model.input.PromptTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * Reranking LLM des résultats de recherche.
 * <p>
 * Implémente un cross-encoder LLM pour affiner le classement des résultats :
 * <ol>
 *   <li>Prend les Top N résultats du RRF (généralement 10)</li>
 *   <li>Utilise un LLM pour scorer la pertinence query-result</li>
 *   <li>Re-classe par score LLM</li>
 *   <li>Retourne Top K final (généralement 3-5)</li>
 * </ol>
 *
 * <p><b>Avantages</b> :</p>
 * <ul>
 *   <li>Compréhension sémantique fine (LLM)</li>
 *   <li>Contexte élargi (signature, javaDoc, relations)</li>
 *   <li>Amélioration 10-15% précision vs RRF seul</li>
 * </ul>
 *
 * <p><b>Note</b> : Nécessite LLM configuré (Ollama, OpenAI, etc.)</p>
 */
public class LLMReranker {

    private static final Logger logger = LoggerFactory.getLogger(LLMReranker.class);

    private final ChatModel llmModel;
    private final boolean useBatchScoring; // Si true, score tous les résultats en 1 appel LLM

    /**
     * Constructeur avec modèle LLM.
     *
     * @param llmModel Modèle de chat LLM (Ollama, OpenAI, etc.)
     */
    public LLMReranker(ChatModel llmModel) {
        this(llmModel, false);
    }

    /**
     * Constructeur avec configuration avancée.
     *
     * @param llmModel Modèle de chat LLM
     * @param useBatchScoring Si true, score tous résultats en 1 appel (plus rapide mais moins précis)
     */
    public LLMReranker(ChatModel llmModel, boolean useBatchScoring) {
        this.llmModel = llmModel;
        this.useBatchScoring = useBatchScoring;

        if (llmModel == null) {
            throw new IllegalArgumentException("llmModel ne peut pas être null");
        }
    }

    /**
     * Reranke une liste de résultats par pertinence LLM.
     * <p>
     * Utilise le LLM pour évaluer la pertinence de chaque résultat par rapport à la requête,
     * puis re-classe les résultats par score décroissant.
     *
     * @param query Requête utilisateur
     * @param candidates Candidats à reranker (généralement Top 10 du RRF)
     * @param topK Nombre de résultats finaux à retourner
     * @return Résultats rerankés (meilleurs en tête)
     * @throws SearchException Si erreur LLM
     */
    public List<EntryPoint> rerank(
        String query,
        List<EntryPoint> candidates,
        int topK
    ) throws SearchException {

        if (query == null || query.isBlank()) {
            throw new IllegalArgumentException("query ne peut pas être vide");
        }

        if (candidates == null || candidates.isEmpty()) {
            return List.of();
        }

        if (topK < 1) {
            throw new IllegalArgumentException("topK doit être > 0");
        }

        logger.debug("Reranking LLM: {} candidats → Top {}", candidates.size(), topK);

        try {
            if (useBatchScoring) {
                return rerankBatch(query, candidates, topK);
            } else {
                return rerankIndividual(query, candidates, topK);
            }
        } catch (Exception e) {
            logger.warn("Erreur reranking LLM: {}. Fallback sur ordre RRF original", e.getMessage());
            // Fallback: retourner ordre RRF original si LLM échoue
            return candidates.stream().limit(topK).collect(Collectors.toList());
        }
    }

    /**
     * Reranking individuel : 1 appel LLM par candidat (plus précis mais plus lent).
     */
    private List<EntryPoint> rerankIndividual(
        String query,
        List<EntryPoint> candidates,
        int topK
    ) throws SearchException {

        List<ScoredEntry> scoredEntries = new ArrayList<>();

        for (EntryPoint candidate : candidates) {
            double llmScore = scoreCandidateLLM(query, candidate);
            scoredEntries.add(new ScoredEntry(candidate, llmScore));
        }

        // Trier par score LLM décroissant
        scoredEntries.sort(Comparator.comparingDouble(ScoredEntry::llmScore).reversed());

        logger.debug("Reranking individuel: {} candidats scorés", scoredEntries.size());

        return scoredEntries.stream()
            .limit(topK)
            .map(ScoredEntry::entryPoint)
            .collect(Collectors.toList());
    }

    /**
     * Reranking batch : 1 appel LLM pour tous les candidats (plus rapide mais moins précis).
     */
    private List<EntryPoint> rerankBatch(
        String query,
        List<EntryPoint> candidates,
        int topK
    ) throws SearchException {

        // Construire liste candidats pour LLM
        StringBuilder candidatesList = new StringBuilder();
        for (int i = 0; i < candidates.size(); i++) {
            EntryPoint candidate = candidates.get(i);
            candidatesList.append(String.format(
                "%d. %s (%s)\n   FQN: %s\n   %s\n\n",
                i + 1,
                candidate.name(),
                candidate.nodeType(),
                candidate.fqn(),
                extractJavaDoc(candidate)
            ));
        }

        PromptTemplate template = PromptTemplate.from("""
            Voici une requête utilisateur et une liste de résultats de recherche dans du code Java.
            Classe les résultats du plus pertinent au moins pertinent par rapport à la requête.

            Requête: "{{query}}"

            Résultats:
            {{candidates}}

            Retourne UNIQUEMENT les numéros des {{topK}} résultats les plus pertinents, séparés par des virgules.
            Format attendu: 3, 1, 7
            (Pas d'explication, juste les numéros)
            """);

        Prompt prompt = template.apply(Map.of(
            "query", query,
            "candidates", candidatesList.toString(),
            "topK", topK
        ));

        String response = llmModel.chat(prompt.text());

        // Parser la réponse
        List<Integer> rankedIndices = parseRankedIndices(response, candidates.size());

        logger.debug("Reranking batch: réponse LLM = {}", response);

        // Construire résultats rerankés
        List<EntryPoint> reranked = new ArrayList<>();
        for (int index : rankedIndices) {
            if (index >= 0 && index < candidates.size()) {
                reranked.add(candidates.get(index));
            }
        }

        // Compléter si pas assez de résultats parsés
        if (reranked.size() < topK) {
            for (EntryPoint candidate : candidates) {
                if (!reranked.contains(candidate) && reranked.size() < topK) {
                    reranked.add(candidate);
                }
            }
        }

        return reranked.stream().limit(topK).collect(Collectors.toList());
    }

    /**
     * Score un candidat individuel avec le LLM.
     * <p>
     * Demande au LLM d'évaluer la pertinence sur une échelle de 0 à 10.
     *
     * @param query Requête utilisateur
     * @param candidate Candidat à scorer
     * @return Score de pertinence (0.0 - 10.0)
     */
    private double scoreCandidateLLM(String query, EntryPoint candidate) {
        try {
            String javaDoc = extractJavaDoc(candidate);
            String signature = extractSignature(candidate);

            PromptTemplate template = PromptTemplate.from("""
                Évalue la pertinence de ce résultat par rapport à la requête utilisateur.

                Requête: "{{query}}"

                Résultat:
                - Type: {{nodeType}}
                - Nom: {{name}}
                - FQN: {{fqn}}
                - Signature: {{signature}}
                - Description: {{javaDoc}}

                Donne un score de pertinence de 0 à 10 (10 = très pertinent, 0 = pas pertinent).
                Réponds UNIQUEMENT avec un nombre (ex: 7.5).
                """);

            Prompt prompt = template.apply(Map.of(
                "query", query,
                "nodeType", candidate.nodeType(),
                "name", candidate.name(),
                "fqn", candidate.fqn(),
                "signature", signature,
                "javaDoc", javaDoc
            ));

            String response = llmModel.chat(prompt.text()).trim();

            // Parser le score
            return parseScore(response);

        } catch (Exception e) {
            logger.warn("Erreur scoring LLM pour {}: {}. Score par défaut: 5.0",
                candidate.name(), e.getMessage());
            return 5.0; // Score neutre en cas d'erreur
        }
    }

    /**
     * Extrait le JavaDoc d'un EntryPoint (max 200 caractères).
     */
    private String extractJavaDoc(EntryPoint entry) {
        Object javaDoc = entry.properties().get("javaDoc");
        if (javaDoc instanceof String doc && !doc.isBlank()) {
            return doc.length() > 200 ? doc.substring(0, 200) + "..." : doc;
        }
        return "(Pas de documentation)";
    }

    /**
     * Extrait la signature d'un EntryPoint.
     */
    private String extractSignature(EntryPoint entry) {
        Object signature = entry.properties().get("signature");
        if (signature instanceof String sig && !sig.isBlank()) {
            return sig;
        }
        return entry.name(); // Fallback sur le nom
    }

    /**
     * Parse un score LLM (format attendu: nombre entre 0 et 10).
     */
    private double parseScore(String response) {
        try {
            // Extraire premier nombre trouvé
            Pattern pattern = Pattern.compile("\\d+\\.?\\d*");
            Matcher matcher = pattern.matcher(response);

            if (matcher.find()) {
                double score = Double.parseDouble(matcher.group());
                // Clamp entre 0 et 10
                return Math.max(0.0, Math.min(10.0, score));
            }

            logger.warn("Impossible de parser score LLM: '{}'. Score par défaut: 5.0", response);
            return 5.0;

        } catch (NumberFormatException e) {
            logger.warn("Format score invalide: '{}'. Score par défaut: 5.0", response);
            return 5.0;
        }
    }

    /**
     * Parse les indices rerankés depuis la réponse LLM (format: "3, 1, 7").
     */
    private List<Integer> parseRankedIndices(String response, int maxIndex) {
        List<Integer> indices = new ArrayList<>();

        try {
            // Extraire tous les nombres
            Pattern pattern = Pattern.compile("\\d+");
            Matcher matcher = pattern.matcher(response);

            while (matcher.find()) {
                int index = Integer.parseInt(matcher.group()) - 1; // Convertir 1-based → 0-based
                if (index >= 0 && index < maxIndex && !indices.contains(index)) {
                    indices.add(index);
                }
            }

        } catch (Exception e) {
            logger.warn("Erreur parsing indices rerankés: {}. Fallback sur ordre original", e.getMessage());
        }

        return indices;
    }

    /**
     * Entry avec score LLM.
     */
    private record ScoredEntry(
        EntryPoint entryPoint,
        double llmScore
    ) {}
}
