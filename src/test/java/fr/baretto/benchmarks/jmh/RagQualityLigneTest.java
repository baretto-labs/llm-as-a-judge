package fr.baretto.benchmarks.jmh;

import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Vérifie que les lignes JSONL écrites par {@link RagQualityEvaluation} sont du JSON valide,
 * avec et sans volet réponse.
 *
 * <p><b>Pourquoi ce test existe.</b> Ces lignes sont produites par un {@code String.format} de
 * plus de vingt arguments, et l'erreur d'arité ne se manifeste qu'à l'écriture — c'est-à-dire
 * <b>après</b> la boucle de génération. Sur un banc de deux heures, la découvrir à la fin
 * coûterait la campagne entière. Ici elle coûte une seconde et aucun appel de modèle.</p>
 */
class RagQualityLigneTest {

    private static final String[] INDICES = {"fr.baretto.Foo"};

    private static RagContextJudge.Judgement jugement(String verdict, Map<String, Boolean> checks) {
        return new RagContextJudge.Judgement(checks, verdict, "parce que \"ça\" dépasse\nde la ligne", 0.5, true);
    }

    private static RagQualityEvaluation.Paire paire(boolean avecReponse) {
        var q = QuestionCorpus.QUESTIONS.get(0);
        var jc = jugement("PASS", Map.of("contexte_pertinent", true,
            "contexte_suffisant", true, "bruit_maitrise", true));
        var jr = jugement("FAIL", Map.of("affirmations_etayees", false,
            "absence_invention", false, "citations_exactes", true));
        var a = new RagAnswerer.Answer("Une réponse\tavec \"guillemets\" et un \\ antislash", "ctx", 1234L, false);
        return new RagQualityEvaluation.Paire(q,
            List.of("extrait A", "extrait B"), jc,
            List.of("extrait C"), jc,
            avecReponse ? a : null, avecReponse ? jr : null,
            avecReponse ? a : null, avecReponse ? jr : null);
    }

    /** Analyseur minimal : il suffit de prouver que la ligne est équilibrée et bien échappée. */
    private static Map<String, String> champs(String ligne) {
        assertTrue(ligne.startsWith("{") && ligne.strip().endsWith("}"), "accolades : " + ligne);
        var out = new java.util.LinkedHashMap<String, String>();
        boolean dansChaine = false, echappe = false;
        int profondeur = 0;
        StringBuilder courant = new StringBuilder();
        String cle = null;
        for (char c : ligne.strip().substring(1, ligne.strip().length() - 1).toCharArray()) {
            if (echappe)            { echappe = false; courant.append(c); continue; }
            if (c == '\\')          { echappe = true;  courant.append(c); continue; }
            if (c == '"')           { dansChaine = !dansChaine; courant.append(c); continue; }
            if (dansChaine)         { courant.append(c); continue; }
            if (c == '{' || c == '[') profondeur++;
            if (c == '}' || c == ']') profondeur--;
            if (c == ':' && profondeur == 0 && cle == null) {
                cle = courant.toString().strip().replaceAll("^\"|\"$", "");
                courant.setLength(0);
                continue;
            }
            if (c == ',' && profondeur == 0) {
                out.put(cle, courant.toString().strip());
                cle = null; courant.setLength(0);
                continue;
            }
            courant.append(c);
        }
        if (cle != null) out.put(cle, courant.toString().strip());
        assertEquals(0, profondeur, "imbrication déséquilibrée : " + ligne);
        assertTrue(!dansChaine, "chaîne non refermée : " + ligne);
        return out;
    }

    @Test
    void ligneDetailAvecReponseEstDuJsonValide() {
        var sb = new StringBuilder();
        var p = paire(true);
        RagQualityEvaluation.ligneDetail(sb, p, "lucene", p.ctxLucene(), p.jLucene(),
            p.aLucene(), p.rLucene(), "juge-ctx", "knn-only|hybrid-graph", "qwen2.5:7b", "mistral-24b");
        var f = champs(sb.toString());
        assertEquals("\"binaire-v2\"", f.get("schema"));
        assertEquals("\"FAIL\"", f.get("answerVerdict"));
        assertEquals("1234", f.get("answerMillis"));
        assertEquals("\"qwen2.5:7b\"", f.get("answerModel"));
        assertTrue(f.containsKey("context"), "le champ s'appelle context, plus generated");
        assertTrue(!f.containsKey("generated"), "generated ne doit plus être écrit");
        assertTrue(f.get("answerChecks").contains("absence_invention"), f.get("answerChecks"));
    }

    @Test
    void ligneDetailSansReponsePorteDesNullsEtNonDesZeros() {
        var sb = new StringBuilder();
        var p = paire(false);
        RagQualityEvaluation.ligneDetail(sb, p, "neo4j", p.ctxNeo4j(), p.jNeo4j(),
            p.aNeo4j(), p.rNeo4j(), "juge-ctx", "hybrid|hybrid", "disabled", "disabled");
        var f = champs(sb.toString());
        // Un 0 ici se lirait « aucune réponse fidèle » au lieu de « pas de réponse jugée ».
        for (String c : List.of("answer", "answerVerdict", "answerChecks", "answerHintCoverage")) {
            assertEquals("null", f.get(c), c);
        }
    }

    @Test
    void ligneSyntheseEstDuJsonValideDansLesDeuxRegimes() {
        for (boolean avecReponse : new boolean[]{true, false}) {
            var sb = new StringBuilder();
            var paires = List.of(paire(avecReponse));
            RagQualityEvaluation.ligneSynthese(sb, paires, "lucene", "ALL", "juge-ctx",
                "knn-only|hybrid-graph", RagQualityEvaluation.mcNemarPourTest(paires),
                avecReponse ? "qwen2.5:7b" : "disabled", avecReponse ? "mistral-24b" : "disabled");
            var f = champs(sb.toString());
            assertEquals(avecReponse ? "0,000" .replace(',', '.') : "null", f.get("answerPassRate"));
            assertEquals("\"binaire-v2\"", f.get("schema"));
        }
    }
}
