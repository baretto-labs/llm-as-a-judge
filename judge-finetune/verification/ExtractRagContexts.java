import fr.baretto.benchmarks.jmh.QuestionCorpus;
import fr.baretto.benchmarks.strategy.FeatureFlags;
import fr.baretto.benchmarks.strategy.LuceneRagStrategy;
import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import fr.baretto.benchmarks.strategy.RagStrategy;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * Extrait les contextes RÉELLEMENT récupérés par une stratégie RAG, pour servir de matière
 * aux exemples RAG_CONTEXT_RELEVANCE et RAG_FAITHFULNESS du corpus de fine-tuning.
 *
 * Le contexte est conservé tel quel — bruit, doublons, troncatures comprises : c'est
 * précisément ce que le juge devra trancher en production.
 *
 * Usage :
 *   java -cp "target/classes:target/test-classes:$(cat cp.txt)" ExtractRagContexts.java \
 *        <codebase> <sortie.jsonl> <lucene|neo4j> <preset>
 *
 * Exemple :
 *   ... ~/Workspaces/Labs/OllamAssist contextes-lucene.jsonl lucene hybrid
 */
public class ExtractRagContexts {

    public static void main(String[] args) throws Exception {
        Path codebase = Path.of(args.length > 0 ? args[0] : System.getProperty("user.home") + "/Workspaces/Labs/OllamAssist");
        Path sortie = Path.of(args.length > 1 ? args[1] : "contextes-rag.jsonl");
        String strategie = args.length > 2 ? args[2] : "lucene";
        String preset = args.length > 3 ? args[3] : "hybrid";

        if (!Files.isDirectory(codebase)) {
            System.err.println("Codebase introuvable : " + codebase);
            System.exit(1);
        }

        FeatureFlags flags = FeatureFlags.fromPreset(preset);
        System.out.printf("Stratégie=%s preset=%s codebase=%s%n", strategie, preset, codebase);

        long t0 = System.nanoTime();
        try (RagStrategy rag = creer(strategie, flags)) {
            System.out.println("Indexation en cours…");
            rag.indexDirectory(codebase);
            System.out.printf("Indexation terminée en %.1f s%n", (System.nanoTime() - t0) / 1e9);

            List<String> lignes = new ArrayList<>();
            int i = 0;
            for (QuestionCorpus.Question q : QuestionCorpus.QUESTIONS) {
                i++;
                long tq = System.nanoTime();
                List<String> contexte;
                String erreur = null;
                try {
                    contexte = rag.retrieveContext(q.text());
                } catch (Exception e) {
                    contexte = List.of();
                    erreur = e.getClass().getSimpleName() + ": " + e.getMessage();
                }
                double ms = (System.nanoTime() - tq) / 1e6;

                int caracteres = contexte.stream().mapToInt(String::length).sum();
                double couverture = couvertureIndices(contexte, q.expectedFqnHints());
                long distincts = contexte.stream().distinct().count();

                System.out.printf("  %2d/%d  %-12s %2d extraits, %5d car., doublons=%d, indices=%.0f%%, %.0f ms%s%n",
                        i, QuestionCorpus.QUESTIONS.size(), q.difficulty(), contexte.size(), caracteres,
                        contexte.size() - distincts, couverture * 100, ms,
                        erreur == null ? "" : "  ERREUR " + erreur);

                lignes.add(versJson(strategie, preset, q, contexte, caracteres, distincts, couverture, ms, erreur));
            }
            Files.write(sortie, String.join("\n", lignes).getBytes(StandardCharsets.UTF_8));
            System.out.printf("%d contextes écrits dans %s%n", lignes.size(), sortie.toAbsolutePath());
        }
    }

    private static RagStrategy creer(String nom, FeatureFlags flags) {
        return switch (nom) {
            case "lucene" -> new LuceneRagStrategy(Path.of("./lucene-db-extract"), flags);
            case "neo4j" -> new Neo4jGraphRagStrategy("./neo4j-db-extract", flags);
            default -> throw new IllegalArgumentException("stratégie inconnue : " + nom);
        };
    }

    /** Fraction des indices attendus présents dans le contexte, calcul déterministe sans LLM. */
    private static double couvertureIndices(List<String> contexte, String[] indices) {
        if (indices == null || indices.length == 0) return 1.0;
        String tout = String.join("\n", contexte).toLowerCase();
        long trouves = 0;
        for (String indice : indices) {
            if (tout.contains(indice.toLowerCase())) trouves++;
        }
        return (double) trouves / indices.length;
    }

    private static String versJson(String strategie, String preset, QuestionCorpus.Question q,
                                   List<String> contexte, int caracteres, long distincts,
                                   double couverture, double ms, String erreur) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\"strategie\":").append(ech(strategie));
        sb.append(",\"preset\":").append(ech(preset));
        sb.append(",\"question\":").append(ech(q.text()));
        sb.append(",\"difficulte\":").append(ech(q.difficulty().name()));
        sb.append(",\"indices_attendus\":[");
        for (int i = 0; i < q.expectedFqnHints().length; i++) {
            if (i > 0) sb.append(',');
            sb.append(ech(q.expectedFqnHints()[i]));
        }
        // Locale.ROOT impératif : la locale par défaut (fr) écrit « 1,000 », ce qui casse le JSON.
        sb.append("],\"couverture_indices\":").append(String.format(java.util.Locale.ROOT, "%.3f", couverture));
        sb.append(",\"nb_extraits\":").append(contexte.size());
        sb.append(",\"nb_extraits_distincts\":").append(distincts);
        sb.append(",\"caracteres\":").append(caracteres);
        sb.append(",\"latence_ms\":").append(String.format(java.util.Locale.ROOT, "%.0f", ms));
        sb.append(",\"erreur\":").append(erreur == null ? "null" : ech(erreur));
        sb.append(",\"contexte\":[");
        for (int i = 0; i < contexte.size(); i++) {
            if (i > 0) sb.append(',');
            sb.append(ech(contexte.get(i)));
        }
        sb.append("]}");
        return sb.toString();
    }

    private static String ech(String s) {
        StringBuilder sb = new StringBuilder("\"");
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
                }
            }
        }
        return sb.append('"').toString();
    }
}
