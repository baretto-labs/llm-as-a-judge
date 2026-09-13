import java.util.Optional;

/** Probe for batch_03 b03-006: Optional.orElse evaluates its argument eagerly. */
public class Probe03 {

    static int calls = 0;

    static String expensiveDefault() {
        calls++;
        System.out.println("    -> expensiveDefault() appelé");
        return "défaut";
    }

    static String before(Optional<String> value) {
        if (value.isPresent()) {
            return value.get();
        }
        return expensiveDefault();
    }

    static String afterOrElse(Optional<String> value) {
        return value.orElse(expensiveDefault());
    }

    static String afterOrElseGet(Optional<String> value) {
        return value.orElseGet(Probe03::expensiveDefault);
    }

    public static void main(String[] args) {
        Optional<String> present = Optional.of("valeur");

        calls = 0;
        System.out.println("version d'origine, Optional présent : " + before(present));
        System.out.println("  appels au défaut : " + calls);

        calls = 0;
        System.out.println("orElse, Optional présent : " + afterOrElse(present));
        System.out.println("  appels au défaut : " + calls);

        calls = 0;
        System.out.println("orElseGet, Optional présent : " + afterOrElseGet(present));
        System.out.println("  appels au défaut : " + calls);
    }
}
