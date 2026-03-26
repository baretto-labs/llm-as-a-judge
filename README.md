# RAG Benchmark — Lucene vs GraphRAG

*March 2026 · OllamAssist codebase · 126 Java classes · qwen2.5:14b as judge*

---

I built this benchmark because I was stuck on a decision I couldn't resolve by intuition alone.

[OllamAssist](https://github.com/baretto/ollamassist) is an IntelliJ plugin with an AI assistant. Before answering a question, it retrieves context from the codebase through a RAG pipeline. I had two reasonable options in front of me: a classic Lucene-based approach (BM25 + KNN + RRF, embedded, zero external dependencies) and a Neo4j GraphRAG approach (knowledge graph built from the Java AST, K-hop expansion at query time). Both looked promising on paper.

The usual answer here is to measure latency. But latency tells you how fast a strategy runs, not whether the context it returns actually lets the LLM answer the question. Those are different problems.

So I built something to measure both.

---

## What this is

A JMH benchmark that compares two retrieval strategies across 30 questions written specifically for OllamAssist, evaluated by an LLM judge.

**Two strategies:**

| | Lucene | Neo4j GraphRAG |
|---|---|---|
| Core approach | BM25 + KNN + RRF | Knowledge graph + hybrid search + K-hop expansion |
| Infrastructure | Embedded | Neo4j Embedded (no server needed) |
| Baseline latency | ~35 ms | ~100 ms |

**Feature flags** let you activate each layer independently, so you can measure the marginal value of each component rather than comparing two black boxes:

| Preset | What's active |
|---|---|
| `knn-only` | Vector similarity only — the baseline |
| `hybrid` | + BM25 + RRF |
| `hybrid-graph` | + K-hop graph expansion (Neo4j only) |
| `hybrid-graph-hyde` | + HyDE (hypothetical document expansion) |

**30 questions across 3 difficulty levels:**

| Level | What it tests |
|---|---|
| LOCAL (×10) | A specific method — *"What does `calculateDynamicThreshold` compute?"* |
| STRUCTURAL (×10) | Inheritance, interfaces — *"What interfaces does `OllamaService` implement?"* |
| CROSS_MODULE (×10) | Call chains across modules — *"How does `DocumentIndexingPipeline` interact with `LuceneEmbeddingStore`?"* |

---

## Evaluation: LLM-as-a-judge

Each retrieval result is scored by `qwen2.5:14b` acting as a judge:

```
  question asked
+ context returned by the strategy
─────────────────────────────────────
        qwen2.5:14b (judge)
─────────────────────────────────────
  score 0–10
  rationale: "Context contains X but is missing Y"
  suggestsUnknown: true/false
```

A few implementation details worth mentioning:

- **Structured output via LangChain4j `AiServices`** — no regex, no fragile JSON parsing
- **3 few-shot examples** in the system prompt (score 9 / 4 / 0) to anchor the scale
- **Chunk order shuffled before each judgment** to reduce position bias
- **`hintCoverage`** — a deterministic check that verifies whether the expected symbols appear in the returned context, independent of the LLM. Acts as a sanity check when LLM scores fluctuate.

For multi-judge runs, use `-Djmh.judge.models=model1,model2`. Each judge evaluates independently (no deliberation, to avoid sycophancy).

---

## Results

### Latency

| Strategy | Preset | Avg. latency |
|---|---|---|
| Lucene | knn-only | 35 ms |
| Lucene | hybrid | 37 ms |
| Neo4j | hybrid | 92 ms |
| Neo4j | hybrid-graph | **106 ms — 3× slower** |

The graph traversal has a real cost. Whether it's worth paying depends on whether quality goes up.

### Quality — LLM-as-a-judge score (out of 10)

**The biggest lever is BM25, not the graph:**

| Preset | Global score |
|---|---|
| Lucene knn-only | 1.8 / 10 |
| Lucene hybrid | **4.5 / 10** |

**+154% from adding BM25.** KNN finds what looks similar; BM25 finds `calculateDynamicThreshold` and `OllamaService` — the exact names that matter in code. For a code retrieval use case, lexical search is not optional.

**Detail by difficulty level:**

| | LOCAL | STRUCTURAL | CROSS_MODULE |
|---|---|---|---|
| Lucene knn-only | 2.6 | 0.8 | 1.9 |
| Lucene hybrid | **6.1** | 3.2 | **4.2** |
| Neo4j hybrid | 2.7 | 2.7 | 2.1 |
| Neo4j hybrid-graph | 2.7 | **3.3** | 1.5 |

**Neo4j results are essentially flat.** The K-hop expansion helps slightly on STRUCTURAL (3.3 vs 2.7), but LOCAL and CROSS_MODULE don't move. The reason: JavaParser misses lambdas, method references, and anonymous classes in the IntelliJ SDK — so a significant portion of `CALLS` relations are absent from the graph, and K-hop expansion traverses a skeleton rather than the real call graph.

Lucene hybrid wins on 2 out of 3 question types, at 3× lower latency.

### The chunking bug — 20 lines, +60% on STRUCTURAL

STRUCTURAL questions had 80% "I don't know" responses before a small fix. The root cause was in how chunks were built:

```
// Before
Type: fr.baretto.ollamassist.OllamaService
Field: private OllamaClient client;

// After — full declaration included
Type: class fr.baretto.ollamassist.OllamaService
      extends OllamaServiceBase
      implements Disposable, ModelListener   ← the answer was here
Field: private OllamaClient client;
```

STRUCTURAL went from 2.0 → 3.2 without touching the retrieval pipeline at all. A good reminder that chunking sets the ceiling — no amount of clever search strategy compensates for context that was never there.

### Summary

| | Lucene hybrid | Neo4j hybrid-graph |
|---|---|---|
| Avg. latency | **37 ms** | 106 ms |
| LOCAL | **6.1 / 10** | 2.7 / 10 |
| STRUCTURAL | 3.2 / 10 | **3.3 / 10** |
| CROSS_MODULE | **4.2 / 10** | 1.5 / 10 |

Neo4j is 3× slower and only wins on STRUCTURAL, by a thin margin.

---

## Running the benchmark

**Prerequisites:**
- Java 21+
- Maven 3.9+
- Ollama running locally at `http://localhost:11434` with `nomic-embed-text` and `qwen2.5:14b`
- Docker (only for tests in the `search/` package that use Testcontainers)

```bash
# Build
mvn compile

# Run tests
mvn test

# Run the benchmark (adjust --source-dir to your codebase)
./run-benchmarks.sh \
  --source-dir /path/to/your/java/project/src \
  --scenario "knn-only|hybrid,hybrid|hybrid,hybrid|hybrid-graph"
```

Benchmark output lands in `target/`:
- `jmh-judge.jsonl` — aggregated scores per (strategy, scenario, fileCount, difficulty)
- `jmh-judge-detail.jsonl` — one line per question with the full context, rationale, and score

---

## What's next

Three things worth doing before investing more in GraphRAG:

**1. Parse bytecode instead of source (ASM)**
JavaParser is the bottleneck for Neo4j quality. Bytecode makes lambdas, method references, and anonymous classes explicit. Switching to ASM for building the `CALLS` graph would give K-hop expansion something real to traverse — the expected payoff is on CROSS_MODULE questions, where Neo4j currently underperforms Lucene by a wide margin.

**2. Query router**
The results suggest Lucene and Neo4j are good at different things. A router that detects whether a question is LOCAL/STRUCTURAL/CROSS_MODULE before picking a strategy could get the best of both without the full cost.

**3. Cross-encoder reranker (BGE)**
The LLM reranker (`LLMReranker`) works but is slow. A local cross-encoder like BGE-Reranker runs 10–50× faster with roughly equivalent ranking quality for code.

---

## Tech stack

| | |
|---|---|
| LangChain4j 1.11.0 | LLM/embedding abstraction, Ollama integration, AiServices |
| Neo4j Embedded 2026.01.4 | Graph database, no external server |
| Apache Lucene 9.12.0 | BM25 + KNN, embedded |
| JavaParser 3.26.2 | Java AST parsing for graph construction |
| JMH | Microbenchmark harness |
| Testcontainers | Neo4j container for search integration tests |
| nomic-embed-text | Embeddings (768 dimensions) |
| qwen2.5:14b | LLM judge |