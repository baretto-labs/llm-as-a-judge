package fr.baretto.benchmarks.search;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests unitaires pour l'algorithme RRF (Reciprocal Rank Fusion).
 * Vérifie le comportement mathématique de la fusion sans dépendance externe.
 */
class RRFFusionTest {

    @Test
    @DisplayName("Un nœud 1er dans les 2 listes devrait gagner haut la main")
    void testNodeFirstInBothListsWins() {
        // Arrange
        List<Long> lexical = List.of(100L, 200L, 300L);
        List<Long> vector = List.of(100L, 400L, 500L);

        // Act
        List<Long> result = RRFFusion.fuse(List.of(lexical, vector), 3);

        // Assert
        assertEquals(100L, result.get(0), "Le nœud 100 devrait être en tête");

        // Vérifier le score RRF
        double score100 = RRFFusion.calculateScore(100L, List.of(lexical, vector), 60);
        double score200 = RRFFusion.calculateScore(200L, List.of(lexical, vector), 60);

        // score(100) = 1/(60+1) + 1/(60+1) ≈ 0.0328
        // score(200) = 1/(60+2)            ≈ 0.0161
        assertTrue(score100 > score200, "Le score du nœud 100 devrait être supérieur à celui de 200");
    }

    @Test
    @DisplayName("RRF favorise les nœuds présents dans plusieurs listes")
    void testRRFFavorsMultiListPresence() {
        // Arrange
        // Node 1: présent dans les 2 listes (rang 2 et 3)
        // Node 2: présent dans 1 liste uniquement (rang 1)
        List<Long> list1 = List.of(2L, 1L, 3L);
        List<Long> list2 = List.of(4L, 5L, 1L);

        // Act
        Map<Long, Double> scores = RRFFusion.fuseWithScores(List.of(list1, list2), 60, 5);

        // Assert
        // Node 1 : score = 1/(60+2) + 1/(60+3) ≈ 0.0320
        // Node 2 : score = 1/(60+1)            ≈ 0.0164
        double score1 = scores.get(1L);
        double score2 = scores.get(2L);

        assertTrue(score1 > score2,
            "Node 1 (présent dans 2 listes) devrait avoir un meilleur score que Node 2 (1 liste)");
    }

    @Test
    @DisplayName("Calcul correct du score RRF avec k=60")
    void testRRFScoreCalculation() {
        // Arrange
        List<Long> list1 = List.of(10L, 20L, 30L);
        List<Long> list2 = List.of(30L, 10L, 40L);

        // Act
        double score10 = RRFFusion.calculateScore(10L, List.of(list1, list2), 60);
        double score30 = RRFFusion.calculateScore(30L, List.of(list1, list2), 60);

        // Assert
        // Node 10: rang 1 dans list1, rang 2 dans list2
        // score = 1/(60+1) + 1/(60+2) = 1/61 + 1/62 ≈ 0.0325
        double expected10 = (1.0 / 61) + (1.0 / 62);
        assertEquals(expected10, score10, 0.0001, "Score du node 10 incorrect");

        // Node 30: rang 3 dans list1, rang 1 dans list2
        // score = 1/(60+3) + 1/(60+1) = 1/63 + 1/61 ≈ 0.0323
        double expected30 = (1.0 / 63) + (1.0 / 61);
        assertEquals(expected30, score30, 0.0001, "Score du node 30 incorrect");

        assertTrue(score10 > score30, "Node 10 devrait avoir un meilleur score que Node 30");
    }

    @Test
    @DisplayName("Top K limite correctement le nombre de résultats")
    void testTopKLimitsResults() {
        // Arrange
        List<Long> list1 = List.of(1L, 2L, 3L, 4L, 5L);
        List<Long> list2 = List.of(5L, 4L, 3L, 2L, 1L);

        // Act
        List<Long> top3 = RRFFusion.fuse(List.of(list1, list2), 3);

        // Assert
        assertEquals(3, top3.size(), "Devrait retourner exactement 3 résultats");
    }

    @Test
    @DisplayName("Fusion avec une seule liste retourne cette liste triée")
    void testFusionWithSingleList() {
        // Arrange
        List<Long> singleList = List.of(10L, 20L, 30L);

        // Act
        List<Long> result = RRFFusion.fuse(List.of(singleList), 3);

        // Assert
        assertEquals(3, result.size());
        assertEquals(List.of(10L, 20L, 30L), result, "L'ordre de la liste unique devrait être préservé");
    }

    @Test
    @DisplayName("Gestion des doublons : même nœud dans plusieurs listes")
    void testDuplicatesAcrossLists() {
        // Arrange
        List<Long> list1 = List.of(100L, 200L);
        List<Long> list2 = List.of(100L, 300L);
        List<Long> list3 = List.of(100L, 400L);

        // Act
        List<Long> result = RRFFusion.fuse(List.of(list1, list2, list3), 5);

        // Assert
        assertEquals(100L, result.get(0), "Node 100 (dans toutes les listes) devrait être en tête");
        assertEquals(4, result.size(), "Devrait avoir 4 résultats uniques (100, 200, 300, 400)");

        // Vérifier que 100 a le meilleur score
        double score100 = RRFFusion.calculateScore(100L, List.of(list1, list2, list3), 60);
        double score200 = RRFFusion.calculateScore(200L, List.of(list1, list2, list3), 60);

        // score(100) = 3 * 1/(60+1) ≈ 0.0492
        // score(200) = 1/(60+2)     ≈ 0.0161
        assertTrue(score100 > score200);
    }

    @Test
    @DisplayName("Listes de tailles différentes")
    void testListsOfDifferentSizes() {
        // Arrange
        List<Long> shortList = List.of(1L, 2L);
        List<Long> longList = List.of(3L, 4L, 5L, 6L, 7L);

        // Act
        List<Long> result = RRFFusion.fuse(List.of(shortList, longList), 10);

        // Assert
        assertEquals(7, result.size(), "Devrait retourner tous les nœuds uniques");
    }

    @Test
    @DisplayName("Constante k affecte les scores")
    void testKParameterAffectsScores() {
        // Arrange
        List<Long> list1 = List.of(10L, 20L);
        List<Long> list2 = List.of(20L, 10L);

        // Act avec k=60
        Map<Long, Double> scores60 = RRFFusion.fuseWithScores(List.of(list1, list2), 60, 2);

        // Act avec k=10 (plus petit k = plus de différence entre rangs)
        Map<Long, Double> scores10 = RRFFusion.fuseWithScores(List.of(list1, list2), 10, 2);

        // Assert
        // Les scores avec k=10 devraient être plus grands (dénominateur plus petit)
        assertTrue(scores10.get(10L) > scores60.get(10L),
            "Scores avec k=10 devraient être supérieurs à ceux avec k=60");
    }

    @Test
    @DisplayName("Exception si rankedLists est null ou vide")
    void testExceptionIfRankedListsNullOrEmpty() {
        assertThrows(IllegalArgumentException.class,
            () -> RRFFusion.fuse(null, 3),
            "Devrait lancer une exception si rankedLists est null");

        assertThrows(IllegalArgumentException.class,
            () -> RRFFusion.fuse(List.of(), 3),
            "Devrait lancer une exception si rankedLists est vide");
    }

    @Test
    @DisplayName("Exception si topK <= 0")
    void testExceptionIfTopKInvalid() {
        List<Long> list = List.of(1L, 2L, 3L);

        assertThrows(IllegalArgumentException.class,
            () -> RRFFusion.fuse(List.of(list), 0),
            "Devrait lancer une exception si topK = 0");

        assertThrows(IllegalArgumentException.class,
            () -> RRFFusion.fuse(List.of(list), -1),
            "Devrait lancer une exception si topK < 0");
    }

    @Test
    @DisplayName("Nœud absent d'une liste a un score partiel")
    void testNodeAbsentFromOneList() {
        // Arrange
        List<Long> list1 = List.of(10L, 20L, 30L);
        List<Long> list2 = List.of(40L, 50L, 60L);

        // Act
        double score10 = RRFFusion.calculateScore(10L, List.of(list1, list2), 60);

        // Assert
        // Node 10 est dans list1 (rang 1) mais absent de list2
        // score = 1/(60+1) + 0 = 1/61 ≈ 0.0164
        double expected = 1.0 / 61;
        assertEquals(expected, score10, 0.0001,
            "Score devrait être calculé uniquement sur la liste où le nœud est présent");
    }

    @Test
    @DisplayName("Exemple réel : UserService recherché")
    void testRealWorldExample() {
        // Arrange : Simulation d'une recherche "UserService"
        // Lexical (BM25) : trouve UserService en 1er, UserRepository en 2e
        List<Long> lexical = List.of(101L, 102L, 103L, 104L); // 101 = UserService

        // Vector (cosine) : trouve UserService en 3e (moins bon match sémantique)
        List<Long> vector = List.of(105L, 106L, 101L, 107L); // 101 = UserService (rang 3)

        // Act
        List<Long> result = RRFFusion.fuse(List.of(lexical, vector), 60, 5);

        // Assert
        assertEquals(101L, result.get(0),
            "UserService (101) devrait être en tête car présent dans les 2 listes");

        // Calculer les scores
        double score101 = RRFFusion.calculateScore(101L, List.of(lexical, vector), 60);
        double score102 = RRFFusion.calculateScore(102L, List.of(lexical, vector), 60);

        // 101: 1/(60+1) + 1/(60+3) ≈ 0.0323
        // 102: 1/(60+2) + 0        ≈ 0.0161
        assertTrue(score101 > score102,
            "UserService présent dans 2 listes bat UserRepository présent dans 1 seule");
    }

    @Test
    @DisplayName("FuseWithScores retourne une map ordonnée")
    void testFuseWithScoresReturnsOrderedMap() {
        // Arrange
        List<Long> list1 = List.of(1L, 2L, 3L);
        List<Long> list2 = List.of(3L, 1L, 4L);

        // Act
        Map<Long, Double> scores = RRFFusion.fuseWithScores(List.of(list1, list2), 60, 10);

        // Assert
        List<Long> orderedKeys = scores.keySet().stream().toList();

        // Vérifier que les clés sont dans l'ordre des scores décroissants
        for (int i = 0; i < orderedKeys.size() - 1; i++) {
            double score1 = scores.get(orderedKeys.get(i));
            double score2 = scores.get(orderedKeys.get(i + 1));
            assertTrue(score1 >= score2,
                "Les scores devraient être en ordre décroissant dans la map");
        }
    }
}
