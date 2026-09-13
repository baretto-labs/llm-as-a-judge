import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.Function;
import java.util.stream.Collectors;

public class FactCheck {
    record Customer(String email, boolean isActive) {}

    static Map<String, Customer> loop(List<Customer> customers) {
        Map<String, Customer> index = new HashMap<>();
        for (Customer c : customers) {
            if (c.isActive()) {
                index.put(c.email().toLowerCase(Locale.ROOT), c);
            }
        }
        return index;
    }

    static Map<String, Customer> stream(List<Customer> customers) {
        return customers.stream()
                .filter(Customer::isActive)
                .collect(Collectors.toMap(
                        c -> c.email().toLowerCase(Locale.ROOT),
                        Function.identity(),
                        (previous, next) -> next,
                        HashMap::new));
    }

    static volatile int count;

    public static void main(String[] args) throws Exception {
        // Example 1: duplicates, last wins, same map type
        List<Customer> cs = List.of(new Customer("A@x.com", true), new Customer("b@x.com", false), new Customer("a@x.com", true));
        Map<String, Customer> l = loop(cs), s = stream(cs);
        System.out.println("ex1 equal=" + l.equals(s) + " type=" + s.getClass().getSimpleName() + " value=" + s);
        try {
            cs.stream().filter(Customer::isActive).collect(Collectors.toMap(c -> c.email().toLowerCase(Locale.ROOT), Function.identity()));
        } catch (IllegalStateException e) {
            System.out.println("ex1 naive toMap throws ISE: " + e.getMessage());
        }

        // Example 4: nested future does not propagate async inner failure; sync throw does
        CompletableFuture<CompletableFuture<Integer>> nested = CompletableFuture.completedFuture(1)
                .thenApply(x -> CompletableFuture.<Integer>failedFuture(new RuntimeException("inner")));
        System.out.println("ex4 outer exceptional=" + nested.isCompletedExceptionally() + " inner exceptional=" + nested.join().isCompletedExceptionally());
        CompletableFuture<CompletableFuture<Integer>> syncThrow = CompletableFuture.completedFuture(1)
                .thenApply(x -> { throw new RuntimeException("sync"); });
        System.out.println("ex4 sync throw -> outer exceptional=" + syncThrow.isCompletedExceptionally());

        // Example 5: count++ on volatile loses updates
        Thread[] ts = new Thread[8];
        for (int i = 0; i < ts.length; i++) {
            ts[i] = new Thread(() -> { for (int j = 0; j < 1_000_000; j++) count++; });
            ts[i].start();
        }
        for (Thread t : ts) t.join();
        System.out.println("ex5 expected=8000000 actual=" + count);
    }
}
