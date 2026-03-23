# Benchmarker du RAG sans se mentir à soi-même
### Lucene vs GraphRAG — LLM-as-a-judge comme arbitre

---

## 1. Le problème

Tu construis un système RAG. Tu as deux options devant toi.

```
Option A : Lucene          Option B : Neo4j GraphRAG
BM25 + KNN + RRF           Graphe de connaissances
Rapide, simple             Riche en relations
```

**Comment tu choisis ?**

La réponse habituelle : on teste, on mesure la latence, on choisit le plus rapide.

```
❌ La latence ne mesure pas si le contexte retourné
   permet réellement de répondre à la question.
```

Ce qu'il faut mesurer c'est **la qualité du retrieval** — et c'est difficile à objectiver.

---

## 2. Les deux stratégies

### Lucene — Recherche hybride

```
Question ──► BM25 (lexical)  ─┐
         └─► KNN (vectoriel) ─┴──► RRF fusion ──► Top-K contexte
```

- Rapide, embarqué, sans infrastructure
- Voit les mots, pas les **relations** entre entités

---

### Neo4j GraphRAG — Graphe de connaissances

Le code source est parsé en graphe :

```
Class ──EXTENDS──► Class
Class ──DECLARES──► Method
Method ──CALLS──► Method
Method ──USES──► Class
```

Puis la recherche traverse ce graphe :

```
Question ──► Hybrid Search ──► Top-K nœuds
                           └──► K-hop expansion ──► contexte élargi
```

- Comprend les dépendances entre classes
- Peut retrouver une chaîne d'appels que le vecteur manquerait
- Coûteux en latence

---

## 3. Feature flags — isoler la valeur de chaque optimisation

Plutôt que de comparer deux boîtes noires, on active les optimisations une par une :

| Preset | Ce qui est actif | Question |
|---|---|---|
| `knn-only` | KNN vectoriel pur | Quelle est la baseline ? |
| `hybrid` | + BM25 + RRF | Qu'apporte le lexical ? |
| `hybrid-graph` | + expansion K-hop | Qu'apporte le graphe ? |

→ Chaque étape a un **coût mesurable** et un **gain mesurable**.

---

## 4. Le problème de la mesure

On a la latence. Mais comment mesurer si le contexte retourné est *pertinent* ?

### Option naïve : vérifier manuellement
- Non reproductible
- Ne scale pas avec le corpus
- Biaisé par le rédacteur

### Notre approche : LLM-as-a-judge

```
Question posée
+ Contexte retourné par la stratégie
─────────────────────────────────────────────
         LLM juge (≥14B, qwen2.5:14b)
─────────────────────────────────────────────
→ Score 0–10
→ Rationale : "Le contexte contient X mais manque Y"
→ suggestsUnknown : le contexte forcerait-il "je ne sais pas" ?
```

**Structured output** via LangChain4j AiServices — pas de regex, type safety garantie par le schéma JSON Ollama.

---

## 5. Ce que le juge ne suffit pas à mesurer

Le score LLM est subjectif. On ajoute une mesure déterministe :

**hintCoverage** : fraction des entités attendues trouvées dans le contexte retourné.

```java
// Exemple — question : "What does Class0Service depend on ?"
expectedFqnHints = ["OllamaClient", "CompletionRequest", "StreamHandler"]

// Contexte retourné contient "OllamaClient" et "CompletionRequest"
hintCoverage = 2/3 = 0.67
```

→ Mesure programmatique, reproductible, indépendante du LLM.

---

## 6. Les 3 niveaux de difficulté

Les questions sont classées pour révéler les forces et faiblesses de chaque stratégie :

| Niveau | Ce qu'il teste | Avantage attendu |
|---|---|---|
| **LOCAL** | Une seule classe ou méthode | Aucun — les deux stratégies sont équivalentes |
| **STRUCTURAL** | Héritage, relations directes | GraphRAG — les relations sont explicites dans le graphe |
| **CROSS_MODULE** | Chaîne d'appels multi-packages | GraphRAG — le K-hop traverse les dépendances |

---

## 7. Résultats — sur OllamAssist

*(à compléter après le run)*

### Performance

| Stratégie | Preset | p50 (ms) | p99 (ms) |
|---|---|---|---|
| Lucene | knn-only | — | — |
| Lucene | hybrid | — | — |
| Neo4j | hybrid | — | — |
| Neo4j | hybrid-graph | — | — |

### Qualité (score juge /10)

| Stratégie | Preset | LOCAL | STRUCTURAL | CROSS_MODULE |
|---|---|---|---|---|
| Lucene | knn-only | — | — | — |
| Lucene | hybrid | — | — | — |
| Neo4j | hybrid | — | — | — |
| Neo4j | hybrid-graph | — | — | — |

---

## 8. Ce que les résultats nous apprennent

*(à affiner selon les vrais chiffres)*

**Ce qu'on observe :**
- Sur les questions LOCAL : Lucene est compétitif — le vecteur suffit, le graphe n'apporte rien de significatif
- Sur les questions CROSS_MODULE : le K-hop fait la différence — le graphe retrouve des chaînes d'appels que le vecteur manque
- Le coût du graphe est réel : Neo4j hybrid-graph est ~Xx plus lent que Lucene hybrid

**La vraie conclusion :**

```
Il n'y a pas de stratégie universellement meilleure.
Le choix dépend de la nature des questions que
ton système doit traiter.
```

→ C'est exactement pour ça qu'on a besoin d'un benchmark.

---

## 9. Ce qu'on retient

Le benchmark n'est pas l'objectif — c'est **l'outil pour prendre une décision éclairée**.

| Si tes questions sont... | Utilise... |
|---|---|
| Locales (une classe, une méthode) | Lucene hybrid — rapide, suffisant |
| Structurelles (héritage, dépendances) | Neo4j hybrid-graph |
| Cross-module (chaînes d'appels) | Neo4j hybrid-graph |
| Un mix des trois | Benchmarke sur ta codebase |

---

## Références

- **MT-Bench** — LLM-as-a-judge (Zheng et al., 2023)
- **GraphRAG** — From Local to Global (Edge et al., Microsoft, 2024)
- **RRF** — Reciprocal Rank Fusion (Cormack et al., 2009)
- **BEIR** — Benchmark for Information Retrieval (Thakur et al., 2021)
