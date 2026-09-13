/** Complément batch_05 : dépassement d'entier avec des bornes réalistes. */
public class Probe05b {
    public static void main(String[] args) {
        System.out.println("── milieu de recherche binaire, bornes hautes");
        int lo = 2_000_000_000, hi = 2_100_000_000;
        System.out.println("   lo = " + lo + ", hi = " + hi);
        System.out.println("   (lo + hi) / 2      = " + ((lo + hi) / 2) + "   <- dépassement");
        System.out.println("   lo + (hi - lo) / 2 = " + (lo + (hi - lo) / 2));
        System.out.println("   >>> décalage non signé : " + ((lo + hi) >>> 1));

        System.out.println("── cumul de tailles de fichiers");
        int[] sizesMb = {900, 900, 900};
        int totalInt = 0;
        long totalLong = 0;
        for (int mb : sizesMb) {
            totalInt += mb * 1024 * 1024;
            totalLong += (long) mb * 1024 * 1024;
        }
        System.out.println("   cumul en int  : " + totalInt + " octets");
        System.out.println("   cumul en long : " + totalLong + " octets");
        System.out.println("   900 * 1024 * 1024 en int = " + (900 * 1024 * 1024));

        System.out.println("── conversions");
        try {
            Math.toIntExact(3_000_000_000L);
            System.out.println("   Math.toIntExact(3e9) : aucune exception");
        } catch (ArithmeticException e) {
            System.out.println("   Math.toIntExact(3e9) : ArithmeticException — " + e.getMessage());
        }
        System.out.println("   (int) 3_000_000_000L = " + (int) 3_000_000_000L);
    }
}
