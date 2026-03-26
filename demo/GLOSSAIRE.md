# Glossaire — Benchmarker du RAG

> Termes utilisés dans la présentation, dans l'ordre où ils apparaissent.

---

## RAG — Retrieval-Augmented Generation

Technique qui consiste à chercher du contexte pertinent dans une base de données avant de demander au LLM de répondre. Le LLM ne génère pas depuis sa mémoire seule — il s'appuie sur des documents récupérés à la volée.

---

## Embedding / Vecteur

Représentation numérique d'un texte sous forme d'un tableau de flottants (ex. 768 dimensions). Deux textes sémantiquement proches produisent des vecteurs proches dans l'espace. C'est ce qui permet de faire de la recherche par sens plutôt que par mots-clés exacts.

---

## Modèle d'embedding

Réseau de neurones (de type Transformer) entraîné à produire des embeddings. Exemples : `nomic-embed-text`, `all-MiniLM-L6-v2`, `jina-embeddings-v3`. Différent d'un LLM : il ne génère pas de texte, il encode.

---

## Token / Tokenisation

Un token est l'unité de base traitée par un Transformer — approximativement un mot ou un fragment de mot. "OllamaClient" peut devenir `["Ollama", "##Client"]`. La tokenisation est la première étape avant l'embedding.

---

## Transformer

Architecture de réseau de neurones basée sur le mécanisme d'attention. Permet à chaque token de "regarder" les autres tokens de la séquence pour ajuster sa représentation selon le contexte. Base de tous les LLMs et modèles d'embedding modernes.

---

## Cosine similarity

Mesure de proximité entre deux vecteurs. Vaut 1 si les vecteurs pointent dans la même direction (sens identique), 0 s'ils sont orthogonaux (sens sans rapport), -1 s'ils sont opposés. Utilisée pour comparer un vecteur de requête aux vecteurs indexés.

---

## KNN — K-Nearest Neighbors

Recherche des K vecteurs les plus proches d'un vecteur de requête dans l'index. Aussi appelée recherche vectorielle ou recherche sémantique. Dans Lucene : `KnnFloatVectorQuery`. Trouve ce qui **ressemble**, même sans mot en commun.

---

## BM25

Algorithme de recherche par mots-clés (lexical), standard dans les moteurs de recherche depuis les années 90. Calcule un score basé sur la fréquence des termes dans le document et leur rareté dans le corpus. Trouve les correspondances **exactes** — noms de méthodes, identifiants, termes techniques.

---

## RRF — Reciprocal Rank Fusion

Algorithme qui fusionne plusieurs listes de résultats ordonnés en une seule. Chaque document reçoit un score `1 / (k + rang)` dans chaque liste, puis les scores sont sommés. Permet de combiner BM25 et KNN sans avoir à normaliser leurs scores respectifs.

```
Score RRF(doc) = Σ  1 / (k + rang_dans_liste_i)
```

`k = 60` par défaut — atténue l'impact des premiers rangs pour éviter qu'une seule liste domine.

---

## Chunking

Découpage d'un document en fragments (chunks) avant l'indexation. Chaque chunk est embedé et stocké séparément. La qualité du chunking détermine le plafond de qualité du RAG — un chunk qui coupe une déclaration de classe en deux rend la recherche structurelle impossible.

---

## GraphRAG

Variante du RAG où les documents sont indexés dans un graphe de connaissances plutôt que dans un index vectoriel plat. La recherche peut traverser les relations du graphe (K-hop) pour remonter des informations structurellement liées à la requête.

---

## K-hop expansion

Technique de GraphRAG qui, à partir des nœuds trouvés par la recherche initiale, remonte K niveaux de relations dans le graphe pour enrichir le contexte. Avec K=2 : nœud trouvé → voisins directs → voisins des voisins.

```
OllamaService (trouvé)
    └──CALLS──► connect()          (hop 1)
                    └──USES──► OllamaClient  (hop 2)
```

---

## Reranking / Reranker

Étape optionnelle après la recherche initiale : un modèle plus puissant réévalue et réordonne les résultats selon leur pertinence réelle pour la question. Deux types :
- **LLM reranker** : envoie les chunks au LLM pour notation — précis mais lent
- **Cross-encoder** (ex. BGE-Reranker) : modèle dédié, 10-50× plus rapide

---

## LLM-as-a-judge

Technique d'évaluation où un LLM externe note la qualité d'une réponse ou d'un contexte retourné. Standard de l'industrie (MT-Bench, LMSYS Chatbot Arena). Requiert un modèle suffisamment grand (≥14B) pour que le jugement soit fiable et des exemples annotés (few-shot) pour calibrer l'échelle de notation.

---

## Few-shot prompting

Technique consistant à inclure des exemples annotés dans le prompt pour guider le comportement du LLM. Dans le contexte du juge : 3 exemples de jugements avec score 9, 4 et 0 permettent de calibrer l'échelle et de réduire la variance.

---

## Position bias

Biais du LLM juge qui tend à favoriser le chunk placé en premier dans le contexte. Mitigation : mélanger l'ordre des chunks aléatoirement avant le jugement.

---

## Structured output

Technique qui force un LLM à produire une réponse dans un format structuré (JSON avec schéma fixe) plutôt qu'en texte libre. Élimine le besoin de parser du texte fragile avec des regex. Implémenté ici via LangChain4j AiServices + schéma Ollama.

---

## hintCoverage

Mesure déterministe (non-LLM) qui vérifie si les entités attendues (noms de classes, méthodes) sont présentes dans le contexte retourné. Complémentaire au score LLM — reproductible, indépendant du modèle juge.

```
Attendu  : ["OllamaService", "Disposable", "ModelListener"]
Retourné : contient "OllamaService" et "Disposable"
Coverage : 2/3 = 0.67
```

---

## JMH — Java Microbenchmark Harness

Framework de benchmarking pour la JVM. Gère le warmup, les forks de JVM, les biais de compilation JIT et les mesures statistiques. Standard de l'industrie pour mesurer des temps d'exécution Java de façon fiable.

---

## HyDE — Hypothetical Document Embedding

Technique RAG qui génère un document hypothétique (via LLM) correspondant à la réponse attendue, puis l'embed pour la recherche — plutôt que d'ember la question directement. Améliore la recherche sémantique quand la question et les documents sont dans des styles très différents. Non inclus dans la démo (instable sur code Java compilé).

---

## ASM / Bytecode

ASM est une bibliothèque Java qui analyse le bytecode compilé (`.class`) plutôt que le code source. Avantage sur JavaParser : les lambdas, méthodes de référence et classes anonymes sont explicites dans le bytecode — les relations `CALLS` ne peuvent pas être ratées.
