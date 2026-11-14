import java.math.BigDecimal;
import java.util.Currency;
import java.util.Objects;

/** Fact-checks the Java claims of batch_03 (b03-013 : record + constructeur compact). */
public class FactCheck03 {

    public record Money(BigDecimal amount, Currency currency) {
        public Money {
            Objects.requireNonNull(amount, "amount");
            Objects.requireNonNull(currency, "currency");
            if (amount.signum() < 0) {
                throw new IllegalArgumentException("montant négatif");
            }
            amount = amount.stripTrailingZeros();   // réaffectation du paramètre
        }
    }

    static void ok(String label, boolean cond, String detail) {
        System.out.println((cond ? "OK  " : "KO  ") + label + (detail.isEmpty() ? "" : "  " + detail));
    }

    public static void main(String[] args) {
        Currency eur = Currency.getInstance("EUR");

        Money m = new Money(new BigDecimal("2.50"), eur);
        ok("le constructeur compact normalise le paramètre", m.amount().compareTo(new BigDecimal("2.5")) == 0
                && m.amount().toString().equals("2.5"), "amount()=" + m.amount());

        ok("equals généré compare les composants",
                new Money(new BigDecimal("2.5"), eur).equals(new Money(new BigDecimal("2.50"), eur)),
                "");

        try {
            new Money(new BigDecimal("-1"), eur);
            ok("montant négatif rejeté", false, "aucune exception");
        } catch (IllegalArgumentException e) {
            ok("montant négatif rejeté", true, e.getMessage());
        }

        try {
            new Money(null, eur);
            ok("amount null rejeté", false, "aucune exception");
        } catch (NullPointerException e) {
            ok("amount null rejeté", true, e.getMessage());
        }

        ok("le record est implicitement final", java.lang.reflect.Modifier.isFinal(Money.class.getModifiers()), "");
        ok("toString généré", m.toString().startsWith("Money[amount="), m.toString());
    }
}
