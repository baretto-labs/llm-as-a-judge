import java.io.*;
import java.util.*;

/** Probes for batch_08: serialVersionUID, préchauffage JIT, HashMap avec clé mutable. */
public class Probe08 {

    static class V1 implements Serializable {
        private static final long serialVersionUID = 1L;
        final String nom;
        V1(String nom) { this.nom = nom; }
    }

    static class V2Sans implements Serializable {
        // pas de serialVersionUID : la JVM en calcule un à partir de la structure
        final String nom;
        final int age;
        V2Sans(String nom, int age) { this.nom = nom; this.age = age; }
    }

    static class Cle {
        int valeur;
        Cle(int valeur) { this.valeur = valeur; }
        @Override public boolean equals(Object o) { return o instanceof Cle c && c.valeur == valeur; }
        @Override public int hashCode() { return Integer.hashCode(valeur); }
    }

    static byte[] serialise(Object o) throws IOException {
        var bos = new ByteArrayOutputStream();
        try (var oos = new ObjectOutputStream(bos)) { oos.writeObject(o); }
        return bos.toByteArray();
    }

    public static void main(String[] args) throws Exception {
        System.out.println("── serialVersionUID");
        byte[] flux = serialise(new V1("ana"));
        System.out.println("   V1 sérialisée : " + flux.length + " octets");
        try (var ois = new ObjectInputStream(new ByteArrayInputStream(flux))) {
            V1 relu = (V1) ois.readObject();
            System.out.println("   relecture même classe : " + relu.nom);
        }
        // Simule une évolution de classe sans UID explicite : deux structures différentes
        byte[] fluxSans = serialise(new V2Sans("ana", 30));
        System.out.println("   V2Sans (sans UID explicite) sérialisée : " + fluxSans.length + " octets");
        System.out.println("   UID calculé par la JVM pour V2Sans : "
                + ObjectStreamClass.lookup(V2Sans.class).getSerialVersionUID());
        System.out.println("   UID déclaré pour V1 : " + ObjectStreamClass.lookup(V1.class).getSerialVersionUID());

        System.out.println("── préchauffage JIT");
        long[] mesures = new long[5];
        for (int tour = 0; tour < mesures.length; tour++) {
            long t0 = System.nanoTime();
            long acc = 0;
            for (int i = 0; i < 20_000_000; i++) acc += i % 7;
            mesures[tour] = (System.nanoTime() - t0) / 1_000_000;
            if (acc == Long.MIN_VALUE) System.out.print("");
        }
        System.out.println("   durées successives (ms) : " + Arrays.toString(mesures));
        System.out.println("   rapport 1er / dernier : "
                + String.format("%.1fx", mesures[0] / (double) Math.max(1, mesures[mesures.length - 1])));

        System.out.println("── clé mutable dans une HashMap");
        Map<Cle, String> map = new HashMap<>();
        Cle cle = new Cle(1);
        map.put(cle, "valeur");
        System.out.println("   avant mutation : get(new Cle(1)) = " + map.get(new Cle(1)));
        cle.valeur = 2;
        System.out.println("   après mutation : get(new Cle(2)) = " + map.get(new Cle(2)));
        System.out.println("   après mutation : get(new Cle(1)) = " + map.get(new Cle(1)));
        System.out.println("   containsValue  = " + map.containsValue("valeur") + ", taille = " + map.size());
    }
}
