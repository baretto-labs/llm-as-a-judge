# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Write the code and comments in English, but always respond in the user's language in the chat.

## Working Memory — WIP.md

**Always read `WIP.md` at the start of any session before touching code.**

`WIP.md` is the project's working memory. It contains:
- The list of completed work (with the files modified and the rationale)
- The prioritized backlog of improvements identified by the 2026 audit
- Architecture decisions already taken (do not revisit without good reason)
- Open questions pending user input

**Consult WIP.md when:**
- Starting a new task (check if it's already planned or done)
- About to make an architecture decision (check if it conflicts with a prior decision)
- Implementing anything from the backlog (follow the priority order)
- Finishing a task (update the "Complétés" section and the last-updated date)

## Build & Run Commands

```bash
# Build
mvn compile

# Run all tests
mvn test

# Run a single test class
mvn test -Dtest=TestIndexationRecuperation

# Run a single test method
mvn test -Dtest=TestGraphRelations#myTestMethod

# Run the Swing UI application
mvn exec:java
```

## Architecture Overview

This is a **RAG (Retrieval-Augmented Generation) benchmark** comparing two retrieval strategies for Java codebases, using LangChain4j + Ollama as the LLM layer.

### Strategy Pattern (core abstraction)

`RagStrategy` interface has two implementations:
- **`LuceneRagStrategy`** — classic vector/keyword search with Apache Lucene (embedded)
- **`Neo4jGraphRagStrategy`** — GraphRAG using Neo4j Embedded; parses Java source with JavaParser to build a knowledge graph, then traverses it for retrieval

`RagService` owns the active strategy and routes indexation/retrieval calls. The Swing `App` lets users switch strategies at runtime.

### Neo4j Graph Schema

Nodes: `File`, `Class`, `Interface`, `Enum`, `Record`, `Function`, `Constructor`, `Property`, `Parameter`, `Annotation`, `Import`, `Package`, `Project`

Relations: `CONTAINS`, `IMPORTS`, `EXTENDS`, `IMPLEMENTS`, `DECLARES`, `CALLS`, `USES`, `RETURNS`, `HAS_PARAMETER`, `ANNOTATED_WITH`

The default embedded DB path is `./neo4j-db`. Tests use a custom path passed via constructor (`Neo4jGraphRagStrategy(String customDbPath)`).

### Advanced Search Pipeline (`search/` package)

`GraphSearchHook` interface → two implementations:
1. **`HybridSearchService`** — BM25 full-text + vector (cosine) search fused with RRF (Reciprocal Rank Fusion). Requires full-text index `codeFullText` and vector index `codeVector` in Neo4j.
2. **`AdvancedSearchService`** — full pipeline: Hybrid Search → K-hop Graph Expansion (`GraphTraversal`) → LLM Reranking (`LLMReranker`). Also supports community-based global search via `CommunityDetection`.

### Key Dependencies

| Dependency | Role |
|---|---|
| LangChain4j 1.11.0 | LLM/embedding abstraction (Ollama integration) |
| Neo4j Embedded 2026.01.4 | Graph database (no external server needed for strategy) |
| Neo4j Java Driver 5.15.0 | Used by search services (bolt protocol) |
| JavaParser 3.26.2 | Java AST parsing for graph construction |
| Apache Lucene 9.12.0 | Lucene strategy only |
| Testcontainers (neo4j) | Integration tests spin up a Neo4j container |

### External Dependencies (runtime)

- **Ollama** must be running locally at `http://localhost:11434` for LLM/embedding features
- Integration tests (`search/` package) use Testcontainers and require Docker

### Test Layout

- `fr.baretto.benchmarks.*` — unit/integration tests for Neo4j graph construction (indexation, Cypher queries, relation resolution)
- `fr.baretto.benchmarks.search.*` — integration tests for hybrid search, graph traversal, community detection, LLM reranking (require Docker/Testcontainers)

### `SymbolTable`

Used during indexation by `Neo4jGraphRagStrategy` to resolve Java type names (simple name → FQN). Resolution order: explicit imports → same package → `java.lang` → global unique match.