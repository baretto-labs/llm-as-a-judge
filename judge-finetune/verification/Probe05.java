import java.util.*;
import java.util.concurrent.*;

/** Probes for batch_05: overflow, division, intern, stabilité du tri, HashMap partagée. */
public class Probe05 {

    record Employee(String dept, String name) {}

    public static void main(String[] args) throws Exception {
        System.out.println("── dépassement d'entier");
        System.out.println("   Integer.MAX_VALUE + 1 = " + (Integer.MAX_VALUE + 1));
        try {
            Math.addExact(Integer.MAX_VALUE, 1);
            System.out.println("   Math.addExact : aucune exception");
        } catch (ArithmeticException e) {
            System.out.println("   Math.addExact : ArithmeticException — " + e.getMessage());
        }
        int lo = 0, hi = Integer.MAX_VALUE;
        System.out.println("   (lo + hi) / 2       = " + ((lo + hi) / 2) + "   <- milieu de recherche binaire");
        System.out.println("   lo + (hi - lo) / 2  = " + (lo + (hi - lo) / 2));

        System.out.println("── division entière");
        System.out.println("   7 / 2 = " + (7 / 2) + " | -7 / 2 = " + (-7 / 2)
                + " | Math.floorDiv(-7, 2) = " + Math.floorDiv(-7, 2));
        System.out.println("   -7 % 2 = " + (-7 % 2) + " | Math.floorMod(-7, 2) = " + Math.floorMod(-7, 2));

        System.out.println("── identité des chaînes");
        String a = "config", b = "config";
        String c = new String("config");
        System.out.println("   littéral == littéral        : " + (a == b));
        System.out.println("   littéral == new String      : " + (a == c));
        System.out.println("   littéral == c.intern()      : " + (a == c.intern()));
        System.out.println("   equals                      : " + a.equals(c));
        String concat = "con" + "fig";              // constante de compilation
        String runtime = new StringBuilder("con").append("fig").toString();
        System.out.println("   concat constante == littéral: " + (a == concat));
        System.out.println("   concat runtime  == littéral : " + (a == runtime));

        System.out.println("── stabilité du tri");
        List<Employee> staff = new ArrayList<>(List.of(
                new Employee("R&D", "Ana"), new Employee("Ops", "Bob"),
                new Employee("R&D", "Cid"), new Employee("Ops", "Dan")));
        staff.sort(Comparator.comparing(Employee::dept));
        System.out.println("   List.sort par dept : " + staff);
        Employee[] array = {new Employee("R&D", "Ana"), new Employee("Ops", "Bob"),
                new Employee("R&D", "Cid"), new Employee("Ops", "Dan")};
        Arrays.sort(array, Comparator.comparing(Employee::dept));
        System.out.println("   Arrays.sort(Object[]) : " + Arrays.toString(array));

        System.out.println("── HashMap partagée entre threads");
        for (int run = 1; run <= 3; run++) {
            Map<Integer, Integer> shared = new HashMap<>();
            Map<Integer, Integer> safe = new ConcurrentHashMap<>();
            int threads = 4, perThread = 20_000;
            ExecutorService pool = Executors.newFixedThreadPool(threads);
            for (int t = 0; t < threads; t++) {
                int base = t * perThread;
                pool.submit(() -> {
                    for (int i = 0; i < perThread; i++) {
                        shared.put(base + i, i);
                        safe.put(base + i, i);
                    }
                });
            }
            pool.shutdown();
            pool.awaitTermination(30, TimeUnit.SECONDS);
            int expected = threads * perThread;
            System.out.println("   run " + run + " : HashMap=" + shared.size()
                    + " / ConcurrentHashMap=" + safe.size() + " (attendu " + expected + ")");
        }
    }
}
