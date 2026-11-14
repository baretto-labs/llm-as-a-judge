import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

/** Probes for batch_06: exceptions avalées par CompletableFuture, paresse des flux, ThreadLocal en pool. */
public class Probe06 {

    static final ThreadLocal<String> TENANT = new ThreadLocal<>();

    public static void main(String[] args) throws Exception {
        System.out.println("── CompletableFuture : exception non consommée");
        CompletableFuture<String> failing = CompletableFuture.supplyAsync(() -> {
            throw new IllegalStateException("échec métier");
        });
        CompletableFuture<Void> chained = failing.thenAccept(v -> System.out.println("   thenAccept exécuté : " + v));
        Thread.sleep(200);
        System.out.println("   future en échec ? " + failing.isCompletedExceptionally());
        System.out.println("   chaîne en échec ? " + chained.isCompletedExceptionally());
        System.out.println("   -> aucune trace dans les journaux si personne ne fait join()/get()");
        chained.exceptionally(e -> {
            System.out.println("   exceptionally voit : " + e.getClass().getSimpleName() + " / " + e.getMessage());
            return null;
        }).join();
        try {
            failing.join();
        } catch (CompletionException e) {
            System.out.println("   join() lève : " + e.getClass().getSimpleName()
                    + " causé par " + e.getCause().getClass().getSimpleName());
        }

        System.out.println("── paresse des flux");
        List<String> seen = new ArrayList<>();
        Stream<String> pipeline = Stream.of("a", "b", "c", "d")
                .peek(seen::add)
                .filter(s -> s.compareTo("b") >= 0);
        System.out.println("   avant opération terminale, éléments traversés : " + seen);
        Optional<String> first = pipeline.findFirst();
        System.out.println("   après findFirst=" + first.orElse("?") + ", traversés : " + seen);
        List<String> seenAll = new ArrayList<>();
        long count = Stream.of("a", "b", "c", "d").peek(seenAll::add).filter(s -> s.compareTo("b") >= 0).count();
        System.out.println("   count=" + count + ", traversés : " + seenAll);

        System.out.println("── ThreadLocal dans un pool réutilisé");
        ExecutorService pool = Executors.newFixedThreadPool(1);
        pool.submit(() -> {
            TENANT.set("client-A");
            System.out.println("   tâche 1 pose  : " + TENANT.get());
        }).get();
        pool.submit(() -> System.out.println("   tâche 2 lit   : " + TENANT.get() + "  <- fuite entre tâches")).get();
        pool.submit(() -> {
            try {
                TENANT.set("client-B");
                System.out.println("   tâche 3 pose  : " + TENANT.get());
            } finally {
                TENANT.remove();
            }
        }).get();
        pool.submit(() -> System.out.println("   tâche 4 lit   : " + TENANT.get() + "  <- après remove()")).get();
        pool.shutdown();
    }
}
