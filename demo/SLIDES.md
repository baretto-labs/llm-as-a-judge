---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
style: |
  section {
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 1.2rem;
  }
  h1 { color: #1a1a2e; font-size: 2rem; }
  h2 { color: #16213e; border-bottom: 3px solid #e94560; padding-bottom: 0.3em; }
  h3 { color: #0f3460; }
  code { background: #f4f4f8; border-radius: 4px; padding: 2px 6px; }
  pre { background: #1a1a2e; color: #e0e0e0; border-radius: 8px; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #1a1a2e; color: white; padding: 8px 12px; }
  td { padding: 8px 12px; border-bottom: 1px solid #eee; }
  section.title { background: #1a1a2e; color: white; }
  section.title h1 { color: white; font-size: 2.6rem; }
  section.title h2 { color: #e94560; border: none; font-size: 1.3rem; }
  section.title p { color: #aaa; font-size: 1rem; }
  section.big { display: flex; flex-direction: column; justify-content: center; text-align: center; }
  section.big h2 { border: none; font-size: 2rem; }
  section.big p { font-size: 1.4rem; }
---

<!-- _class: title -->

# Benchmarker du RAG

## Lucene vs GraphRAG — LLM-as-a-judge comme arbitre

*OllamAssist · 126 classes Java · qwen2.5:14b comme juge*

---

## Le contexte

J'ai un plugin IntelliJ avec un assistant IA — **OllamAssist**.

Avant de répondre, il cherche du contexte dans la codebase via un RAG.

J'ai deux options devant moi :

| | Lucene | Neo4j GraphRAG |
|---|---|---|
| Approche | BM25 + KNN + RRF | Graphe de connaissances |
| Latence | ~35 ms | ~100 ms |
| Infrastructure | embarqué | Neo4j server |

---

<!-- _class: big -->

## Comment je choisis ?

**La réponse habituelle : "on mesure la latence."**

---

## Le problème avec la latence

```
Question : "Comment OllamaService initialise-t-il la connexion ?"

Lucene  → 3 méthodes génériques de 3 classes différentes   35 ms ✓
Neo4j   → OllamaService + ses dépendances directes         105 ms ✗
```

La latence mesure **le temps**.

Elle ne mesure pas si le contexte retourné permet **réellement** de répondre à la question.

---

<!-- _class: big -->

## On a besoin de mesurer la qualité du retrieval.

*Pas juste la vitesse.*

---

## Stratégie 1 — Lucene hybride

```
Question ──► BM25 (mots-clés exacts)  ─┐
         └──► KNN (similarité vectorielle) ┴──► RRF ──► Top-10
```

- Voit ce qui **ressemble**
- Rapide, embarqué, zéro infrastructure externe
- Excellent sur les noms de méthodes et de classes

---

## Comment fonctionne l'embedding

On rentre une phrase. On sort un vecteur.

```
  "public void initialize(OllamaClient client)"
                    │
             nomic-embed-text
                    │
   [ 0.23, -0.87,  0.41,  0.12, -0.33,  0.76, ... ]
     └────────────────── 768 dimensions ────────────────┘
```

Mais comment ce vecteur est-il calculé ?

---

## À l'intérieur du modèle d'embedding

**Étape 1 — Tokenisation**

```
"initialize(OllamaClient client)"
     │
     ▼
["init", "##ialize", "(", "Ollama", "##Client", "client", ")"]
```

Chaque token devient un vecteur initial (lookup table).

---

## À l'intérieur du modèle d'embedding

**Étape 2 — Attention (Transformer)**

Chaque token regarde les autres et ajuste sa représentation selon le contexte :

```
 "initialize"  ◄──────────────────── regarde ────► "OllamaClient"
      │                                                    │
      │   "ah, ici initialize est lié à un client réseau"  │
      ▼                                                    ▼
  [0.41, ...]                                         [-0.12, ...]
                     (12 couches d'attention)
```

**Étape 3 — Pooling**

Les N vecteurs de tokens sont fusionnés en un seul :

```
[token1] [token2] [token3] ... [tokenN]
              │
           moyenne
              │
   [0.23, -0.87, 0.41, ...]  ← le vecteur final
```

---

## Ce que ça veut dire en pratique

Deux phrases sémantiquement proches → vecteurs proches dans l'espace

```
  "public void initialize(OllamaClient client)"
   → [ 0.23, -0.87,  0.41, ... ]
                                    ┐
                          cos = 0.94  ← très proche
                                    ┘
  "Comment initialise-t-on la connexion Ollama ?"
   → [ 0.21, -0.91,  0.38, ... ]
```

```
  "calculateDynamicThreshold(List<Float> scores)"
   → [-0.54,  0.33, -0.12, ... ]
                                    ┐
                          cos = 0.11  ← très loin
                                    ┘
  "Comment initialise-t-on la connexion Ollama ?"
   → [ 0.21, -0.91,  0.38, ... ]
```

**Le modèle n'a jamais vu OllamAssist — il généralise depuis son entraînement.**

---

## Stratégie 2 — Neo4j GraphRAG

```
Code Java ──► JavaParser ──► Graphe
                              Class ──EXTENDS──► Class
                              Method ──CALLS──► Method
                              Class ──IMPLEMENTS──► Interface
```

```
Question ──► Hybrid Search ──► nœuds
                           └──► K-hop expansion ──► voisins
```

- Voit ce qui **dépend**
- Comprend les chaînes d'appels inter-modules

---

## Comment le graphe se construit

JavaParser lit chaque fichier Java et en extrait les nœuds et relations :

```java
// OllamaService.java
public class OllamaService extends OllamaServiceBase
        implements Disposable, ModelListener {

    private OllamaClient client;          // ──DECLARES──► Property

    public void initialize() {
        client.connect();                 // ──CALLS──► connect()
    }
}
```

```
(OllamaService:Class)
    ──EXTENDS──────► (OllamaServiceBase:Class)
    ──IMPLEMENTS───► (Disposable:Interface)
    ──IMPLEMENTS───► (ModelListener:Interface)
    ──DECLARES─────► (client:Property)
    ──DECLARES─────► (initialize:Function)
          │
          └──CALLS──► (OllamaClient.connect:Function)
                           └──USES──► (OllamaClient:Class)
```

La recherche K-hop traverse ces relations pour élargir le contexte.

---

## Isoler chaque variable avec des feature flags

Plutôt que comparer deux boîtes noires, on active les couches une par une :

| Preset | Ce qui est actif |
|---|---|
| `knn-only` | KNN vectoriel pur — la baseline |
| `hybrid` | + BM25 + RRF |
| `hybrid-graph` | + expansion K-hop |

Chaque étape a un coût mesurable et un gain mesurable.

---

<!-- _class: big -->

## Mais comment mesurer la pertinence du contexte ?

---

## LLM-as-a-judge

```
  Question posée
+ Contexte retourné par la stratégie
─────────────────────────────────────
       qwen2.5:14b (juge)
─────────────────────────────────────
  Score 0–10
  Rationale : "Le contexte contient X mais manque Y"
  suggestsUnknown : true/false
```

- Structured output via LangChain4j — pas de regex fragile
- Few-shot : 3 exemples annotés (score 9 / 4 / 0)
- Position bias : ordre des chunks mélangé avant jugement

---

## + hintCoverage — mesure déterministe

Le score LLM peut varier. On l'ancre avec une vérification programmatique :

```
Question : "What interfaces does OllamaService implement?"

Attendu  : ["OllamaService", "Disposable", "ModelListener"]
Retourné : contient "OllamaService" et "Disposable"

hintCoverage = 2/3 = 0.67
```

Reproductible, indépendant du LLM juge.

---

## 30 questions sur OllamAssist — 3 niveaux

| Niveau | Ce qu'il teste |
|---|---|
| **LOCAL** (×10) | Une méthode précise — *"What does `calculateDynamicThreshold` compute?"* |
| **STRUCTURAL** (×10) | Héritage, interfaces — *"What interfaces does `OllamaService` implement?"* |
| **CROSS_MODULE** (×10) | Chaînes d'appels — *"How does `DocumentIndexingPipeline` interact with `LuceneEmbeddingStore`?"* |

---

## Résultats — Latence

| Stratégie | Preset | Latence moy. |
|---|---|---|
| Lucene | knn-only | 35 ms |
| Lucene | hybrid | 37 ms |
| Neo4j | hybrid | 92 ms |
| Neo4j | hybrid-graph | **106 ms — 3× plus lent** |

Le graphe a un coût. Il faut s'assurer qu'il le vaut.

---

<!-- _class: big -->

## Résultats qualité

*Score LLM-as-a-judge / 10 · 30 questions OllamAssist*

---

## Le levier n°1 : BM25

| Preset | Score global |
|---|---|
| Lucene knn-only | 1.8 / 10 |
| Lucene **hybrid** | **4.5 / 10** |

### +154% en ajoutant BM25

Le KNN cherche ce qui *ressemble*.
BM25 cherche `calculateDynamicThreshold`, `OllamaService` — les noms exacts.

**Pour du code, le lexical est indispensable.**

---

## Par niveau de difficulté

| | LOCAL | STRUCTURAL | CROSS_MODULE |
|---|---|---|---|
| Lucene knn-only | 2.6 | 0.8 | 1.9 |
| Lucene hybrid | **6.1** | 3.2 | **4.2** |

Le BM25 améliore **tous les niveaux**.
L'écart est particulièrement fort sur LOCAL — les noms de méthodes font tout.

---

## Le fix chunking — 20 lignes, +60%

STRUCTURAL avait 80% de "je ne sais pas". La raison :

```
// AVANT
Type: fr.baretto.ollamassist.OllamaService
Field: private OllamaClient client;

// APRÈS — déclaration complète
Type: class fr.baretto.ollamassist.OllamaService
      extends OllamaServiceBase
      implements Disposable, ModelListener  ← voilà la réponse
Field: private OllamaClient client;
```

| | STRUCTURAL avant | STRUCTURAL après |
|---|---|---|
| Lucene hybrid | 2.0 / 10 | **3.2 / 10 (+60%)** |

---

<!-- _class: big -->

## Sans benchmark,

## on n'aurait jamais su

## que ce chunk manquait.

---

## Résultats Neo4j

| Preset | LOCAL | STRUCTURAL | CROSS_MODULE |
|---|---|---|---|
| knn-only | 2.7 | 2.7 | 1.5 |
| hybrid | 2.7 | 2.7 | 2.1 |
| **hybrid-graph** | 2.7 | **3.3** | 1.5 |

Les scores sont **plats** sur LOCAL et CROSS_MODULE.

Le K-hop commence à aider sur STRUCTURAL — mais le graphe est incomplet.

---

## Pourquoi le graphe est plat

JavaParser rate les lambdas, les méthodes de référence et les classes anonymes du SDK IntelliJ.

Les relations `CALLS` manquantes → la K-hop expansion ne trouve pas les bons voisins.

```
OllamAssistStartup
    └── () -> EditorListener.register()   ← lambda, non parsée
              └── CALLS manquant dans le graphe
```

**La solution : parser le bytecode compilé (ASM).**
Les lambdas sont explicites dans le bytecode — elles ne mentent pas.

---

## Tableau de bord final

| | Lucene hybrid | Neo4j hybrid-graph |
|---|---|---|
| Latence | **37 ms** | 106 ms |
| LOCAL | **6.1 / 10** | 2.7 / 10 |
| STRUCTURAL | 3.2 / 10 | **3.3 / 10** |
| CROSS_MODULE | **4.2 / 10** | 1.5 / 10 |

Neo4j 3× plus lent. Gagne uniquement sur STRUCTURAL.
Sans benchmark, j'aurais payé ce coût **pour zéro gain sur 2 questions sur 3**.

---

## Ce qu'on retient

**BM25 + KNN, pas KNN seul**
+154% — le lexical et le sémantique se complètent pour du code.

**Le chunking détermine le plafond**
20 lignes → +60% sur STRUCTURAL. Avant d'ajouter des features, vérifier les chunks.

**GraphRAG dépend de la qualité du graphe**
Source Java → lambdas ratées → K-hop inutile.
Bytecode → graphe complet → K-hop pertinent.

---

## Prochaines étapes

**Graphe via bytecode (ASM)**
Corriger les relations CALLS manquantes → débloquer Neo4j sur CROSS_MODULE.

**Query router**
Détecter la nature de la question → envoyer vers la stratégie optimale.

**Cross-encoder reranker (BGE)**
Remplacer le LLM reranker — 10-50× plus rapide, qualité équivalente.

---

<!-- _class: title -->

# Merci

*Code + benchmark + dashboard disponibles sur le repo*

---

<!-- _class: big -->

## Le vecteur trouve ce qui ressemble.

## Le graphe trouve ce qui dépend.


