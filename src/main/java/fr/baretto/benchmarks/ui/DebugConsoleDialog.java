package fr.baretto.benchmarks.ui;

import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.io.File;

/**
 * Console de debug pour exécuter des requêtes Cypher sur Neo4j Embedded.
 */
public class DebugConsoleDialog extends JDialog {

    private static final Logger logger = LoggerFactory.getLogger(DebugConsoleDialog.class);

    private final Neo4jGraphRagStrategy strategy;
    private JTextArea queryArea;
    private JTextArea resultArea;
    private JButton executeButton;

    public DebugConsoleDialog(Frame owner, Neo4jGraphRagStrategy strategy) {
        super(owner, "Console Debug Neo4j", false);
        this.strategy = strategy;
        initializeUI();
    }

    private void initializeUI() {
        setSize(900, 700);
        setLocationRelativeTo(getOwner());
        setLayout(new BorderLayout(10, 10));

        // Panneau du haut : requête
        JPanel topPanel = new JPanel(new BorderLayout(5, 5));
        topPanel.setBorder(new EmptyBorder(10, 10, 10, 10));

        JLabel queryLabel = new JLabel("Requête Cypher:");
        queryLabel.setFont(new Font("Arial", Font.BOLD, 12));

        queryArea = new JTextArea(8, 80);
        queryArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        queryArea.setText("// Exemples de requêtes :\n" +
                "// MATCH (f:File) RETURN f.name LIMIT 10\n" +
                "// MATCH (c:Class) RETURN c.name, c.type LIMIT 10\n" +
                "// MATCH (f:File)-[:CONTAINS]->(c:Class) RETURN f.name, c.name LIMIT 10\n\n" +
                "MATCH (f:File) RETURN f.name, f.size LIMIT 10");

        JScrollPane queryScroll = new JScrollPane(queryArea);

        executeButton = new JButton("Exécuter (Ctrl+Enter)");
        executeButton.setFont(new Font("Arial", Font.BOLD, 14));

        topPanel.add(queryLabel, BorderLayout.NORTH);
        topPanel.add(queryScroll, BorderLayout.CENTER);
        topPanel.add(executeButton, BorderLayout.SOUTH);

        // Panneau du bas : résultats
        JPanel bottomPanel = new JPanel(new BorderLayout(5, 5));
        bottomPanel.setBorder(new EmptyBorder(0, 10, 10, 10));

        JLabel resultLabel = new JLabel("Résultats:");
        resultLabel.setFont(new Font("Arial", Font.BOLD, 12));

        resultArea = new JTextArea();
        resultArea.setFont(new Font("Monospaced", Font.PLAIN, 11));
        resultArea.setEditable(false);
        resultArea.setText("Prêt. Entrez une requête Cypher et cliquez sur Exécuter.");

        JScrollPane resultScroll = new JScrollPane(resultArea);

        // Boutons d'exemples
        JPanel examplePanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JButton statsButton = new JButton("Stats générales");
        JButton filesButton = new JButton("Lister fichiers");
        JButton classesButton = new JButton("Lister classes");
        JButton searchButton = new JButton("Test recherche");
        JButton exportButton = new JButton("📤 Exporter CSV pour Neo4j Desktop");
        JButton clearButton = new JButton("Effacer");

        examplePanel.add(statsButton);
        examplePanel.add(filesButton);
        examplePanel.add(classesButton);
        examplePanel.add(searchButton);
        examplePanel.add(exportButton);
        examplePanel.add(clearButton);

        bottomPanel.add(resultLabel, BorderLayout.NORTH);
        bottomPanel.add(resultScroll, BorderLayout.CENTER);
        bottomPanel.add(examplePanel, BorderLayout.SOUTH);

        // Ajouter les panneaux
        add(topPanel, BorderLayout.NORTH);
        add(bottomPanel, BorderLayout.CENTER);

        // Event handlers
        executeButton.addActionListener(e -> executeQuery());

        // Ctrl+Enter pour exécuter
        queryArea.getInputMap().put(KeyStroke.getKeyStroke("control ENTER"), "execute");
        queryArea.getActionMap().put("execute", new AbstractAction() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent e) {
                executeQuery();
            }
        });

        // Boutons d'exemples
        statsButton.addActionListener(e -> {
            queryArea.setText(
                "// Statistiques générales\n" +
                "MATCH (f:File) WITH COUNT(f) as files\n" +
                "MATCH (c:Class) WITH files, COUNT(c) as classes\n" +
                "MATCH (fn:Function) WITH files, classes, COUNT(fn) as functions\n" +
                "MATCH (i:Import) WITH files, classes, functions, COUNT(i) as imports\n" +
                "RETURN files, classes, functions, imports"
            );
        });

        filesButton.addActionListener(e -> {
            queryArea.setText("MATCH (f:File)\n" +
                    "RETURN f.name as fichier, f.size as taille\n" +
                    "ORDER BY f.size DESC\n" +
                    "LIMIT 20");
        });

        classesButton.addActionListener(e -> {
            queryArea.setText("MATCH (f:File)-[:CONTAINS]->(c:Class)\n" +
                    "RETURN f.name as fichier, c.name as classe, c.type as type\n" +
                    "LIMIT 20");
        });

        searchButton.addActionListener(e -> {
            queryArea.setText("// Test de recherche avec CONTAINS\n" +
                    "MATCH (f:File)\n" +
                    "OPTIONAL MATCH (f)-[:CONTAINS]->(entity)\n" +
                    "WHERE toLower(f.content) CONTAINS toLower('RagService')\n" +
                    "   OR toLower(entity.name) CONTAINS toLower('RagService')\n" +
                    "RETURN DISTINCT f.name, COUNT(entity) as score\n" +
                    "ORDER BY score DESC\n" +
                    "LIMIT 10");
        });

        clearButton.addActionListener(e -> {
            resultArea.setText("");
            queryArea.setText("");
            queryArea.requestFocus();
        });

        exportButton.addActionListener(e -> handleExport());
    }

    private void handleExport() {
        // Demander où sauvegarder les fichiers CSV
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Choisir un dossier pour l'export CSV");
        fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);

        int result = fileChooser.showSaveDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            java.io.File directory = fileChooser.getSelectedFile();

            // Créer un sous-dossier pour l'export
            java.io.File exportDir = new File(directory, "neo4j-csv-export");

            resultArea.setText("Export CSV en cours vers: " + exportDir.getAbsolutePath() + "\n");
            resultArea.append("Veuillez patienter...\n");
            executeButton.setEnabled(false);

            // Exporter dans un thread séparé
            SwingWorker<Void, String> worker = new SwingWorker<>() {
                @Override
                protected Void doInBackground() throws Exception {
                    publish("Démarrage de l'export CSV...\n");
                    strategy.exportToCSV(exportDir.toPath());
                    publish("Export terminé avec succès!\n");
                    return null;
                }

                @Override
                protected void process(java.util.List<String> chunks) {
                    for (String msg : chunks) {
                        resultArea.append(msg);
                    }
                }

                @Override
                protected void done() {
                    try {
                        get();
                        resultArea.append("\n✅ EXPORT RÉUSSI!\n");
                        resultArea.append("\nDossier: " + exportDir.getAbsolutePath() + "\n");
                        resultArea.append("\nFichiers générés:\n");
                        resultArea.append("\n  📜 SCRIPT D'IMPORT (TOUT EN UN!):\n");
                        resultArea.append("     import_complet.cypher  ← LE SEUL FICHIER NÉCESSAIRE!\n");
                        resultArea.append("\n  📊 CSV (optionnels, pour référence):\n");
                        resultArea.append("     11 fichiers CSV de backup\n");
                        resultArea.append("\n  📖 GUIDE:\n");
                        resultArea.append("     LIRE_MOI_IMPORT.txt (instructions détaillées)\n");
                        resultArea.append("\n=== IMPORT ULTRA SIMPLE (3 ÉTAPES!) ===\n");
                        resultArea.append("\n1. Démarrez votre base Neo4j Desktop\n");
                        resultArea.append("\n2. Ouvrez Neo4j Browser\n");
                        resultArea.append("\n3. Ouvrez 'import_complet.cypher', copiez TOUT\n");
                        resultArea.append("   et collez dans Neo4j Browser\n");
                        resultArea.append("\n4. Exécutez bloc par bloc:\n");
                        resultArea.append("   - Contraintes (5 sec)\n");
                        resultArea.append("   - Nœuds (1-2 min)\n");
                        resultArea.append("   - Relations (1-2 min)\n");
                        resultArea.append("   - Vérification\n");
                        resultArea.append("\n⏱️  Temps total: 2-5 minutes\n");
                        resultArea.append("\n💡 Pas besoin de copier les CSV!\n");
                        resultArea.append("   Tout est dans le fichier .cypher!\n");

                        // Proposer d'ouvrir le dossier
                        int choice = JOptionPane.showConfirmDialog(
                                DebugConsoleDialog.this,
                                "Export CSV réussi!\n\n" +
                                "Fichiers exportés dans:\n" + exportDir.getAbsolutePath() + "\n\n" +
                                "Voulez-vous ouvrir le dossier?",
                                "Export terminé",
                                JOptionPane.YES_NO_OPTION,
                                JOptionPane.INFORMATION_MESSAGE
                        );

                        if (choice == JOptionPane.YES_OPTION) {
                            try {
                                Desktop.getDesktop().open(exportDir);
                            } catch (Exception ex) {
                                logger.error("Impossible d'ouvrir le dossier", ex);
                            }
                        }

                    } catch (Exception ex) {
                        resultArea.append("\n❌ ERREUR LORS DE L'EXPORT:\n");
                        resultArea.append(ex.getMessage() + "\n");
                        logger.error("Erreur lors de l'export CSV", ex);

                        JOptionPane.showMessageDialog(
                                DebugConsoleDialog.this,
                                "Erreur lors de l'export CSV:\n" + ex.getMessage(),
                                "Erreur",
                                JOptionPane.ERROR_MESSAGE
                        );
                    } finally {
                        executeButton.setEnabled(true);
                    }
                }
            };

            worker.execute();
        }
    }

    private void executeQuery() {
        String query = queryArea.getText().trim();

        // Enlever les commentaires pour affichage
        String cleanQuery = query.replaceAll("//[^\n]*\n", "").trim();

        if (cleanQuery.isEmpty()) {
            resultArea.setText("Erreur: La requête est vide.");
            return;
        }

        resultArea.setText("Exécution de la requête...\n");
        executeButton.setEnabled(false);

        // Exécuter dans un thread séparé pour ne pas bloquer l'UI
        SwingWorker<String, Void> worker = new SwingWorker<>() {
            @Override
            protected String doInBackground() {
                StringBuilder result = new StringBuilder();
                result.append("=== REQUÊTE ===\n");
                result.append(cleanQuery).append("\n\n");
                result.append("=== RÉSULTATS ===\n");

                try {
                    strategy.executeDebugQueryWithResult(cleanQuery, result);
                } catch (Exception e) {
                    result.append("\nERREUR: ").append(e.getMessage());
                    logger.error("Erreur lors de l'exécution de la requête", e);
                }

                return result.toString();
            }

            @Override
            protected void done() {
                try {
                    resultArea.setText(get());
                } catch (Exception e) {
                    resultArea.setText("Erreur: " + e.getMessage());
                }
                executeButton.setEnabled(true);
            }
        };

        worker.execute();
    }
}
