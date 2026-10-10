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
