# Plan de démo — RAG Benchmark
> Notes internes présentateur. Ne pas partager.

---

## Checklist avant la démo

- [ ] Ollama tourne (`ollama serve`)
- [ ] Modèles disponibles : `nomic-embed-text`, `qwen2.5:14b`
- [ ] OllamAssist indexé (run d'indexation fait à l'avance)
- [ ] Benchmark tourné : `target/jmh-results.json`, `target/jmh-judge.jsonl`, `target/jmh-judge-detail.jsonl`
- [ ] Dashboard ouvert dans le navigateur, fichiers chargés
- [ ] Une ligne CROSS_MODULE pré-sélectionnée avec un écart de score visible entre Lucene et Neo4j

---

## Timing — 20 minutes

| Bloc | Durée | Objectif |
|---|---|---|
| 1. Le problème | 2 min | Poser la question — comment mesurer la qualité RAG ? |
| 2. Les deux stratégies | 3 min | Lucene vs GraphRAG — ce qui les différencie fondamentalement |
| 3. Feature flags | 2 min | Comment on isole la valeur de chaque optimisation |
| 4. LLM-as-a-judge | 3 min | Comment on mesure la qualité objectivement |
| 5. Les résultats | 7 min | Dashboard — perf + qualité + panneau dépliable |
| 6. La vraie conclusion | 3 min | Pas de winner universel — le benchmark EST la réponse |

---

## Bloc 1 — Le problème (2 min)

**Message** : la latence ne suffit pas à choisir une stratégie RAG.

- Poser le dilemme : Lucene (simple, rapide) vs GraphRAG (riche, coûteux)
- "Comment vous choisissez aujourd'hui ?" — laisser la question résonner
- "On a besoin de mesurer la *qualité* du contexte retourné, pas juste la vitesse"

**À éviter** : rentrer dans les détails techniques ici. Juste le problème.

---

## Bloc 2 — Les deux stratégies (3 min)

**Message** : deux philosophies radicalement différentes face au même problème.

- **Lucene** : BM25 + KNN + RRF. Voit les mots, pas les relations.
- **Neo4j** : le code est parsé en graphe (EXTENDS, CALLS, DECLARES). La recherche traverse les relations.
- Montrer le schéma du graphe dans SUPPORT.md — 30 secondes, puis passer.

**À éviter** : expliquer RRF en détail. "Fusion des deux résultats" suffit.

---

## Bloc 3 — Feature flags (2 min)

**Message** : on active les optimisations une par une pour mesurer leur valeur marginale.

- Montrer les 3 presets : `knn-only` → `hybrid` → `hybrid-graph`
- "Chaque étape a un coût et un gain qu'on va mesurer"
- Pas besoin de montrer le code — le tableau du SUPPORT.md suffit

**Ne pas mentionner** : HyDE, LLM reranking. Hors scope.

---

## Bloc 4 — LLM-as-a-judge (3 min)

**Message** : on demande à un LLM de noter le contexte retourné — reproductible, explicable.

- Expliquer le principe en 1 phrase : "On donne la question + le contexte au juge, il note de 0 à 10"
- Insister sur le **structured output** — pas de parsing fragile, le schéma est garanti
- Présenter hintCoverage comme filet de sécurité déterministe
- "Le juge explique son score — c'est ça qui rend l'évaluation actionnable"

**Transition** : "Voyons ce que ça donne sur OllamAssist"

---

## Bloc 5 — Les résultats (7 min)

**Séquence dashboard :**

**5a. Latence (2 min)**
- Montrer le graphe latence — l'écart Neo4j / Lucene est visible
- "Le graphe coûte plus cher — est-ce que ça vaut le coup ?"
- Ne pas commenter les chiffres absolus — la comparaison relative est le message

**5b. Scores judge (2 min)**
- Montrer les 3 charts judge (Score / Hint Coverage / Unknown Rate)
- Pointer le breakdown par difficulté — LOCAL similaire, CROSS_MODULE diverge
- "Sur les questions locales, Lucene est compétitif. Sur les questions cross-module, le graphe fait la différence."

**5c. Panneau dépliable — moment fort (3 min)**
- Ouvrir une ligne CROSS_MODULE avec écart de score Lucene vs Neo4j
- Lire la question à voix haute
- Montrer le contexte Lucene : "Il a retourné la classe, mais pas la chaîne d'appels"
- Montrer le contexte Neo4j : "Le K-hop a remonté toute la chaîne de délégation"
- Lire la rationale du juge
- Laisser le silence faire son effet

---

## Bloc 6 — La vraie conclusion (3 min)

**Message** : il n'y a pas de winner universel — le benchmark est l'outil pour décider.

- "GraphRAG n'est pas universellement meilleur"
- "Sur des questions locales, payer le surcoût du graphe ne sert à rien"
- "Sur des questions cross-module, le graphe retrouve ce que le vecteur manque"
- **La conclusion actionnable** : "Benchmarke sur *ta* codebase, avec *tes* questions"
- Montrer le tableau récap du SUPPORT.md §9

**Dernière phrase à dire** :
> "Le benchmark n'est pas la destination — c'est la boussole."

---

## Questions probables

**"Pourquoi OllamAssist comme corpus ?"**
> C'est un vrai projet Java avec des vraies relations entre classes — pas du code synthétique. Et je connais le code, donc je sais si le contexte retourné est réellement pertinent.

**"Le juge LLM peut se tromper ?"**
> Oui. C'est pour ça qu'on combine score LLM + hintCoverage déterministe. Et qu'on peut brancher plusieurs juges pour mitiger le biais d'un modèle unique.

**"HyDE c'est quoi ?"**
> Une optimisation qu'on a implémentée mais qu'on n'a pas incluse dans la démo — ça mérite un talk à part entière.

**"Ça marche sur d'autres langages que Java ?"**
> Le parser AST est Java-specific aujourd'hui. Le pattern LLM-as-a-judge est universel — l'adaptation du parser est l'effort principal.

**"Vous utilisez ça en prod ?"**
> C'est un benchmark de recherche pour l'instant. L'objectif c'est de prendre une décision éclairée avant de choisir une stratégie en prod.
