package fr.baretto.benchmarks.strategy.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Représente un fichier Java parsé.
 */
public class ParsedFile {
    public String path;
    public String packageName;
    public List<ParsedImport> imports = new ArrayList<>();
    public List<ParsedClass> classes = new ArrayList<>();
    public String content; // Optionnel, pour debug

    public ParsedFile(String path) {
        this.path = path;
        this.packageName = "";
    }
}
