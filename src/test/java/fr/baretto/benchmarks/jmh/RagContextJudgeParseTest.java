package fr.baretto.benchmarks.jmh;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * L'analyse de la sortie du juge est tolérante et écrite à la main : la réponse commence par un
 * bloc {@code <thinking>} qu'aucun analyseur JSON strict n'accepte. Ces cas fixent ce qu'elle doit
 * garantir, avant qu'on lui fasse confiance sur un benchmark.
 */
class RagContextJudgeParseTest {

    @Test
    @DisplayName("extrait verdict, contrôles et motif d'une sortie au format du corpus")
    void sortieNominale() {
        String brut = """
            <thinking>
            1. Énumération : dix extraits, aucun corps de méthode.
            2. Vérification point par point : la requête porte sur le « comment ».
            3. Synthèse : les noms annoncent une intention, pas la mécanique. FAIL.
            </thinking>
            {
              "checks": {"contexte_pertinent": true, "contexte_suffisant": false, "bruit_maitrise": true},
              "verdict": "FAIL",
              "reason": "Aucun corps de méthode dans les extraits."
            }""";
        var j = RagContextJudge.parse(brut, 0.5);
        assertEquals("FAIL", j.verdict());
        assertEquals(3, j.checks().size());
        assertTrue(j.checks().get("contexte_pertinent"));
        assertFalse(j.checks().get("contexte_suffisant"));
        assertEquals("Aucun corps de méthode dans les extraits.", j.reason());
        assertEquals(0.5, j.hintCoverage());
        assertTrue(j.coherent(), "FAIL avec un contrôle faux respecte PASS ⟺ tous vrais");
    }

    @Test
    @DisplayName("une accolade dans le <thinking> ne détourne pas l'analyse")
    void accoladeDansLeRaisonnement() {
        String brut = """
            <thinking>
            Le contexte montre `{ "id": 1 }` dans un extrait, ce qui n'est pas un verdict.
            Synthèse : tout est étayé. PASS.
            </thinking>
            {"checks": {"contexte_pertinent": true, "contexte_suffisant": true, "bruit_maitrise": true},
             "verdict": "PASS", "reason": "Tous les extraits portent sur le symbole visé."}""";
        var j = RagContextJudge.parse(brut, 1.0);
        assertEquals("PASS", j.verdict());
        assertEquals(3, j.checks().size());
        assertTrue(j.coherent());
    }

    @Test
    @DisplayName("un PASS avec un contrôle faux est relevé comme incohérent, pas corrigé")
    void contradictionDuJuge() {
        String brut = """
            {"checks": {"contexte_pertinent": true, "contexte_suffisant": false, "bruit_maitrise": true},
             "verdict": "PASS", "reason": "Contradiction volontaire."}""";
        var j = RagContextJudge.parse(brut, 0.0);
        assertEquals("PASS", j.verdict());
        assertFalse(j.coherent(), "PASS avec un contrôle faux viole la règle et doit être signalé");
    }

    @Test
    @DisplayName("une sortie inexploitable vaut INVALID, jamais PASS")
    void sortieInexploitable() {
        assertTrue(RagContextJudge.parse("Je ne peux pas répondre.", 0.3).isInvalid());
        assertTrue(RagContextJudge.parse("", 0.3).isInvalid());
        assertTrue(RagContextJudge.parse(null, 0.3).isInvalid());
        assertFalse(RagContextJudge.parse("{\"foo\": 1}", 0.3).isPass());
    }

    @Test
    @DisplayName("hintCoverage est déterministe et insensible à la casse")
    void couvertureDesIndices() {
        String ctx = "class ContextRetriever implements ContentRetriever { List<Content> retrieve(Query q) }";
        assertEquals(1.0, RagContextJudge.computeHintCoverage(ctx, new String[]{"contextretriever", "RETRIEVE"}));
        assertEquals(0.5, RagContextJudge.computeHintCoverage(ctx, new String[]{"ContextRetriever", "absent"}));
        assertEquals(1.0, RagContextJudge.computeHintCoverage(ctx, new String[]{}));
    }
}
