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
  section table { display: table; width: 100%; font-size: 1rem; }
  section th, section td { padding: 0.4em 0.7em; }
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
RAGots et Hallucinations : votre chatbot passe devant le juge.

Le titre se lit à voix haute, sinon le jeu de mots se perd. Les RAGots, ce que
votre système raconte dans votre dos. Et « passer devant le juge », dans les deux
sens : le tribunal, et le juge automatique qu'on va construire ensemble.

Vingt minutes. Une question : comment savoir si mon RAG s'améliore, sans croire
mon juge sur parole.
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
grand-mère. Il demande au chatbot du site s'il peut obtenir le tarif deuil. Le
chatbot lui répond qu'il peut faire la demande après le voyage.

Cette politique n'existe pas. La vraie règle exige de la demander avant. Il paie
le plein tarif, et il attaque.

Devant le tribunal, Air Canada plaide que le chatbot est une entité juridique
distincte, responsable de ses propres actes.

Le tribunal répond — je vous le lis en anglais, c'est l'original : « This is a
remarkable submission. While a chatbot has an interactive component, it is still
just a part of Air Canada's website. »

Six cent cinquante dollars. Le montant est dérisoire, et c'est ce qui rend la
décision intéressante : ce n'est pas le préjudice qui compte, c'est le principe.
Vous répondez de ce que votre chatbot affirme.

==============================================================

⚠ Vérifié sur la décision : membre Christopher C. Rivers, 14 février 2024,
650,88 $ CA. Ne pas citer de mémoire le délai annoncé par le chatbot ni le total
avec frais — non vérifiés, volontairement absents de l'écran.
-->
---

<!-- _class: dense -->

## Et ce n'est pas un cas isolé

<div class="deux">
<div>

**DOCUMENTÉ** <span class="ref">— décision de justice ou document public</span>

- **Mata v. Avianca, 2023** — un avocat dépose **six décisions de justice inventées** par ChatGPT, avec des citations d'apparence normale. Le juge constate « conscious avoidance ». **5 000 $** de sanction. <span class="ref">S.D.N.Y., 22-cv-1461, juge P. Kevin Castel, 22 juin 2023</span>

- **NYC MyCity, audit public 2025** — le chatbot de la ville rend des réponses différentes à une question identique. L'administration annonçait **95 à 99 % d'exactitude** ; l'audit établit que ce calcul **excluait les réponses jugées perfectibles**. <span class="ref">Bureau du Contrôleur de New York, audit IT25PAR20028, 30 décembre 2025</span>

</div>
<div>

**RAPPORTÉ PAR LA PRESSE** <span class="ref">— non vérifié sur source primaire</span>

- **Deloitte Australie, 2025** — rapport à **440 000 AUD** remis à un ministère, références fabriquées, **~97 000 AUD remboursés**.

- **Chevrolet de Watsonville, 2023** — chatbot détourné par injection de prompt, accepte de vendre un véhicule pour **1 $**.

</div>
</div>

<!--
Et ce n'est pas un cas isolé. Je passe vite, vous les retrouverez dans le
support.

Mata contre Avianca : un avocat dépose au tribunal six décisions de justice
inventées par ChatGPT. Le juge parle d'évitement conscient. Cinq mille dollars de
sanction.

New York, audit public : le chatbot de la ville rend des réponses différentes à
une question identique. Et l'administration annonçait 95 à 99 % d'exactitude —
l'audit établit que ce calcul excluait les réponses jugées perfectibles.

En dessous, deux cas que je n'ai pas pu vérifier sur source primaire, et qui
restent donc étiquetés comme tels.

J'aurais pu en remplir beaucoup plus. Je ne garde que ceux que je peux prouver.

==============================================================

⚠ Deux secondes minimum à l'écran, sinon l'effet de volume tombe. Mata v.
Avianca : SIX décisions inventées, pas neuf — trois des noms qui circulent sont
de vraies décisions citées dans les fausses. Et l'audit de New York ne documente
PAS le conseil illégal : ça, c'est la presse.

⚠ Mata v. Avianca : SIX décisions inventées (Varghese, Shaboon, Petersen,
Martinez, Estate of Durden, Miller). Des résumés en annoncent neuf — les trois
autres noms qui circulent (Zicherman, Ehrlich, In re Air Crash Disaster) sont de
VRAIES décisions citées à l'intérieur des fausses. Ne pas se tromper en public.

⚠ NYC MyCity : l'audit du Contrôleur est une source primaire, VÉRIFIÉE. Mais il
ne documente PAS le conseil d'enfreindre la loi — ça, c'est The Markup, mars
2024, donc de la presse. Ne citer de l'audit que ce qu'il contient : les réponses
incohérentes, et le taux d'exactitude annoncé qui excluait les mauvais cas.

Et c'est le meilleur exemple du talk : une administration publie 95 % avec une
métrique qui écarte les cas gênants, et c'est un auditeur public qui le relève.
C'est exactement le sujet.

⚠ Deloitte descend chez les cas rapportés : concordant sur AP, Fortune et CFO
Dive, mais la source primaire du DEWR n'a jamais pu être ouverte. Si tu la
vérifies, la ligne peut remonter.
 
Diapositive à survoler, deux secondes minimum à l'écran — en dessous, la salle
ne perçoit pas qu'elle est dense et l'effet de volume tombe.

« J'aurais pu en remplir beaucoup plus — mais je ne garde que ceux que je peux
prouver. » Survol assumé : « je ne m'arrête pas, vous les retrouverez », jamais
« je n'ai pas le temps ».

Dire pourquoi la diapositive est coupée en deux : un talk sur la mesure
rigoureuse range ses propres anecdotes par niveau de preuve.
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
Alors pourquoi personne n'a rien vu ?

Parce que le faux avait exactement la forme du vrai. Un avocat ne relit pas une
citation bien formatée. « 925 F.3d 1339, onzième circuit, 2019 » — ça a la forme
d'une vraie référence, et c'est tout ce que notre œil vérifie.

Et nos outils ne nous aident pas. Un test unitaire vérifie une valeur de retour,
pas un raisonnement. Comparer mot à mot la réponse attendue et la réponse
obtenue, ça pénalise une bonne réponse formulée autrement et ça laisse passer une
mauvaise réponse bien écrite. Et de toute façon il n'y a pas d'oracle : la même
question admet dix bonnes réponses.

Donc on livre en se fiant à l'impression qu'on a en relisant trois sorties à la
main.
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
Moi, mon terrain, c'est OllamAssist. C'est un assistant de code dans mon IDE,
qui tourne entièrement sur ma machine. Je l'ai écrit pour comprendre ce que l'IA
fait vraiment, plutôt que de le lire. Un labo.

Au début, c'est un chatbot : je pose une question, il répond avec ce qu'il sait.

Puis c'est devenu un agent : il lit mon workspace, et il répond sur mon code.

Et là, tout change. Sa réponse ne dépend plus surtout du modèle. Elle dépend de
ce qu'il a trouvé.

C'est ce déplacement qui justifie de mesurer la récupération, et pas seulement le
modèle.

==============================================================

⚠ La carte de droite est un gabarit à remplacer la veille :
demo/img/ollamassist-marketplace.png, 768 x 638, même nom, puis relancer le
rendu. Les faits si on demande : plugin JetBrains sur la Marketplace, Ollama,
mode hors-ligne, 162 fichiers Java indexés — c'est ma codebase, donc je vois
quand il se trompe.

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

Je vais donc construire un juge. Et la question devient :
**comment savoir que mon RAG s'améliore, sans croire mon juge sur parole ?**

<!--
Comment mesurer la qualité des réponses de mon assistant ?

J'avais deux stratégies de récupération : Lucene d'un côté, un graphe Neo4j de
l'autre. Et aucun moyen de les départager.

Le seul juge disponible, c'était moi. Sur quelques exemples. Choisis par moi.
Trois rôles en conflit : j'écris le système, je choisis les cas de test, et je
juge.

Ma crainte, c'était d'avancer à l'aveugle. Modifier, livrer, et ne jamais savoir
si j'ai amélioré ou dégradé. Le mot exact, c'est tunnel : pas de retour, donc
chaque modification est un pari, et les paris s'accumulent.

Je vais donc construire un juge. Et la question devient : comment savoir que mon
RAG s'améliore, sans croire mon juge sur parole.
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
Le principe tient en une image.

On donne trois choses à un modèle : la question, le contexte qui a été récupéré,
et la réponse à évaluer. Il rend un verdict, et pourquoi.

Le point important, c'est qu'il ne génère pas la réponse. Il la juge. Ce sont
deux tâches d'une difficulté très différente — écrire un livre est difficile, le
lire et dire s'il est bon, beaucoup moins. Du coup un modèle plus petit suffit,
et ça change le prix.

Et notez les trois entrées : il voit aussi le contexte. C'est ce qui lui permet de
dire « cette réponse est peut-être vraie, mais rien dans le contexte ne
l'étaye ».
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
Il y a trois façons de s'y prendre, et je vais vous les donner en images.

La première : deux copies côte à côte, laquelle est la meilleure. Je sais les
classer. Je ne sais pas si l'une mérite la moyenne.

La deuxième : le corrigé type. Je compare la copie au corrigé. C'est fiable, mais
il faut écrire le corrigé de chaque question.

La troisième : le barème seul. Pas de corrigé, une liste de points à vérifier.
C'est mon choix — et tout repose alors sur le barème.

Pourquoi pas le corrigé ? Parce que sur du code, le corrigé est exactement ce que
je n'ai pas. Si je savais écrire la bonne réponse à mes soixante questions, je
n'aurais pas besoin de RAG.

==============================================================

⚠ Le « A contre B, puis B contre A » neutralise le biais de position ENTRE DEUX
RÉPONSES. Ce que j'ai mesuré est un biais de position sur L'ORDRE DES CONTEXTES
RÉCUPÉRÉS (12 verdicts sur 60). Même phénomène, dispositif différent : dire
lequel a été mesuré.
-->

---

## Première question : que ne PAS lui donner à juger

Avant de lire une copie, le correcteur vérifie trois choses :
elle est **signée**, elle est dans la **bonne matière**, elle n'est pas
**hors-sujet**.

Il ne lit pas pour ça. **Il écarte.**

```
  Ça compile ?             →  le compilateur
  Le JSON est valide ?     →  un parseur
  Le style tient ?         →  le linter
```

**Tout ce qui est déterministe ne passe pas par le juge.**
Pas pour l'économiser — **parce qu'il est moins bon que le compilateur à ça.**

Mon filtre à moi : l'équilibrage des parenthèses.
C'est tout. **Ce n'est pas un filtre, c'est un début.**

<!--
[À REFORMULER AVEC TES MOTS]

Première question, et elle est à l'envers de ce qu'on attend : qu'est-ce qu'il ne
faut surtout PAS donner à juger ?

Pensez à un correcteur devant une pile de copies. Avant d'en lire une seule, il
vérifie trois choses : qu'elle est signée, qu'elle est dans la bonne matière,
qu'elle n'est pas hors-sujet. Il ne lit pas pour ça. Il écarte.

Chez nous c'est pareil. Est-ce que ça compile ? Est-ce que le JSON est valide ?
Est-ce que le style tient ? Le compilateur, un parseur, le linter.

Et attention à la raison. Ce n'est pas pour économiser le juge. C'est parce qu'il
est moins bon que le compilateur à cette tâche-là : un compilateur répond en
cinquante millisecondes, ne coûte rien, et ne se trompe jamais.

Mon filtre à moi ? L'équilibrage des parenthèses. C'est tout. Ce n'est pas un
filtre, c'est un début — parce que ce que je fais juger, ce sont des explications
en prose qui contiennent du code, donc « est-ce que ça compile » ne s'applique
pas directement. Il faudrait extraire les blocs et les compiler à part. Je ne
l'ai pas fait. C'est une raison, pas une excuse.

==============================================================

⚠ Garder les DEUX moitiés de l'argument : le coût ET la fiabilité. Le coût seul
est la moitié faible. « Le prof à la deux-centième copie se trompe, le scanner
non. »

⚠ Ne pas réutiliser ici l'image du corrigé ou du QCM : elle sert déjà la
diapositive 8, pour une idée différente. Ici le geste est « écarter avant de
lire », pas « comparer à une référence ».

⚠ Cette idée revient en partie 3 sous une autre forme : hintCoverage, un contrôle
déterministe sans LLM. En amont il économise des jetons, en aval il sert de
contre-expertise.
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
[À REFORMULER AVEC TES MOTS]

Deuxième question : quand ?

Dans la CI, à chaque modification : c'est de la non-régression. On rejoue les
mêmes questions. Et comme elles ne changent pas, le corrigé type ou le barème
fonctionnent tous les deux.

En production, par échantillonnage. Là, plus de questions figées, donc le barème
seul. Combien, à quelle fréquence ? Ça dépend de trop de choses pour que j'en
parle ici. Un échantillon suffit.

Moi, je suis à cent pour cent dans la CI. Aucun échantillonnage de production.

Et c'est la CI qui ferme le tunnel : rejouer les mêmes questions, c'est la seule
façon de savoir si ma modification améliore ou dégrade — et la seule façon de
comparer deux stratégies.
-->

---

## Le correcteur se laisse impressionner par l'épaisseur

Quatre pages, c'est sérieux. Une réponse courte, ça fait négligé.

**Le même défaut, écrit deux fois** — une version bavarde, une version sèche.
Si le juge valide plus souvent la bavarde, il note la forme, pas le fond.

**Chez moi : 46 % de faux PASS sur les défauts bavards.**

<!--
[À REFORMULER AVEC TES MOTS]

Premier biais, et c'est le plus humain : le correcteur se laisse impressionner
par l'épaisseur de la copie. Quatre pages, ça fait sérieux. Une réponse en trois
lignes, ça fait bâclé.

Comment je le détecte ? J'écris le même défaut deux fois. Une version bavarde,
une version sèche. Même erreur, deux habillages. Si mon juge valide plus souvent
la bavarde, il note la forme et pas le fond.

Chez moi, 46 % de faux PASS sur les défauts bavards.

==============================================================

[AJOUT AU SCHÉMA : le jeu de questions doit être APPARIÉ — chaque défaut existe
en version longue et en version courte. C'est une contrainte sur le corpus, pas
sur le pipeline.]

⚠ Le chiffre exact : 46 % de faux PASS sur défauts verbeux contre 42 % sur
défauts concis — l'écart lui-même est petit, c'est le NIVEAU qui est mauvais.
Ne pas vendre l'écart, vendre le niveau.
-->

---

## Le même devoir, selon sa place dans la pile

La première copie et la vingtième ne sont pas notées pareil.

Pour un juge, c'est **l'ordre des extraits** qu'on lui donne.

**Je mélange le contexte — avec une graine tirée de la question**, pour que la
mesure se rejoue à l'identique.

Ça atténue. Ça ne supprime pas :
**12 verdicts sur 60 basculent au seul réordonnancement.**

<!--
[À REFORMULER AVEC TES MOTS]

Deuxième biais : la place dans la pile. Un correcteur ne note pas la première
copie comme la vingtième. Pour un juge LLM, ce n'est pas la pile, c'est l'ordre
des extraits qu'on lui donne dans le contexte.

Ma parade : je mélange les extraits. Mais attention — avec une graine tirée de la
question, sinon la mesure n'est plus rejouable, et j'en ai fait les frais.

Et je veux être honnête : ça atténue, ça ne supprime pas. Douze verdicts sur
soixante basculent au seul réordonnancement, à récupération strictement
identique.

==============================================================

[AJOUT AU SCHÉMA : une boîte « mélange graîné » entre la récupération et le juge.]

⚠ Sans graine, les exécutions de la veille faisaient bouger le même bras de
55,9 % à 43,3 %. Une mesure qui ne se rejoue pas n'est pas une mesure.

⚠ Ne pas confondre avec le « A contre B puis B contre A » de la comparaison par
paires : là c'est l'ordre de DEUX RÉPONSES, ici c'est l'ordre des EXTRAITS.
-->

---

## Un correcteur indulgent a l'air fiable

Il valide presque tout. Donc il se trompe rarement.
Il ne se trompe que sur les copies qu'il aurait dû recaler.

```
   27 mauvaises copies   →  il en recale 16.  Il en laisse passer 11.
   23 bonnes copies      →  il en valide 22.
```

**76 % de décisions justes. Et 4 défauts sur 10 qui passent.**

Le même juge, deux chiffres. **Ne publiez jamais le premier sans le second.**

<!--
[À REFORMULER AVEC TES MOTS]

Troisième biais, et c'est celui qu'aucun tableau ne montre : l'indulgence.

Un correcteur qui valide presque tout se trompe rarement. Forcément : il ne se
trompe que sur les copies qu'il aurait dû recaler.

Mon juge, sur vingt-sept mauvaises réponses, en recale seize. Il en laisse passer
onze. Sur vingt-trois bonnes, il en valide vingt-deux.

Ça fait soixante-seize pour cent de décisions justes — et quatre défauts sur dix
qui passent. Le même juge, deux chiffres.

Et pour moi les deux erreurs n'ont pas le même prix : un défaut qui passe, c'est
une explication fausse sur ma codebase livrée à l'utilisateur. Un bon code
recalé, c'est juste une relecture inutile.

==============================================================

[AJOUT AU SCHÉMA : le juge ne sort pas UN chiffre mais DEUX — les décisions
justes, et les erreurs attrapées.]

⚠ Un juge qui répondrait PASS à tout sur un corpus où 95 % des réponses sont
bonnes afficherait 95 % d'exactitude et attraperait zéro erreur. C'est l'exemple
à donner si quelqu'un doute.

⚠ Ce biais recoupe les deux autres : 46 % de faux PASS sur les défauts verbeux,
et un juge qui rend PASS 64 % du temps là où l'étalon en compte 46 %. Trois
mesures indépendantes, un même diagnostic.
-->

---

## Et il y a le quatrième, que je n'ai pas mesuré

**L'auto-préférence** : un modèle préfère ce qui ressemble à ce qu'il aurait
écrit.

Je ne l'ai **pas mesuré chez moi**. Je le cite.

La parade connue : **ne pas faire juger un modèle par sa propre famille.**

<!--
[À REFORMULER AVEC TES MOTS]

Il y en a un quatrième, et je vais être clair sur son statut : l'auto-préférence.
Un modèle préfère ce qui ressemble à ce qu'il aurait écrit lui-même.

Celui-là, je ne l'ai pas mesuré. Je le cite. La parade connue, c'est de ne pas
faire juger un modèle par un modèle de sa propre famille.

Je le dis parce que mélanger ce qu'on a mesuré et ce qu'on a lu, c'est la
meilleure façon de perdre la confiance de la salle sur tout le reste.

==============================================================

⚠ C'est la diapositive qui protège les trois précédentes. Si on ne distingue pas
mesuré et cité, la salle a raison de douter de tout. Référence pour les biais de
position, verbosité et auto-préférence : Zheng et al., NeurIPS 2023, MT-Bench.

⚠ Possible de la fusionner avec la précédente si le temps manque — mais ne pas la
supprimer : c'est elle qui rend les trois autres crédibles.
-->

---

## Et le RAG a ses propres pièges

Trois cas, tirés de **vraies extractions** sur ma codebase. Rien d'inventé.

**Le quasi-homonyme** — je demande `OllamaService`, le moteur rend
`OllamaSettings`. Même forme, classe voisine, interface sans rapport.
Le contexte **ressemble** à une réponse.

**Les corps tronqués** — dix extraits, pas un seul corps de méthode, pour une
question en « comment ». Les noms annoncent une intention, ils ne livrent pas la
mécanique.

**Le vrai mais non étayé** — une réponse exacte dans ma codebase, mais absente du
contexte fourni. **Elle doit tomber.**

<!--
[À REFORMULER AVEC TES MOTS]

Jusqu'ici j'ai parlé des biais du juge. Mais le RAG a les siens, et ils arrivent
avant — ils sont dans le contexte qu'on donne au juge.

Trois cas, et ce sont de vraies extractions sur ma codebase, gardées telles
quelles.

Le quasi-homonyme. Je demande OllamaService, le moteur me rend OllamaSettings.
Même forme, classe voisine, interface sans aucun rapport. Le contexte ressemble à
une réponse — et il invite à répondre faux.

Les corps tronqués. Dix extraits, pas un seul corps de méthode, pour une question
qui commence par « comment ». Les noms annoncent une intention, ils ne livrent
pas la mécanique.

Et le plus subtil : le vrai mais non étayé. Une réponse exacte — elle est juste,
je peux le vérifier dans ma codebase — mais rien dans le contexte fourni ne
l'appuie. Celle-là doit tomber. Parce que si je l'accepte au motif qu'elle est
vraie, je valide le même comportement sur un dossier où il aura inventé.

==============================================================

⚠ C'est la promesse de l'abstract : « comprendre quelques biais des systèmes
RAG », pas seulement des biais de juge. Ne pas sauter cette diapositive.

⚠ Le troisième cas est le test décisif de la posture en monde fermé. Si la salle
ne retient qu'un des trois, c'est celui-là.
-->

---

## Ce que ça change pour le juge

Si le contexte peut tromper, alors **juger la réponse ne suffit pas.**

Le juge reçoit **trois choses**, pas deux : la question, **le contexte**, et la
réponse.

Et il répond séparément :

```
   le contexte est-il pertinent ?
   permet-il de répondre sans rien supposer ?
   la réponse s'appuie-t-elle sur lui ?
```

C'est ce qui distingue **un défaut de récupération** d'un **défaut de
génération**.

<!--
[À REFORMULER AVEC TES MOTS]

Alors qu'est-ce que ça change pour mon juge ?

Si le contexte peut tromper, juger la réponse ne suffit plus. Le juge doit
recevoir trois choses, pas deux : la question, le contexte, et la réponse.

Et il doit répondre séparément : est-ce que le contexte est pertinent ? Est-ce
qu'il permet de répondre sans rien supposer ? Est-ce que la réponse s'appuie
dessus ?

Parce que c'est ce qui me permet de distinguer deux pannes très différentes : le
moteur n'a rien trouvé d'utile, ou le modèle a mal utilisé ce qu'il avait.

Sans ça, j'ai un taux d'échec et aucune idée de quoi corriger.

==============================================================

[AJOUT AU SCHÉMA : le contexte récupéré entre DANS le juge, pas seulement dans
l'assistant. Et la sortie du juge se décompose.]

⚠ C'est ce qui permettra, plus tard, de dire que Neo4j souffre d'un défaut de
rappel — 66 % de contextes jugés insuffisants contre 40 % — et pas d'un problème
de bruit. Sans cette décomposition : 25 points d'écart sans explication.
-->

---

## Donc j'ai un juge. Mais s'il se trompe ?

Tout ce qu'on vient de faire sert à **mieux juger**.
Rien ne dit que **ça marche**.

Deux questions, et il faut les deux :

```
   est-il d'accord avec un humain ?     →  son alignement
   est-il d'accord avec lui-même ?      →  sa stabilité
```

Un juge qui change d'avis d'une lecture à l'autre n'est pas un juge.
Un juge constant mais faux non plus.

<!--
[À REFORMULER AVEC TES MOTS]

Donc voilà, j'ai un juge. Des critères, un format, des parades contre les biais.

Sauf que tout ce que je viens de vous montrer sert à mieux juger. Rien, là-dedans,
ne me dit que ça marche.

Et pour le savoir, il faut deux questions, pas une. Est-ce qu'il est d'accord
avec un humain — c'est son alignement. Et est-ce qu'il est d'accord avec
lui-même — c'est sa stabilité.

Les deux comptent. Un juge qui change d'avis d'une lecture à l'autre n'est pas un
juge. Mais un juge parfaitement constant et parfaitement faux non plus.

==============================================================

⚠ C'est la bascule du talk. Ralentir, marquer un temps.

⚠ Ne pas annoncer la réponse ici. Le fait que mon juge échoue son propre seuil
arrive plus tard, et ça n'a de force que si la question est posée franchement
d'abord.
-->

---

## Mesurer un accord, c'est enlever le hasard

Deux correcteurs qui **recaleraient tout le monde sans rien lire** seraient
d'accord 9 fois sur 10, si 9 copies sur 10 sont mauvaises.

Deux correcteurs, 100 copies, d'accord sur **90**.
Chacun valide une copie sur cinq — donc **même au hasard**, ils tomberaient
d'accord **68 fois**.

```
  0                                        68          90        100
  ├──────── donné par le hasard ────────────┼─ conquis ─┼─ raté ──┤
                                               22           10
```

**κ = 22 conquis sur les 32 qui restaient = 0,69**

<!--
[À REFORMULER AVEC TES MOTS]

Avant de vous donner mes chiffres, il faut un outil, parce que l'accord brut ne
veut rien dire.

Imaginez deux correcteurs qui recaleraient tout le monde, sans rien lire. Si neuf
copies sur dix sont mauvaises, ils sont d'accord neuf fois sur dix. Leur accord
ne mesure pas leur compétence, il mesure le déséquilibre du paquet.

Alors prenons un vrai cas. Deux correcteurs, cent copies, d'accord sur
quatre-vingt-dix. Chacun valide une copie sur cinq. Donc même en cochant au
hasard, ils tomberaient d'accord soixante-huit fois sur cent.

Partant de soixante-huit, il ne restait que trente-deux points à conquérir. Ils
en ont pris vingt-deux. Kappa, c'est ça : la part conquise de ce qu'il restait à
conquérir. Zéro virgule soixante-neuf — alors que l'accord brut affichait
quatre-vingt-dix pour cent.

==============================================================

⚠ Échelle usuelle, si on demande : au-dessus de 0,8 fort, 0,6 à 0,8 correct,
0,4 à 0,6 moyen. Ce sont des conventions, pas des lois.

⚠ Et le piège marche dans les deux sens : sur mon critère le plus fréquent,
78 % d'accord brut pour un κ de 0,386. Le paquet est très déséquilibré, donc le κ
paraît médiocre alors que les relecteurs se trompent rarement. Donner le κ seul
sous-estime, donner le pourcentage seul surestime.
-->

---

## Deux κ qu'on confond tout le temps

| | ce qu'il mesure | |
|---|---|---|
| **κ du corpus** | l'humain contre mes étiquettes | **0,880** |
| **κ du juge** | le juge contre l'étalon | **0,44** |

Le premier dit *« ma règle est-elle fiable ? »*.
Le second dit *« mon juge est-il aligné ? »*.

**0,880 entre humains. 0,44 pour le juge.**
Le plafond n'est pas le modèle — **c'est ce que mon corpus enseigne.**

<!--
[À REFORMULER AVEC TES MOTS]

Et là il y a deux kappas qu'on confond tout le temps.

Le premier mesure l'accord entre un humain et mes étiquettes de référence. Il
répond à : est-ce que ma règle est fiable ? Parce que mesurer contre une règle
fausse ne vaut rien. Il vaut zéro virgule quatre-vingt-huit — deux personnes ont
relu les mêmes copies, séparément, sans se parler.

Le second mesure l'accord entre mon juge et cette règle. Il répond à : est-ce que
mon juge est aligné ? Il vaut zéro virgule quarante-quatre.

Présenter le premier à la place du second, c'est l'erreur la plus fréquente, et
la plus flatteuse : on annonce un alignement qu'on n'a jamais mesuré.

Et l'écart entre les deux est la vraie information. Mon plafond n'est pas le
modèle. C'est ce que mon corpus lui enseigne.

Une dernière chose, découverte en mesurant, et c'est peut-être le conseil le plus
utile de tout le talk : l'invite nue de mon juge ne rendait aucun JSON
exploitable. Zéro sur cent cinquante. Quatre phrases de conventions écrites l'ont
fait passer à soixante-seize pour cent de réponses justes. Avant d'envisager quoi
que ce soit de plus sophistiqué — écrivez vos conventions.

==============================================================

⚠ Le κ du corpus vient d'une relecture en aveugle AVANT discussion : 47 verdicts
identiques sur 50. IC 95 % [0,720 — 1,000].

⚠ Le κ du juge : 0,44, IC [0,27 — 0,60].

⚠ Pourquoi le corpus plafonne : sur 50 items, 17 portent un désaccord sur au
moins un contrôle, dont 15 que le verdict masque. Le verdict est reproductible,
les raisons beaucoup moins — et c'est sur les raisons qu'un juge apprend.

⚠ Les conventions : 0 % → 76 % de réponses justes, et 0 % → 100 % de JSON
exploitable. C'est l'item à ne pas perdre si on coupe cette diapositive.
-->

---

## Le banc : 60 questions sur ma codebase

| niveau | ce qu'il teste |
|---|---|
| **LOCAL** | une méthode précise, dans un seul fichier |
| **STRUCTURAL** | héritage, interfaces, ce qui implémente quoi |
| **CROSS_MODULE** | une chaîne qui traverse plusieurs paquets |

Les **mêmes** 60 questions pour les deux stratégies, dans la **même** exécution.

Mélange du contexte **graîné par la question** → la mesure se rejoue à
l'identique.

<!--
[À REFORMULER AVEC TES MOTS]

Maintenant le banc. Soixante questions sur ma codebase, en trois niveaux.

Local : une méthode précise, dans un seul fichier. Structural : héritage,
interfaces, ce qui implémente quoi. Et inter-modules : une chaîne qui traverse
plusieurs paquets — c'est là qu'on attend le graphe.

Deux choses qui comptent plus qu'elles n'en ont l'air.

Les deux stratégies répondent aux mêmes questions, dans la même exécution. C'est
ce qui autorise une comparaison appariée, et une comparaison appariée est
beaucoup plus puissante à effectif égal.

Et le mélange du contexte est tiré de la question. Sans ça, la mesure ne se
rejoue pas — et j'en ai fait les frais : les exécutions de la veille faisaient
bouger le même bras de cinquante-six à quarante-trois pour cent.

==============================================================

⚠ Ne pas appeler ces 60 questions « golden set » : l'étalon, c'est les 50 items
étiquetés qui servent à vérifier le juge. Deux jeux, deux rôles.
-->

---

## Le résultat

| | Lucene | Neo4j |
|---|---|---|
| **Réponses justes** | **48 %** | **24 %** |
| Contexte jugé insuffisant | 40 % | **66 %** |

Sur 60 questions, **24 les départagent**. Lucene en gagne **19**, Neo4j **5**.
Le hasard donnerait 12–12 : c'est tirer **19 fois pile sur 24 lancers**.

Et une mesure **sans aucun LLM** — compter les identifiants attendus dans le
contexte — **les classe dans le même ordre**.

<span class="ref">Sur ce corpus, selon ce juge.</span>

<!--
[À REFORMULER AVEC TES MOTS]

Le résultat. Lucene, quarante-huit pour cent de réponses justes. Mon graphe
Neo4j, vingt-quatre.

Mais le chiffre qui m'intéresse est le deuxième : le contexte de Neo4j est jugé
insuffisant deux fois sur trois, contre quatre fois sur dix pour Lucene. Ce n'est
pas un problème de bruit, c'est un défaut de rappel — le moteur ne rapporte pas
assez de matière. Sans mes critères décomposés, j'aurais vingt-cinq points
d'écart et aucune idée de quoi corriger.

Sur les soixante questions, vingt-quatre les départagent — les trente-six autres,
les deux font pareil, elles ne tranchent rien. Lucene en gagne dix-neuf, Neo4j
cinq. Le hasard donnerait douze-douze. Obtenir dix-neuf contre cinq, c'est tirer
dix-neuf fois pile sur vingt-quatre lancers.

Et pour ne pas dépendre du seul juge : une mesure qui ne passe par aucun modèle —
je compte les identifiants attendus dans le contexte récupéré — classe les deux
dans le même ordre. Elle ne valide pas les verdicts, elle mesure autre chose.
Mais deux instruments indépendants qui classent pareil, c'est mieux qu'un seul.

==============================================================

⚠ p = 0,0066. hintCoverage 0,697 contre 0,596.

⚠ Ne PAS dire que hintCoverage valide le juge : il corrobore un CLASSEMENT et
mesure une autre propriété.

⚠ La réserve à énoncer : sur ce corpus, selon ce juge — dont l'alignement est de
0,44. Un écart de 25 points est large, mais c'est une comparaison, pas une
vérité sur GraphRAG.
-->

---

## Moteur, ou traversée de graphe ?

J'ai rejoué les 60 questions **sans** l'expansion de graphe.
Et j'ai laissé **Lucene strictement identique** : son taux **doit** être le même.

**Il l'est. 48,3 %, à la décimale, et sur les trois niveaux.**

Le témoin n'a pas bougé. Neo4j, lui, gagne **1,7 point — une question sur 59.**

**L'écart vient du moteur de récupération, pas du parcours de graphe.**

<!--
[À REFORMULER AVEC TES MOTS]

Mais attention. Mon pipeline Neo4j fait deux choses : il cherche, puis il étend
la recherche en suivant les liens du graphe. Lequel des deux pose problème ?

Alors j'ai rejoué les soixante questions sans l'expansion de graphe. Et surtout,
j'ai laissé Lucene strictement identique dans les deux exécutions. Son taux doit
donc être le même.

Il l'est. Quarante-huit virgule trois pour cent, à la décimale, et sur chacun des
trois niveaux. Le témoin n'a pas bougé — et c'est ça qui rend l'attribution
possible. S'il avait bougé, je n'aurais rien pu conclure du tout.

Neo4j, lui, gagne un virgule sept point. Une question sur cinquante-neuf.

Donc l'écart vient du moteur de récupération, pas de la traversée. Et la nuance
compte : je ne dis pas « le graphe est mal implémenté ». Je dis que ce
pipeline-là rapporte moins de matière. Ce n'est pas la même critique, et ce n'est
pas le même correctif.

==============================================================

⚠ C'est la diapositive qui rend tout le reste défendable. Le bras témoin
invariant est la seule chose qui autorise à attribuer l'écart.
-->

---

## Ce qui conclut, et ce qui ne conclut pas

Sur les trois niveaux, **un seul écart tient** : les questions inter-modules.
Là, sur les 8 questions où les deux ont divergé, **Lucene a gagné les 8.**

Sur les deux autres : **5 piles sur 7, et 6 sur 9. Banal.**

**Deux écarts sur trois ne concluent pas** — et c'était une limite
**annoncée avant** de lancer la mesure, pas une surprise.

<!--
[À REFORMULER AVEC TES MOTS]

Et je veux être honnête sur ce qui conclut.

Par niveau, un seul écart tient : les questions inter-modules. Là, sur les huit
questions où les deux stratégies ont divergé, Lucene a gagné les huit. Huit piles
d'affilée.

Sur les deux autres niveaux : cinq piles sur sept, et six sur neuf. Banal.

Donc deux écarts sur trois ne concluent pas. Et ce n'est pas une surprise : à cet
effectif, je savais avant de lancer que je ne verrais rien en dessous d'un
certain écart. C'était écrit dans mon protocole.

Dire « non concluant » sur deux niveaux, c'est ce qui donne du poids au
troisième. Si j'avais présenté les trois comme trois résultats — les écarts bruts
vont tous dans le même sens — vous auriez eu raison de ne pas me croire.

==============================================================

⚠ p : LOCAL 0,453 · STRUCTURAL 0,508 · CROSS_MODULE 0,0078.

⚠ C'est ici que vit la discipline du « non concluant déclaré d'avance ». Ne pas
la perdre : c'est ce qui distingue ce talk d'une démonstration arrangée.
-->

---

## Cinq fois, mon banc a mesuré le vide

Et cinq fois, il a affiché **BUILD SUCCESS**.

La pire : une option d'adaptateur **acceptée, puis ignorée**.
Deux heures de calcul. 150 réponses plausibles. Et un rapport annonçant
**« le fine-tuning dégrade la justesse de 76 % »**, intervalle de confiance
compris.

**Publiable tel quel. Entièrement faux.**

Aucune erreur. Aucun avertissement.

<!--
[À REFORMULER AVEC TES MOTS]

Dernière chose, et c'est le retour d'expérience qui m'a le plus coûté.

Cinq fois, mon banc d'essai a mesuré le vide. Et cinq fois, il a affiché « build
success ».

Je vous raconte la pire. J'avais passé une option pour charger un modèle
particulier. Le serveur l'a acceptée — et il a répondu avec un autre. Deux heures
de calcul, cent cinquante réponses parfaitement plausibles, aucune erreur, aucun
avertissement.

Et au bout, un rapport avec son intervalle de confiance, qui m'annonçait un
résultat net. Publiable tel quel. Entièrement faux.

Ce qui a fini par le révéler, ce n'est pas une métrique. C'est un détail de
style dans les réponses, qui ne collait pas à ce que j'attendais.

La leçon, et c'est le correctif que j'ai mis en place : avant de dépenser une
heure de calcul, faites un appel, et vérifiez une propriété qui ne peut pas
apparaître par hasard si la plomberie est cassée. Pas l'absence d'erreur. Une
preuve positive.

==============================================================

⚠ Les quatre autres, si on demande : options non transmises par le lanceur de
tests, propriété vide au lieu de l'adaptateur, un pgrep qui matchait son propre
script, un mélange non graîné. Ne pas les énumérer à l'écran — cinq bugs
cryptiques enterrent le signal, qui est le NOMBRE.
-->

---

## Aucun instrument n'a été juste du premier coup

| ce qui devait mesurer | ce qui l'a révélé |
|---|---|
| le corpus | un test de permutation, puis **un humain** |
| le relevé de coût — faux **trois fois** | une comparaison avec le journal |
| le correctif d'une fuite | le désaccord d'un relecteur |
| le banc d'essai — **cinq fois** | une sonde avant de lire les chiffres |

**Chacun a été corrigé parce qu'on a regardé.
Jamais parce qu'une métrique a protesté.**

<!--
[À REFORMULER AVEC TES MOTS]

Je termine là-dessus.

Le corpus devait mesurer la qualité : il contenait des fuites. Mon relevé de coût
était faux trois fois. Le correctif d'une fuite en a créé une pire. Et mon banc
d'essai a mesuré le vide cinq fois.

Regardez la colonne de droite. Un test de permutation. Un humain. Une comparaison
avec le journal. Une sonde avant de lire les chiffres.

Chacun a été corrigé parce qu'on a regardé. Jamais parce qu'une métrique a
protesté.

C'est la phrase que je veux que vous reteniez : on construit un juge pour arrêter
d'avancer à l'aveugle. Mais le juge est lui-même un instrument. Et un instrument,
ça se vérifie. Sinon on a simplement déplacé l'aveuglement d'un cran.

==============================================================

⚠ Ralentir. C'est la conclusion.
-->

---

## Trois choses à faire lundi

**1. Écrivez vos conventions avant tout le reste.**
Chez moi : d'aucun JSON exploitable à 76 % de réponses justes. Quatre phrases.

**2. Décomposez en critères, et mettez les contrôles avant le verdict.**
Un modèle génère de gauche à droite. L'ordre des champs change le comportement.

**3. Exigez une preuve positive avant de dépenser du calcul.**
Un banc qui ne sait pas prouver qu'il a mesuré la bonne chose ne mesure rien —
et il le fait silencieusement.

<span class="ref">Corpus, protocole et mesures : le dépôt est partagé.</span>

<!--
[À REFORMULER AVEC TES MOTS]

Trois choses, applicables lundi, sans rien installer.

Un. Écrivez vos conventions avant tout le reste. Chez moi, mon juge passait
d'aucun JSON exploitable à soixante-seize pour cent de réponses justes. Pour
quatre phrases.

Deux. Décomposez en critères, et mettez les contrôles avant le verdict. Un modèle
génère de gauche à droite — l'ordre des champs change son comportement, et ça ne
coûte rien à corriger.

Trois. Exigez une preuve positive avant de dépenser du calcul. Un banc qui ne
sait pas prouver qu'il a mesuré la bonne chose ne mesure rien, et il le fait
silencieusement.

Tout est dans le dépôt : le corpus, le protocole avec ses amendements datés, et
les générations écartées avec la raison de leur mise à l'écart.

Merci.

==============================================================

⚠ Les trois sont applicables sans budget et sans installation. C'est ce qui en
fait des actions et pas des conseils.
-->

---

## Les sources

**Les incidents** — tous vérifiés sur la source primaire
<span class="ref">Moffatt v. Air Canada, 2024 BCCRT 149 · Mata v. Avianca, S.D.N.Y. 22-cv-1461 · NYC Comptroller, audit IT25PAR20028</span>

**Les biais du juge** — position, verbosité, auto-préférence
<span class="ref">Zheng et al., NeurIPS 2023 — MT-Bench & Chatbot Arena, arXiv 2306.05685</span>

**Questions binaires plutôt que notes graduées**
<span class="ref">CheckEval, Lee et al., EMNLP 2025 — aclanthology.org/2025.emnlp-main.796</span>

**Pour aller plus loin** — le raisonnement en chaîne, et sa fidélité
<span class="ref">Sprague et al., ICLR 2025, arXiv 2409.12183 · Turpin et al., NeurIPS 2023 · Lanham et al., arXiv 2307.13702</span>

**OllamAssist** — le plugin, et tout le protocole
<span class="ref">plugins.jetbrains.com/plugin/26388 · github.com/baretto-labs/llm-as-a-judge</span>

<!--
[À REFORMULER AVEC TES MOTS]

Je ne lis pas cette diapositive. Je la laisse deux secondes, je dis qu'elle est
dans le support partagé, et j'enchaîne.

Deux choses à dire quand même, parce qu'elles disent ce que vaut le reste. Les
trois incidents du début, je les ai vérifiés sur la source primaire : la décision
de justice, l'opinion du juge, le rapport d'audit. Et les affirmations que je
n'ai pas mesurées moi-même sont là, avec leur référence — vous pouvez aller voir.

==============================================================

⚠ UNE SEULE source académique pour « binaire plutôt que gradué » : CheckEval. Ne
pas dire « les études montrent », dire « une étude montre ». Et elle vaut pour
les tâches qu'elle a étudiées.

⚠ « Pour aller plus loin » est étiqueté comme tel parce que ces trois références
ne soutiennent rien de ce qui est affirmé dans le talk — elles ouvrent une suite.
Ne pas les présenter comme des appuis.

⚠ Deloitte n'est PAS sur cette diapositive : sa source primaire n'a jamais été
ouverte. Si on la vérifie un jour, elle peut y entrer.
-->

---

## Dites-moi ce qui n'a pas marché

<div class="carte">
<div class="texte">

Ce talk raconte **cinq mesures qui m'ont menti** parce que personne ne les avait
regardées.

Alors regardez celle-ci.

Ce qui n'était pas clair, ce qui vous a semblé faux, ce que vous auriez fait
autrement : **c'est ce qui me sert.**

</div>
<img src="img/qr-feedback.png" width="300" height="300" alt="QR code de retour">
</div>

<!--
[À REFORMULER AVEC TES MOTS]

Une dernière chose, et c'est une demande.

Ce talk raconte cinq mesures qui m'ont menti, simplement parce que personne ne
les avait regardées. Alors regardez celle-ci.

Ce qui n'était pas clair, ce qui vous a paru faux, ce que vous auriez fait
autrement — c'est exactement ce qui me sert. Le QR code est là, il y restera
pendant les questions.

Merci.

==============================================================

⚠ À FAIRE AVANT : générer le QR vers ton formulaire et écraser
demo/img/qr-feedback.png — même nom, 620 x 620, puis relancer le rendu.

⚠ Laisser cette diapositive affichée pendant les questions : c'est le moment où
les gens dégainent leur téléphone.

⚠ L'angle « vous avez vu un talk sur la vérification, vérifiez-moi » est
cohérent avec le propos. Éviter le « n'hésitez pas à me faire un retour » neutre.
-->
