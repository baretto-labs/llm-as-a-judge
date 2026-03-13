package test;

/**
 * Classe minimale pour tester le Symbol Solver.
 */
public class MinimalTest {

    private String name;

    public MinimalTest(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void greet() {
        System.out.println("Hello " + getName());
    }
}
