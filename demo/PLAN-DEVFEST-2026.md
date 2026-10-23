# Plan du talk — DevFest Paris 2026

**Arrêté le 2026-10-17.** 13 diapositives, **16 min 55** annoncées, 20 min de créneau
questions comprises. Remplace tout plan antérieur.

Ce plan est un **REX** : ce que j'ai fait et les pièges dans lesquels je suis tombé.
Ce n'est pas un exposé de méthodes. La méthode se coupe, les quatre preuves restent.

## Le minutage

| # | Diapositive | Durée |
|---|---|---|
| 1 | Bonjour | 0:40 |
| 2 | La thèse à l'écran + Air Canada *(absorbe l'ancienne 3)* | 0:50 |
| 4 | OllamAssist, les deux stratégies, **l'annonce du renversement** | 1:35 |
| 5 | Le principe du juge | 2:15 |
| 6 | L'implémentation LangChain4j | 1:30 |
| 7 | L'expert + le dataset *(fusionnés)* | 1:30 |
| 8 | Le banc : vectoriel contre graphe | 0:50 |
| 9 | Juger le juge — l'étalon, l'accord, ce que 50 items ne tranchent pas | 1:30 |
| 10 | Résultats, la surprise, mon bug | 2:15 |
| 11 | **Trois biais RAG constatés sur mes runs** | 1:15 |
| 12 | BM25, rerun, en production dans l'heure | 1:15 |
| 13 | Ouverture : le fine-tuning, le dépôt | 0:45 |
| 14 | Conclusion | 0:45 |

La numérotation saute le 3 : l'ancienne diapo 3 est fondue dans la 2. Je garde les numéros
d'origine pour que les notes déjà écrites restent utilisables.

## Réserve de coupe, déclarée maintenant

Un plan à 16:55 non répété se joue en 19 à 20 minutes. Si la première passe chronométrée
dépasse, je descends cette liste **dans l'ordre** — je ne réarbitre pas la veille au soir.
C'est exactement ce qui m'a piégé la fois précédente.

| | Coupe | Gain | Total |
|---|---|---|---|
| 1 | diapo 2 → 0:40 (Air Canada en deux phrases) | 10 s | 16:45 |
| 2 | diapo 8 → 0:40 (dispositif resserré) | 10 s | 16:35 |
| 3 | diapo 7 → 1:20 (« l'expert, c'était moi », sans développement) | 10 s | 16:25 |
| 4 | diapo 13 → 0:30 (simple pointeur vers le dépôt) | 15 s | 16:10 |
| 5 | diapo 5 → 2:00 | 15 s | 15:55 |

Une minute de réserve. **Aucune ne touche aux diapos 4, 6, 9, 10, 11, 12 ni 14** : ce sont
les quatre preuves et les deux phrases porteuses.

## Les trois phrases à écrire mot pour mot

Elles ne s'improvisent pas sur scène. Elles restent à rédiger.

1. **Diapo 4 — l'annonce du renversement.** Elle arme tout le reste ; la diapo 14 la referme.
2. **Diapo 6 — la thèse.** *Le code n'est pas le problème.* Tout le talk en découle :
   l'expert, le dataset, juger le juge.
3. **Diapo 14 — la fermeture de la boucle ouverte en 4.**

Sur la diapo 6 : douze lignes de code au maximum, une seule surlignée, et ne pas la lire à
voix haute. S'il faut faire défiler, le point est mort.

## Diapo 11 — les trois biais

Tirés de la campagne du 2026-09-24 : 240 jugements, 60 questions × 2 stratégies × 2 scénarios.
Ils viennent de mes runs, pas de la littérature — c'est la seule raison pour laquelle cette
diapo n'est pas un cours.

**Biais 1 — ce n'est pas le bruit, c'est le manque.** Taux d'échec par contrôle :

| | `contexte_pertinent` | `contexte_suffisant` | `bruit_maitrise` |
|---|---|---|---|
| Lucene | 38 % | **43 %** | 27 % |
| Neo4j | 45 % | **67 %** | 27 % |

Le réflexe est « le RAG ramène n'importe quoi ». Les mesures disent l'inverse : le contexte
est bien plus souvent **incomplet** que hors sujet, et le bruit est le contrôle qui échoue
le moins — identiquement pour les deux stratégies.

**Biais 2 — le graphe ramène la structure, pas le corps.** 22 % des items Neo4j sont
*pertinents mais insuffisants*, contre 7 % pour Lucene. Trois fois plus.

**Biais 3 — l'angle mort est là où j'attendais le gain.** Sur les questions cross-module,
Neo4j passe à 10 %, Lucene à 50 %. Je suis allé au GraphRAG *pour* la traversée
inter-modules, et c'est son pire terrain.

**La phrase qui relie la 10 et la 11, et qui vaut mieux que les trois biais pris séparément :**

> « J'ai nommé trois biais à partir de mes mesures, puis j'ai découvert que deux n'en
> faisaient qu'un — et qu'il était à moi. »

Les biais 2 et 3 partagent une racine unique, des nœuds sans corps de méthode, et cette
racine est probablement mon code de projection, pas le GraphRAG. L'aveu est la **preuve**,
pas le propos : le sujet de la phrase est celui qui détecte.

**L'exemple travaillé de la diapo 11**, à préparer : *« What interface does ContextRetriever
implement and what does it override? »* — le graphe rend le nom de l'interface et aucune
méthode. Même question, contexte tronqué → réponse fausse ; contexte complet → réponse juste.
Ce n'était pas une hallucination. **Cet exemple ne dépend d'aucun run** : dix minutes de
travail, pas une nuit.

## Ce que l'abstract engage, et où c'est tenu

| Engagement | Tenu par |
|---|---|
| des **biais des systèmes RAG** | diapo 11 — c'était le trou du plan précédent |
| un **banc d'essai des stratégies** | diapos 8, 10, 12 |
| une **implémentation** | diapo 6 |

## Ce qui reste à décider ou à faire

- [ ] Rédiger les trois phrases mot pour mot.
- [ ] Préparer l'exemple travaillé `ContextRetriever` (dix minutes, sans run).
- [ ] **Diapo 12** : les chiffres post-BM25 ne sont pas dans ce dépôt — `benchmarks/` ne
      contient qu'une campagne, 2026-09-24. Les produire ou reformuler la diapo.
- [ ] Corrections déjà relevées dans le support : dénominateurs 58/59 contre 57 ; « McNemar
      p = 0,0066 sur 24 paires » confond les discordances avec n.
- [ ] Deux PNG encore en magenta : `demo/img/ollamassist-marketplace.png`,
      `demo/img/qr-feedback.png`.
- [ ] Première passe au chronomètre, puis appliquer la réserve de coupe si besoin.
