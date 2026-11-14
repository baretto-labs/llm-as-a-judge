import java.lang.annotation.*;
import java.lang.reflect.*;
import java.util.*;

/** Probes for batch_09: rétention d'annotations, réflexion, Optional et null. */
public class Probe09 {

    @Retention(RetentionPolicy.CLASS)
    @Target(ElementType.METHOD)
    @interface AuditCompile { }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    @interface AuditRuntime { }

    static class Service {
        @AuditCompile void compile() { }
        @AuditRuntime void runtime() { }
        private String secret = "valeur privée";
    }

    public static void main(String[] args) throws Exception {
        System.out.println("── rétention des annotations");
        for (Method m : Service.class.getDeclaredMethods()) {
            Annotation[] vues = m.getAnnotations();
            System.out.println("   méthode " + m.getName() + " : " + vues.length + " annotation(s) visible(s) par réflexion "
                    + Arrays.toString(Arrays.stream(vues).map(a -> a.annotationType().getSimpleName()).toArray()));
        }
        System.out.println("   -> une annotation en rétention CLASS est dans le .class mais absente à l'exécution");

        System.out.println("── réflexion et champ privé");
        Service s = new Service();
        Field f = Service.class.getDeclaredField("secret");
        System.out.println("   lecture directe sans setAccessible : ");
        try {
            System.out.println("   " + f.get(s));
        } catch (IllegalAccessException e) {
            System.out.println("   IllegalAccessException — " + e.getMessage().substring(0, Math.min(90, e.getMessage().length())));
        }
        f.setAccessible(true);
        System.out.println("   après setAccessible(true) : " + f.get(s));

        System.out.println("── Optional et null");
        System.out.println("   Optional.ofNullable(null).isPresent() = " + Optional.ofNullable(null).isPresent());
        try {
            Optional.of(null);
        } catch (NullPointerException e) {
            System.out.println("   Optional.of(null) -> NullPointerException");
        }
        Optional<String> vide = Optional.empty();
        System.out.println("   vide.map(String::length).orElse(-1) = " + vide.map(String::length).orElse(-1));
        Map<String, String> map = new HashMap<>();
        map.put("cle", null);
        System.out.println("   HashMap avec valeur null : get=" + map.get("cle")
                + ", containsKey=" + map.containsKey("cle"));
        System.out.println("   Optional.ofNullable(map.get(\"cle\")).isPresent() = "
                + Optional.ofNullable(map.get("cle")).isPresent() + "   <- indistinguable d'une clé absente");
        System.out.println("   getOrDefault sur clé présente à null : " + map.getOrDefault("cle", "défaut"));
    }
}
