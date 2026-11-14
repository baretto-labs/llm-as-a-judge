# Plan — banc multi-juges et campagne RAG à trois bras

Écrit le **2026-10-18**, avant toute génération. Ce document est un **plan de travail**,
pas un pré-enregistrement : chaque phase reçoit le sien, écrit juste avant son lancement
avec sa preuve positive d'absence de résultats.

## 0. Constat bloquant, vérifié avant d'engager quoi que ce soit

**`gemma-4-12B` est inutilisable avec ce harnais.** Son `model_type` racine est
`gemma4_unified`, et le module `mlx_lm.models.gemma4_unified` n'existe **ni dans la
version 0.31.3 installée, ni dans la 0.32.2** (arbre GitHub `v0.32.2` inspecté). Les trois
builds publiés — `gemma-4-12B-4bit`, `-it-4bit`, `-it-qat-4bit` — portent tous ce type. Le
téléchargement a été arrêté à la vérification.

Conséquence : **l'échelle de taille ne peut pas venir de la famille Gemma.** Elle vient de
la famille Qwen, où deux paliers sont déjà mesurés. Gemma fournit le contrôle inter-familles
et l'axe MoE.

Repli **écarté** le 2026-10-18 : `gemma-4-e4b-it-4bit` (type racine `gemma4`, donc
chargeable, 42 couches, hidden 2560) aurait redonné un petit palier à Gemma, mais c'est un
modèle de la série « E », pas un dense frère du 31B. Il ouvrirait un troisième axe au lieu de
compléter une échelle, et une échelle bancale vaut moins qu'une échelle absente.

## 1. Les juges candidats

| juge | famille | architecture | poids 4 bits | état |
|---|---|---|---|---|
| Qwen2.5-Coder-14B | Qwen 2.5 | dense, 48 c. | 8,3 Go | **déjà mesuré** κ 0,479 |
| Qwen2.5-Coder-32B | Qwen 2.5 | dense, 64 c., h 5120 | 18,4 Go | **déjà mesuré** κ 0,801 |
| Mistral-Small-24B | Mistral | dense | 13,5 Go | **déjà mesuré** κ 0,349 |
| **Qwen3.8-27B** | Qwen 3.8 | dense, 64 c., h 5120 | 16,1 Go | à mesurer |
| **gemma-4-31b-it** | Gemma 4 | dense, 60 c., h 5376 | 18,4 Go | à mesurer |
| **gemma-4-26b-a4b-it** | Gemma 4 | **MoE**, 128 experts, ~4B actifs, 30 c., h 2816 | 15,3 Go | à mesurer |
| gemma-4 fine-tuné | Gemma 4 | QLoRA sur le corpus | — | phase 4 |

**Trois axes, séparés et nommés** — aucune ligne ne sera lue sur un axe qui n'est pas le sien :

1. **Taille, à famille et conventions constantes** : Qwen 14B → 32B. *Seul axe où la taille
   est isolée*, et le seul qui peut répondre à « faut-il une taille minimale ».
2. **Famille, à taille comparable (~30B dense)** : Qwen2.5-32B ↔ Qwen3.8-27B ↔ gemma-4-31b.
3. **Architecture** : gemma-4-26b-a4b (MoE, 4B actifs) contre les denses du même poids disque.
   **Ce n'est pas un point de taille** : son tronc dense est plus petit que celui d'un 12B.

## 2. Deux expériences, et une seule tranche la question

**A — Sur l'étalon.** Les 50 items de `data/golden/test.jsonl` portent des **étiquettes de
référence**. C'est le seul endroit où un juge peut avoir tort, donc le seul où « taille
minimale » a un sens. Harnais existant, inchangé : `scripts/bench_variant.sh`, 3 passes,
T = 0,2, mêmes conventions mot pour mot. **150 générations par juge.**

**B — Sur la campagne RAG.** Les 60 questions n'ont **aucune étiquette de référence**.
Comparer des juges là-dessus mesure leur **accord entre eux**, jamais leur justesse. C'est
un résultat réel — *la conclusion sur quel RAG gagne dépend du juge qu'on interroge* — mais
il ne validera aucune taille. Écrit ici pour qu'aucune lecture ne glisse de l'un à l'autre.

## 2 bis. Le générateur de la campagne RAG

**`qwen3.8:27b` sous Ollama**, et non `llama3.1`. Arbitré le 2026-10-18 : on ne mesure pas
un pipeline RAG avec un générateur plus ancien et plus petit que les juges qui le notent.
Déjà présent localement (18 Go, quantization **nvfp4**, 27,8 B, `architecture qwen3_5`).

**Famille.** Le générateur est alors de la famille de l'un des juges candidats
(Qwen3.8-27B). Ce n'est pas un accident à corriger : c'est **la mesure de l'auto-préférence**,
déclarée comme telle. Le juge principal de la campagne sera choisi sur l'étalon (phase 1) ;
si c'est Qwen3.8-27B, le fait qu'il note sa propre sortie sera dit, et la dispersion de la
phase 3 donnera l'écart avec les juges d'autres familles.

**C'est un modèle à raisonnement, et le raisonnement est actif par défaut** (`thinking`,
niveau `medium`, niveaux disponibles `false | low | medium | xhigh`). Sonde du 2026-10-18,
un appel sur une question triviale :

```
  champs du message : content, role, thinking
  thinking 545 caractères · content 355 · 208 jetons évalués
```

Second volet de la sonde, **à chaud, mais sous contention** (trois téléchargements en cours),
même question :

```
  thinking medium      1317 c de réflexion   3589 c de réponse   1303 jetons   73,7 s
  thinking désactivé      0 c                3225 c de réponse    846 jetons   54,3 s
```

Le raisonnement ajoute **~457 jetons et ~20 s par appel** pour une réponse à peine plus
longue. Extrapolé aux 240 générations : **~4 h 55 contre ~3 h 37**. Chiffres contendus, à
refaire au portail de coût — ils donnent l'ordre de grandeur, pas le budget.

Deux conséquences :

1. **Le raisonnement ne pollue pas la réponse** : Ollama le rend dans un champ `thinking`
   distinct de `content`. `RagAnswerer` lit donc une réponse propre — **à condition que
   LangChain4j lise bien `message.content`**, à vérifier dans le code avant la campagne.
2. **Le raisonnement reste ACTIF, au niveau `medium` par défaut.** Arbitré le 2026-10-18,
   avant toute génération. Motif : c'est le comportement par défaut du modèle, donc ce qu'un
   développeur obtient réellement. Coût accepté : **~4 h 55 pour les 240 générations** contre
   ~3 h 37 sans, à confirmer au portail de coût.

   *Un argument écarté, parce qu'il était faux* : « désactivé, c'est plus comparable à un
   générateur classique ». Aucune comparaison avec un générateur non raisonnant n'existe dans
   cette campagne — les trois bras partagent le même générateur, seul le moteur de
   récupération varie. Et couper le canal ne transforme pas un modèle entraîné à raisonner en
   modèle qui ne raisonne pas : cela supprime une sortie. Le seul arbitrage réel était coût
   contre représentativité.

   Deux conséquences, à tenir :
   - **Aucune dépendance à LangChain4j sur ce point.** Garder le défaut dispense d'avoir à
     émettre `think: false` depuis `OllamaChatModel`.
   - **Le juge de fidélité ne voit que `content`, jamais `thinking`.** C'est voulu : on juge
     la réponse. Mais cela rend `absence_invention` *plus* susceptible de se déclencher — si
     le modèle raisonne dans le canal caché et ne restitue qu'une conclusion, celle-ci peut
     s'appuyer sur sa mémoire paramétrique plutôt que sur le contexte fourni. Ce n'est pas un
     défaut du dispositif : c'est le phénomène même que démontre la diapositive 11, et il se
     dira ainsi.

## 3. Modifications du code, avant toute exécution

1. **Scinder la boucle de `RagQualityEvaluation`.** Elle génère et juge dans la même passe
   (lignes 154-175) : générateur et juge doivent donc être résidents ensemble. Avec un
   générateur à **18 Go** et un juge à 18,4 Go contre une limite *wired* de ~27 Go, c'est
   impossible — ce n'est plus une optimisation, c'est une condition d'exécution. Deux phases : **générer et persister les 240 réponses**, décharger, **puis
   juger**. La persistance rend aussi le rejugement par un second juge gratuit en génération.
2. ~~Vérifier que `RagAnswerer` lit `message.content`~~ — **fait le 2026-10-18, aucun
   changement nécessaire.** Vérifié dans le bytecode de `langchain4j-ollama-1.20.0`, la
   version réellement résolue sur le classpath : `InternalOllamaHelper.aiMessageFrom` mappe
   `Message.getContent()` sur `AiMessage.text()` et `Message.getThinking()` sur
   `AiMessage.thinking()`, deux champs distincts. `model.chat(String)` rend `text()`, donc la
   réponse seule. Le juge de fidélité ne peut pas voir la réflexion.
   *(Au passage : `CLAUDE.md` annonce LangChain4j 1.11.0, le `pom.xml` résout 1.20.0.)*
3. **Trois variantes dans `configs/variants.json`**, ports 8087 / 8088 / 8089, avec leur
   paire de comparaison déclarée. Le fichier n'est jamais recréé depuis un gabarit.
4. **Aucune modification des invites, des conventions ni du corpus.** La comparaison ne tient
   que si tout le reste est identique mot pour mot.

## 4. Portails à franchir avant de dépenser le calcul

Chacun produit une **preuve positive**, pas une absence d'erreur :

| portail | ce qu'on mesure | critère |
|---|---|---|
| chargement | chaque modèle se sert et répond | une complétion JSON valide par modèle |
| gabarit | le rôle `system` est bien pris | le suffixe de conventions se retrouve dans l'invite rendue |
| **raisonnement** | les trois gabarits mentionnent `thinking` | si le modèle émet son propre canal de réflexion, les jetons et la latence explosent et `parse` peut rompre — **à sonder avant le banc** |
| coût | 3 appels de chaque sorte, ajustement à deux points | budget par juge, comme le 2026-10-17 pour le few-shot |
| mémoire | pic résident sous la limite *wired* | relevé pendant la sonde |

## 5. Séquencement

| phase | contenu | générations |
|---|---|---|
| **1** | Étalon : Qwen3.8-27B, gemma-4-31b, gemma-4-26b-a4b | 3 × 150 = **450** |
| **2** | Campagne RAG, trois bras, **un seul juge** — le meilleur de la phase 1 | 240 réponses + 480 jugements |
| **3** | Dispersion inter-juges **sur la paire principale seulement** (vectoriel ↔ vectoriel+BM25), réponses déjà persistées | 240 jugements par juge ajouté |
| **4** | Fine-tune QLoRA d'un Gemma 4 (`gemma4_text` est supporté par mlx-lm), puis son passage à l'étalon | 1 entraînement + 150 |

La phase 2 ne démarre qu'après la phase 1 : **le juge de la campagne est choisi sur une
mesure**, comme le 2026-10-17 l'a imposé après coup pour Mistral-24B.

## 6. Ce que chaque résultat autorise à dire

- **Phase 1, axe taille** : si le palier Qwen 14B → 32B se retrouve dans une seconde famille,
  « il faut une taille minimale pour juger » devient défendable. Sinon, c'est un effet de
  modèle, et le support continue de ne pas l'affirmer (diapo 21, ligne 1289 du script).
- **Phase 1, axe MoE** : si le 26B-A4B tient le niveau des denses de même poids, la phrase
  est « un MoE à 4B actifs juge aussi bien », résultat d'**architecture**, utile parce qu'il
  tourne vite sur un portable. Jamais présenté comme un point de taille.
- **Phase 3** : la dispersion inter-juges se publie en effectifs. Si les juges divergent sur
  le vainqueur, c'est le résultat le plus parlant de toute la campagne.
- **Le talk ne dépend d'aucun de ces résultats.** Ils vont à l'article ; la diapo 21 gagne au
  plus une ligne, et toute matrice à l'écran doit remplacer quelque chose.

---

# 7. Plan d'exécution détaillé

Écrit le **2026-10-18**, avant la première génération des trois nouveaux juges.
Il répond à trois questions dans l'ordre : *quelles mesures*, *quels bancs*, *avec
quels modèles*.

## 7.1 Les mesures voulues, et sur quelle expérience chacune existe

Une mesure lue sur la mauvaise expérience ne veut rien dire. Le tableau porte donc
la colonne qui l'interdit.

| # | mesure | étalon (50 items étiquetés) | campagne RAG (60 questions, **sans étiquette**) |
|---|---|---|---|
| 1 | **κ de Cohen verdict ↔ étalon**, IC95 bootstrap 10 000 | **métrique principale** | n'existe pas : il n'y a pas d'étalon |
| 2 | justesse stricte (verdict **et** les 3 contrôles) | oui, sans pouvoir de décision à n = 50 | non |
| 3 | justesse **par contrôle** (les 3 marqueurs) | oui, descriptif | non |
| 4 | stabilité du verdict sur 3 passes, T = 0,2 | oui | non |
| 5 | format strict : part de JSON exploitable au premier appel | oui | oui |
| 6 | jetons de complétion et latence médiane | oui | oui |
| 7 | les **8 erreurs systématiques gelées** corrigées, en effectifs | oui, **jamais en pourcentage** | non |
| 8 | taux PASS de **pertinence du contexte** par bras | non | oui |
| 9 | taux PASS de **fidélité de la réponse** par bras | non | oui |
| 10 | **McNemar** sur les paires déclarées | non | oui |
| 11 | **accord inter-juges** sur des réponses identiques | non | oui, phase 3 |

La ligne 1 est la seule qui tranche « faut-il une taille minimale ». Les lignes 8
à 10 comparent des **stratégies de récupération**, pas des juges. La ligne 11
compare des juges **sans dire lequel a raison** : aucune réponse RAG n'a d'étiquette.

## 7.2 Ce que coûte un juge à raisonnement, mesuré avant de le dépenser

Sonde du 2026-10-18 sur `Qwen3.8-27B-4bit`, invite réelle de 923 jetons, un item
du golden set, `mlx_lm.server` :

```
  réflexion active   3052 jetons rendus   418,3 s   finish=stop   content présent
  réflexion coupée    631 jetons rendus   101,9 s   finish=stop   content présent
  (coupée par --chat-template-args '{"enable_thinking": false}')
```

**Le harnais sait lire les deux.** `extract_judgment` rend le JSON complet dans les
deux cas, et les deux rendent le même verdict correct sur cet item — à n = 1, cela
ne dit rien de la qualité, seulement que le format tient.

Un premier essai à `max_tokens=900` avait rendu un message **sans clef `content`**,
seulement `reasoning` : c'était la **troncature en pleine réflexion**, pas une
incompatibilité de format. La conséquence reste réelle, parce que
`benchmark_judges.py:228` lit `message["content"]` et que le `KeyError` est
**attrapé** ligne 236 : une troncature ne lèverait pas d'erreur, elle rendrait
trois tentatives et `text = ""`, soit 0 % de JSON exploitable **sans un seul
message d'alerte**. Même piège que l'adaptateur du 2026-09-24.

Deux réglages de service en découlent, à poser avant le premier item :

| réglage | défaut du harnais | requis |
|---|---|---|
| `--max-tokens` | 1024 | **1536** : 631 jetons observés réflexion coupée, 1024 laisse trop peu de marge |
| `--timeout` | 300 s | **300 s suffit** réflexion coupée (102 s), **insuffisant** réflexion active (418 s) |

Ni l'un ni l'autre ne touche aux items, aux invites ou à la métrique.

### Le format strict : 0 %, et ce n'est pas un défaut des nouveaux juges

Sonde du 2026-10-18 avec **les messages exacts que `messages_for` construit** (couple
`system` / `user` du corpus, conventions fondues dans le système) : les trois juges
échouent à `is_strict_format`. Ils enferment le JSON dans une clôture ```` ```json ````,
que `json.loads` refuse, et dérivent sur les clefs — `evaluations` pour le 26b-a4b,
contrôles aplatis à la racine pour le 31b, `reason` absent partout.

**Ce n'est pas discriminant** : `results/metrics.json` donne `strict_format_rate = 0.0`
pour **toutes** les variantes déjà publiées — 14B nue, 14B à conventions, 14B entraînée,
32B, Mistral-24B — et 0,04 pour la few-shot. La cause est dans l'invite : le message
système dit « rends ton verdict JSON » et **ne donne jamais le schéma**
`{checks, verdict, reason}`, qui n'a jamais été appris que par l'entraînement.
La mesure qui porte est `json_parse_rate` (1,0 pour les variantes à conventions),
pas le format strict. Aucun changement d'invite : le modifier ferait mesurer un
changement d'invite autant qu'un changement de juge.

À surveiller en revanche : la justesse **par contrôle** (mesure n° 3) suppose de
retrouver les contrôles sous la clef `checks`. Le 31b les aplatit et le 26b-a4b les
nomme `evaluations` — `criteria_accuracy` risque de rendre `nan`, comme il le fait
déjà pour `14B-baseline-conventions`. Mesure descriptive, sans pouvoir de décision :
on la rapporte manquante plutôt que de toucher à l'extraction.

### Pourquoi le *structured output* ne règle pas le format

Question posée le 2026-10-18 : LangChain4j sait contraindre le schéma, faut-il passer
par là ? **Non**, pour trois raisons vérifiées.

1. **Le serveur ne lit pas le champ.** `mlx_lm.server` 0.31.3 lit 25 champs du corps
   (`adapters`, `chat_template_kwargs`, `logit_bias`, `seed`, `stop`, `tools`,
   `top_k`…) ; `response_format` n'en fait pas partie, et il est absent de tout
   `mlx_lm/` hors d'un gabarit deepseek. Sonde du 2026-10-18 avec
   `response_format: {type: json_schema, strict: true}` sur gemma-4-26b-a4b :
   **HTTP 200, aucun avertissement, schéma sans effet** — sortie `{verdict, errors}`,
   une **troisième** forme encore différente. Brancher `strictJsonSchema(true)`
   donnerait cette sortie-là, avec la conviction en prime que le format est garanti.
   Le seul levier serveur est `tools`, injecté dans le gabarit puis reparsé :
   amorçage d'invite, pas décodage contraint.
2. **Ce n'est pas la moitié du projet concernée.** Le `strict_format_rate = 0.0` vient
   du banc étalon, `benchmark_judges.py`, qui parle en `urllib.request` direct :
   LangChain4j n'y intervient jamais. Les juges Java servent la campagne RAG.
3. **Ce serait un bris de protocole.** Les six variantes publiées ont été mesurées
   avec cette invite et ce décodage. Contraindre le schéma pour les trois nouveaux
   juges les rendrait incomparables aux six autres.

Le sujet reste légitime **comme expérience séparée et déclarée** — « forcer le schéma
change-t-il le κ ? » — sur un serveur capable de décodage contraint (vLLM, llama.cpp
et sa grammaire GBNF, ou mlx-lm via `outlines`). Chantier à part, pas un correctif
à glisser dans la phase 1.

### Le choix réflexion active / coupée, pour le rôle de juge

C'est une décision **distincte** de celle prise pour le générateur de la campagne
RAG : là-bas la réflexion est active, et elle le reste. Ici elle décide de la
faisabilité :

| | par appel | 150 générations | les trois juges |
|---|---|---|---|
| réflexion active | 418 s | **17,4 h** | **52 h** |
| réflexion coupée | 102 s | **4,25 h** | **12,8 h** |

Le banc se lance réflexion **coupée**, et le dit. Non parce qu'un juge sans
réflexion serait meilleur — rien ici ne le mesure — mais parce que 52 h sur un
portable n'est pas un banc, et qu'un écart de 4× sur le coût d'inférence est
lui-même un résultat à publier pour des développeurs. Si la décision est l'inverse,
c'est une nuit par juge et le `--timeout` passe à 900 s.

## 7.3 Les bancs à lancer, run par run

Toutes les commandes de l'étalon se lancent depuis `judge-finetune/`, celles du RAG
depuis la racine. **Un seul serveur à la fois** : 36 Go de machine, ~27 Go *wired*.

### Phase 0 — portails (aucun chiffre publié n'en sort)

| run | commande | preuve attendue |
|---|---|---|
| 0.a | sonde de chargement, un appel par modèle | une complétion par modèle, pic mémoire relevé |
| 0.b | sonde de canal | où atterrit la réponse pour chacun des trois |
| 0.c | sonde de coût, 3 appels, ajustement à deux points | budget par juge, comme le 2026-10-17 |

`Qwen3.8-27B` est franchi : 16,99 Go de pic en génération directe, 8,6 jetons/s en
décodage, 100 jetons/s en préremplissage. Restent gemma-4-31b et gemma-4-26b-a4b.

### Phase 1 — étalon, trois juges (la seule phase qui répond à la question de taille)

```sh
cd judge-finetune
./scripts/bench_variant.sh Qwen3.8-27B-conventions        # port 8087
./scripts/bench_variant.sh gemma-4-31b-conventions        # port 8088
./scripts/bench_variant.sh gemma-4-26b-a4b-conventions    # port 8089
make report
```

| | modèle servi | suffixe | items × passes |
|---|---|---|---|
| `Qwen3.8-27B-conventions` | `mlx-community/Qwen3.8-27B-4bit` | `configs/conventions.md` | 50 × 3 = **150** |
| `gemma-4-31b-conventions` | `mlx-community/gemma-4-31b-it-4bit` | idem, **mot pour mot** | 150 |
| `gemma-4-26b-a4b-conventions` | `mlx-community/gemma-4-26b-a4b-it-4bit` | idem | 150 |

**Sans `--format-normalise`, et réflexion coupée** (§ 7.2). À 102 s par appel mesurés,
150 générations coûtent **4,25 h par juge**, soit **12,8 h** pour les trois ; la passe
secondaire doublerait à 25 h, et la réflexion active la porterait à 52 h.
Même arbitrage que `bench-fewshot` le 2026-10-17 : contrainte pratique, pas
protocolaire, et elle se dit.

Lecture sur les **trois axes déjà déclarés**, jamais mélangés :

| axe | comparaison | ce qu'elle isole |
|---|---|---|
| taille | 14B ↔ 32B (déjà mesuré) **confirmé ou non** par les familles nouvelles | le seul axe propre |
| famille | Qwen2.5-32B ↔ Qwen3.8-27B ↔ gemma-4-31b, à ~30 Go denses | effet de famille à taille proche |
| architecture | gemma-4-26b-a4b (MoE, ~4B actifs) ↔ les denses | **jamais lu comme un palier de taille** |

### Phase 2 — campagne RAG, trois bras, un seul juge

Le juge est **le meilleur κ de la phase 1**, pas un choix a priori. Générateur :
`qwen3.8:27b` sur Ollama, *thinking* actif, constant sur les trois bras.

```sh
# 2.a — générer et PERSISTER les réponses (serveur MLX arrêté)
mvn test -Dtest=RagQualityEvaluation -Drag.scenario=knn-only \
         -Drag.answer.enabled=true -Drag.answer.model=qwen3.8:27b
mvn test -Dtest=RagQualityEvaluation -Drag.scenario=hybrid ...
mvn test -Dtest=RagQualityEvaluation -Drag.scenario=hybrid-graph ...

# 2.b — juger les réponses persistées (Ollama déchargé, serveur MLX démarré)
#        -Djmh.judge.model / -Djmh.answerjudge.model pointent le juge retenu
```

| bras | récupération | questions | réponses |
|---|---|---|---|
| vectoriel | `knn-only` | 60 | 60 |
| vectoriel + BM25 | `hybrid` | 60 | 60 |
| GraphRAG | `hybrid-graph` | 60 | 60 |

180 réponses, chacune jugée deux fois (pertinence du contexte, fidélité de la
réponse) = **360 jugements**. La scission 2.a / 2.b n'est pas une optimisation :
18 Go de générateur plus 18,4 Go de juge ne tiennent pas sous 27 Go.

### Phase 3 — dispersion inter-juges, sur la paire principale seulement

Les réponses de la phase 2 étant persistées, chaque juge ajouté ne coûte **aucune
génération**. Paire principale uniquement — vectoriel ↔ vectoriel + BM25 —, soit
120 réponses × 2 critères = 240 jugements par juge ajouté.

Ce qui en sort : **l'accord entre juges**, et surtout *les juges désignent-ils le
même bras vainqueur*. Pas une justesse : il n'y a pas d'étiquette.

### Phase 4 — fine-tune d'un Gemma 4

Nouvelle cible `train-gemma4` dans le `Makefile`, mêmes hyperparamètres que
`train-14b` et `train-32b` — c'est la condition d'une comparaison équitable. Puis
un passage à l'étalon, 150 générations, lu contre la version non entraînée du
**même** modèle.

## 7.4 Volume total

| phase | générations | heures estimées |
|---|---|---|
| 0 | ~12 appels | < 1 h |
| 1 | 450 | **12,8 h** (réflexion coupée ; 52 h si active) |
| 2 | 180 réponses + 360 jugements | ~5 h + **10,2 h** |
| 3 | 240 par juge ajouté | **6,8 h** par juge |
| 4 | 1 entraînement + 150 | une nuit + **4,25 h** |

Les estimations viennent des sondes du 2026-10-18 sur Qwen3.8-27B : 8,6 jetons/s en
décodage, 102 s par jugement réflexion coupée. Elles seront
remplacées par les mesures de la phase 0 pour les deux Gemma, dont le débit est
inconnu — le MoE devrait être nettement plus rapide, et c'est précisément une des
choses que l'étude a intérêt à publier.
