import java.util.*;
import java.util.concurrent.*;

/** Probes for batch_07: verrous croisés, effacement de type, initialisation paresseuse. */
public class Probe07 {

    static final Object LOCK_A = new Object();
    static final Object LOCK_B = new Object();

    static void deadlockDemo() throws Exception {
        CountDownLatch both = new CountDownLatch(2);
        Thread t1 = new Thread(() -> {
            synchronized (LOCK_A) {
                both.countDown();
                try { both.await(1, TimeUnit.SECONDS); } catch (InterruptedException ignored) { }
                synchronized (LOCK_B) { System.out.println("   t1 a obtenu les deux verrous"); }
            }
        }, "t1");
        Thread t2 = new Thread(() -> {
            synchronized (LOCK_B) {
                both.countDown();
                try { both.await(1, TimeUnit.SECONDS); } catch (InterruptedException ignored) { }
                synchronized (LOCK_A) { System.out.println("   t2 a obtenu les deux verrous"); }
            }
        }, "t2");
        t1.setDaemon(true);
        t2.setDaemon(true);
        t1.start();
        t2.start();
        t1.join(2000);
        t2.join(2000);
        System.out.println("   après 2 s : t1=" + t1.getState() + ", t2=" + t2.getState());
        ThreadMXBeanCheck();
    }

    static void ThreadMXBeanCheck() {
        long[] deadlocked = java.lang.management.ManagementFactory.getThreadMXBean().findDeadlockedThreads();
        System.out.println("   findDeadlockedThreads : "
                + (deadlocked == null ? "aucun" : deadlocked.length + " thread(s) en interblocage"));
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    static void erasureDemo() {
        List<String> names = new ArrayList<>();
        System.out.println("   ArrayList<String>.getClass() == ArrayList<Integer>.getClass() ? "
                + (names.getClass() == new ArrayList<Integer>().getClass()));

        List raw = names;                 // type brut : le compilateur ne vérifie plus rien
        raw.add(42);                      // accepté à la compilation comme à l'exécution
        System.out.println("   après raw.add(42), taille = " + names.size() + ", contenu = " + names);
        try {
            String s = names.get(0);      // le transtypage inséré par le compilateur échoue ici
            System.out.println("   lecture typée : " + s);
        } catch (ClassCastException e) {
            System.out.println("   lecture typée : ClassCastException — " + e.getMessage());
        }
        System.out.println("   l'élément réellement stocké est un " + ((Object) names.get(0)).getClass().getName());
    }

    static class Holder {
        private Map<String, String> cache;          // initialisation paresseuse non synchronisée
        Map<String, String> cache() {
            if (cache == null) {
                cache = new HashMap<>();
            }
            return cache;
        }
    }

    static void lazyInitDemo() throws Exception {
        int collisions = 0;
        for (int run = 0; run < 200; run++) {
            Holder holder = new Holder();
            CountDownLatch start = new CountDownLatch(1);
            Set<Map<String, String>> seen = ConcurrentHashMap.newKeySet();
            Thread[] threads = new Thread[4];
            for (int i = 0; i < threads.length; i++) {
                threads[i] = new Thread(() -> {
                    try { start.await(); } catch (InterruptedException ignored) { }
                    seen.add(holder.cache());
                });
                threads[i].start();
            }
            start.countDown();
            for (Thread t : threads) t.join();
            if (seen.size() > 1) collisions++;
        }
        System.out.println("   sur 200 essais, " + collisions
                + " où les threads ont obtenu des instances de cache différentes");
    }

    public static void main(String[] args) throws Exception {
        System.out.println("── verrous croisés");
        deadlockDemo();
        System.out.println("── effacement de type");
        erasureDemo();
        System.out.println("── initialisation paresseuse non synchronisée");
        lazyInitDemo();
    }
}
