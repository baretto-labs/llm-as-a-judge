import java.util.*;

/** Probes for batch_10: contrat de Comparable, tri de grandes listes, Cleaner contre finalize. */
public class Probe10 {

    record Candidat(String nom, double score) { }

    static List<Candidat> jeu(int taille) {
        Random rng = new Random(42);
        List<Candidat> liste = new ArrayList<>(taille);
        for (int i = 0; i < taille; i++) {
            liste.add(new Candidat("c" + i, rng.nextInt(5)));   // beaucoup d'ex æquo
        }
        return liste;
    }

    public static void main(String[] args) {
        System.out.println("── comparateur qui ne renvoie jamais 0");
        for (int taille : new int[]{16, 32, 100, 1000}) {
            List<Candidat> liste = new ArrayList<>(jeu(taille));
            try {
                liste.sort((a, b) -> a.score() >= b.score() ? 1 : -1);
                System.out.println("   n=" + taille + " : tri terminé sans exception");
            } catch (IllegalArgumentException e) {
                System.out.println("   n=" + taille + " : IllegalArgumentException — " + e.getMessage());
            }
        }

        System.out.println("── comparateur correct");
        List<Candidat> liste = new ArrayList<>(jeu(1000));
        liste.sort(Comparator.comparingDouble(Candidat::score));
        System.out.println("   Comparator.comparingDouble : tri terminé, premier=" + liste.get(0).score()
                + ", dernier=" + liste.get(liste.size() - 1).score());

        System.out.println("── soustraction dans un comparateur");
        int grand = Integer.MAX_VALUE - 1, petit = -10;
        System.out.println("   grand - petit = " + (grand - petit) + "   <- débordement, signe inversé");
        System.out.println("   Integer.compare(grand, petit) = " + Integer.compare(grand, petit));
        double a = 0.1 + 0.2, b = 0.3;
        System.out.println("   (0.1+0.2) - 0.3 = " + (a - b) + " -> cast en int : " + (int) (a - b));
        System.out.println("   Double.compare(0.1+0.2, 0.3) = " + Double.compare(a, b));

        System.out.println("── ordre naturel incohérent avec equals");
        record Version(int majeur, int mineur) implements Comparable<Version> {
            @Override public int compareTo(Version o) { return Integer.compare(majeur, o.majeur); }
        }
        Version v1 = new Version(1, 0), v2 = new Version(1, 5);
        System.out.println("   v1.equals(v2) = " + v1.equals(v2) + ", v1.compareTo(v2) = " + v1.compareTo(v2));
        TreeSet<Version> arbre = new TreeSet<>(List.of(v1, v2));
        Set<Version> hache = new HashSet<>(List.of(v1, v2));
        System.out.println("   TreeSet.size = " + arbre.size() + "   <- compareTo fait foi, v2 est perdue");
        System.out.println("   HashSet.size = " + hache.size() + "   <- equals fait foi");
    }
}
