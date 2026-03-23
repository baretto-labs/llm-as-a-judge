package fr.baretto.benchmarks.jmh;

import fr.baretto.benchmarks.strategy.LuceneRagStrategy;
import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;

import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.concurrent.TimeUnit;

/**
 * Microbenchmark JMH — temps d'indexation par taille de projet.
 *
 * Paramètres : 10 / 100 / 1000 / 10000 fichiers Java.
 *
 * ⚠ Temps estimés (machine standard, sans GPU) :
 *   -    10 fichiers : Lucene ~2s  | Neo4j ~20s
 *   -   100 fichiers : Lucene ~15s | Neo4j ~90s
 *   -  1000 fichiers : Lucene ~2min| Neo4j ~15min
 *   - 10000 fichiers : Lucene ~20min| Neo4j ~2h+
 *
 * Réduire à iterations=1 et exclure Neo4j pour 10000 si nécessaire :
 *   mvn test -Dtest=BenchmarkRunner#indexation -Djmh.include=luceneIndexation
 */
@BenchmarkMode(Mode.SingleShotTime)
@OutputTimeUnit(TimeUnit.SECONDS)
@State(Scope.Benchmark)
@Fork(value = 1, warmups = 0)
@Warmup(iterations = 0)
@Measurement(iterations = 3)
public class IndexationBenchmark {

    @Param({"10", "100", "1000", "10000"})
    public int fileCount;

    private Path sourceDir;
    private Path luceneDir;
    private Path neo4jDir;

    // ── Setup ───────────────────────────────────────────────────────────────

    @Setup(Level.Trial)
    public void generateSources() throws IOException {
        sourceDir = BenchmarkSources.create(fileCount);
    }

    @TearDown(Level.Trial)
    public void cleanSources() throws IOException {
        BenchmarkSources.delete(sourceDir);
    }

    @Setup(Level.Invocation)
    public void freshDirs() throws IOException {
        luceneDir = Files.createTempDirectory("bench-lucene-idx-" + fileCount);
        neo4jDir  = Files.createTempDirectory("bench-neo4j-idx-" + fileCount);
    }

    @TearDown(Level.Invocation)
    public void cleanDirs() throws IOException {
        deleteDir(luceneDir);
        deleteDir(neo4jDir);
    }

    // ── Benchmarks ──────────────────────────────────────────────────────────

    @Benchmark
    public void luceneIndexation(MemoryStats mem, CpuStats cpu, Blackhole bh) throws Exception {
        try (LuceneRagStrategy strategy = new LuceneRagStrategy(luceneDir)) {
            strategy.indexDirectory(sourceDir);
            bh.consume(strategy.getStrategyName());
        }
    }

    @Benchmark
    public void neo4jIndexation(MemoryStats mem, CpuStats cpu, Blackhole bh) throws Exception {
        Neo4jGraphRagStrategy strategy = new Neo4jGraphRagStrategy(neo4jDir.toString());
        strategy.indexDirectory(sourceDir);
        strategy.shutdown();
        bh.consume(strategy.getStrategyName());
    }

    // ── AuxCounters ─────────────────────────────────────────────────────────

    @State(Scope.Thread)
    @AuxCounters(AuxCounters.Type.EVENTS)
    public static class MemoryStats {
        public long heapDeltaMB;
        private long before;

        @Setup(Level.Invocation)
        public void before() { System.gc(); before = usedHeap(); }

        @TearDown(Level.Invocation)
        public void after() { heapDeltaMB = Math.max(0, (usedHeap() - before) / (1024 * 1024)); }

        private long usedHeap() { return Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory(); }
    }

    @State(Scope.Thread)
    @AuxCounters(AuxCounters.Type.EVENTS)
    public static class CpuStats {
        public long cpuTimeMs;
        private long before;

        @Setup(Level.Invocation)
        public void before() { before = ManagementFactory.getThreadMXBean().getCurrentThreadCpuTime(); }

        @TearDown(Level.Invocation)
        public void after() { cpuTimeMs = Math.max(0, (ManagementFactory.getThreadMXBean().getCurrentThreadCpuTime() - before) / 1_000_000); }
    }

    // ── Utilitaire ──────────────────────────────────────────────────────────

    private void deleteDir(Path dir) throws IOException {
        if (dir != null && Files.exists(dir)) {
            Files.walk(dir).sorted(Comparator.reverseOrder())
                    .forEach(p -> { try { Files.delete(p); } catch (IOException ignored) {} });
        }
    }
}
