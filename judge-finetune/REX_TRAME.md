# REX — trame de l'exposé (novembre 2026)

> **Titre, abstract et objectifs : figés.** L'abstract a été retenu, il engage.
> **Plan arrêté le 2026-09-21**, avec quatre retouches appliquées le même jour — détaillées en fin
> de document, avec leur motif.
> Durée : **20 min**. Le décompte du plan tombe à 20 pile (3+4+4+6+3), sans marge : toute
> respiration se prend sur du contenu, pas sur du temps qui n'existe pas.

---

## Titre

> **RAGots et Hallucinations : votre chatbot passe devant le juge**

## Abstract — retenu, verbatim, ne pas retoucher

> Lorsqu'un assistant IA répond à côté de la plaque, le premier réflexe est d'accuser le modèle
> d'« halluciner ». Pourtant, la réponse dépend avant tout de la vue qu'on lui donne : le contexte. Si les
> informations récupérées par le RAG sont incomplètes ou bruitées, même le meilleur LLM ne peut que deviner
> la vérité. À travers le développement d'un système utilisant le RAG, cette session propose de sortir du
> « pifomètre » pour entrer dans l'ingénierie de la mesure. Nous passerons au banc d'essai les différentes
> stratégies de récupération d'information en utilisant un protocole de LLM-as-a-judge. En sortie, vous allez
> comprendre quelques biais des systèmes RAG, comprendre l'intérêt de mesurer la « pertinence » de vos
> chatbot et une implémentation de l'approche LLM-as-a-judge.

**Ce que l'abstract engage**, et qu'il faut tenir : (1) des **biais des systèmes RAG**, pas seulement des
biais de juge ; (2) un **banc d'essai des stratégies de récupération** ; (3) **une implémentation**.

## Objectifs

1. Pourquoi mesurer/quantifier la qualité des réponses de son chat.
2. Présenter l'approche LLM-as-a-judge.
3. Présenter une implémentation — *promesse de l'abstract retenu*.
4. Avantages et limitations.
5. REX.

---

# Plan — 20 min

## Introduction (3 min) — Pourquoi évaluer ses systèmes LLM / Agents ?

- **Le constat** : tests unitaires et métriques lexicales (BLEU/ROUGE) sont aveugles aux erreurs
  sémantiques.
- **Quand l'IA dérape en production.** Trois cas d'école :
  - **Air Canada** — hallucination RAG entraînant une responsabilité juridique. *Décision de tribunal :
    source primaire disponible, la citer.*
  - **NYC Bot** — conseils réglementaires illégaux, risque métier.
  - **Chevy Chatbot** — injection de prompt, perte de contrôle commercial.
  - ⚠️ Les deux derniers reposent sur de la presse. Vérifier et attribuer — la règle « pas de chiffre sans
    source primaire » vaut aussi pour les anecdotes.
- **REX OllamAssist** : pourquoi j'ai voulu évaluer mon assistant de code, et ma crainte initiale.

## Partie 1 (4 min) — La méthode : les questions à se poser avant de construire son juge

- **Que faut-il évaluer, et ne PAS évaluer ?** La règle du filtre déterministe (L0) : compilation, types
  JSON, linter — par du code classique, avant de consommer le moindre jeton.
- **Quand évaluer ?** Offline (CI/CD, non-régression) contre online (échantillonnage de production).
- **Quel format de verdict ?** Abandonner les échelles 1-10 vagues au profit du **binaire PASS/FAIL**.
  - Règle dure retenue : **PASS ⟺ tous les contrôles vrais.** Pas de demi-mesure.
  - Et **contrôles avant verdict** dans le JSON : la génération est séquentielle, le modèle pose les faits
    avant de trancher. L'ordre inverse le laisserait décider puis justifier.
- **REX** : mon filtre L0 en amont, et mon choix du binaire pour la suite de tests.
  - Moment d'honnêteté à assumer : **mon propre harnais RAG utilisait une échelle 0-10** — celle que je
    vous dis d'abandonner. La migration vers le binaire est en cours, et c'est un REX, pas une leçon.

## Partie 2 (4 min) — L'ingénierie des rubriques & la maîtrise des biais

- **Rédiger une rubrique fiable** : *reasoning-then-scoring* — le juge raisonne dans `<thinking>` avant de
  noter — et décomposition en **critères atomiques vrai/faux**.
- **L'approche modulaire** : séparer le moteur de jugement neutre des rubriques spécifiques au domaine. Un
  seul modèle entraîné à être *fiable* et à **coller à une grille** ; c'est la grille qui porte le domaine.
- **Les biais systématiques.** Distinguer nettement ce que **je mesure** de ce que **la littérature
  documente** :
  - **Verbosité — mesuré chez moi.** Taux de faux PASS sur défauts verbeux contre défauts concis.
  - **Position, auto-préférence — littérature.** Le biais de position est *mitigé* chez moi (mélange des
    extraits) mais **jamais quantifié**. L'auto-préférence n'est pas mesurée du tout. À citer comme connus,
    jamais comme mes résultats.
- **REX — une seule fuite, racontée en entier** : voir « La fuite retenue » plus bas.

## Partie 3 (6 min) — Le choix de l'infrastructure & l'implémentation (cas d'étude local)

- **Les options** : modèles frontier en cloud, modèles distillés, SLM fine-tunés en local — arbitrages
  coût, latence, confidentialité.
- **Constitution du jeu de données (principe LIMA)** : un golden set de 100–150 exemples d'experts
  rédigés à la main suffit à **enseigner la posture** de juge.
  - ⚠️ **Et voici ce que mes données ajoutent** : à 150 exemples, le surapprentissage est **reproductible**.
    Trois runs, même courbe. LIMA enseigne la posture, *et* le modèle commence à mémoriser avant la fin.
    Détail à donner : le minimum de validation tombe à l'itération 250, et mes points de contrôle sont à
    100/200/300/400 — **le meilleur modèle n'a jamais été sauvegardé.**
- **REX OllamAssist** :
  - Pourquoi un **SLM 14B en local sur Mac M3** : confidentialité du code, zéro coût de jetons.
  - La démarche **QLoRA via `mlx-lm`**, et le juge servi par **`mlx_lm.server`** sur une API
    OpenAI-compatible, interrogé depuis le harnais Java.
  - **Un seul modèle, plusieurs grilles d'évaluation** : on entraîne le juge à être fiable et à coller à
    une grille ; la grille évalue le domaine.
  - Précision à ne pas sur-vendre : **le RAG lui-même tourne toujours sur Ollama** — génération,
    embeddings, reranker. Le juge passe par MLX, le système jugé reste sur Ollama. Les deux sont locaux,
    la promesse « tout en local » tient — mais la démo fait tourner les deux **plus** Neo4j embarqué sur
    36 Go. À répéter avant le jour J.
- **Le banc d'essai** : Lucene contre GraphRAG-Neo4j, jugés par le même juge, sur les mêmes questions.

### Le résultat, mesuré le 2026-09-24

Deux scénarios, 60 questions sur la codebase réelle, juge 14B fine-tuné au checkpoint 200, mélange
du contexte **graîné par la question** — donc reproductible. Une heure par scénario.

**Le contrôle d'équité d'abord**, parce qu'il valide tout le reste. Lucene est configuré à
l'identique dans les deux scénarios : son taux **doit** être le même. Il l'est, au chiffre près —
**48,3 %**, `hintCoverage` **0,697**, 2 invalides, dans les deux. La mesure est reproductible, et ce
n'est pas un acquis : les runs de la veille, au mélange non graîné, faisaient bouger ce même bras de
55,9 % à 43,3 %.

| | Lucene | Neo4j |
|---|---|---|
| **Justesse (taux de PASS)** | **48,3 %** | **23,7 %** |
| `hintCoverage` — **sans LLM** | **0,697** | 0,596 |
| Contexte jugé insuffisant | 39,7 % | **66,1 %** |
| Cohérence du juge | 100 % | 98,3 % |

**McNemar exact bilatéral : p = 0,0066 sur 24 paires discordantes** — Lucene seul juste sur 19,
Neo4j seul juste sur 5. Seules les paires discordantes portent de l'information, et leur nombre est
le vrai déterminant de la puissance à cet effectif : il est donné avec le p, jamais sans.

**Le chiffre qui donne du poids au reste :** `hintCoverage` classe les deux stratégies dans le même
ordre, et cette métrique **ne passe pas par le juge** — elle compte des identifiants attendus dans le
contexte récupéré. La conclusion ne repose donc pas sur l'instrument seul. C'est une validation
croisée qui ne coûte rien, et elle concorde.

**L'attribution, tranchée par le contrôle d'équité :**

| scénario | Neo4j | écart | p | discordantes |
|---|---|---|---|---|
| `hybrid|hybrid-graph` — avec expansion K-hop | 22,0 % | +26,3 pts | 0,0041 | 25 |
| `hybrid|hybrid` — **même preset des deux côtés** | 23,7 % | +24,6 pts | 0,0066 | 24 |

Retirer l'expansion de graphe ne fait gagner à Neo4j que **1,7 point, soit une question sur 59** —
du bruit. **L'écart de ~25 points n'est donc pas imputable à la traversée de graphe : il vient du
moteur de récupération lui-même.** C'est une nuance qui *affine* l'hypothèse de départ au lieu de la
confirmer : ce n'est pas « le graphe est mal implémenté », c'est le pipeline Neo4j qui rappelle moins.

**Et le mécanisme est lisible dans les contrôles atomiques** : le contexte Neo4j est jugé
**insuffisant dans 66 % des cas** contre 39,7 % pour Lucene. Ce n'est pas un problème de bruit mal
maîtrisé, c'est un **défaut de rappel** — le moteur ne rapporte pas assez de matière. C'est
exactement ce que les critères atomiques apportent sur une note globale : ils disent *lequel* échoue.

**Par strate, et il faut être honnête sur ce qui conclut :**

| strate | Lucene | Neo4j | p | discordantes |
|---|---|---|---|---|
| `LOCAL` | 31,6 % | 20,0 % | 0,453 — **non concluant** | 7 |
| `STRUCTURAL` | 63,2 % | 42,1 % | 0,508 — **non concluant** | 9 |
| `CROSS_MODULE` | **50,0 %** | **10,0 %** | **0,0078** | 8 |

**Un seul écart tient par strate : `CROSS_MODULE`**, et il est identique dans les deux scénarios.
Les deux autres ne concluent pas — 7 à 10 paires discordantes ne suffisent pas, et c'est la limite de
puissance annoncée d'avance, pas une surprise.

> **Réserve de portée.** Ces chiffres valent pour *cette* implémentation Neo4j, à ces presets, sur
> *cette* codebase. Dire « GraphRAG fait moins bien » serait un abus ; « ce pipeline-ci rappelle moins
> que Lucene sur ce corpus » est ce que la mesure soutient.
>
> **Et la réserve sur l'instrument, maintenant chiffrée** (banc du juge du 2026-09-24) : ce juge
> s'accorde à l'étalon humain à **κ = 0,44** et ne rend le même verdict que **58 %** du temps sur trois
> passes à T = 0,2. Un écart de 25 points survit largement à ce bruit — c'est pourquoi la conclusion
> tient — mais **les écarts par strate de 7 à 10 paires discordantes, non. C'est une deuxième raison,
> indépendante de l'effectif, de ne rien conclure sur `LOCAL` et `STRUCTURAL`.** Le garde-fou reste
> `hintCoverage`, qui classe les deux stratégies dans le même ordre **sans passer par le juge**.

## Partie 4 & Conclusion (3 min) — Calibration & triage humain dans la boucle

- **Mesurer la fiabilité du juge — et distinguer deux κ qu'on confond tout le temps :**

  | κ | ce qu'il mesure | état |
  |---|---|---|
  | **κ du corpus** | accord entre l'annotateur humain et les étiquettes de référence | **mesuré : 0,880, IC 95 % [0,720 — 1,000]**, accord de verdict 47/50 sur les 50 items |
  | **κ du juge** | accord entre le juge et l'étalon | **mesuré le 2026-09-24 : 0,44** IC 95 % [0,27 — 0,60] pour le fine-tuné, **0,48** [0,29 — 0,66] pour la baseline à conventions |

  Ne pas présenter le premier comme le second. Le premier dit *« mon étalon est-il fiable ? »*, le second
  *« mon juge est-il aligné ? »*. Et l'écart entre les deux est la diapositive : **0,880 entre humains,
  0,44 pour le juge.** Le plafond n'est pas le modèle, c'est ce que le corpus enseigne.

- **Le verdict du banc du juge — et la branche « non concluant » qui était écrite d'avance.** Voir le
  détail en Matière : à effectif égal, le fine-tuning **n'améliore pas la justesse** (76,0 % contre
  76,0 %, p = 1,0000) mais achète le **format auditable** (0 % → 100 %). C'est le moment où le
  pré-enregistrement paie : la conclusion « non concluant » était une issue déclarée, pas un échec.

- **Le chiffre qui dit l'inverse, et qu'il faut donner juste après** : **17 items sur 50 portent un
  désaccord sur au moins un contrôle, dont 15 que le verdict absorbe.** Le verdict est une conjonction :
  dès qu'un contrôle échoue des deux côtés, un désaccord sur un autre devient invisible.
  **Le verdict est reproductible ; les raisons le sont beaucoup moins** — or le juge est entraîné sur les
  raisons. C'est un plafond sur ce que le fine-tuning peut apprendre, une propriété du corpus, pas un
  défaut de la méthode.

- **Et un κ bas qui ne veut pas dire ce qu'on croit** : le contrôle le plus fréquent, `respect_consignes`,
  tombe à **κ = 0,386 pour 78 % d'accord brut**. Marges très déséquilibrées. Publier le κ seul sous-estime
  l'accord, publier les 78 % seuls le surestime. Les deux vont ensemble, avec les marges.

- **Une asymétrie qui n'est pas du bruit** : **16 désaccords sur 22 vont dans le même sens**, l'annotateur
  humain plus sévère que l'étiquette rédigée par le LLM. Une vérité de référence écrite par un LLM puis
  relue est **plus indulgente** que ce que l'humain aurait produit seul.

- **Le triage par niveau de confiance** : automatiser les décisions nettes, router les cas ambigus vers
  l'humain.
  - Le signal de confiance existe déjà dans le harnais : **la stabilité du verdict sur plusieurs passes**.
    Un item instable est un item à router. Le rattacher à cette mesure, ne pas l'inventer.

- **Takeaways** : les 3 étapes clés pour concevoir son propre évaluateur dès demain.

---

# Matière

## Les chiffres, mesurés et non estimés

| | |
|---|---|
| Durée d'entraînement | **90 min 58 s** (13,65 s/itération) — dont 76 min d'itérations et 14,7 min de validation |
| Pic mémoire | **11,32 Go** sur 36 Go |
| Itérations | 400, batch 1 |
| Jetons entraînés | 169 513 |
| Adaptateur | **43,8 Mo** — 11,5 M paramètres sur 14,77 Md, soit **0,078 %** |
| Coût en jetons facturés | **zéro** |

**91 minutes sur un portable.** C'est l'argument « le fine-tuning n'est pas si coûteux », mesuré.

Et une correction à raconter : j'ai d'abord publié **76 minutes**. La méthode de substitution déclarée ne
dérivait la durée que des itérations d'entraînement et **excluait les 9 passes de validation**, soit
14,7 minutes. L'utilisateur attend 91 minutes, pas 76. Corriger rendait le chiffre **moins** flatteur —
c'est précisément ce qui rend la correction crédible.

⚠️ **À dire, parce que c'est un REX** : ce relevé était **faux** au premier jet. L'horloge annonçait
690 minutes — un facteur **9,1** — la machine ayant été suspendue pendant l'entraînement. Pour la
troisième fois, et **rien ne l'a signalé** : le script n'a aucune détection, il écrit la valeur brute dans
le champ qui fait foi. La correction est manuelle, comme les deux précédentes.

**Courbe de validation** — troisième reproduction quasi identique :

```
1: 1,816 → 50: 1,259 → 100: 1,164 → 150: 1,131 → 200: 1,124
→ 250: 1,103  ← minimum
→ 300: 1,200 → 350: 1,199 → 400: 1,183
```

## Le banc du juge — mesuré le 2026-09-24, 450 générations

Trois variantes, 50 items du golden set, 3 passes, T = 0,2, bootstrap 10 000. Un serveur à la fois sur
le M3 Pro. `14B-baseline-nu` et `14B-baseline-conventions` ne diffèrent **que** par un suffixe d'invite :
les quatre conventions de PROTOCOLE.md, reprises mot pour mot.

| | κ du juge | Justesse | JSON exploitable | Format strict | Stabilité du verdict |
|---|---|---|---|---|---|
| **Invite nue** | 0,00 | 0 % | **0 %** | 0 % | 0 % |
| **+ conventions** | **0,48** [0,29 — 0,66] | **76,0 %** | 100 % | 0 % | **76 %** |
| **Fine-tuné (ckpt 200)** | 0,44 [0,27 — 0,60] | **76,0 %** | 100 % | **100 %** | 58 % |

**Trois résultats, et aucun n'est celui que j'attendais.**

**1. L'invite vaut plus que le modèle.** L'invite nue ne rend **aucun JSON exploitable** : 0 sur 150. Le
seul ajout des quatre conventions fait passer la justesse de 0 à 76 %, soit **+76 points**, McNemar
p = 0,0000 sur 38 paires discordantes. Avant de fine-tuner quoi que ce soit, écrire ses conventions.

**2. La comparaison principale est non concluante — et c'était une issue déclarée.**

> `14B-baseline-conventions` **76,0 %** contre `14B-finetuned` **76,0 %**.
> Δ = **+0,0 %**, IC 95 % apparié **[-14,0 %, +14,0 %]**, McNemar exact **p = 1,0000** sur
> **12 paires discordantes** — 6 d'un côté, 6 de l'autre. Symétrie parfaite.

À n = 50, l'étude ne pouvait pas détecter moins de ~15 points d'écart, et **cette limite était écrite en
§5 avant les résultats**. La branche « non concluant » était pré-enregistrée avec sa formulation. C'est
exactement ce à quoi sert un pré-enregistrement : pouvoir dire « je ne sais pas » sans que ce soit un
échec, et sans céder à la tentation de re-découper les données jusqu'à trouver un p < 0,05.

**3. Ce que le fine-tuning a réellement acheté : le format, pas le jugement.** La baseline à conventions
rend un verdict valide mais des **clés plates** — 0 objet `checks` sur 150 générations. Le fine-tuné rend
le schéma imbriqué **150 fois sur 150**. C'est la seule variante sur laquelle on puisse mesurer un accord
**par contrôle** : `validation_entree` 100 %, `contexte_pertinent` 89 %, `absence_invention` 83 %, et à
l'autre bout `format_impose` 33 %, `bruit_maitrise` 50 %. Sur les deux autres variantes, ces treize
colonnes sont `n/a` — il n'y a rien à comparer.

**Et le contre-chiffre, à donner dans la même diapositive** : la stabilité du verdict **baisse**, 76 % → 58 %,
et la résistance au biais de verbosité ne bouge pas (46 % de faux PASS des deux côtés). Le fine-tuning
a acheté l'**auditabilité**, pas la justesse ni la constance. Aucune des trois variantes ne passe le
filtre de recevabilité opérationnelle — à dire aussi.

> **La diapositive qui compte :** j'ai passé 91 minutes à fine-tuner un juge pour découvrir que le gain
> tient dans quatre phrases d'invite, et que le fine-tuning sert à autre chose que ce que je croyais.

### ⚠️ Le cinquième `BUILD SUCCESS` sur du vide — à raconter, c'est le fil du REX

Le premier rapport de ce banc annonçait, tableaux et intervalles à l'appui : **« le fine-tuning dégrade
la justesse de -76,0 %, IC 95 % [-88 %, -64 %], McNemar p = 0,0000 »**. Publiable tel quel. Faux de bout
en bout.

`mlx_lm.server` avait reçu `--adapter-path adapters/14b-judge-ckpt200` et **répondait avec le modèle de
base** : aucune erreur, aucun avertissement, 150 réponses plausibles, deux heures de calcul. Ce qui a mis
la puce à l'oreille n'est pas une métrique, c'est un **détail de style** — des clés plates dans une
clôture markdown, là où les 135 cibles d'entraînement portent toutes un JSON nu et imbriqué.

La preuve a tenu en un test : le même adaptateur, chargé en processus par `mlx_lm.load(adapter_path=...)`,
sur le même item, avec le même template, rend le format d'entraînement exact. L'adaptateur était bon ;
la plomberie ne l'était pas. Pire : **j'avais déjà corrigé ce bug côté Java** en passant l'adaptateur dans
le corps de la requête, sans reporter la correction côté Python.

**Le compte, pour ce seul projet : cinq mesures rendues sur du vide, toutes avec un `BUILD SUCCESS`.**
`-D` non transmis par surefire, adaptateur arrivant en chaîne vide, `pgrep` matchant son propre script,
mélange non graîné, et celle-ci. *Le point du talk : un banc d'évaluation qui ne sait pas prouver qu'il a
mesuré la bonne chose ne mesure rien — et il le fait silencieusement.* Correctif retenu : `sonde_adaptateur()`
exige une **preuve positive** sur un appel avant d'en dépenser cent cinquante, et les générations écartées
sont **conservées** sous `results/runs-invalides/` avec leur notice, pas supprimées.

## La fuite retenue — le correctif qui aggrave

*Une seule fuite est racontée, en entier. Les deux autres sont en note plus bas, permutables.*

- 17 requêtes portaient « si tu as le temps, dis un mot de X ». **Les 17 étaient PASS. 17/17.**
- Déterministe, pas statistique : un juge n'a qu'à détecter la chaîne pour marquer 17 sur 17.
- Correctif : ajouter la clause à des FAIL existants. Règle de surface ramenée à 57 %.
- **Sauf que le correctif plaçait la clause en paragraphe isolé**, là où les 17 d'origine la portaient en
  incise. Nouvelle règle apprise : « paragraphe isolé ⇒ FAIL », **30 items sur 30**.
- Elle a traversé **une régénération, une validation à 0 erreur, trois mesures et un commit**.
- **Ce qui l'a révélée : un humain.** Le relecteur a répondu différemment sur un item, après avoir appliqué
  la règle correctement quatre fois. Ce n'était pas un relâchement — le stimulus était réellement différent.

> **La diapositive qui compte :** les métriques ont trouvé ce que je leur avais demandé de chercher.
> L'humain a trouvé ce que je ne savais pas chercher.

**Les deux autres fuites, coupées faute de temps** — à permuter si l'audience est plus statisticienne :

- **Verbosité** : longueur prédisant le verdict à 75 % pour une base de 53 %, annoncé **+8,8 σ**.
  Spectaculaire et faux : la statistique avait été maximisée sur 145 seuils et deux directions, puis
  comparée à un taux de base. Test de permutation : **+1,3 σ, p = 0,132**. Du bruit.
  *Règle acquise : tout seuil choisi après coup se compare à un tirage de permutation du même maximum.*
- **Mise en forme** : balayage systématique de 22 traits. Le nombre de titres `##` sépare les verdicts —
  **0 PASS contre 24 FAIL** chez les non verbeux, puis les tableaux à **0/18**. J'écrivais les réponses
  fausses en documents soignés et les justes en prose directe, quatorze lots durant.
  *Le point piquant : la littérature 2026 documente le biais inverse — les juges notent plus haut les
  réponses à titres. Mon corpus enseignait à contredire l'a priori du modèle de base.*

## Les biais RAG, sur données réelles — la promesse de l'abstract

Trois cas tirés d'**extractions réelles** sur ma propre codebase, gardées telles quelles :

1. **Le quasi-homonyme.** Requête sur `OllamaService` ; le moteur rend `OllamaSettings` — même forme, classe
   voisine, interface sans rapport. Le contexte *ressemble* à une réponse et invite à répondre faux.
2. **Les corps tronqués.** Dix extraits, aucun corps de méthode, pour une question en « comment ». Les noms
   annoncent une intention, ils ne livrent pas la mécanique.
3. **Le vrai mais non étayé.** Une réponse exacte dans la codebase réelle, mais absente du contexte fourni.
   **Elle doit tomber** — c'est le test décisif de la posture en monde fermé. L'accepter au motif qu'elle
   est vraie reviendrait à valider, sur un autre dossier, une hallucination indiscernable.

## Ce qu'il ne faut pas dire

- « Notre corpus ne contient pas de fuite. » Invérifiable, et probablement faux.
- « Tendance à l'amélioration », « non significatif mais encourageant ». Interdit par le pré-enregistrement.
- Les chiffres de blogs d'éditeurs, du type « un juge est d'accord avec l'humain 85 % du temps, plus que
  deux humains entre eux ». Aucune source primaire.
- Présenter un résultat de la littérature comme une mesure maison.

## Questions à préparer

- *Pourquoi pas GPT-4 / Gemini comme juge ?* → coût, reproductibilité (une API change sous vous, un
  adaptateur LoRA est figé), confidentialité du code.
- *Votre vérité de référence a été écrite par un LLM — est-ce surprenant qu'un LLM y réussisse ?*
  → c'est la limite la plus sérieuse, d'où le κ humain et son intervalle.
- *Combien de temps au total ?* → chiffrer honnêtement, y compris les trois tours de correction.
- *Votre benchmark conclut sur combien de questions ?* → ~30, en design apparié. Ne détecte que de gros
  écarts, et la compétence du juge sur cette tâche précise repose sur **6 items** du golden set. À dire
  avant le résultat, pas après.

---

## Fil conducteur, formulé par l'utilisateur le 2026-09-20

> **« Même le harnais d'évaluation ne doit pas être construit sans observation ni réflexion. »**

| ce qui devait mesurer | ce qui n'allait pas | ce qui l'a révélé |
|---|---|---|
| le corpus | trois fuites de surface, dont une déterministe | un test de permutation, puis un humain, puis un balayage |
| `sweep_surface.py`, écrit pour trouver les fuites | deux bugs : direction non rapportée, coupes dans les ex æquo | relecture du code au moment d'interpréter un chiffre absurde |
| le relevé de coût | durée et mémoire fausses, machine suspendue — **trois fois**, jamais détecté | une comparaison avec le débit relevé dans le journal |
| le protocole de relecture | convention d'attribution ambiguë | suspension de la mesure plutôt qu'accumulation |
| le correctif de la fuite n°2 | il a créé une fuite pire — 30/30 au lieu de 17/17 | le désaccord d'un relecteur humain, après douze mesures muettes |
| le parseur du κ | rendait **42 items sur 50** en silence, et manquait les 3 désaccords d'un contrôle | des recoupements contre des décomptes notés pendant la relecture |
| le banc d'essai RAG | **trois runs consécutifs invalides**, trois causes distinctes : corpus synthétique indexé au lieu de la vraie codebase, adaptateur perdu sur une propriété vide donc juge de base, et jugement étranglé par l'échéance de JMH. **Les trois ont rendu `BUILD SUCCESS`** | une sonde du contexte récupéré avant de lire les chiffres — `hintCoverage` à 0,000 partout ne pouvait pas être un résultat |
| la durée publiée du fine-tuning | 76 min annoncées, **91 réelles** : la méthode de substitution excluait les 9 passes de validation | un recoupement du débit relevé au journal contre l'horloge |
| le tirage « déterministe » | ordre des lignes dépendant du processus : adaptateurs non rejouables à graine égale | un contrôle d'empreintes avant l'entraînement final |
| **deux documents normatifs divergents** | le plus ancien restait exécutable, et le code le suivait fidèlement | la confrontation du code au protocole écrit **avant** lui |

**Aucun instrument de ce projet n'a été juste du premier coup.** Chacun a été corrigé parce qu'on a
regardé — jamais parce qu'une métrique a protesté. **C'est la diapositive de conclusion.**

---

## Les quatre retouches du 2026-09-21

1. **Ollama retiré de la Partie 3.** L'export GGUF est bloqué : `mlx_lm.fuse` refuse `qwen2` (seuls
   `llama`/`mixtral`/`mistral`) et refuse les modèles quantifiés. Le contournement par llama.cpp
   produirait un **artefact différent** de celui mesuré. Le juge est servi par `mlx_lm.server` en
   OpenAI-compatible ; le RAG reste sur Ollama, et c'est dit.
2. **Les deux κ séparés en Partie 4.** Le κ mesuré qualifie le **corpus**, pas le juge. Le κ du juge
   n'existera qu'après le benchmark. Les confondre serait annoncer un alignement qu'on n'a pas mesuré.
3. **LIMA assorti de sa réserve.** Le surapprentissage à 150 exemples est reproductible sur trois runs, et
   le minimum de validation tombe là où aucun point de contrôle n'est écrit.
4. **Une fuite au lieu de trois.** Les 4 minutes de la Partie 2 ne peuvent pas porter trois fuites *plus*
   l'ingénierie des rubriques. Le correctif qui aggrave est retenu : c'est celui qui porte le fil
   conducteur. Les deux autres restent rédigées ci-dessus, permutables sans recherche.

## Ce qui reste à produire

Au 2026-09-24 au soir, **toutes les mesures du plan sont faites**. Le juge Java binaire, le banc RAG, le
contrôle d'équité et le banc du juge sont mesurés et reproductibles (Partie 3 et Matière).

Réglés depuis la version précédente de cette trame :

- ~~Le κ du juge~~ → **0,44** [0,27 — 0,60] fine-tuné, **0,48** [0,29 — 0,66] baseline à conventions.
- ~~La comparaison `14B-finetuned` contre `14B-baseline-conventions`~~ → **non concluante**, Δ = 0,0 %,
  p = 1,0000 sur 12 paires discordantes, dans la branche pré-enregistrée. Le fine-tuning achète le
  format (0 % → 100 %), pas la justesse.
- ~~Le contrôle d'équité `hybrid|hybrid`~~ → **témoin invariant à la décimale** sur les trois strates,
  l'écart RAG est imputable au moteur et non au parcours de graphe.

Restent, et il faut les **déclarer** plutôt que les taire :

- **Le 32B n'est pas entraîné** — `make train-32b` n'a jamais été lancé, et sa faisabilité en QLoRA sur
  36 Go reste ouverte. Les deux lignes `32B-*` de `configs/variants.json` restent gelées, sans données.
- **La passe « format normalisé » n'a pas été jouée** (`BENCH_ARGS=`), pour tenir le temps de calcul de
  la soirée. Elle mesurerait la part de l'écart imputable à la mise en forme plutôt qu'au fond. À dire
  comme une limite, pas comme un oubli.
- **Aucune des trois variantes ne passe la recevabilité opérationnelle** : au mieux 76 % de stabilité de
  verdict pour un seuil à 95 %. Le juge mesuré ici **n'est pas prêt pour la production**, et c'est une
  conclusion en soi.
