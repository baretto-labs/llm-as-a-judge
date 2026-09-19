# REX — trame de l'exposé (novembre 2026)

> Brouillon de structure, à faire évoluer. Durée visée : ~20 min + questions.
> Décision du 2026-09-19 : la colonne vertébrale est **la construction du jeu d'évaluation**,
> pas le fine-tuning. Le fine-tuning devient un résultat parmi d'autres, publié avec son
> intervalle, « non concluant » compris.

---

## Le message à faire passer

**Un jeu d'évaluation est un logiciel, et il a des bugs.** On ne les voit pas en le relisant :
on les voit en le mesurant, et certains ne se voient qu'avec un humain dans la boucle.

Trois messages secondaires, dans l'ordre d'importance :

1. Les métriques ne trouvent que ce qu'on pense à leur demander.
2. Un seuil choisi après avoir vu les données ne prouve rien — il faut un tirage de permutation.
3. Pré-enregistrer, c'est s'attacher les mains pendant qu'on est encore impartial.

---

## 1. Le problème (2 min)

- Comment mesurer objectivement la qualité d'un assistant de code ?
- LLM-as-a-judge : un modèle juge les sorties d'un autre.
- Contrainte posée d'emblée : **tout en local**. Pas de cloud, pas d'API, un portable M3 Pro 36 Go.
- La question pratique du public : *faut-il fine-tuner un juge local, ou un bon prompt suffit-il ?*

## 2. Ce qu'on a construit (3 min)

- 200 exemples, trois postures séparées par marqueur de tâche : `CODE_ANALYSIS` (monde ouvert),
  `RAG_CONTEXT_RELEVANCE` et `RAG_FAITHFULNESS` (monde fermé strict).
- Schéma unique : `<thinking>` puis `{checks, verdict, reason}`. **Contrôles avant verdict**, la
  génération étant séquentielle — le modèle pose les faits avant de trancher.
- Règle dure : **PASS ⟺ tous les contrôles vrais**. Pas de note graduée, pas de demi-mesure.
- Rubrique variable : un contrôle dédié apparaît quand la requête porte une contrainte explicite
  (`format_impose`, `aucune_dependance_externe`, `signature_publique_inchangee`…), pour empêcher
  le raccourci « marqueur de tâche → triplet figé ».
- Les 50 contextes RAG viennent d'extractions **réelles** (Lucene, Neo4j), gardées telles quelles —
  bruit, doublons, troncatures compris.

**Slide à soigner :** un exemple complet, lisible, avec son raisonnement et son verdict.

## 3. Le cœur : trois fois où le corpus nous a menti (8 min)

C'est le moteur narratif de l'exposé. Chaque fuite a la même forme : *un trait de surface prédit
le verdict, donc un juge peut réussir sans rien comprendre.*

### Fuite 1 — la verbosité, et la leçon qui coûte le plus cher

- Constat initial : la longueur de la réponse prédit le verdict à 75 %, pour une base de 53 %.
- Écart annoncé : **+8,8 écarts-types**. Spectaculaire. Et faux.
- L'erreur : la statistique avait été **maximisée sur 145 seuils et deux directions**, puis comparée
  à un taux de base. On ne compare pas un maximum à une moyenne.
- Le test de permutation remet les pendules à l'heure : **+1,3 σ, p = 0,132**. Du bruit.
- **Règle adoptée :** tout seuil choisi après coup se compare à un tirage de permutation du même
  maximum, jamais à un taux de base.

### Fuite 2 — la consigne facultative, et le correctif qui aggrave

- 17 requêtes portaient « si tu as le temps, dis un mot de X ». Les 17 étaient PASS. **17/17.**
- Déterministe, pas statistique : un juge n'a qu'à détecter la chaîne pour marquer 17/17.
- Correctif : ajouter la clause à des FAIL existants. Règle de surface ramenée à 57 %.
- **Sauf que le correctif plaçait la clause en paragraphe isolé**, là où les 17 d'origine la
  portaient en incise. Nouvelle règle : « paragraphe isolé ⇒ FAIL », **30 items sur 30**.
- Elle a traversé une régénération, une validation à 0 erreur, trois mesures et un commit.
- **Ce qui l'a révélée : un humain.** Le relecteur a répondu différemment sur un item, après avoir
  appliqué la règle correctement quatre fois. Ce n'était pas un relâchement : le stimulus était
  réellement différent.

> **La diapositive qui compte :** les métriques ont trouvé ce que je leur avais demandé de chercher.
> L'humain a trouvé ce que je ne savais pas chercher.

### Fuite 3 — la mise en forme, trouvée par méthode

- Après la fuite 2, écriture d'un **balayage systématique** : 22 traits de forme testés d'un coup,
  et le test porte sur le **maximum** comparé à un null de permutation du même maximum.
- Trouvaille : le nombre de titres `##` sépare les verdicts. Dans la strate non verbeuse,
  **0 PASS contre 24 FAIL** — aucune réponse juste ne portait de titre. Puis les tableaux : **0/18**.
- Cause : j'écrivais les réponses fausses en documents soignés — titres, tableaux, gras — et les
  justes en prose directe. Quatorze lots durant, sans m'en apercevoir.
- **Le point piquant :** la littérature 2026 documente le biais inverse — les juges notent *plus haut*
  les réponses à titres et puces. Mon corpus enseignait donc à contredire l'a priori du modèle de
  base, sur un signal de forme.

## 4. Ce qui protège (4 min)

- **Pré-enregistrement daté et signé avant tout entraînement** : une seule métrique principale, le
  test, la puissance connue d'avance (~15 points détectables, moins de 10 non concluant), et surtout
  **ce qui sera déclaré non concluant**. Formulations interdites listées noir sur blanc.
- **Relecture humaine à deux colonnes** : le premier passage alimente le κ, fatigue comprise ;
  l'arbitrage à froid fixe l'étiquette. Les deux ne se mélangent jamais.
- **κ = 0,901, IC 95 % [0,674 — 1,000]** sur 21 items. Et le chiffre qu'il faut donner en premier :
  l'accord **complet, contrôle par contrôle**, n'est que de **16/21 = 76 %**.
- **Tirages à graine déclarée**, et rejets documentés avec leur motif (un lot à 7 java sur 8 quand le
  vivier en compte 42 % ; un lot contenant des items déjà relus, dont le texte porte une mesure).
- Le corpus n'est jamais édité à la main : tout passe par les générateurs et `make regen`.

## 5. Les résultats (3 min)

- **Coût mesuré, pas estimé** : durée, mémoire de pointe, jetons vus, versions épinglées, machine.
  Les poids sont récupérés **hors chronomètre** — un téléchargement inclus fausserait le chiffre.
- Comparaison principale : **14B base + conventions dans l'invite** contre **14B fine-tuné**. Le
  concurrent sérieux du fine-tune n'est pas le modèle nu : lui refuser le règlement intérieur qu'on
  a appris à l'autre serait un homme de paille.
- L'intervalle est donné à chaque fois. Si zéro est dedans, **« non concluant »**, sans atténuation.
- 14B contre 32B : **exploratoire et sous-dimensionné**, annoncé comme tel.

## 6. Ce que je referais autrement (2 min)

- **150 exemples d'entraînement, quand le domaine appelle « petite échelle » un jeu de 6 000.**
  C'est la limite la plus honnête de l'étude.
- LoRA/SFT seul, quand la frontière est au SFT + GRPO et aux juges à raisonnement entraînés par RL.
- Un juge fine-tuné se dégrade sur des questions non vues — c'est documenté, et notre découpage par
  familles nous place précisément dans ce cas.
- **Audit par normalisation de format** : rejouer le juge sur des réponses dépouillées de leur
  Markdown, l'écart mesure la part de forme dans le score. À faire dès le départ, pas à la fin.

---

## Ce qu'il ne faut pas dire

- « Notre corpus ne contient pas de fuite. » Invérifiable, et probablement faux.
- « Tendance à l'amélioration », « non significatif mais encourageant ». Interdit par le
  pré-enregistrement.
- Les chiffres de blogs d'éditeurs, du type « un juge est d'accord avec l'humain 85 % du temps,
  plus que deux humains entre eux ». Aucune source primaire.

## Questions à préparer

- *Pourquoi pas GPT-4 / Gemini comme juge ?* → coût, reproductibilité (une API change sous vous, un
  adaptateur LoRA est figé), et confidentialité du code.
- *Votre vérité de référence a été écrite par un LLM — est-ce surprenant qu'un LLM y réussisse ?*
  → c'est la limite la plus sérieuse, d'où le κ humain et son intervalle.
- *Combien de temps au total ?* → chiffrer honnêtement, y compris les trois tours de correction.
