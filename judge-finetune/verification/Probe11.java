import java.time.*;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;

/** Probes for batch_11: LocalDateTime sans fuseau, arithmétique et changement d'heure. */
public class Probe11 {

    public static void main(String[] args) {
        ZoneId paris = ZoneId.of("Europe/Paris");

        System.out.println("── LocalDateTime ne porte aucun fuseau");
        LocalDateTime local = LocalDateTime.of(2026, 3, 29, 1, 30);
        System.out.println("   LocalDateTime           : " + local);
        System.out.println("   même valeur à Paris     : " + local.atZone(paris));
        System.out.println("   même valeur en UTC      : " + local.atZone(ZoneOffset.UTC));
        System.out.println("   instants différents ?   : "
                + !local.atZone(paris).toInstant().equals(local.atZone(ZoneOffset.UTC).toInstant()));

        System.out.println("── heure locale inexistante (passage à l'heure d'été)");
        LocalDateTime inexistante = LocalDateTime.of(2026, 3, 29, 2, 30);
        ZonedDateTime resolue = inexistante.atZone(paris);
        System.out.println("   2026-03-29T02:30 à Paris -> " + resolue + "   <- décalée, pas d'exception");

        System.out.println("── arithmétique : plusHours contre plusDays");
        ZonedDateTime veille = ZonedDateTime.of(2026, 3, 28, 20, 0, 0, 0, paris);
        System.out.println("   départ            : " + veille);
        System.out.println("   plusHours(24)     : " + veille.plusHours(24));
        System.out.println("   plusDays(1)       : " + veille.plusDays(1));
        System.out.println("   écart réel en heures entre les deux résultats : "
                + ChronoUnit.HOURS.between(veille.plusDays(1), veille.plusHours(24)));

        System.out.println("── Instant, epoch et formatage");
        Instant instant = Instant.parse("2026-03-29T00:30:00Z");
        System.out.println("   Instant                     : " + instant);
        System.out.println("   à Paris                     : " + instant.atZone(paris));
        System.out.println("   epochSecond                 : " + instant.getEpochSecond());
        try {
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm").format(instant);
        } catch (Exception e) {
            System.out.println("   formater un Instant sans fuseau : "
                    + e.getClass().getSimpleName() + " — " + e.getMessage());
        }
        System.out.println("   avec withZone               : "
                + DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm").withZone(paris).format(instant));

        System.out.println("── durée entre deux dates et changement d'heure");
        ZonedDateTime debut = ZonedDateTime.of(2026, 3, 28, 23, 0, 0, 0, paris);
        ZonedDateTime fin = ZonedDateTime.of(2026, 3, 29, 4, 0, 0, 0, paris);
        System.out.println("   ChronoUnit.HOURS.between : " + ChronoUnit.HOURS.between(debut, fin));
        System.out.println("   Duration.between         : " + Duration.between(debut, fin).toHours() + " h");
        System.out.println("   différence d'heure locale affichée : "
                + (fin.getHour() - debut.getHour() + 24) % 24 + " h");
    }
}
