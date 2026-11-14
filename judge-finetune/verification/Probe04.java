import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;
import java.util.stream.Stream;

/** Probes for batch_04 Java candidates: CME, Arrays.asList, stream reuse, float money, concat. */
public class Probe04 {

    public static void main(String[] args) {
        System.out.println("── suppression pendant l'itération");
        List<String> items = new ArrayList<>(List.of("a", "b", "c", "d"));
        try {
            for (String s : items) {
                if (s.equals("b")) items.remove(s);
            }
            System.out.println("   for-each + remove : aucune exception, liste=" + items);
        } catch (ConcurrentModificationException e) {
            System.out.println("   for-each + remove : ConcurrentModificationException");
        }
        // Cas piégeux : supprimer l'avant-dernier élément ne lève PAS d'exception
        List<String> two = new ArrayList<>(List.of("a", "b"));
        try {
            for (String s : two) {
                if (s.equals("a")) two.remove(s);
            }
            System.out.println("   avant-dernier élément : aucune exception, liste=" + two);
        } catch (ConcurrentModificationException e) {
            System.out.println("   avant-dernier élément : ConcurrentModificationException");
        }
        List<String> ok = new ArrayList<>(List.of("a", "b", "c", "d"));
        ok.removeIf(s -> s.equals("b"));
        System.out.println("   removeIf : liste=" + ok);

        System.out.println("── Arrays.asList");
        List<String> fixed = Arrays.asList("a", "b");
        try {
            fixed.add("c");
            System.out.println("   add : accepté");
        } catch (UnsupportedOperationException e) {
            System.out.println("   add : UnsupportedOperationException");
        }
        try {
            fixed.set(0, "z");
            System.out.println("   set : accepté, liste=" + fixed);
        } catch (UnsupportedOperationException e) {
            System.out.println("   set : UnsupportedOperationException");
        }
        try {
            List.of("a", "b").set(0, "z");
            System.out.println("   List.of + set : accepté");
        } catch (UnsupportedOperationException e) {
            System.out.println("   List.of + set : UnsupportedOperationException");
        }

        System.out.println("── réutilisation d'un Stream");
        Stream<String> stream = Stream.of("a", "b", "c");
        System.out.println("   premier terminal : " + stream.count());
        try {
            System.out.println("   second terminal : " + stream.count());
        } catch (IllegalStateException e) {
            System.out.println("   second terminal : IllegalStateException — " + e.getMessage());
        }

        System.out.println("── flottants et monnaie");
        System.out.println("   0.1 + 0.2 == 0.3 ? " + (0.1 + 0.2 == 0.3) + "  (valeur=" + (0.1 + 0.2) + ")");
        double total = 0;
        for (int i = 0; i < 10; i++) total += 0.1;
        System.out.println("   somme de dix fois 0.1 = " + total + ", == 1.0 ? " + (total == 1.0));
        BigDecimal bd = new BigDecimal("0.10").multiply(BigDecimal.valueOf(3));
        System.out.println("   BigDecimal 0.10 x 3 = " + bd);
        System.out.println("   0.615 arrondi HALF_UP à 2 déc. = "
                + new BigDecimal("0.615").setScale(2, RoundingMode.HALF_UP)
                + " | double 0.615 -> " + BigDecimal.valueOf(0.615).setScale(2, RoundingMode.HALF_UP));

        System.out.println("── concaténation en boucle");
        int n = 20000;
        long t0 = System.nanoTime();
        String s = "";
        for (int i = 0; i < n; i++) s += "x";
        long concatMs = (System.nanoTime() - t0) / 1_000_000;
        t0 = System.nanoTime();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) sb.append("x");
        long builderMs = (System.nanoTime() - t0) / 1_000_000;
        System.out.println("   " + n + " concaténations : String += " + concatMs + " ms, StringBuilder " + builderMs + " ms");
    }
}
