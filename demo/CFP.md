pour m# CFP — DevLille 2026
> Brouillon de soumission. Format : Quicky (20 min). Catégorie : BigData & AI.

---

## Titre

**"Mon IA fait ses devoirs, mais est-ce qu'elle comprend vraiment ?"**
*Benchmarker la qualité d'un RAG avec LLM-as-a-judge*

---

## Titre alternatif (plus direct)

**"RAG : arrêtons de deviner si ça marche vraiment"**
*De la latence à la pertinence — mesurer ce qui compte vraiment*

---

## Abstract (public — affiché sur le programme)

L'année dernière, OllamAssist avait des problèmes de performance.
On a sorti JMH, on a mesuré, on a corrigé.

Cette année, les temps de réponse sont bons. Mais est-ce que les réponses sont **bonnes** ?

C'est une question radicalement différente — et beaucoup plus difficile à mesurer.

Pour y répondre, j'ai benchmarké deux stratégies RAG sur la codebase d'OllamAssist :
une approche vectorielle classique (Lucene, BM25+KNN+RRF) et une approche GraphRAG
(Neo4j, graphe de connaissances parsé depuis le code source).

Mais comment comparer la *qualité* du contexte retourné ? En demandant à un LLM de jouer
le rôle du juge. LLM-as-a-judge : score 0-10, rationale explicite, mesure reproductible.

Ce talk c'est l'histoire d'un dev qui a arrêté de deviner si son RAG était bon —
et qui a construit les outils pour le savoir.

**Ce que tu repars avec :** une méthode concrète pour benchmarker n'importe quel
système RAG, un framework open-source réutilisable, et une réponse claire à
"Lucene ou GraphRAG ?" — qui n'est pas "ça dépend", mais "voilà quand choisir quoi".

---

## Description jury (non publique — arguments de sélection)

### Pourquoi ce sujet maintenant

RAG était à DevLille en 2024 (LangChain4j) et en 2025 (RAG+MCP). Mais personne
n'a encore adressé la question de **l'évaluation** : comment savoir si ton RAG
retourne du bon contexte ? La majorité des équipes mesurent la latence et s'arrêtent là.
Ce talk comble ce trou.

### Ce qui est original

- **LLM-as-a-judge appliqué au retrieval** (pas à la génération) — angle peu traité
- **Structured output** via LangChain4j AiServices — zero regex, type safety garantie
- **Feature flags RAG** — isole la valeur marginale de chaque optimisation (BM25, K-hop...)
- **Dashboard interactif** avec drill-down question/contexte/score — démontrable en live

### La narrative

Ce talk est la suite naturelle de ma soumission au Tremplin 2025 sur JMH + VisualVM.
L'année dernière : OllamAssist apprend à marcher, on mesure ses performances.
Cette année : OllamAssist entre en adolescence, on mesure sa maturité intellectuelle.

La même question — *"est-ce qu'on mesure vraiment ce qui compte ?"* — appliquée
à un nouveau problème. La même conviction : un dev sans mesure, c'est un dev qui devine.

### Format Quicky — pourquoi 20 min suffisent

Le message tient en une idée : **mesurez la qualité de votre RAG, pas juste sa vitesse**.
La démo dashboard est visuelle et immédiate. La conclusion est actionnable en 1 slide.
Pas besoin de plus.

### Niveau

Intermédiaire. Connaître RAG n'est pas requis — le concept est posé en 2 minutes.
Connaître JMH ou LangChain4j non plus. Le talk est accessible à tout dev curieux des LLMs.

---

## Structure du talk (pour le jury)

| Temps | Contenu |
|---|---|
| 0–2 min | Le problème : latence ≠ qualité. La question qu'on ne pose pas assez. |
| 2–5 min | Les deux stratégies : Lucene (similarité) vs GraphRAG (dépendances) |
| 5–7 min | Feature flags : isoler la valeur de chaque optimisation |
| 7–10 min | LLM-as-a-judge : comment on mesure la qualité objectivement |
| 10–17 min | Live dashboard : résultats sur OllamAssist — perf + qualité + drill-down |
| 17–20 min | Conclusion : vecteur vs graphe — quand choisir quoi, et pourquoi |

---

## Tags suggérés

`RAG` `LLM` `GraphRAG` `Benchmark` `LangChain4j` `Java` `Neo4j` `Qualité IA`

---

## Notes pour la soumission

- Catégorie : **BigData & AI**
- Format : **Quicky (20 min)**
- Niveau : **Intermédiaire**
- Langue : **Français**
- Slides : en français, code en anglais
- Demo : live sur dashboard interactif (pas de slides de code)
