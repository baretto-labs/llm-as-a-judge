package fr.baretto.benchmarks.ui;

import javax.swing.*;
import javax.swing.border.TitledBorder;
import java.awt.*;
import java.lang.management.ManagementFactory;
import java.util.HashMap;
import java.util.Map;

/**
 * Panneau de métriques temps réel : mémoire JVM, CPU process, et tableau comparatif
 * des temps de réponse entre les deux stratégies RAG.
 */
public class MetricsPanel extends JPanel {

    private static final String LUCENE = "Vectoriel (Lucene)";
    private static final String NEO4J = "GraphRAG (Neo4j)";
    private static final Color COLOR_LUCENE = new Color(30, 120, 200);
    private static final Color COLOR_NEO4J = new Color(0, 150, 80);

    // Métriques système
    private JProgressBar memoryBar;
    private JProgressBar cpuBar;
    private JLabel memoryLabel;
    private JLabel cpuLabel;

    // Métriques par stratégie
    private final Map<String, StrategyStats> stats = new HashMap<>();
    private JLabel[] luceneValues;
    private JLabel[] neo4jValues;

    public MetricsPanel() {
        stats.put(LUCENE, new StrategyStats());
        stats.put(NEO4J, new StrategyStats());

        setLayout(new BorderLayout(8, 8));
        setBorder(new TitledBorder("Métriques en temps réel"));

        add(createSystemPanel(), BorderLayout.WEST);
        add(createComparisonPanel(), BorderLayout.CENTER);

        startSystemMonitor();
    }

    // ── Panneau gauche : métriques système ───────────────────────────────────

    private JPanel createSystemPanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(BorderFactory.createTitledBorder("JVM"));
        panel.setPreferredSize(new Dimension(220, 0));

        memoryBar = makeBar(Color.decode("#3a86ff"));
        cpuBar = makeBar(Color.decode("#ff6b6b"));
        memoryLabel = new JLabel("Mémoire : -- MB / -- MB");
        cpuLabel = new JLabel("CPU process : --%");
        memoryLabel.setFont(memoryLabel.getFont().deriveFont(Font.PLAIN, 11f));
        cpuLabel.setFont(cpuLabel.getFont().deriveFont(Font.PLAIN, 11f));

        panel.add(Box.createRigidArea(new Dimension(0, 6)));
        panel.add(memoryLabel);
        panel.add(Box.createRigidArea(new Dimension(0, 2)));
        panel.add(memoryBar);
        panel.add(Box.createRigidArea(new Dimension(0, 10)));
        panel.add(cpuLabel);
        panel.add(Box.createRigidArea(new Dimension(0, 2)));
        panel.add(cpuBar);
        panel.add(Box.createVerticalGlue());

        return panel;
    }

    private JProgressBar makeBar(Color color) {
        JProgressBar bar = new JProgressBar(0, 100);
        bar.setForeground(color);
        bar.setMaximumSize(new Dimension(Integer.MAX_VALUE, 14));
        bar.setAlignmentX(LEFT_ALIGNMENT);
        return bar;
    }

    // ── Panneau droit : tableau comparatif ───────────────────────────────────

    private JPanel createComparisonPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBorder(BorderFactory.createTitledBorder("Comparaison par stratégie"));

        String[] rows = {"Dernier appel", "Nb requêtes", "Moyenne", "Min", "Max", "Chunks"};

        JPanel table = new JPanel(new GridBagLayout());
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(2, 8, 2, 8);
        c.fill = GridBagConstraints.HORIZONTAL;

        // En-têtes
        c.gridy = 0;
        c.gridx = 0; table.add(new JLabel(""), c);
        c.gridx = 1; table.add(header(LUCENE, COLOR_LUCENE), c);
        c.gridx = 2; table.add(header(NEO4J, COLOR_NEO4J), c);

        // Séparateur
        c.gridy = 1; c.gridx = 0; c.gridwidth = 3;
        table.add(new JSeparator(), c);
        c.gridwidth = 1;

        luceneValues = new JLabel[rows.length];
        neo4jValues = new JLabel[rows.length];

        for (int i = 0; i < rows.length; i++) {
            luceneValues[i] = value("--");
            neo4jValues[i] = value("--");

            c.gridy = i + 2;
            c.gridx = 0; table.add(rowLabel(rows[i]), c);
            c.gridx = 1; table.add(luceneValues[i], c);
            c.gridx = 2; table.add(neo4jValues[i], c);
        }

        panel.add(table, BorderLayout.CENTER);
        return panel;
    }

    private JLabel header(String text, Color color) {
        JLabel l = new JLabel(text, SwingConstants.CENTER);
        l.setFont(l.getFont().deriveFont(Font.BOLD, 11f));
        l.setForeground(color);
        return l;
    }

    private JLabel rowLabel(String text) {
        JLabel l = new JLabel(text + " :", SwingConstants.RIGHT);
        l.setFont(l.getFont().deriveFont(Font.PLAIN, 11f));
        l.setForeground(Color.GRAY);
        return l;
    }

    private JLabel value(String text) {
        JLabel l = new JLabel(text, SwingConstants.CENTER);
        l.setFont(l.getFont().deriveFont(Font.PLAIN, 11f));
        return l;
    }

    // ── API publique ──────────────────────────────────────────────────────────

    /**
     * Enregistre le résultat d'un appel RAG pour la stratégie donnée.
     * Doit être appelé depuis l'EDT.
     */
    public void recordQuery(String strategyName, long responseTimeMs, int chunksCount) {
        StrategyStats s = stats.get(strategyName);
        if (s == null) return;

        s.record(responseTimeMs, chunksCount);

        JLabel[] values = strategyName.equals(LUCENE) ? luceneValues : neo4jValues;
        values[0].setText(responseTimeMs + " ms");
        values[1].setText(String.valueOf(s.count));
        values[2].setText(String.format("%.0f ms", s.average()));
        values[3].setText(s.min + " ms");
        values[4].setText(s.max + " ms");
        values[5].setText(String.valueOf(chunksCount));

        // Mise en évidence comparative si les deux ont des données
        StrategyStats lucene = stats.get(LUCENE);
        StrategyStats neo4j = stats.get(NEO4J);
        if (lucene.count > 0 && neo4j.count > 0) {
            boolean luceneFaster = lucene.average() <= neo4j.average();
            luceneValues[2].setForeground(luceneFaster ? new Color(0, 150, 80) : Color.RED);
            neo4jValues[2].setForeground(luceneFaster ? Color.RED : new Color(0, 150, 80));
        }
    }

    // ── Monitoring système ────────────────────────────────────────────────────

    private void startSystemMonitor() {
        Timer timer = new Timer(1000, e -> refreshSystemMetrics());
        timer.start();
    }

    private void refreshSystemMetrics() {
        Runtime rt = Runtime.getRuntime();
        long usedMB = (rt.totalMemory() - rt.freeMemory()) / (1024 * 1024);
        long totalMB = rt.totalMemory() / (1024 * 1024);
        long maxMB = rt.maxMemory() / (1024 * 1024);
        int memPct = (int) (usedMB * 100 / Math.max(maxMB, 1));

        memoryLabel.setText(String.format("Mémoire : %d MB / %d MB", usedMB, totalMB));
        memoryBar.setValue(memPct);

        double cpu = getCpuLoad();
        if (cpu >= 0) {
            int cpuPct = (int) (cpu * 100);
            cpuLabel.setText(String.format("CPU process : %d%%", cpuPct));
            cpuBar.setValue(cpuPct);
        }
    }

    private double getCpuLoad() {
        try {
            var osBean = ManagementFactory.getOperatingSystemMXBean();
            if (osBean instanceof com.sun.management.OperatingSystemMXBean sunBean) {
                return sunBean.getProcessCpuLoad();
            }
        } catch (Exception ignored) {
        }
        return -1;
    }

    // ── Stats par stratégie ───────────────────────────────────────────────────

    private static class StrategyStats {
        int count;
        long totalMs;
        long min = Long.MAX_VALUE;
        long max;
        int lastChunks;

        void record(long ms, int chunks) {
            count++;
            totalMs += ms;
            min = Math.min(min, ms);
            max = Math.max(max, ms);
            lastChunks = chunks;
        }

        double average() {
            return count == 0 ? 0 : (double) totalMs / count;
        }
    }
}
