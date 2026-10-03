---
# ---------------------------------------------------------------------------
# Support de la conférence de novembre 2026. 20 min.
#
# Les chiffres font foi dans judge-finetune/REX_TRAME.md ; ce fichier en est la
# mise en scène. Les commentaires HTML sous chaque diapositive sont les NOTES
# ORATEUR : ce qui se dit, pas ce qui s'affiche. Les lignes ⚠ sont des garde-fous
# factuels.
#
# ATTENTION : demo/SLIDES.md est un AUTRE deck, celui du talk précédent. Il note
# la qualité sur 10 avec le juge gradué abandonné le 2026-09-13. N'y reprendre
# aucun chiffre — sauf la diapositive « Ce que j'ai présenté il y a quelques
# mois », qui le cite exprès.
#
# RENDU (marp-cli via docker, voir demo/SUPPORT.md) :
#   docker run --rm -v "$(pwd)/demo:/home/marp/app" marpteam/marp-cli \
#     CONFERENCE-2026.md --html --output CONFERENCE-2026.html
#
# STYLE — règle arrêtée le 2026-09-30, gouverne toute réécriture :
#   · rien de pompeux, phrases courtes, une idée par phrase
#   · une MÉTAPHORE explique, un exemple OLLAMASSIST illustre
#   · famille de métaphores unique : le CORRECTEUR DE COPIES et son barème
#       la grille = le barème · κ = deux correcteurs sur la même copie
#       accord dû au hasard = deux correcteurs qui recalent tout le monde
#       erreurs ratées = un correcteur indulgent
#       verdict instable = deux notes pour la même copie
#       renvoi à l'humain = la double correction
#       filtre L0 = la copie hors-sujet, écartée avant lecture
#   · les chiffres exacts, σ et intervalles descendent dans les notes orateur
#
# Ces lignes sont dans le front-matter et non en commentaire HTML : un
# commentaire HTML placé avant la première diapositive devient sa note orateur.
# ---------------------------------------------------------------------------
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
style: |
  section {
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 1.35rem;
    color: #1a1a1a;
    padding: 70px;
  }
  h1 { font-size: 2.2rem; font-weight: 600; }
  h2 { font-size: 1.7rem; font-weight: 600; margin-bottom: 0.8em; }
  ul { line-height: 1.8; }
  strong { font-weight: 700; }
  table { font-size: 0.95rem; }
  .ref { font-size: 0.85rem; color: #666; }
  section.title { justify-content: center; }
  .carte { display: flex; gap: 2.5rem; align-items: flex-start; }
  .carte > .texte { flex: 1; min-width: 0; }
  .carte img { border: 1px solid #e5e5e5; border-radius: 6px; flex: none; }
  section.dense { font-size: 1.2rem; }
  section.dense h2 { font-size: 1.5rem; margin-bottom: 0.5em; }
  section.dense ul { line-height: 1.45; }
  section.dense li { margin-bottom: 0.55em; }
  .deux { display: grid; grid-template-columns: 1fr 1fr; gap: 2.2rem; }
---

<!-- _class: title -->

# RAGots et Hallucinations

## votre chatbot passe devant le juge

Mehdi Elketroussi
Novembre 2026

<!--
Lire le titre à voix haute dès la première seconde : « RAGots » est un jeu de
mots qui se perd à l'écrit, la moitié de la salle ne le verra pas.

« Passe devant le juge » porte les deux sens du talk : le juge automatique qu'on
construit, et le tribunal.
-->

---

## Air Canada, 2024

Le chatbot du site invente une politique de tarif deuil.

Air Canada plaide que le chatbot est
**« une entité juridique distincte, responsable de ses propres actes »**.

Le tribunal :

> « This is a remarkable submission. While a chatbot has an interactive
> component, it is still just a part of Air Canada's website. »

**650,88 $ CA** — négligence dans la présentation d'informations

<span class="ref">Moffatt v. Air Canada, 2024 BCCRT 149</span>

<!--
Novembre 2022. Jake Moffatt réserve un vol pour les funérailles de sa
grand-mère. Le chatbot lui indique qu'il peut demander le tarif deuil après le
voyage. La politique réelle exige de le demander avant. Il paie le plein tarif
et se retourne contre la compagnie.

Le montant est dérisoire, et c'est ce qui rend la décision intéressante : ce
n'est pas le préjudice qui compte, c'est le principe de responsabilité posé.
Une entreprise répond de ce que son chatbot affirme.

Traduire la citation à l'oral en la commentant — elle reste en anglais à l'écran
parce que c'est l'original, donc vérifiable.

⚠ Vérifié sur la décision : membre Christopher C. Rivers, 14 février 2024,
650,88 $ CA. NE PAS citer de mémoire le délai annoncé par le chatbot (90 jours
selon des sources secondaires) ni le total avec intérêts et frais : non vérifiés
sur pièce, donc volontairement absents de l'écran.
-->

---

<!-- _class: dense -->

## Et ce n'est pas un cas isolé

<div class="deux">
<div>

**DOCUMENTÉ** <span class="ref">— décision de justice ou document public</span>

- **Mata v. Avianca, 2023** — un avocat dépose **six décisions de justice inventées** par ChatGPT, avec des citations d'apparence normale. Le juge constate « conscious avoidance ». **5 000 $** de sanction. <span class="ref">S.D.N.Y., 22-cv-1461, juge P. Kevin Castel, 22 juin 2023</span>

- **Deloitte Australie, 2025** — rapport à **440 000 AUD** remis à un ministère. Références fabriquées, dont une citation attribuée à un juge fédéral. **~97 000 AUD remboursés.** <span class="ref">la version corrigée mentionne l'usage d'Azure OpenAI</span>

</div>
<div>

**RAPPORTÉ PAR LA PRESSE** <span class="ref">— non vérifié sur source primaire</span>

- **NYC MyCity, 2024** — le chatbot de la ville conseille des pratiques contraires au droit du travail.

- **Chevrolet de Watsonville, 2023** — chatbot détourné par injection de prompt, accepte de vendre un véhicule pour **1 $**.

</div>
</div>

<!--
Diapositive à survoler, deux secondes minimum à l'écran — en dessous, la salle
ne perçoit pas qu'elle est dense et l'effet de volume tombe.

« J'aurais pu en remplir beaucoup plus — mais je ne garde que ceux que je peux
prouver. » Survol assumé : « je ne m'arrête pas, vous les retrouverez », jamais
« je n'ai pas le temps ».

Dire pourquoi la diapositive est coupée en deux : un talk sur la mesure
rigoureuse range ses propres anecdotes par niveau de preuve.

⚠ Mata v. Avianca : SIX décisions inventées (Varghese, Shaboon, Petersen,
Martinez, Estate of Durden, Miller). Des résumés en annoncent neuf — les trois
autres noms qui circulent (Zicherman, Ehrlich, In re Air Crash Disaster) sont de
VRAIES décisions citées à l'intérieur des fausses. Ne pas se tromper en public.

⚠ Deloitte : concordant sur AP, Fortune et CFO Dive, mais la source primaire
(rapport révisé du DEWR) n'a pas pu être ouverte le 2026-09-24. La confirmer
avant l'oral, sinon basculer la ligne dans RAPPORTÉ.
-->

---

## Pourquoi personne n'a rien vu

**Le faux avait exactement la forme du vrai.**

- Un test unitaire vérifie une valeur de retour, **pas un raisonnement**

- Comparer mot à mot la réponse attendue et la réponse obtenue :
  une réponse **juste** formulée autrement est pénalisée,
  une réponse **fausse** bien formulée passe

- Il n'y a pas d'oracle : la même question admet dix bonnes réponses

<!--
Un avocat ne relit pas une citation bien formatée. « 925 F.3d 1339 (11th Cir.
2019) » a la forme d'une vraie référence, et c'est tout ce que notre œil
vérifie.

La conséquence pratique : on livre en se fiant à l'impression qu'on a en
relisant trois sorties à la main.

Les six citations inventées sont la démonstration du deuxième point — inutile
d'argumenter que la forme trompe, on vient de le montrer sur un avocat, un
ministère et une compagnie aérienne.
-->

---

## OllamAssist

<div class="carte">
<div class="texte">

**Un assistant de code dans mon IDE.
Il tourne entièrement sur ma machine.**

Pourquoi je l'ai écrit : pour comprendre ce que
l'IA fait vraiment, plutôt que de le lire. **Un labo.**

D'abord un **chatbot** — je pose une question,
il répond avec ce qu'il sait.

Puis un **agent** — il lit mon workspace,
et répond sur **mon** code.

Et là, tout change : sa réponse ne dépend plus
surtout du modèle.
**Elle dépend de ce qu'il a trouvé.**

</div>
<img src="img/ollamassist-marketplace.png" width="384" height="319" alt="Carte OllamAssist sur la JetBrains Marketplace">
</div>

<!--
⚠ À FAIRE LA VEILLE : l'image de droite est un gabarit. Prendre une capture de
la carte sur plugins.jetbrains.com/plugin/26388, et ÉCRASER le fichier
demo/img/ollamassist-marketplace.png — même nom, idéalement 768 x 638. Puis
relancer le rendu. Aucune modification du markdown.
Un iframe a été écarté : il exigeait du réseau pendant la présentation et ne
s'exportait pas en PDF.

Les faits, si on demande : c'est un plugin JetBrains, publié sur la Marketplace,
propulsé par Ollama, avec un mode entièrement hors-ligne. Chat dans l'IDE,
autocomplétion expérimentale, messages de commit générés depuis le diff.

La codebase qu'il indexe fait 162 fichiers Java. C'est la mienne — donc je vois
quand il se trompe. C'est ce qui rend l'exercice possible : sur du code que je ne
connais pas, je n'aurais aucun moyen de juger le juge.

La dernière ligne est la charnière de tout l'exposé. Tant que c'est un chatbot,
la qualité vient du modèle. Dès qu'il lit le workspace, elle vient d'abord de ce
que la récupération a rapporté. C'est ce déplacement qui justifie de mesurer le
RAG et pas seulement le modèle.
-->

---

## Comment mesurer la qualité des réponses de mon assistant ?

- J'avais deux stratégies de RAG — Lucene et un graphe Neo4j —
  et **aucun moyen de les départager**

- Le seul juge disponible, c'était moi,
  sur quelques exemples **choisis par moi**

- Ma crainte : **avancer à l'aveugle.**
  Modifier, livrer, et ne jamais savoir si j'ai amélioré ou dégradé.

<!--
Trois rôles en conflit : auteur du système, sélectionneur des cas de test, et
juge.

Le mot exact, c'est TUNNEL. Pas de boucle de retour, donc chaque modification
est un pari, et les paris s'accumulent sans qu'on sache lequel a coûté quoi.

Cette crainte se vérifie à la fin du talk : 91 minutes de fine-tuning pour une
justesse de 76,0 % contre 76,0 %. Exactement « j'ai modifié sans savoir si
j'améliorais » — sauf que cette fois, je l'ai su.
-->

---

## LLM-as-a-Judge, en une image

```
  Question           ┐
  Contexte récupéré  ├──►   JUGE   ──►   PASS / FAIL  + pourquoi
  Réponse produite   ┘    (un LLM)
```

**Il ne génère pas la réponse. Il la juge.**

Écrire un livre est difficile. Le lire et dire s'il est bon, beaucoup moins.

→ un modèle plus petit suffit, et ça change le prix

<!--
L'idée tient en une phrase, et c'est précisément pour ça qu'elle est dangereuse :
elle a l'air gratuite.

Insister sur les TROIS entrées. Le juge voit aussi le contexte récupéré, et
c'est ce qui lui permet de dire « cette réponse est peut-être vraie, mais rien
dans le contexte ne l'étaye ». Tout le banc Lucene/Neo4j repose là-dessus.

La confusion numéro un dans la salle : on croit qu'on demande au modèle de
refaire le travail, alors qu'on lui demande de vérifier. Deux tâches d'une
difficulté très différente.
-->

---

## Trois façons de juger

**1. Deux copies côte à côte** — « laquelle est la meilleure ? »
Je sais les classer. **Je ne sais pas si l'une mérite la moyenne.**

**2. Le corrigé type** — je compare la copie au corrigé.
Fiable. Mais il faut **écrire le corrigé de chaque question.**

**3. Le barème seul** — pas de corrigé, une liste de points à vérifier.
← *mon choix* · **Tout repose alors sur le barème.**

<!--
Pourquoi le corrigé type est hors de portée chez moi : si je savais écrire la
bonne réponse à mes 60 questions sur OllamAssist, je n'aurais pas besoin de RAG.
Le corrigé, c'est justement ce que je cherche.

Et la première méthode ne répond pas à ma question. Je ne veux pas savoir laquelle
de mes deux stratégies est la moins mauvaise, je veux savoir si l'une des deux est
utilisable.

La troisième approche déplace le problème sur la grille — et c'est le sujet de
la partie suivante.

⚠ Le « A contre B, puis B contre A » neutralise le biais de position ENTRE DEUX
RÉPONSES. Ce que j'ai mesuré est un biais de position sur L'ORDRE DES CONTEXTES
RÉCUPÉRÉS (12 verdicts sur 60). Même phénomène, dispositif différent : dire
lequel a été mesuré.
-->

---

## Première question : que ne PAS lui donner à juger

**Tout ce qui est déterministe ne passe pas par le juge.**

Ça compile ? Le JSON est valide ? Le style tient ?
→ **le compilateur, un parseur, le linter.**

La copie hors-sujet est écartée **avant** d'être lue.

Mon filtre à moi : l'équilibrage des parenthèses.
C'est tout. **Ce n'est pas un filtre, c'est un début.**

<!--
Un compilateur répond en cinquante millisecondes, ne coûte rien et n'a pas
d'humeur. Demander ça à un LLM, c'est payer pour une réponse moins fiable.

L'aveu, et pourquoi il est utile : si mon filtre est aussi mince, c'est que ce
que je fais juger n'est pas du code compilable, ce sont des explications en prose
qui contiennent du code. « Est-ce que ça compile » ne s'applique pas
directement — il faudrait extraire les blocs et les compiler à part. Je ne l'ai
pas fait. C'est une raison, pas une excuse.

L'action concrète à donner à la salle : extraire les blocs de code de la réponse
et les passer au compilateur avant le juge. Faisable en une après-midi.

Cette idée reviendra en partie 3 sous une autre forme : hintCoverage, un contrôle
déterministe sans LLM, qui classera les deux stratégies dans le même ordre que
le juge.
-->

---

## Deuxième question : quand évaluer ?

**Dans la CI, à chaque modification — la non-régression.**
Les **mêmes** questions, rejouées. Le corrigé type ou le barème : les deux
marchent, puisque les questions ne changent pas.

**En production, par échantillonnage.**
Là, plus de questions figées : **le barème seul.**
Combien, à quelle fréquence ? Ça dépend de trop de choses.
**Un échantillon suffit.**

Moi : **100 % dans la CI.** Aucun échantillonnage de production.

<!--
La vraie opposition n'est pas le moment, c'est le coût. L'offline exige un jeu
figé, donc un corpus à construire, et c'est là que part tout l'effort : 200
exemples, un golden set de 50. L'online ne demande aucun corpus mais ne donne
aucune comparabilité — les conversations de mardi ne sont pas celles de lundi,
donc rien ne s'attribue à ma modification.

C'est l'offline qui ferme le tunnel dont je parlais tout à l'heure. Rejouer les
MÊMES questions est la seule façon de savoir si une modification améliore ou
dégrade, et la seule façon de comparer deux stratégies : Lucene et Neo4j doivent
répondre aux mêmes 60 questions pour être comparables.
-->

---

## Troisième question : quel format de verdict ?

Pas une note sur 10. **PASS / FAIL.**

**Parce que « 13/20 », ça ne veut rien dire.**
Est-ce qu'on livre, ou pas ? La note ne répond pas.

Et une note invite les cinq erreurs du correcteur d'un coup :
la longueur impressionne, la main glisse vers le milieu,
et personne ne peut dire ce qui sépare 13 de 14.

**Une question binaire force la décision.** Elle se discute, donc elle se corrige.

<span class="ref">Mesuré ailleurs : décomposer en questions binaires fait gagner 0,45 d'accord entre 12 modèles évaluateurs — CheckEval, EMNLP 2025</span>

<!--
À dire clairement : ce point-là, je ne l'ai pas mesuré. Je m'appuie sur la
littérature. C'est la seule affirmation du talk dans ce cas, et autant le dire
plutôt que le laisser croire.

Exemple OllamAssist : « cette explication de ma classe RagService, elle vaut
13 ou 14 sur 20 ? » La question n'a pas de réponse. « Est-ce qu'elle cite une
méthode qui n'existe pas ? » en a une.

Si on demande pourquoi j'y crois : j'ai moi-même présenté, il y a quelques mois,
« +154 % en ajoutant BM25 » — calculé sur un passage de 1,8 à 4,5 sur 10. Un
pourcentage d'augmentation sur une échelle sans ancrage ne mesure rien, et d'une
exécution à l'autre le juge ne redonnait pas 4,5. La classe correspondante est
marquée @deprecated depuis le 2026-09-13, la raison est écrite dans le code.

Je n'ai pas fait combattre le gradué contre le binaire chez moi. J'ai abandonné
le gradué, je ne l'ai pas battu en duel — la nuance compte, et quelqu'un dans la
salle la verra.

⚠ Références exactes :
- CheckEval, EMNLP 2025, Lee, Kim, Kim, Cho, Kang, Kang, Kim.
  aclanthology.org/2025.emnlp-main.796/ — l'abstract attribue les incohérences
  aux « subjective evaluation criteria combined with Likert scale scoring » et
  mesure « improves the average agreement across evaluator models by 0.45 ».
- Zheng et al., NeurIPS 2023, Datasets and Benchmarks. arxiv.org/abs/2306.05685
-->

---

## L'ordre des champs décide du comportement

```
  ✗  {                        ✓  <thinking> … </thinking>
       "verdict": "PASS",          {
       "checks": { … }               "checks":  { … },
     }                               "verdict": "FAIL",
                                     "reason":  "…"
                                   }

     décide, puis justifie       constate, puis conclut
```

Un LLM génère **de gauche à droite**. Il ne revient pas en arrière.
Verdict en premier : les contrôles sont écrits pour être **cohérents avec une
décision déjà prise**.

Et le verdict ne s'opine pas, il se calcule :
**PASS si et seulement si tous les contrôles sont vrais.** Un seul `false` ⇒ FAIL.

<!--
C'est la chose la moins intuitive de tout le talk, et c'est deux caractères dans
un schéma JSON. Aucun modèle, aucun fine-tuning, aucun prompt ne rattrape un
mauvais ordre de champs : le texte déjà écrit conditionne le texte suivant, et
jamais l'inverse.

Le bloc <thinking> obéit à la même logique. Raisonnement avant les contrôles,
contrôles avant le verdict : chaque étape conditionne la suivante dans le bon
sens. Ce n'est pas trois décisions, c'en est une.

Le verdict est calculé, donc vérifiable : on peut le recalculer depuis les
contrôles et détecter un juge qui se contredit. C'est comme ça que sa cohérence
est mesurée.

Le vrai gain de la décomposition n'est pas la fiabilité. Une note globale dit
QU'une réponse échoue ; les contrôles atomiques disent LEQUEL échoue. C'est ce
qui permettra, en partie 3, de conclure que Neo4j souffre d'un défaut de rappel
et non d'un problème de bruit.

« reason » vient en dernier : il est écrit pour l'humain qui relira, et venant
après le verdict il ne peut pas l'influencer.

Contre-chiffre à ne pas taire, il revient en partie 4 : la conjonction ABSORBE
les désaccords. Sur 50 items, 17 portent un désaccord sur au moins un contrôle,
dont 15 que le verdict masque.

⚠ Je n'ai PAS mesuré l'écart entre les deux ordres : j'ai choisi le bon dès le
départ. C'est un raisonnement sur le fonctionnement de la génération, pas un
résultat expérimental. Le dire tel quel.
-->

---

## Mes critères, et d'où ils viennent

Un critère se formule comme **une question sur le texte**, jamais comme une
propriété du monde. Et ils ne sont **pas une liste que j'ai choisie.**

```
  GÉNÉRIQUES — toute analyse de code            sur 150 / 150 exemples
    les faits techniques affirmés sont-ils vrais ?
    un défaut visible rend-il la réponse fausse ?
    la réponse fait-elle ce qui était demandé ?

  PAR TYPE DE TÂCHE — ici, juger un contexte RAG       25 exemples
    le contexte est-il pertinent ?
    permet-il de répondre sans rien supposer ?
    le bruit reste-t-il maîtrisé ?

  DICTÉS PAR LA REQUÊTE — lus dans la demande       9 critères
    « sans dépendance externe »  →  aucune_dependance_externe
    « sans changer la signature » →  signature_publique_inchangee
```

<!--
C'est la réponse à « comment savez-vous que ce sont les bons critères ». Je ne le
décide pas pour la troisième catégorie : je la lis dans la requête. Si la demande
impose une contrainte, elle devient un critère nommé. Sinon il n'existe pas.

Exemple OllamAssist : « refactorise cette méthode avec l'API Stream, sans changer
la signature publique ». La contrainte est dans la phrase. Le critère aussi.

Il y a neuf critères de ce type dans mon corpus, chacun apparaissant deux à six
fois. Ce sont les cas où la requête était précise.
-->

---

## Les trois tests d'un bon critère

**1. Décidable** — la réponse se lit dans ce qui est fourni.

**2. Falsifiable** — je sais dire ce qui le rendrait faux.

**3. Reproductible** — deux personnes répondent pareil.
**Et celui-là, il se mesure.**

Mon plus mauvais critère : **`respect_consignes`, κ = 0,386.**

C'est aussi **le seul qui n'a pas de définition propre** — il hérite de la
requête. Ce n'est pas un hasard.

<!--
Les deux premiers tests sont des règles d'écriture. Le troisième est une mesure —
et c'est le seul qui tranche vraiment.

L'aveu, et il vaut mieux que n'importe quelle justification : mon critère le plus
ambigu est celui qui n'en est pas vraiment un. « respect_consignes » est un
fourre-tout, il change de sens à chaque requête, et il a le pire accord entre
relecteurs de toute ma grille.

Le correctif est déjà dans le corpus : quand la contrainte est explicite, je la
sors en critère nommé. Les neuf critères dictés par la requête sont exactement la
décomposition de ce fourre-tout.

Un critère qui échoue au troisième test doit être réécrit ou découpé. Pas défendu.
-->

---

## Séparer le moteur de la grille

**Un seul correcteur. Deux barèmes.**

```
  BARÈME « CODE »                    BARÈME « DOCUMENTATION »

  les API citées existent            les étapes sont dans l'ordre
  un défaut visible fausse tout      aucune commande inventée
  la consigne est respectée          les prérequis sont dits
```

Le modèle n'apprend pas **mon** domaine.
Il apprend à **suivre un barème** — et c'est le barème qui porte le domaine.

<!--
C'est ce qui rend le juge réutilisable. Si j'avais entraîné le modèle sur « ce
qu'est une bonne réponse pour OllamAssist », il ne servirait qu'à OllamAssist.
Entraîné à coller à une grille, il change de domaine en changeant de grille.

Conséquence directe sur le corpus : mes exemples d'entraînement portent trois
marqueurs de tâche différents — analyse de code, pertinence du contexte
récupéré, fidélité au contexte. Le même moteur, trois grilles.
-->

---

## Cinq façons de se tromper sans être incompétent

Un correcteur honnête, fatigué par 200 copies :

```
  il se laisse impressionner par la longueur    4 pages, ça fait sérieux

  il note selon l'ordre des copies              la 1re et la 20e

  il préfère son propre style                   il se reconnaît dedans

  il a reconnu l'écriture                       il note l'auteur, pas la copie

  il préfère valider que recaler                c'est moins coûteux
```

**Aucune de ces cinq erreurs n'est une faute de compétence.
Toutes déforment la note.**

<!--
C'est la diapositive à poser avant de parler de mesure, parce qu'elle explique
pourquoi une note globale ne suffit pas. Un juge LLM fait exactement ces cinq
choses, et pour les mêmes raisons qu'un humain fatigué.

La quatrième est la plus vicieuse et c'est celle qui m'est arrivée : le modèle
avait appris à reconnaître MA tournure de phrase. Il ne jugeait plus la réponse,
il me reconnaissait.

La cinquième est celle qu'on ne voit jamais dans les tableaux, parce qu'elle
améliore l'exactitude globale au lieu de la dégrader.
-->

---

## Comment je m'en protège

| l'erreur | la parade | chez moi |
|---|---|---|
| la longueur | comparer les faux PASS sur défauts **verbeux** et **concis** | **mesuré** — 46 % |
| l'ordre | mélanger le contexte, **graine tirée de la question** | **mesuré** — 12 / 60 |
| son propre style | ne pas faire juger un modèle par sa propre famille | *cité* |
| l'écriture reconnue | un **relecteur humain**, et un test de permutation | **mesuré** — 17 / 17 |
| l'indulgence | publier le **taux d'erreurs attrapées**, pas l'exactitude | **mesuré** — 59 % |

**La dernière colonne est le sujet de cette diapositive.**
Ne jamais présenter un biais **cité** comme un biais **mesuré**.

<!--
Quatre des cinq parades sont des mesures, une seule est une précaution reprise de
la littérature. C'est la seule chose qui sépare un retour d'expérience d'une revue
de littérature mal digérée — et c'est aussi ce qui me permet de dire « je ne sais
pas » sur l'auto-préférence sans que ça décrédibilise le reste.

Sur l'ordre : le mélange atténue le biais, il ne le supprime pas. 12 verdicts sur
60 basculent encore au seul réordonnancement, à récupération identique. Et la
graine vient de la question, donc la mesure se rejoue à l'identique.

Sur l'écriture reconnue : aucune métrique ne l'a trouvée. C'est un relecteur
humain qui a changé d'avis sur un item. J'y reviens juste après.

Les parades coûtent peu. Ce sont des comparaisons appariées et un mélange graîné,
pas des instruments de recherche.
-->

---

## Le chiffre spectaculaire

**La question :** est-ce que la simple **longueur** d'une réponse suffit à
deviner son verdict ?

Si oui, le juge n'a plus besoin de comprendre — **il compte les caractères.**

J'ai essayé 145 seuils de longueur, dans les deux sens. **290 essais.**

Le meilleur devinait le verdict **3 fois sur 4** — le hasard en fait 1 sur 2.

→ un effet **quasi impossible à devoir au hasard.**

<!--
Pourquoi la question compte : une fuite de ce genre dispense le modèle
d'apprendre. Le raccourci le plus facile est toujours celui qu'il prendra.

« Dans les deux sens » : plus long ⇒ PASS, et plus long ⇒ FAIL. On ne savait pas
a priori quel sens chercher, donc les deux ont été testés.

Marquer un temps sur la dernière ligne : c'est le chiffre que j'ai annoncé, et
c'est celui qui était faux.

⚠ Chiffres exacts si la question vient : 75 % de bonne prédiction contre un taux
de base de 53 %, annoncé à +8,8 σ. Le « quasi impossible » est la traduction de
ce 8,8 σ.
-->

---

## …et pourquoi il ne valait rien

**J'ai jugé mon meilleur essai comme si c'était mon seul essai.**

Le meilleur de 290 tirages est bon **même quand il n'y a rien à trouver.**

Le bon test : **mélanger les étiquettes**, refaire **les 290 essais**, garder le
meilleur. Mille fois.

→ **p = 0,132.** Mon « 3 sur 4 » est ce que le hasard produit couramment.

**Du bruit.**

<!--
L'image à donner : le tireur qui mitraille un mur de grange, puis dessine la
cible autour du groupe le plus serré. Pour un public de développeurs : un seuil
optimisé sur les données, puis évalué comme s'il avait été choisi avant de les
voir. De l'overfitting, mais sur une statistique.

Pourquoi mélanger les étiquettes : ça détruit tout lien réel s'il en existait un.
Ce qui reste est la seule référence utile — à quoi ressemble le meilleur de 290
essais quand il n'y a rien à trouver. Réponse : à 3 sur 4.

La règle à emporter, et c'est la plus transférable du talk pour qui manipule des
chiffres : tout seuil choisi après coup se compare à un tirage de permutation du
MÊME maximum. Jamais à un taux de base. Sinon on mesure sa propre liberté de
choix, pas un effet.

Le piège ne se voit pas : le calcul était juste, la statistique était juste.
C'est la référence de comparaison qui était fausse.

⚠ Le test de permutation ramène l'effet à +1,3 σ, p = 0,132.
-->

---

## La fuite : 17 sur 17

17 requêtes du corpus portaient la même incise —
*« si tu as le temps, dis un mot de X »*.

**Les 17 étaient étiquetées PASS. 17 sur 17.**

Aucune statistique à faire : un juge n'a qu'à détecter la chaîne de caractères
pour marquer 17 points.

**Le modèle n'apprend pas à juger. Il apprend à repérer ma signature.**

<!--
C'est une fuite déterministe, pas un biais statistique. La différence est
importante : un biais déforme, une fuite dispense d'apprendre.

Et elle vient de moi. En rédigeant le corpus, j'ai associé sans y penser une
tournure de politesse à des réponses que je considérais bonnes.

C'est le risque propre à un corpus écrit par une seule personne — et c'est
exactement mon cas.
-->

---

## Le correctif qui aggrave : 30 sur 30

Correctif évident : ajouter la même incise à des FAIL existants.
Règle de surface ramenée à **57 %**. Réglé.

**Sauf que le correctif plaçait l'incise en paragraphe isolé**,
là où les 17 d'origine la portaient au fil du texte.

Nouvelle règle apprise : *« paragraphe isolé ⇒ FAIL »*. **30 sur 30.**

Elle a traversé une régénération, une validation à zéro erreur,
**trois mesures et un commit.**

<!--
La fuite corrigée était à 17 sur 17. La fuite créée par le correctif est à 30 sur
30. J'ai aggravé le problème en le réparant, et aucune de mes vérifications ne
l'a vu.

Ce qui est instructif, ce n'est pas l'erreur, c'est qu'elle soit passée à travers
tout un dispositif conçu exprès pour l'attraper.

Toute correction d'un corpus est une nouvelle écriture, et toute écriture
introduit une signature.
-->

---

## Ce qui l'a trouvée : un humain

Les métriques ont trouvé ce que je leur avais demandé de chercher.

**L'humain a trouvé ce que je ne savais pas chercher.**

Un relecteur a répondu **différemment** sur un item, après avoir appliqué la
règle correctement quatre fois de suite.

Ce n'était pas un relâchement : le stimulus était réellement différent.

<!--
C'est la diapositive qui compte de toute cette partie.

Un balayage automatique cherche les régularités qu'on a listées. Il ne peut pas
signaler celle à laquelle on n'a pas pensé — et une fuite, par définition, est
celle à laquelle on n'a pas pensé.

Le relecteur humain n'a pas trouvé la fuite en la cherchant. Il a trouvé une
incohérence dans son propre comportement, et c'est en la creusant que la règle
est apparue.

C'est l'argument central pour garder un humain dans la boucle, même quand tout
est automatisé — et j'y reviens à la fin, avec le triage.
-->

---

## Tout en local, et pourquoi

Un MacBook Pro M3 Pro, 36 Go. **Aucun service cloud, aucun jeton facturé.**

**91 minutes** d'entraînement.
**11,3 Go** de mémoire au pic, sur 36 disponibles.
**43,8 Mo** d'adaptateur produit — 0,078 % des paramètres du modèle.

**Le fine-tuning d'un juge n'est pas un projet d'infrastructure.
C'est une soirée.**

<!--
Les chiffres exacts, si la question vient : Qwen2.5-Coder-14B quantifié en 4 bits,
8,3 Go sur disque, QLoRA via MLX, 400 itérations, 13,65 s par itération, 169 513
jetons entraînés.
Le message de cette diapositive est le prix d'entrée, pas la performance. Tout
le monde dans la salle a la machine qu'il faut.

Et une correction à raconter : j'ai d'abord publié 76 minutes. Ma méthode de
calcul excluait les 9 passes de validation, soit 14,7 minutes. La vraie durée
que l'utilisateur attend est 91 minutes. Corriger rendait mon chiffre moins
flatteur, et c'est précisément ce qui rend la correction crédible.

Pire : le tout premier relevé annonçait 690 minutes — un facteur 9 — parce que la
machine s'était mise en veille pendant l'entraînement. Rien ne l'a signalé.
Troisième fois que ça arrivait.
-->

---

## Le corpus : c'est là que part le travail

**200 exemples** écrits à la main, **50** mis de côté comme étalon.

Chaque exemple : une requête, un contexte, une réponse à évaluer,
et le jugement attendu — contrôles, verdict, raison.

**Accord entre annotateurs humains sur l'étalon : κ = 0,880**
<span class="ref">IC 95 % [0,720 — 1,000] — accord de verdict 47 items sur 50</span>

Le modèle s'entraîne en 91 minutes.
**Le corpus a pris des semaines.**

<!--
Si vous ne retenez qu'une chose de cette partie : le coût n'est pas le GPU,
c'est l'étalon.

Le κ de Cohen mesure l'accord en retirant l'accord dû au hasard. 0,880, c'est un
accord fort — mais c'est l'accord sur MON étalon, entre un humain et des
étiquettes. Ce n'est pas encore l'accord du juge. J'y reviens à la fin, parce
que ces deux κ se confondent tout le temps.

Les contextes RAG des exemples ne sont pas inventés : ce sont de vraies
extractions Lucene et Neo4j sur ma codebase, gardées telles quelles, avec leurs
quasi-homonymes et leurs corps tronqués.
-->

---

## Le banc d'essai : 60 questions, 3 niveaux

| Niveau | Ce qu'il teste |
|---|---|
| **LOCAL** | une méthode précise, dans un seul fichier |
| **STRUCTURAL** | héritage, interfaces, ce qui implémente quoi |
| **CROSS_MODULE** | une chaîne qui traverse plusieurs paquets |

Les **mêmes** 60 questions pour les deux stratégies, dans la **même** exécution.

Mélange du contexte **graîné par la question** → la mesure est reproductible.

<!--
Poser les deux stratégies face à la même question dans la même boucle, c'est ce
qui autorise un test apparié — et un test apparié est beaucoup plus puissant à
effectif égal.

Les trois niveaux ne sont pas décoratifs : ils séparent ce qu'une recherche
lexicale trouve facilement de ce qui demande de suivre des liens. C'est là qu'on
attend le graphe.

Le mélange graîné par la question n'est pas un détail : sans graine, les runs de
la veille faisaient bouger le même bras de 55,9 % à 43,3 %. Une mesure qui ne se
rejoue pas n'est pas une mesure.
-->

---

## Le résultat

| | Lucene | Neo4j |
|---|---|---|
| **Réponses justes** | **48,3 %** | **23,7 %** |
| Contexte jugé insuffisant | 39,7 % | **66,1 %** |

Sur les 60 questions, **24 les départagent.**
**Lucene en gagne 19. Neo4j en gagne 5.**

Le hasard seul donnerait 12 – 12. → **p = 0,0066**

<!--
Chiffre retiré de l'écran mais disponible : la cohérence du juge, c'est-à-dire la
part des verdicts qui correspondent bien à ses propres contrôles, est de 100 %
pour Lucene et 98,3 % pour Neo4j.
Seules les paires discordantes portent de l'information : les questions où les
deux stratégies font pareil ne départagent rien. Leur nombre est le vrai
déterminant de la puissance à cet effectif, donc je le donne avec le p, jamais
sans.

Et la deuxième ligne du tableau dit le mécanisme : ce n'est pas un problème de
bruit mal maîtrisé, c'est un DÉFAUT DE RAPPEL. Le moteur ne rapporte pas assez
de matière. Sans critères atomiques, j'aurais un écart de 25 points sans
explication.

C'est exactement ce que les critères atomiques apportent sur une note globale :
ils disent lequel échoue.
-->

---

## Pourquoi 36 questions sur 60 ne comptent pas

Sur 60 questions, les deux stratégies font **pareil 36 fois** :
soit les deux réussissent, soit les deux échouent.

Ces 36 ne départagent rien. **Il reste 24 questions** où l'une gagne
et l'autre perd.

```
      Lucene gagne     19
      Neo4j  gagne      5
```

S'il n'y avait aucune différence, on attendrait **12 – 12.**
Obtenir 19 – 5, c'est tirer **19 fois pile sur 24 lancers.**

→ **p = 0,0066.** Le test, c'est exactement ce calcul. Rien de plus.

<!--
C'est la diapositive qui démystifie le test apparié. McNemar n'est pas une boîte
noire : c'est une pièce lancée autant de fois qu'il y a de questions qui
départagent.

Insister sur le fait que les 36 questions identiques ne sont pas perdues — elles
disent que les deux stratégies se valent là-dessus. Elles ne peuvent simplement
pas servir à trancher.

La conséquence pratique, et c'est pour ça que je donne toujours le nombre de
paires avec le p : doubler le nombre de questions ne sert à rien si elles sont
faciles. Ce qui compte, c'est combien de questions font diverger les deux
systèmes.
-->

---

## Le contrôle qui ne passe pas par le juge

`hintCoverage` — on compte les identifiants attendus
présents dans le contexte récupéré. **Aucun LLM.**

**Lucene 0,697. Neo4j 0,596.**

Le même ordre que le juge — sans juge.

**La conclusion ne repose donc pas sur l'instrument seul.**

<!--
C'est le filtre déterministe du début du talk, qui revient sous une autre forme.
En amont il économise des jetons ; en aval il sert de validation croisée.

Et ça ne coûte rien : une liste d'identifiants attendus par question, un
comptage. Si les deux méthodes s'étaient contredites, je n'aurais rien conclu du
tout — c'est le genre de garde-fou qu'on construit avant de connaître le
résultat, pas après.
-->

---

## Moteur ou graphe ? Le contrôle d'équité

J'ai rejoué les 60 questions **sans** le parcours de graphe.

Lucene est configuré à l'identique : son taux **doit** être le même.
Il l'est. **48,3 %, à la décimale, et sur chacun des trois niveaux.**

Le témoin n'a pas bougé. Neo4j, lui, gagne **1,7 point — une question sur 59.**

**L'écart vient du moteur de récupération, pas de la traversée de graphe.**

<!--
Le bras témoin n'a pas bougé d'une décimale entre les deux exécutions, et sur
chacun des trois niveaux. C'est ça qui autorise l'attribution : si Lucene avait
bougé, je n'aurais rien pu conclure du tout.

Et ça affine l'hypothèse de départ au lieu de la confirmer. Je ne dis pas « le
graphe est mal implémenté » : je dis que le pipeline Neo4j rappelle moins de
matière. Ce n'est pas la même critique, et ce n'est pas le même correctif.
-->

---

## Par niveau : ce qui conclut, et ce qui ne conclut pas

Sur les trois niveaux, un seul écart tient : les questions **inter-modules**.

Là, sur les 8 questions où les deux stratégies ont divergé,
**Lucene a gagné les 8.** Huit piles d'affilée.

Sur les deux autres niveaux : 5 piles sur 7, et 6 sur 9. **Banal.**

**Deux écarts sur trois ne concluent pas** — et c'était une limite annoncée
d'avance, pas une surprise.

<!--
Les chiffres par niveau, si on les demande : LOCAL 31,6 % contre 20,0 %, 5 paires
contre 2, p = 0,453. STRUCTURAL 63,2 % contre 42,1 %, 6 contre 3, p = 0,508.
CROSS_MODULE 50,0 % contre 10,0 %, 8 contre 0, p = 0,0078.
Il aurait été facile de présenter les trois lignes comme trois résultats : les
écarts bruts vont tous dans le même sens. Mais 5 ou 6 paires gagnées ne
départagent rien, et je le savais avant de lancer.

La colonne du milieu est la seule qui décide. 8 – 0 veut dire que sur les huit
questions inter-modules où les deux stratégies ont divergé, Lucene a gagné les
huit. C'est huit piles d'affilée.

Dire un écart « non concluant » n'est pas un aveu de faiblesse, c'est ce qui
donne du poids au seul qui conclut.

⚠ Réserve de portée à énoncer : ces chiffres valent pour CETTE implémentation
Neo4j, à ces réglages, sur CETTE codebase. « GraphRAG fait moins bien » serait un
abus ; « ce pipeline-ci rappelle moins que Lucene sur ce corpus » est ce que la
mesure soutient.
-->

---

## Cinq fois, mon banc a mesuré le vide

Et cinq fois, il a affiché **BUILD SUCCESS**.

| Ce qui était cassé | Ce que ça a produit |
|---|---|
| Les `-D` non transmis par surefire | un corpus synthétique indexé à la place du vrai |
| Une propriété vide au lieu de l'adaptateur | le modèle de base, jugé comme s'il était fine-tuné |
| Un `pgrep` qui matchait son propre script | ~5 heures perdues |
| Un mélange non graîné | 21 questions sur 60 divergentes à récupération identique |
| `--adapter-path` accepté puis ignoré | *« le fine-tuning dégrade de 76 % »* — un résultat qui ne mesurait rien |

**Aucune erreur. Aucun avertissement. Des résultats plausibles.**

<!--
La cinquième est la plus instructive : le rapport annonçait une dégradation de
76 points avec intervalle de confiance et p-value à quatre zéros. Publiable tel
quel. Entièrement faux.

Ce qui l'a révélée n'est pas une métrique, c'est un détail de style : des clés
plates dans un bloc markdown, là où mes exemples d'entraînement portent tous un
JSON nu et imbriqué. Le modèle ne parlait pas la langue que je lui avais apprise.

La leçon, et c'est le correctif que j'ai mis en place : avant de dépenser une
heure de calcul, faire UN appel et vérifier une propriété qui ne peut pas
apparaître par hasard si la plomberie est cassée. Pas l'absence d'erreur — une
preuve positive.
-->

---

## « On est d'accord 9 fois sur 10 »

100 copies à corriger. **90 sont mauvaises.**

Deux correcteurs **recalent tout le monde**, sans rien lire.

→ ils sont **d'accord 9 fois sur 10.**

L'accord brut ne mesure pas la compétence.
Il mesure surtout **le déséquilibre du paquet de copies.**

<!--
C'est le piège le plus facile à tomber dedans, et le plus flatteur : on annonce
un fort taux d'accord, et on croit avoir prouvé que son étalon est fiable.

Or dès qu'une classe domine, l'accord est presque gratuit. Il faut donc enlever
la part du hasard avant de parler de fiabilité.

Le même raisonnement vaut pour une exactitude : 90 % de bonnes réponses sur un
jeu où 90 % des cas sont de la même classe, c'est zéro information.
-->

---

## κ de Cohen, sur un cas réel

Deux correcteurs, 100 copies. Ils sont d'accord sur **90.**

Chacun valide une copie sur cinq. Donc **même en cochant au hasard**,
ils tomberaient d'accord **68 fois sur 100.**

```
  0                                        68          90        100
  ├──────── donné par le hasard ────────────┼─ conquis ─┼─ raté ──┤
                                               22           10
```

**κ = 22 conquis / 32 qui restaient = 0,69**

κ, c'est **la part conquise de ce qu'il restait à conquérir.**

<!--
Le résumé de la formule en une phrase : κ, c'est ce qu'on a gagné divisé par ce
qu'il restait à gagner.

Suivre le tableau à voix haute. Les deux relecteurs disent PASS une fois sur cinq
chacun. Donc même en répondant au hasard, ils tomberaient d'accord 68 fois sur
100 — 4 fois sur un PASS commun, 64 fois sur un FAIL commun. L'accord gratuit,
c'est ça.

Partant de 68, il ne restait que 32 points à conquérir. Ils en ont pris 22. D'où
0,69, alors que l'accord brut affichait 90 %.

L'échelle usuelle : au-dessus de 0,8 l'accord est fort, entre 0,6 et 0,8 il est
correct, entre 0,4 et 0,6 il est moyen.
-->

---

## Et le piège marche dans les deux sens

Sur mon critère le plus fréquent :

**78 % d'accord brut.  κ = 0,386.**

Le paquet est très déséquilibré — donc le κ paraît médiocre
alors que les deux correcteurs se trompent rarement.

**Donner le κ seul sous-estime l'accord.
Donner le pourcentage seul le surestime.**

Les deux vont ensemble. Avec les marges.

<!--
C'est le contre-exemple de la diapositive précédente : là, le pourcentage
flattait. Ici, c'est le κ qui accable à tort.

Un κ bas ne veut donc pas toujours dire ce qu'on croit. Il faut regarder la
répartition avant de juger le chiffre.

C'est le genre de nuance qu'on a envie de sauter. C'est aussi celle qui fait la
différence entre un chiffre qu'on affiche et un chiffre qu'on comprend.
-->

---

## Deux κ qu'on confond tout le temps

| | ce qu'il mesure | valeur |
|---|---|---|
| **κ du corpus** | l'humain contre mes étiquettes de référence | **0,880** <span class="ref">[0,720 — 1,000]</span> |
| **κ du juge** | le juge contre l'étalon | **0,44** <span class="ref">[0,27 — 0,60]</span> |

Le premier dit *« mon étalon est-il fiable ? »*
Le second dit *« mon juge est-il aligné ? »*

**0,880 entre humains. 0,44 pour le juge.**
Le plafond n'est pas le modèle — c'est ce que le corpus enseigne.

<!--
Présenter le premier comme le second est l'erreur la plus fréquente, et la plus
flatteuse : on annonce un alignement qu'on n'a jamais mesuré.

L'écart entre les deux est la vraie information de cette diapositive. Mon juge
est nettement moins aligné sur l'étalon que deux humains ne le sont entre eux.

Et un κ bas ne veut pas toujours dire ce qu'on croit : mon contrôle le plus
fréquent tombe à κ = 0,386 pour 78 % d'accord brut, simplement parce que les
marges sont très déséquilibrées. Publier le κ seul sous-estime l'accord, publier
les 78 % seuls le surestime. Les deux vont ensemble.
-->

---

## Ce que le verdict cache

**17 items sur 50** portent un désaccord sur au moins un contrôle.
**15 d'entre eux : le verdict est identique quand même.**

Le verdict est une conjonction — dès qu'un contrôle échoue des deux côtés,
un désaccord sur un autre devient **invisible**.

**Le verdict est reproductible. Les raisons le sont beaucoup moins.**

Or c'est sur les raisons que le juge s'entraîne.

<!--
C'est le contre-chiffre de ma propre méthode, et je préfère le donner moi-même.

Ce n'est pas un défaut de la conjonction — la conjonction fait exactement ce
qu'on lui demande. C'est un plafond sur ce que le fine-tuning peut apprendre, et
c'est une propriété de mon corpus.

Une asymétrie qui n'est pas du bruit, et qui mérite d'être dite : 16 désaccords
sur 22 vont dans le même sens, l'annotateur humain plus sévère que l'étiquette
rédigée par le modèle. Une vérité de référence écrite par un LLM puis relue est
plus indulgente que ce qu'un humain aurait produit seul.
-->

---

## Un correcteur indulgent a l'air fiable

Un correcteur qui valide presque tout se trompe rarement.
Il ne se trompe que sur les copies qu'il aurait dû recaler.

```
   27 mauvaises copies   →  il en recale 16.  Il en laisse passer 11.
   23 bonnes copies      →  il en valide 22.
```

**76 % de décisions justes. Et 4 défauts sur 10 qui passent.**

Le même juge. Deux chiffres. **Ne publiez jamais le premier sans le second.**

<!--
C'est le piège le plus courant, et il est flatteur. Un juge qui répondrait PASS à
tout sur un corpus où 95 % des réponses sont bonnes afficherait 95 %
d'exactitude — et attraperait zéro erreur.

Exemple OllamAssist : un défaut qui passe, c'est une explication fausse sur ma
propre codebase livrée à l'utilisateur. Un bon code recalé, c'est juste une
relecture inutile. Les deux erreurs n'ont pas le même prix, donc elles ne se
résument pas en un seul pourcentage.

Si le juge est une porte, c'est le taux d'erreurs attrapées qui décide. S'il est
un thermomètre, l'exactitude suffit.

⚠ Chiffres, si la question vient : 16 erreurs détectées sur 27 (59 %) et 22
bonnes réponses validées sur 23 (96 %) pour le fine-tuné ; 17 sur 27 (63 %) et 21
sur 23 (91 %) pour la baseline. L'écart entre les deux variantes est d'UN item :
c'est du bruit, ne pas l'interpréter.

Et ça recoupe deux autres mesures qui disent la même chose : 46 % de faux PASS
sur les défauts verbeux, et un juge qui rend PASS 64 % du temps là où l'étalon en
compte 46 %. Trois mesures indépendantes, un même diagnostic : il est indulgent.
-->

---

## Le fine-tuning a-t-il amélioré mon juge ?

| | Réponses justes | Format exploitable |
|---|---|---|
| Invite nue | 0 % | **0 %** |
| **+ conventions écrites** | **76,0 %** | 100 % |
| **Fine-tuné** (91 min) | **76,0 %** | 100 % |

La stabilité du verdict, elle, **baisse** — j'y viens juste après.

**12 items les départagent. 6 d'un côté, 6 de l'autre.**
Une pièce équilibrée. → **p = 1,0000**

Et les deux **ratent 4 erreurs sur 10.** L'exactitude ne le dit pas.

**Non concluant** — et cette issue était **écrite avant** de lancer la mesure.

<!--
Trois résultats, et aucun n'est celui que j'attendais.

Premier : l'invite nue ne rend AUCUN JSON exploitable. Zéro sur 150. Le seul
ajout de quatre phrases de conventions fait passer la justesse de 0 à 76 %.
Avant de fine-tuner quoi que ce soit : écrivez vos conventions.

Deuxième : le fine-tuning n'améliore pas la justesse. À 50 items, mon étude ne
pouvait pas détecter moins de 15 points d'écart, et c'était écrit dans mon
protocole avant les résultats. La branche « non concluant » était pré-enregistrée
avec sa formulation — c'est exactement ce à quoi sert un pré-enregistrement :
pouvoir dire « je ne sais pas » sans que ce soit un échec, et sans céder à la
tentation de redécouper les données jusqu'à trouver un p inférieur à 0,05.

Troisième : ce qu'il a acheté est ailleurs, et c'est la diapositive suivante.
-->

---

## « Non concluant » ne veut pas dire « identique »

12 questions départagent les deux juges. **6 – 6.**

C'est 6 piles et 6 faces sur 12 lancers : **exactement ce que donne une pièce
équilibrée.**

Je ne peux pas dire que le fine-tuning n'apporte rien.
Je peux seulement dire que **mes 50 items ne voient pas la différence.**

Avec 50 items, tout écart de moins de ~15 points est invisible.
→ intervalle de confiance : **de −14 à +14 points.**

<!--
C'est la distinction que tout le monde saute, et elle change tout. « Pas de
différence détectée » et « pas de différence » sont deux affirmations
différentes. La première parle de mon dispositif, la seconde parlerait du monde.

Traduire l'intervalle à voix haute : la vérité peut être que le fine-tuning fait
perdre 14 points, ou qu'il en fait gagner 14. Mes données ne savent pas
départager. Pour le savoir, il faudrait plus d'items — pas un autre calcul.

Et c'est précisément ce que le pré-enregistrement protège : la limite était
écrite avant les résultats, donc « je ne sais pas » est une issue déclarée et non
un échec. Sans ça, la tentation est de redécouper les données jusqu'à trouver un
p inférieur à 0,05 — et avec 13 contrôles et 3 strates, on finit toujours par en
trouver un.
-->

---

## Ce qu'il a acheté : le contrat, pas le jugement

La baseline **décompose déjà** — elle rend un objet de contrôles.
Mais sous **son propre nom de clé**, et avec **le verdict avant.**

```
   baseline    { "verdict": "PASS",  "controls": { … } }     138 / 150
   fine-tuné   { "checks": { … },    "verdict": "FAIL" }     150 / 150
```

Le fine-tuning ne lui a pas appris à décomposer. Il lui a appris **le contrat
exact** — les bons noms, et les contrôles **avant** le verdict.

C'est ça qui rend deux exécutions comparables.

<!--
91 minutes de fine-tuning pour découvrir que le gain de justesse tenait dans
quatre phrases d'invite, et que le fine-tuning servait à autre chose que ce que je
croyais.

Le modèle de base sait décomposer, si on le lui demande. Ce qu'il ne sait pas,
c'est tenir un nom de clé et un ordre — donc sa sortie n'est pas comparable d'une
exécution à l'autre, et les 13 accords par contrôle ne se calculent que sur le
fine-tuné : validation_entree 100 %, contexte_pertinent 89 %, absence_invention
83 %, et format_impose 33 %.

C'est une leçon d'intégration, pas d'intelligence : un juge sert dans une chaîne
automatisée, et une chaîne a besoin d'un contrat, pas de bonne volonté.
-->

---

## Le contre-chiffre : la stabilité baisse

**76 % → 58 %** de verdicts identiques sur trois passes.

Ce n'est pas le juge qui devient capricieux. C'est **le nombre de choses qui
peuvent bouger** :

```
   baseline    1 engagement pris tôt : le verdict
   fine-tuné   3 contrôles, puis leur ET
```

Mesuré : son verdict ne bouge **jamais** sans qu'un contrôle bouge — **0 item
sur 50.** Et 8 fois, la conjonction **absorbe** la variation.

La baseline est stable parce qu'elle **décide avant de regarder.**

<!--
Les deux chiffres ne mesurent pas le même objet. D'un côté la constance d'un seul
jeton écrit tôt ; de l'autre la constance d'une conjonction de trois décisions.
Un seul des trois contrôles qui bascule fait basculer le verdict.

Le détail, si la question vient : sur les 29 items où les contrôles varient, 1,8
contrôle bascule en moyenne. 21 fois le verdict suit, 8 fois la conjonction
absorbe. Et jamais l'inverse.

Donc la stabilité de la baseline est moins chère — et elle n'achète aucune
justesse : les deux sont à 76,0 % exactement.

⚠ Un piège à ne pas tendre soi-même : la cohérence entre verdict et contrôles est
de 99,3 % DANS LES DEUX CAS. Elle ne départage donc pas les deux ordres, et ne
peut pas servir de preuve ici.

Et il faut le dire en entier : aucune des trois variantes ne passe le filtre de
recevabilité fixé d'avance — au mieux 76 % de stabilité pour un seuil à 95 %. Le
juge présenté ici n'est pas prêt pour la production.

⚠ Ne pas dire « le 32B fait mieux » : il n'a jamais été entraîné. Le déclarer non
réalisé.
-->

---

## Qui décide quoi

```
  déterministe ?     →  le compilateur, le parseur, le linter
                        ni juge, ni humain

  juge d'accord      →  automatique
  avec lui-même ?       PASS si et seulement si tous les contrôles sont vrais

  juge instable ?    →  un humain
                        le seul cas légitime
```

Un humain n'intervient pas « parfois ». Il intervient quand **le juge s'est
contredit d'une passe à l'autre** — ce qui est mesuré, pas ressenti.

Et le signal fonctionne : **83 %** de verdicts justes sur les items stables,
**67 %** sur les instables.

<!--
« Parfois un humain » n'est pas une politique. Il faut un déclencheur mesurable,
et il existe déjà dans le harnais : je fais trois passes pour mesurer la
répétabilité, le même chiffre sert à trier.

⚠ Réserve sur le 83 / 67 : 29 items stables contre 21 instables. C'est une
tendance, pas un effet établi — mais elle va dans le même sens sur les deux
variantes mesurées, baseline comprise (79 % contre 67 %).

Ça referme aussi la partie sur la fuite : c'est un humain qui a trouvé ce que
douze mesures avaient manqué, parce qu'il a changé d'avis sur un item.
L'instabilité est un signal, chez le juge comme chez le relecteur.
-->

---

## Et quand il n'y a pas d'humain ?

Parce que c'est le cas par défaut.

**Une porte** — la CI, la non-régression
→ l'item instable compte **FAIL**. On bloque.
Un doute doit coûter, sinon il ne sert à rien.

**Une mesure** — un échantillonnage descriptif
→ l'item instable est **exclu du taux, et compté à part.**
On ne le force pas, on le déclare.

**Même signal. Deux politiques.** Parce que se tromper ne coûte pas pareil.

<!--
C'est la question qu'on m'a posée et à laquelle je n'avais pas répondu : on ne
peut pas demander une relecture humaine à chaque fois. Personne ne fait vérifier
ses tests unitaires par un collègue à chaque échec.

Donc la règle par défaut doit être déclarée à l'avance, et elle dépend de ce que
le juge garde : une porte ou un thermomètre.

Le piège à éviter dans les deux cas : compter l'item douteux comme un succès.
C'est le seul choix qui se retourne toujours contre vous.
-->

---

## Le seuil n'est pas statistique. C'est votre budget.

Mon filtre de recevabilité exigeait **95 % de verdicts stables.**

**95 % de stabilité = 1 item sur 20 à relire.**
Si vous pouvez en relire un sur vingt, il vous faut 95 %.

Mon juge est à **58 %** — soit **21 items sur 50.**
Quatre fois mon budget.

**C'est pour ça qu'il n'est pas prêt pour la production.**

<!--
Ce seuil avait l'air arbitraire quand je l'ai écrit. Il ne l'est pas : il se
déduit de la quantité de relecture humaine qu'on peut réellement fournir.

Et le raisonnement s'inverse : commencez par votre budget. Combien d'items par
semaine un humain peut-il relire ? Ça vous donne le taux de stabilité qu'il faut
atteindre, et donc si votre juge est utilisable ou pas.

Je préfère finir là-dessus qu'en annonçant une réussite : le juge que je viens de
vous présenter échoue à son propre filtre, et je peux vous dire de combien.
-->

<!--
Ça ne s'invente pas, ça se lit dans le harnais : je fais déjà trois passes pour
mesurer la répétabilité. Le même chiffre sert à trier.

⚠ Réserve à énoncer : 29 items stables contre 21 instables. C'est une tendance,
pas un effet établi — mais elle va dans le même sens sur les deux variantes
mesurées, baseline comprise (79 % contre 67 %), ce qui la rend défendable.

Et ça referme la partie 2 : c'est un humain qui a trouvé la fuite que douze
mesures avaient manquée, parce qu'il a changé d'avis sur un item. L'instabilité
est un signal, chez le juge comme chez le relecteur.

L'objectif n'est pas de retirer l'humain de la boucle. C'est d'arrêter de lui
faire relire ce qui est évident, pour qu'il regarde ce qui ne l'est pas.
-->

---

## Aucun instrument n'a été juste du premier coup

| ce qui devait mesurer | ce qui l'a révélé |
|---|---|
| le corpus | un test de permutation, puis **un humain** |
| le script écrit pour trouver les fuites | la relecture du code devant un chiffre absurde |
| le relevé de coût — faux **trois fois** | une comparaison avec le débit du journal |
| le correctif de la fuite | le désaccord d'un relecteur, après douze mesures muettes |
| le banc d'essai — **cinq fois** | une sonde du contexte avant de lire les chiffres |

**Chacun a été corrigé parce qu'on a regardé.
Jamais parce qu'une métrique a protesté.**

<!--
C'est la conclusion, et c'est la phrase que je veux qu'on retienne : même le
harnais d'évaluation ne doit pas être construit sans observation ni réflexion.

On construit un juge pour arrêter d'avancer à l'aveugle. Mais le juge est
lui-même un instrument, et un instrument se vérifie. Sinon on a simplement
déplacé l'aveuglement d'un cran.

Aucune de ces erreurs n'a été signalée par le dispositif. Toutes ont été trouvées
en regardant quelque chose qui ne collait pas.
-->

---

## Trois choses à faire lundi

**1. Écrivez vos conventions avant de fine-tuner.**
Quatre phrases m'ont rapporté 76 points. Le fine-tuning, zéro.

**2. Décomposez en critères atomiques, contrôles avant verdict.**
Un LLM génère de gauche à droite. L'ordre des champs change le comportement.

**3. Exigez une preuve positive avant de dépenser du calcul.**
Un banc qui ne sait pas prouver qu'il a mesuré la bonne chose ne mesure rien —
et il le fait silencieusement.

<span class="ref">Tout le corpus, le protocole et les mesures sont dans le dépôt.</span>

<!--
Les trois sont applicables sans rien installer et sans budget.

La troisième est celle que j'aurais voulu entendre il y a six mois : elle m'a
coûté cinq mesures nulles et une conclusion publiable entièrement fausse.

Le dépôt contient tout ce qui permet de rejouer les chiffres de ce talk — le
corpus, le protocole pré-enregistré avec ses amendements datés, et les
générations écartées avec la raison de leur mise à l'écart.
-->
