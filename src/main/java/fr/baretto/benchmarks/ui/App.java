package fr.baretto.benchmarks.ui;

import fr.baretto.benchmarks.service.RagService;
import fr.baretto.benchmarks.strategy.LuceneRagStrategy;
import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.TitledBorder;
import java.awt.*;
import java.io.File;
import java.nio.file.Path;

/**
 * Interface principale de l'application Benchmark RAG vs GraphRAG.
 * Implémente une interface Swing propre et responsive avec deux panneaux :
 * - Configuration (gauche) : sélection de dossier, stratégie et modèle
 * - Chat/Évaluation (droite) : interaction avec le LLM
 */
public class App extends JFrame {

    private static final Logger logger = LoggerFactory.getLogger(App.class);

    // Service
    private final RagService ragService;

    // Composants UI - Panneau Configuration
    private JLabel selectedDirectoryLabel;
    private JButton chooseDirectoryButton;
    private ButtonGroup strategyButtonGroup;
    private JRadioButton luceneRadioButton;
    private JRadioButton neo4jRadioButton;
    private JComboBox<String> modelComboBox;
    private JButton indexButton;
    private JLabel statusLabel;

    // Composants UI - Panneau Chat
    private JTextArea chatHistoryArea;
    private JTextField questionField;
    private JButton sendButton;
    private JButton sourcesButton;
    private JLabel responseTimeLabel;

    // Derniers chunks utilisés
    private java.util.List<String> lastContextChunks = java.util.List.of();

    // Panneau métriques
    private MetricsPanel metricsPanel;

    // État
    private Path selectedDirectory;

    /**
     * Constructeur de la fenêtre principale.
     */
    public App() {
        this.ragService = new RagService();
        initializeUI();
        setupEventHandlers();

        // Initialiser la stratégie par défaut (Lucene)
        ragService.setStrategy(new LuceneRagStrategy());
        appendToChatHistory("Stratégie par défaut: Vectoriel (Lucene)\n");

        // Initialiser le modèle par défaut si disponible
        String defaultModel = (String) modelComboBox.getSelectedItem();
        if (defaultModel != null && !defaultModel.contains("Aucun modèle disponible")) {
            try {
                ragService.setOllamaModel(defaultModel);
                appendToChatHistory("Modèle par défaut: " + defaultModel + "\n\n");
            } catch (Exception e) {
                logger.warn("Impossible de configurer le modèle par défaut", e);
                appendToChatHistory("⚠ Erreur: Modèle Ollama non accessible. Vérifiez qu'Ollama est installé et démarré.\n\n");
            }
        } else {
            appendToChatHistory("⚠ Aucun modèle Ollama trouvé. Installez Ollama et téléchargez un modèle:\n");
            appendToChatHistory("   curl -fsSL https://ollama.com/install.sh | sh\n");
            appendToChatHistory("   ollama pull mistral\n\n");
        }
    }

    /**
     * Initialise tous les composants de l'interface utilisateur.
     */
    private void initializeUI() {
        setTitle("Benchmark RAG vs GraphRAG");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 820);
        setLocationRelativeTo(null);

        metricsPanel = new MetricsPanel();
        metricsPanel.setPreferredSize(new Dimension(0, 160));

        JSplitPane splitPane = new JSplitPane(
                JSplitPane.HORIZONTAL_SPLIT,
                createConfigurationPanel(),
                createChatPanel()
        );
        splitPane.setDividerLocation(400);
        splitPane.setResizeWeight(0.3);

        add(splitPane, BorderLayout.CENTER);
        add(metricsPanel, BorderLayout.SOUTH);
    }

    /**
     * Crée le panneau de configuration (gauche).
     */
    private JPanel createConfigurationPanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(new EmptyBorder(10, 10, 10, 10));

        // Section : Sélection du dossier
        panel.add(createDirectorySelectionSection());
        panel.add(Box.createRigidArea(new Dimension(0, 20)));

        // Section : Stratégie RAG
        panel.add(createStrategySelectionSection());
        panel.add(Box.createRigidArea(new Dimension(0, 20)));

        // Section : Modèle Ollama
        panel.add(createModelSelectionSection());
        panel.add(Box.createRigidArea(new Dimension(0, 20)));

        // Bouton d'indexation
        indexButton = new JButton("Lancer l'indexation");
        indexButton.setFont(new Font("Arial", Font.BOLD, 14));
        indexButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        indexButton.setEnabled(false);
        panel.add(indexButton);

        panel.add(Box.createRigidArea(new Dimension(0, 20)));

        // Label de statut
        statusLabel = new JLabel("Prêt");
        statusLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        statusLabel.setForeground(Color.GRAY);
        panel.add(statusLabel);

        panel.add(Box.createRigidArea(new Dimension(0, 10)));

        // Bouton Debug Neo4j (visible uniquement avec Neo4j)
        JButton debugButton = new JButton("🔍 Console Debug Neo4j");
        debugButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        debugButton.setVisible(false); // Caché par défaut
        panel.add(debugButton);

        // Event handler pour le bouton debug
        debugButton.addActionListener(e -> {
            if (ragService.getCurrentStrategy() instanceof Neo4jGraphRagStrategy neo4jStrategy) {
                new DebugConsoleDialog(this, neo4jStrategy).setVisible(true);
            } else {
                JOptionPane.showMessageDialog(this,
                    "La console de debug n'est disponible que pour Neo4j GraphRAG",
                    "Stratégie incorrecte",
                    JOptionPane.INFORMATION_MESSAGE);
            }
        });

        // Afficher/masquer le bouton debug selon la stratégie
        luceneRadioButton.addActionListener(e -> debugButton.setVisible(false));
        neo4jRadioButton.addActionListener(e -> debugButton.setVisible(true));

        panel.add(Box.createRigidArea(new Dimension(0, 5)));

        // Bouton Nettoyer la base (visible uniquement avec Neo4j)
        JButton clearButton = new JButton("🗑️ Nettoyer la base");
        clearButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        clearButton.setVisible(false); // Caché par défaut
        clearButton.setForeground(new Color(220, 53, 69)); // Rouge
        panel.add(clearButton);

        // Event handler pour le bouton nettoyer
        clearButton.addActionListener(e -> {
            if (ragService.getCurrentStrategy() instanceof Neo4jGraphRagStrategy neo4jStrategy) {
                int confirm = JOptionPane.showConfirmDialog(
                    this,
                    "⚠️ Cette action va supprimer TOUTES les données de la base Neo4j.\n\n" +
                    "Voulez-vous continuer ?",
                    "Confirmation",
                    JOptionPane.YES_NO_OPTION,
                    JOptionPane.WARNING_MESSAGE
                );

                if (confirm == JOptionPane.YES_OPTION) {
                    try {
                        appendToChatHistory("\n🗑️ Nettoyage de la base de données...\n");
                        neo4jStrategy.clearDatabase();
                        appendToChatHistory("✅ Base de données nettoyée avec succès!\n\n");
                        JOptionPane.showMessageDialog(
                            this,
                            "✅ Base de données nettoyée avec succès!",
                            "Succès",
                            JOptionPane.INFORMATION_MESSAGE
                        );
                    } catch (Exception ex) {
                        logger.error("Erreur lors du nettoyage", ex);
                        appendToChatHistory("❌ Erreur lors du nettoyage: " + ex.getMessage() + "\n\n");
                        JOptionPane.showMessageDialog(
                            this,
                            "❌ Erreur: " + ex.getMessage(),
                            "Erreur",
                            JOptionPane.ERROR_MESSAGE
                        );
                    }
                }
            } else {
                JOptionPane.showMessageDialog(this,
                    "Le nettoyage n'est disponible que pour Neo4j GraphRAG",
                    "Stratégie incorrecte",
                    JOptionPane.INFORMATION_MESSAGE);
            }
        });

        // Afficher/masquer le bouton nettoyer selon la stratégie
        luceneRadioButton.addActionListener(e -> clearButton.setVisible(false));
        neo4jRadioButton.addActionListener(e -> clearButton.setVisible(true));

        // Glue pour pousser tout en haut
        panel.add(Box.createVerticalGlue());

        return panel;
    }

    /**
     * Crée la section de sélection du dossier.
     */
    private JPanel createDirectorySelectionSection() {
        JPanel panel = new JPanel();
        panel.setLayout(new BorderLayout(5, 5));
        panel.setBorder(new TitledBorder("Dossier à indexer"));

        selectedDirectoryLabel = new JLabel("Aucun dossier sélectionné");
        selectedDirectoryLabel.setForeground(Color.GRAY);

        chooseDirectoryButton = new JButton("Choisir un dossier");

        panel.add(selectedDirectoryLabel, BorderLayout.CENTER);
        panel.add(chooseDirectoryButton, BorderLayout.SOUTH);

        return panel;
    }

    /**
     * Crée la section de sélection de la stratégie RAG.
     */
    private JPanel createStrategySelectionSection() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(new TitledBorder("Stratégie d'indexation/recherche"));

        strategyButtonGroup = new ButtonGroup();

        luceneRadioButton = new JRadioButton("Vectoriel (Lucene) - Implémentation existante");
        luceneRadioButton.setSelected(true);

        neo4jRadioButton = new JRadioButton("GraphRAG (Neo4j Embedded)");

        strategyButtonGroup.add(luceneRadioButton);
        strategyButtonGroup.add(neo4jRadioButton);

        panel.add(luceneRadioButton);
        panel.add(neo4jRadioButton);

        return panel;
    }

    /**
     * Crée la section de sélection du modèle Ollama.
     */
    private JPanel createModelSelectionSection() {
        JPanel panel = new JPanel();
        panel.setLayout(new BorderLayout(5, 5));
        panel.setBorder(new TitledBorder("Modèle Ollama"));

        // Récupérer les modèles disponibles
        String[] models = ragService.getAvailableModels().toArray(new String[0]);
        modelComboBox = new JComboBox<>(models);

        panel.add(new JLabel("Sélectionner un modèle:"), BorderLayout.NORTH);
        panel.add(modelComboBox, BorderLayout.CENTER);

        return panel;
    }

    /**
     * Crée le panneau de chat (droite).
     */
    private JPanel createChatPanel() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(new EmptyBorder(10, 10, 10, 10));

        // Zone d'historique du chat
        chatHistoryArea = new JTextArea();
        chatHistoryArea.setEditable(false);
        chatHistoryArea.setLineWrap(true);
        chatHistoryArea.setWrapStyleWord(true);
        chatHistoryArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        chatHistoryArea.setText("Bienvenue dans le Benchmark RAG vs GraphRAG\n" +
                "========================================\n\n" +
                "1. Choisissez un dossier à indexer\n" +
                "2. Sélectionnez une stratégie (Lucene ou Neo4j)\n" +
                "3. Choisissez un modèle Ollama\n" +
                "4. Lancez l'indexation\n" +
                "5. Posez vos questions !\n\n");

        JScrollPane scrollPane = new JScrollPane(chatHistoryArea);
        scrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);

        panel.add(scrollPane, BorderLayout.CENTER);

        // Panneau inférieur : saisie + bouton
        JPanel inputPanel = new JPanel(new BorderLayout(5, 5));

        questionField = new JTextField();
        questionField.setFont(new Font("Arial", Font.PLAIN, 14));
        questionField.setEnabled(false);

        sendButton = new JButton("Envoyer");
        sendButton.setEnabled(false);

        sourcesButton = new JButton("Sources");
        sourcesButton.setEnabled(false);
        sourcesButton.setToolTipText("Afficher les chunks de contexte utilisés pour la dernière réponse");

        JPanel buttonPanel = new JPanel(new GridLayout(1, 2, 4, 0));
        buttonPanel.add(sendButton);
        buttonPanel.add(sourcesButton);

        inputPanel.add(questionField, BorderLayout.CENTER);
        inputPanel.add(buttonPanel, BorderLayout.EAST);

        // Label temps de réponse
        responseTimeLabel = new JLabel("Temps de réponse: -- ms");
        responseTimeLabel.setHorizontalAlignment(SwingConstants.CENTER);

        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.add(inputPanel, BorderLayout.CENTER);
        bottomPanel.add(responseTimeLabel, BorderLayout.SOUTH);

        panel.add(bottomPanel, BorderLayout.SOUTH);

        return panel;
    }

    /**
     * Configure les gestionnaires d'événements pour tous les composants.
     */
    private void setupEventHandlers() {
        // Bouton de sélection de dossier
        chooseDirectoryButton.addActionListener(e -> handleChooseDirectory());

        // Bouton d'indexation
        indexButton.addActionListener(e -> handleIndexation());

        // Bouton d'envoi de question
        sendButton.addActionListener(e -> handleSendQuestion());

        // Bouton sources
        sourcesButton.addActionListener(e -> showSources());

        // Appuyer sur Entrée dans le champ de question
        questionField.addActionListener(e -> handleSendQuestion());

        // Changement de stratégie
        luceneRadioButton.addActionListener(e -> updateStrategySelection());
        neo4jRadioButton.addActionListener(e -> updateStrategySelection());

        // Changement de modèle
        modelComboBox.addActionListener(e -> updateModelSelection());
    }

    /**
     * Gère la sélection d'un dossier.
     */
    private void handleChooseDirectory() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        fileChooser.setDialogTitle("Sélectionner le dossier de la codebase");

        int result = fileChooser.showOpenDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            File selectedFile = fileChooser.getSelectedFile();
            selectedDirectory = selectedFile.toPath();
            selectedDirectoryLabel.setText(selectedFile.getAbsolutePath());
            selectedDirectoryLabel.setForeground(Color.BLACK);
            indexButton.setEnabled(true);

            appendToChatHistory("Dossier sélectionné: " + selectedFile.getAbsolutePath() + "\n");
        }
    }

    /**
     * Met à jour la stratégie RAG sélectionnée.
     */
    private void updateStrategySelection() {
        try {
            if (luceneRadioButton.isSelected()) {
                ragService.setStrategy(new LuceneRagStrategy());
                appendToChatHistory("Stratégie changée: Vectoriel (Lucene)\n");
            } else if (neo4jRadioButton.isSelected()) {
                ragService.setStrategy(new Neo4jGraphRagStrategy());
                appendToChatHistory("Stratégie changée: GraphRAG (Neo4j)\n");
            }
        } catch (Exception ex) {
            logger.error("Erreur lors du changement de stratégie", ex);
            appendToChatHistory("ERREUR: Impossible de changer de stratégie - " + ex.getMessage() + "\n");
            // Revenir à la stratégie précédente dans l'interface
            if (neo4jRadioButton.isSelected()) {
                luceneRadioButton.setSelected(true);
            }
        }
    }

    /**
     * Met à jour le modèle Ollama sélectionné.
     */
    private void updateModelSelection() {
        String selectedModel = (String) modelComboBox.getSelectedItem();
        if (selectedModel != null && !selectedModel.contains("Aucun modèle disponible")) {
            try {
                ragService.setOllamaModel(selectedModel);
                appendToChatHistory("Modèle Ollama configuré: " + selectedModel + "\n");
            } catch (Exception ex) {
                showError("Erreur lors de la configuration du modèle Ollama", ex);
            }
        }
    }

    /**
     * Gère le lancement de l'indexation (asynchrone avec SwingWorker).
     */
    private void handleIndexation() {
        if (selectedDirectory == null) {
            JOptionPane.showMessageDialog(this,
                    "Veuillez sélectionner un dossier d'abord.",
                    "Aucun dossier",
                    JOptionPane.WARNING_MESSAGE);
            return;
        }

        // Désactiver les contrôles pendant l'indexation
        setControlsEnabled(false);
        statusLabel.setText("Indexation en cours...");
        statusLabel.setForeground(Color.ORANGE);

        // Lancer l'indexation dans un SwingWorker
        SwingWorker<Void, Void> worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() throws Exception {
                ragService.indexDirectory(selectedDirectory);
                return null;
            }

            @Override
            protected void done() {
                try {
                    get(); // Vérifier les exceptions
                    statusLabel.setText("Indexation terminée !");
                    statusLabel.setForeground(new Color(0, 150, 0));
                    appendToChatHistory("\nIndexation terminée avec succès !\n" +
                            "Vous pouvez maintenant poser vos questions.\n\n");

                    // Activer le chat
                    questionField.setEnabled(true);
                    sendButton.setEnabled(true);
                    questionField.requestFocus();

                } catch (Exception ex) {
                    statusLabel.setText("Erreur d'indexation");
                    statusLabel.setForeground(Color.RED);
                    showError("Erreur lors de l'indexation", ex);
                } finally {
                    setControlsEnabled(true);
                }
            }
        };

        worker.execute();
    }

    /**
     * Gère l'envoi d'une question (asynchrone avec SwingWorker).
     */
    private void handleSendQuestion() {
        String question = questionField.getText().trim();
        if (question.isEmpty()) {
            return;
        }

        appendToChatHistory("Vous: " + question + "\n");
        questionField.setText("");
        questionField.setEnabled(false);
        sendButton.setEnabled(false);
        responseTimeLabel.setText("Génération en cours...");

        // Envoyer la question dans un SwingWorker
        SwingWorker<RagService.RagResponse, Void> worker = new SwingWorker<>() {
            @Override
            protected RagService.RagResponse doInBackground() throws Exception {
                return ragService.askQuestion(question);
            }

            @Override
            protected void done() {
                try {
                    RagService.RagResponse response = get();
                    appendToChatHistory("Assistant: " + response.getResponse() + "\n\n");
                    responseTimeLabel.setText(String.format(
                            "Temps de réponse: %d ms | Chunks: %d",
                            response.getResponseTimeMs(),
                            response.getContextChunksCount()
                    ));
                    metricsPanel.recordQuery(
                            ragService.getCurrentStrategyName(),
                            response.getResponseTimeMs(),
                            response.getContextChunksCount()
                    );
                    lastContextChunks = response.getContextChunks();
                    sourcesButton.setEnabled(true);
                } catch (Exception ex) {
                    showError("Erreur lors de la génération de la réponse", ex);
                    responseTimeLabel.setText("Erreur");
                } finally {
                    questionField.setEnabled(true);
                    sendButton.setEnabled(true);
                    questionField.requestFocus();
                }
            }
        };

        worker.execute();
    }

    /**
     * Ouvre une dialog affichant les chunks de contexte de la dernière réponse.
     */
    private void showSources() {
        if (lastContextChunks.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Aucune source disponible.", "Sources", JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        JDialog dialog = new JDialog(this, "Sources utilisées (" + lastContextChunks.size() + " chunks) — " + ragService.getCurrentStrategyName(), false);
        dialog.setSize(800, 600);
        dialog.setLocationRelativeTo(this);

        JTabbedPane tabs = new JTabbedPane();
        for (int i = 0; i < lastContextChunks.size(); i++) {
            JTextArea area = new JTextArea(lastContextChunks.get(i));
            area.setEditable(false);
            area.setLineWrap(true);
            area.setWrapStyleWord(true);
            area.setFont(new Font("Monospaced", Font.PLAIN, 12));
            tabs.addTab("Chunk " + (i + 1), new JScrollPane(area));
        }

        dialog.add(tabs);
        dialog.setVisible(true);
    }

    /**
     * Ajoute un message à l'historique du chat.
     */
    private void appendToChatHistory(String message) {
        chatHistoryArea.append(message);
        chatHistoryArea.setCaretPosition(chatHistoryArea.getDocument().getLength());
    }

    /**
     * Active/désactive les contrôles de configuration.
     */
    private void setControlsEnabled(boolean enabled) {
        chooseDirectoryButton.setEnabled(enabled);
        luceneRadioButton.setEnabled(enabled);
        neo4jRadioButton.setEnabled(enabled);
        modelComboBox.setEnabled(enabled);
        indexButton.setEnabled(enabled);
    }

    /**
     * Affiche une boîte de dialogue d'erreur.
     */
    private void showError(String message, Exception ex) {
        logger.error(message, ex);
        JOptionPane.showMessageDialog(this,
                message + "\n" + ex.getMessage(),
                "Erreur",
                JOptionPane.ERROR_MESSAGE);
    }

    /**
     * Point d'entrée de l'application.
     * Lance l'interface Swing sur l'Event Dispatch Thread (EDT).
     */
    public static void main(String[] args) {
        logger.info("Démarrage de l'application Benchmark RAG vs GraphRAG");

        // Définir le Look and Feel système pour une meilleure intégration
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            logger.warn("Impossible de définir le Look and Feel système", e);
        }

        SwingUtilities.invokeLater(() -> {
            try {
                App app = new App();
                app.setVisible(true);
                logger.info("Interface graphique initialisée avec succès");
            } catch (Exception e) {
                logger.error("Erreur lors de l'initialisation de l'interface", e);
                JOptionPane.showMessageDialog(null,
                        "Erreur lors du démarrage de l'application:\n" + e.getMessage(),
                        "Erreur fatale",
                        JOptionPane.ERROR_MESSAGE);
                System.exit(1);
            }
        });
    }
}
