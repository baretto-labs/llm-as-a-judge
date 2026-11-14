import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

/** Fact-checks the Java claims of batch_02 (b02-003, b02-004, b02-009, b02-010). */
public class FactCheck02 {

    // b02-003 : "fixed" Point where equals only compares x
    static final class PointBroken {
        final int x, y;
        PointBroken(int x, int y) { this.x = x; this.y = y; }
        @Override public boolean equals(Object o) {
            if (!(o instanceof PointBroken p)) return false;
            return x == p.x;
        }
        @Override public int hashCode() { return Integer.hashCode(x); }
    }

    // b02-010 : equals without hashCode
    static final class PointNoHash {
        final int x, y;
        PointNoHash(int x, int y) { this.x = x; this.y = y; }
        @Override public boolean equals(Object o) {
            if (!(o instanceof PointNoHash p)) return false;
            return x == p.x && y == p.y;
        }
    }

    // b02-004 : refactored version
    static String readFirstLine(Path path) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(path.toFile()))) {
            return reader.readLine();
        }
    }

    // b02-009 : the answer's logic (wrong signature, right logic)
    static String firstNonBlank(List<String> values) {
        if (values == null) return null;
        for (String value : values) {
            if (value != null && !value.isBlank()) return value;
        }
        return null;
    }

    static void ok(String label, boolean cond, String detail) {
        System.out.println((cond ? "OK  " : "KO  ") + label + (detail.isEmpty() ? "" : "  " + detail));
    }

    public static void main(String[] args) throws Exception {
        System.out.println("── b02-003");
        var set = new HashSet<>(List.of(new PointBroken(1, 2), new PointBroken(1, 2)));
        ok("le test cible passe (doublons dédupliqués)", set.size() == 1, "size=" + set.size());
        ok("régression : (1,2).equals((1,3))", new PointBroken(1, 2).equals(new PointBroken(1, 3)), "");
        var regression = new HashSet<>(List.of(new PointBroken(1, 2), new PointBroken(1, 3)));
        ok("régression : HashSet écrase (1,3)", regression.size() == 1, "size=" + regression.size());

        System.out.println("── b02-010");
        var noHash = new HashSet<PointNoHash>();
        noHash.add(new PointNoHash(1, 2));
        noHash.add(new PointNoHash(1, 2));
        ok("equals sans hashCode : doublons dans HashSet", noHash.size() == 2, "size=" + noHash.size());
        var map = new HashMap<PointNoHash, String>();
        map.put(new PointNoHash(1, 2), "v");
        ok("equals sans hashCode : map.get renvoie null", map.get(new PointNoHash(1, 2)) == null, "");

        System.out.println("── b02-004");
        Path file = Files.createTempFile("fc02", ".txt");
        Files.writeString(file, "première ligne\nseconde ligne\n");
        ok("première ligne lue", "première ligne".equals(readFirstLine(file)), readFirstLine(file));
        Path empty = Files.createTempFile("fc02empty", ".txt");
        ok("fichier vide -> null", readFirstLine(empty) == null, "");
        Files.deleteIfExists(file);
        Files.deleteIfExists(empty);

        System.out.println("── b02-009");
        var values = new ArrayList<String>(Arrays.asList(null, "  ", "", "premier", "second"));
        ok("logique de sélection correcte", "premier".equals(firstNonBlank(values)), firstNonBlank(values));
        ok("liste sans valeur -> null", firstNonBlank(List.of("", " ")) == null, "");
    }
}
