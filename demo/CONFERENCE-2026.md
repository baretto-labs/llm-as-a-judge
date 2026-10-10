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
Première question à se poser, et elle est à l'envers de ce qu'on attend : qu'est-ce
qu'il ne faut PAS donner à juger ?

Tout ce qui est déterministe. Ça compile ? Le JSON est valide ? Le style tient ?
Le compilateur, un parseur, le linter. C'est la copie hors-sujet, écartée avant
d'être lue.

Un compilateur répond en cinquante millisecondes, ne coûte rien, et n'a pas
d'humeur. Demander ça à un modèle, c'est payer pour une réponse moins fiable.

Et mon filtre à moi ? L'équilibrage des parenthèses. C'est tout. Ce n'est pas un
filtre, c'est un début — parce que ce que je fais juger, ce sont des explications
en prose qui contiennent du code, donc « est-ce que ça compile » ne s'applique
pas directement. Il faudrait extraire les blocs et les compiler à part. Je ne
l'ai pas fait. C'est une raison, pas une excuse.
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

## Troisième question : quel format de verdict ?

Pas une note sur 10. **PASS / FAIL.**

**Parce que « 13/20 », ça ne veut rien dire.**
Est-ce qu'on livre, ou pas ? La note ne répond pas.

Et une note invite les cinq erreurs du correcteur d'un coup :
la longueur impressionne, la main glisse vers le milieu,
et personne ne peut dire ce qui sépare 13 de 14.

**Une question binaire force la décision.** Elle se discute, donc elle se corrige.

Et elle convient **à mon cas** : des critères qu'on tranche un par un, une
décision de livraison, et des erreurs dont le coût n'est pas le même des deux
côtés.

Mesuré ailleurs : douze modèles évaluateurs notent les mêmes textes.
Avec une échelle, leur accord vaut **0,09** — autant dire rien.
Avec des questions binaires, **0,48**.

<span class="ref">CheckEval, EMNLP 2025 — Lee et al.</span>

<!--
Troisième question : sous quelle forme il rend son verdict.

Pas une note sur dix. Pass ou fail.

Parce que « treize sur vingt », ça ne veut rien dire. Est-ce qu'on livre, ou pas ?
La note ne répond pas. Et une note invite d'un coup toutes les erreurs du
correcteur : la longueur impressionne, la main glisse vers le milieu, et personne
ne peut dire ce qui sépare treize de quatorze.

Une question binaire force la décision. Elle se discute, donc elle se corrige.

Et elle convient à mon cas : des critères qu'on tranche un par un, une décision
de livraison, et des erreurs dont le coût n'est pas le même des deux côtés.

Mesuré ailleurs, pas par moi : douze modèles évaluateurs notent les mêmes textes.
Avec une échelle, leur accord vaut zéro virgule zéro neuf — autant dire rien. Avec
des questions binaires, zéro virgule quarante-huit.

⚠ Dire clairement que ce point vient de la littérature. Et CheckEval vaut pour
les tâches étudiées — ça ne prouve pas qu'un verdict binaire soit meilleur
partout, d'où la justification par mon cas.

⚠ Les chiffres exacts, vérifiés dans le papier (arXiv 2403.18771, tables IEA) :
Krippendorff α passe de 0,09 à 0,48 sur SummEval, et de 0,06 à 0,45 sur
Topical-Chat, entre une notation en échelle (G-Eval) et les questions binaires.
L'abstract annonce « +0,45 d'accord moyen » ; les écarts lisibles dans les tables
font plutôt +0,39, la moyenne de l'abstract portant sur plus de groupes. D'où
l'avant/après à l'écran plutôt que le gain — il est tiré de la table et
inattaquable.

Si la question « 0,48 c'est faible, non ? » vient : oui, c'est moyen. Mais le
point n'est pas le niveau atteint, c'est le départ. 0,09, c'est l'accord de
correcteurs qui cocheraient au hasard.

À dire clairement : ce point-là, je ne l'ai pas mesuré, je m'appuie sur la
littérature. Et CheckEval montre que les listes binaires tiennent mieux SUR LES
TÂCHES ÉTUDIÉES — ça ne prouve pas qu'un verdict binaire soit meilleur partout.
D'où la justification par mon cas plutôt que par une règle générale. C'est la seule affirmation du talk dans ce cas, et autant le dire
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

<!-- _class: dense -->

## L'ordre des champs décide du comportement

```
  ✗  {                      ✓  <thinking>  1. …  2. …  3. …  </thinking>
       "verdict": "PASS",       {
       "checks": { … }            "checks": {
     }                              "exactitude_technique": true,
                                    "absence_de_bugs":      false,
                                    "respect_consignes":    true
                                  },
                                  "verdict": "FAIL",
                                  "reason":  "…"
                                }

     décide, puis justifie     constate, puis conclut
```

Un LLM génère **de gauche à droite**. Il ne revient pas en arrière.
Et le verdict ne s'opine pas, il se calcule :
**PASS si et seulement si tous les contrôles sont vrais.**

Et le `<thinking>` ? Il paie sur le **mathématique et le symbolique**, peu
ailleurs. <span class="ref">Sprague et al., ICLR 2025 — méta-analyse</span>

Chez moi, **je n'arrive pas à prouver ce qu'il rapporte** — mais un **mauvais**
raisonnement fait tomber la justesse de 71 % à 36 %.
**Un risque dont je n'ai pas mesuré le bénéfice.** <span class="ref">judge-finetune/fidelite/</span>

<!--
Et maintenant le détail le moins intuitif de tout ce talk. Il tient en deux
caractères.

À gauche, le verdict d'abord, les contrôles ensuite. À droite, l'inverse.

Un modèle génère de gauche à droite. Il ne revient jamais en arrière. Donc si le
verdict est écrit en premier, tout ce qui suit est écrit pour être cohérent avec
une décision déjà prise. Il décide, puis il justifie. Dans l'autre sens, il
constate, puis il conclut.

Et le verdict ne s'opine pas, il se calcule : pass si et seulement si tous les
contrôles sont vrais. Un seul faux, et c'est fail.

Dernier point, sur le bloc de raisonnement. La littérature dit qu'il paie sur le
mathématique et le symbolique, et peu ailleurs. J'ai essayé de le mesurer chez
moi : je n'arrive pas à prouver ce qu'il rapporte. En revanche, un mauvais
raisonnement fait tomber la justesse de 71 à 36 %. C'est donc un risque dont je
n'ai pas mesuré le bénéfice. Le protocole est dans le dépôt.

⚠ C'est le seul endroit où la littérature et ma mesure convergent : le dire.
« Les deux vont dans le même sens, sans que l'un prouve l'autre. » Et ne pas
inverser l'inférence : la méta-analyse parle de familles de tâches, pas de mon
juge. Ma tâche est mixte, à dominante non symbolique — décider si un correctif
fonctionne, c'est du raisonnement algorithmique.

⚠ Deux pièges à éviter en le disant. Ma tâche n'est pas PUREMENT non symbolique :
décider si un correctif fonctionne est du raisonnement algorithmique, là où la
méta-analyse dit que ça paie. Dire « mixte, à dominante non symbolique ».
Et ne pas inverser l'inférence : la méta-analyse parle de familles de tâches, pas
de mon juge. Elle rend mon résultat attendu, elle ne le démontre pas.

Les trois bras, si on creuse : raisonnement propre 72 % de justesse, raisonnement
emprunté 36 %, raisonnement VIDE 74 %. Le troisième ne diffère pas du premier —
13 paires discordantes, 6 contre 7, p = 1,0000 — donc je ne vois pas ce que le
raisonnement rapporte. Et il pèse 73 % des jetons générés : 27 s par jugement
contre 7 s sans lui.

Quand le verdict bascule sous un raisonnement emprunté, il suit ce raisonnement
23 fois sur 24. C'est aussi une prise : qui contrôle le début de la réponse
contrôle la fin.

⚠ Réserve à garder : 46 items. « Je ne vois pas » n'est pas « il n'y a rien » —
un écart réel de 10 points resterait invisible.

⚠ Et G-Eval, la référence du raisonnement-avant-notation en évaluation, ne met en
avant aucune ablation isolant le raisonnement. C'est un ingrédient supposé plutôt
que démontré. (Seul le résumé a été lu.)

⚠ Ne PAS dire « le modèle suit son raisonnement ». La métrique principale — 53 %
de bascule, IC [38 %, 68 %] — tombe dans la zone que j'avais déclarée indécise.
Ce qui est net, c'est la direction : quand ça bascule, ça suit, 23 fois sur 24.
Donc « cause réelle, pas cause unique », et rien de plus.

Validité : réimposer au modèle son PROPRE raisonnement lui fait reprendre sa
décision 45 fois sur 46. Le pré-remplissage ne perturbe donc rien par lui-même.

Littérature, si la question vient : Turpin et al., NeurIPS 2023, montrent qu'une
chaîne peut être plausible et infidèle ; Lanham et al., 2023, proposent de le
tester par perturbation — c'est ce protocole. Et les petits modèles raisonnent
souvent plus fidèlement que les gros, ce qui va dans le sens de ce 14B.
Tout est dans judge-finetune/fidelite/.

⚠ Je n'ai PAS mesuré l'écart entre les deux ordres : j'ai choisi le bon dès le
départ. C'est un raisonnement sur le fonctionnement de la génération, pas un
résultat expérimental. Le dire tel quel.
 
▸ Deux caractères changent le comportement. Sur le thinking : « les deux vont dans le même sens, sans que l'un prouve l'autre » — puis le lien, et on avance.

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

Ne pas entrer dans le détail de l'expérience ici — une phrase, et le lien.

C'est le SEUL endroit du talk où la littérature et ma mesure convergent : partout
ailleurs je dois les séparer. À dire comme tel, c'est l'argument le plus solide
qui existe — ni l'un ni l'autre ne porte le poids seul. Formulation : « la
méta-analyse prédit un bénéfice minime hors mathématique et symbolique, ma tâche
n'est pas symbolique, ma mesure ne voit pas de bénéfice. Les deux vont dans le
même sens, sans que l'un prouve l'autre. »
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
Un critère se formule comme une question sur le texte, jamais comme une
propriété du monde. Personne ne peut démontrer qu'un code n'a pas de bugs. On
peut seulement dire si on en a repéré un.

Et mes critères ne sont pas une liste que j'ai choisie. Il y a trois niveaux.

Trois sont génériques, sur tous mes exemples d'analyse de code : les faits
affirmés sont-ils vrais, un défaut visible rend-il la réponse fausse, et la
réponse fait-elle ce qui était demandé.

Trois dépendent du type de tâche — ici, juger un contexte récupéré.

Et neuf sont dictés par la requête elle-même. Si la demande dit « sans
dépendance externe », le critère apparaît. Si elle dit « sans changer la
signature », il apparaît. Sinon, il n'existe pas.

C'est la réponse à « comment savez-vous que ce sont les bons critères ». Pour la
troisième catégorie, je ne les choisis pas : je les lis dans la demande.
-->
---

## Les trois tests d'un bon critère

**1. Décidable** — la réponse se lit dans ce qui est fourni.

**2. Falsifiable** — je sais dire ce qui le rendrait faux.

**3. Reproductible** — deux personnes répondent pareil.
**Et celui-là, il se mesure.**

Le test a désigné le plus faible des miens : **`respect_consignes`.**

**Le diagnostic :** c'est le seul **sans définition propre** — il hérite de la
requête, donc il change de sens à chaque question.

**Le correctif :** quand la contrainte est explicite, je la sors en critère
nommé. *« sans dépendance externe »*, *« sans changer la signature »*.
**Neuf fois dans mon corpus.**

<!--
Et pour savoir si un critère est bon, trois tests.

Décidable : la réponse se lit dans ce qui est fourni. Falsifiable : je sais dire
ce qui le rendrait faux. Et reproductible : deux personnes répondent pareil.

Les deux premiers sont des règles d'écriture. Le troisième est une mesure, et
c'est le seul qui tranche vraiment.

Alors je l'ai mesuré. Le test a désigné le plus faible des miens : « respect des
consignes ». Le diagnostic, c'est que c'est le seul critère sans définition
propre — il hérite de la requête, donc il change de sens à chaque question.

Le correctif est déjà dans mon corpus : quand la contrainte est explicite, je la
sors en critère nommé. Neuf fois.

⚠ Les chiffres si on demande : kappa 0,386 pour 78 % d'accord brut. Ne pas
s'auto-accabler — je montre plus tard qu'un kappa bas sur des marges
déséquilibrées sous-estime l'accord.
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
Parlons des biais. Et je vais le faire avec un correcteur de copies, parce que
c'est exactement la même chose.

Imaginez un correcteur honnête, fatigué, à la deux-centième copie.

Il se laisse impressionner par la longueur : quatre pages, ça fait sérieux. Il
note selon l'ordre des copies, la première et la vingtième. Il préfère son propre
style, il se reconnaît dedans. Il reconnaît l'écriture, et il note l'auteur
plutôt que la copie. Et il préfère valider que recaler, parce que c'est moins
coûteux.

Aucune de ces cinq erreurs n'est une faute de compétence. Toutes déforment la
note. Un juge automatique fait exactement les mêmes, et pour les mêmes raisons.

La quatrième est la plus vicieuse, et c'est celle qui m'est arrivée. J'y viens.
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

Quatre de ces cinq, je les ai **mesurés chez moi**. Le cinquième, non — je le **cite**.

<!--
Et voilà comment je m'en protège, erreur par erreur.

La longueur : je compare les faux pass sur les défauts verbeux et sur les
défauts concis. Mesuré, 46 %.

L'ordre : je mélange le contexte, avec une graine tirée de la question. Mesuré,
douze verdicts sur soixante basculent au seul réordonnancement.

Son propre style : je ne fais pas juger un modèle par sa propre famille. Ça,
c'est cité, pas mesuré.

L'écriture reconnue : un relecteur humain, et un test de permutation. Mesuré,
dix-sept sur dix-sept — j'y reviens dans une minute.

L'indulgence : je publie le taux d'erreurs attrapées, pas l'exactitude. Mesuré,
59 %.

Quatre de ces cinq, je les ai mesurés chez moi. Le cinquième, non — je le cite.
Et je ne présenterai jamais l'un pour l'autre.
-->
---

## Pourquoi entraîner un juge

Les conventions écrites font déjà beaucoup.
Mon pari : un modèle entraîné sur **mes propres jugements** collera mieux à la
grille, et tiendra le format à chaque fois.

Pour le savoir, il faut un corpus.

**200 exemples** écrits à la main. **50** mis de côté comme étalon, relus en
aveugle par deux personnes : **47 verdicts identiques sur 50.**

**Le corpus a pris des semaines.**

<span class="ref">corpus, protocole et mesures : judge-finetune/ dans le dépôt</span>

<!--
Pourquoi entraîner un juge, alors que les conventions écrites font déjà
beaucoup ?

Mon pari : un modèle entraîné sur mes propres jugements collera mieux à la
grille, et tiendra le format à chaque fois.

Pour le savoir, il faut un corpus. Deux cents exemples écrits à la main.
Cinquante mis de côté comme étalon, relus en aveugle par deux personnes : 47
verdicts identiques sur 50.

Et c'est là que tout le travail est parti. Le corpus a pris des semaines.

Tout est dans le dépôt : le corpus, le protocole, les mesures.

⚠ Annoncer le pari comme un pari. La partie 4 dira s'il était bon, et la réponse
n'est pas celle que j'attendais.
-->
---

## J'ai trouvé un signal

**La question :** est-ce que la simple **longueur** d'une réponse suffit à
deviner son verdict ?

Si oui, le juge n'a plus besoin de comprendre — **il compte les caractères.**

J'ai essayé 145 seuils de longueur, dans les deux sens. **290 essais.**

Le meilleur devinait le verdict **3 fois sur 4** — le hasard en fait 1 sur 2.

→ un effet **quasi impossible à devoir au hasard.**

<!--
Et en construisant ce corpus, j'ai trouvé un signal.

La question que je me posais : est-ce que la simple longueur d'une réponse suffit
à deviner son verdict ? Parce que si oui, le juge n'a plus besoin de comprendre —
il compte les caractères.

J'ai essayé cent quarante-cinq seuils de longueur, dans les deux sens. Deux cent
quatre-vingt-dix essais. Le meilleur devinait le verdict trois fois sur quatre,
là où le hasard en fait une sur deux.

J'ai annoncé un effet quasi impossible à devoir au hasard.

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
Et il ne valait rien.

Mon erreur : j'ai jugé mon meilleur essai comme si c'était mon seul essai. Le
meilleur de deux cent quatre-vingt-dix tirages est bon même quand il n'y a rien à
trouver. C'est le tireur qui mitraille un mur de grange et qui dessine la cible
autour du groupe le plus serré. Pour nous : un seuil optimisé sur les données,
puis évalué comme s'il avait été choisi avant de les voir.

Le bon test, c'est de mélanger les étiquettes, de refaire les deux cent
quatre-vingt-dix essais, de garder le meilleur, et de recommencer mille fois.
Parce que c'est ça, le hasard, quand on cherche deux cent quatre-vingt-dix fois.

Résultat : p égale zéro virgule treize. Mon « trois sur quatre » est ce que le
hasard produit couramment. Du bruit.

La règle que j'en ai tirée : tout seuil choisi après coup se compare à un tirage
de permutation du même maximum. Jamais à un taux de base.

⚠ Le test de permutation ramène l'effet à +1,3 σ, p = 0,132.
-->
---

## La fuite que j'ai créée en la corrigeant

17 requêtes du corpus portaient la même incise — *« si tu as le temps, dis un mot de X »*.
**Les 17 étaient étiquetées PASS.**

Un juge n'a qu'à détecter la chaîne pour marquer 17 points.
**Il n'apprend pas à juger. Il apprend à repérer ma signature.**

Correctif évident : ajouter l'incise à des FAIL. Sauf que je l'ai mise en
**paragraphe isolé**, là où les 17 d'origine la portaient au fil du texte.

Nouvelle règle apprise : *« paragraphe isolé ⇒ FAIL »*. **30 sur 30.**
Elle a traversé une régénération, une validation à zéro erreur,
**trois mesures et un commit.**

<!--
Mais il y avait une vraie fuite, et celle-là, elle était déterministe.

Dix-sept requêtes de mon corpus portaient la même incise : « si tu as le temps,
dis un mot de X ». Les dix-sept étaient étiquetées pass.

Un juge n'a qu'à détecter cette chaîne de caractères pour marquer dix-sept
points. Il n'apprend pas à juger. Il apprend à repérer ma signature.

Le correctif était évident : ajouter l'incise à des réponses en échec. Sauf que
je l'ai mise en paragraphe isolé, là où les dix-sept d'origine la portaient au
fil du texte.

Nouvelle règle apprise par le modèle : paragraphe isolé, donc échec. Trente sur
trente. J'avais aggravé le problème en le réparant.

Et elle a traversé une régénération, une validation à zéro erreur, trois mesures
et un commit.
-->
---

## Ce qui l'a trouvée : un humain

Les métriques ont trouvé ce que je leur avais demandé de chercher.

**L'humain a trouvé ce que je ne savais pas chercher.**

Un relecteur a répondu **différemment** sur un item, après avoir appliqué la
règle correctement quatre fois de suite.

Ce n'était pas un relâchement : le stimulus était réellement différent.

<!--
Alors qu'est-ce qui l'a trouvée ?

Les métriques ont trouvé ce que je leur avais demandé de chercher. L'humain a
trouvé ce que je ne savais pas chercher.

Un relecteur a répondu différemment sur un item, après avoir appliqué la règle
correctement quatre fois de suite. Ce n'était pas un relâchement : le stimulus
était réellement différent.

Un balayage automatique cherche les régularités qu'on a listées. Il ne peut pas
signaler celle à laquelle on n'a pas pensé — et une fuite, par définition, c'est
celle à laquelle on n'a pas pensé.
-->
---

## Tout en local, et pourquoi

Un MacBook Pro M3 Pro, 36 Go. **Aucun service cloud, aucun jeton facturé.**

**91 minutes** d'entraînement.
**11,3 Go** de mémoire au pic, sur 36 disponibles.
**43,8 Mo** d'adaptateur produit — 0,078 % des paramètres du modèle.

Le corpus a pris des semaines. **Le modèle, lui : une soirée.**

**Entraîner un juge n'est pas un projet d'infrastructure.**

<!--
Passons à la mise en œuvre. Tout tourne en local : un MacBook Pro M3 Pro, 36
gigas. Aucun service cloud, aucun jeton facturé.

Quatre-vingt-onze minutes d'entraînement. Onze gigas de mémoire au pic, sur
trente-six disponibles. Et un adaptateur de quarante-trois mégaoctets, soit moins
d'un dixième de pour cent des paramètres du modèle.

Le corpus a pris des semaines. Le modèle, lui : une soirée.

Entraîner un juge n'est pas un projet d'infrastructure.

⚠ Raconter la correction si le temps le permet : j'ai d'abord publié 76 minutes,
ma méthode excluant les neuf passes de validation. Corriger rendait le chiffre
moins flatteur.
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
Le banc d'essai, maintenant. Soixante questions sur ma codebase, réparties en
trois niveaux.

Local : une méthode précise, dans un seul fichier. Structural : héritage,
interfaces, ce qui implémente quoi. Et inter-modules : une chaîne qui traverse
plusieurs paquets. C'est là qu'on attend le graphe.

Les deux stratégies répondent aux mêmes soixante questions, dans la même
exécution. C'est ce qui autorise une comparaison appariée, et une comparaison
appariée est beaucoup plus puissante à effectif égal.

Et le mélange du contexte est tiré de la question, donc la mesure se rejoue à
l'identique. Ce n'est pas un détail : sans graine, les exécutions de la veille
faisaient bouger le même bras de 56 à 43 %.
-->
---

## Le résultat

| | Lucene | Neo4j |
|---|---|---|
| **Réponses justes** | **48,3 %** | **23,7 %** |
| Contexte jugé insuffisant | 39,7 % | **66,1 %** |

Sur les 60 questions, **24 les départagent.**
**Lucene en gagne 19. Neo4j en gagne 5.**

Le hasard seul donnerait 12 – 12. Obtenir 19 – 5, c'est tirer **19 fois pile
sur 24 lancers.** → **p = 0,0066**

Une mesure **sans aucun LLM** — compter les identifiants attendus dans le
contexte récupéré — **les classe dans le même ordre** : 0,697 contre 0,596.

Elle ne valide pas les verdicts, **elle mesure autre chose.** Mais deux
instruments indépendants qui classent pareil, c'est mieux qu'un seul.

<span class="ref">Sur ce corpus, selon ce juge.</span>

<!--
Le résultat.

Lucene, 48 % de réponses justes. Le graphe Neo4j, 24 %.

La deuxième ligne donne le mécanisme : le contexte de Neo4j est jugé insuffisant
dans deux tiers des cas, contre 40 % pour Lucene. Ce n'est pas un problème de
bruit mal maîtrisé, c'est un défaut de rappel — le moteur ne rapporte pas assez
de matière. Sans critères atomiques, j'aurais un écart de vingt-cinq points sans
explication.

Sur les soixante questions, vingt-quatre les départagent. Lucene en gagne
dix-neuf, Neo4j cinq. Le hasard seul donnerait douze-douze — obtenir dix-neuf
contre cinq, c'est tirer dix-neuf fois pile sur vingt-quatre lancers.

Et une mesure qui ne passe pas du tout par le juge — on compte les identifiants
attendus dans le contexte récupéré — les classe dans le même ordre. Elle ne
valide pas les verdicts, elle mesure autre chose. Mais deux instruments
indépendants qui classent pareil, c'est mieux qu'un seul.

⚠ Dire la réserve : sur ce corpus, selon ce juge.

⚠ Ne pas dire que hintCoverage « valide » le juge. Il compte des identifiants
présents dans le contexte ; le juge évalue une réponse. Ce sont deux propriétés
différentes. Ce qu'on peut dire : deux instruments indépendants classent les deux
stratégies dans le même ordre, donc la conclusion ne tient pas au seul juge.

⚠ Et la réserve, à énoncer : ces chiffres valent pour CE corpus, jugé par CE
juge, dont l'alignement est de 0,44 et la stabilité de 58 %. Un écart de 25
points est large, mais c'est une comparaison, pas une vérité sur GraphRAG.

Sur la mesure sans LLM : c'est la même idée que le filtre déterministe du début
du talk. En amont elle économise des jetons, en aval elle sert de contre-expertise.
Elle s'appelle hintCoverage, elle ne coûte qu'une liste d'identifiants attendus
par question et un comptage. Si les deux méthodes s'étaient contredites, je
n'aurais rien conclu du tout — c'est un garde-fou qu'on construit avant de
connaître le résultat, pas après.

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

## Moteur ou graphe ? Le contrôle d'équité

J'ai rejoué les 60 questions **sans** le parcours de graphe.

Lucene est configuré à l'identique : son taux **doit** être le même.
Il l'est. **48,3 %, à la décimale, et sur chacun des trois niveaux.**

Le témoin n'a pas bougé. Neo4j, lui, gagne **1,7 point — une question sur 59.**

**L'écart vient du moteur de récupération, pas de la traversée de graphe.**

<!--
Mais attention : est-ce le moteur de récupération qui est en cause, ou le
parcours de graphe ?

Pour le savoir, j'ai rejoué les soixante questions sans le parcours de graphe.
Et surtout, j'ai laissé Lucene strictement identique dans les deux exécutions.
Son taux doit donc être le même.

Il l'est. Quarante-huit virgule trois pour cent, à la décimale, et sur chacun des
trois niveaux. Le témoin n'a pas bougé — c'est ça qui rend l'attribution
possible. S'il avait bougé, je n'aurais rien pu conclure du tout.

Et Neo4j, lui, gagne un virgule sept point. Une question sur cinquante-neuf.

Donc l'écart vient du moteur de récupération, pas de la traversée de graphe.
Ce n'est pas « le graphe est mal implémenté » : c'est ce pipeline-là qui rappelle
moins de matière.
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
Par niveau, maintenant — et il faut être honnête sur ce qui conclut.

Un seul écart tient : les questions inter-modules. Là, sur les huit questions où
les deux stratégies ont divergé, Lucene a gagné les huit. Huit piles d'affilée.

Sur les deux autres niveaux : cinq piles sur sept, et six sur neuf. Banal.

Donc deux écarts sur trois ne concluent pas. Et ce n'était pas une surprise :
c'est une limite de puissance que j'avais annoncée avant de lancer.

Dire « non concluant » sur deux niveaux, c'est ce qui donne du poids au
troisième.

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
Et maintenant le retour d'expérience qui m'a le plus coûté.

Cinq fois, mon banc d'essai a mesuré le vide. Et cinq fois, il a affiché « build
success ».

Les options non transmises par le lanceur de tests : il a indexé un corpus
synthétique à la place de ma vraie codebase. Une propriété vide au lieu de
l'adaptateur : j'ai noté le modèle de base en croyant juger le modèle entraîné.
Un pgrep qui matchait son propre script : cinq heures perdues. Un mélange non
graîné : vingt-et-une questions sur soixante divergentes à récupération
identique. Et une option d'adaptateur acceptée puis ignorée — celle-là m'a rendu
« le fine-tuning dégrade la justesse de 76 % », un résultat publiable et
entièrement faux.

Aucune erreur. Aucun avertissement. Des résultats plausibles à chaque fois.

Et ce qui a fini par le révéler, ce n'est pas une métrique. C'est un détail de
style : des clés plates dans un bloc markdown, là où mes exemples d'entraînement
portent tous un JSON nu.

La leçon, et c'est le correctif que j'ai mis en place : avant de dépenser une
heure de calcul, faire un appel et vérifier une propriété qui ne peut pas
apparaître par hasard si la plomberie est cassée. Pas l'absence d'erreur. Une
preuve positive.
-->
---

## κ de Cohen, sur un cas réel

Deux correcteurs qui **recaleraient tout le monde sans rien lire** seraient
d'accord 9 fois sur 10. L'accord brut mesure surtout le **déséquilibre du paquet.**

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
Parlons maintenant de la fiabilité du juge lui-même. Et pour ça, il faut un
outil : le kappa de Cohen.

D'abord le problème. Deux correcteurs qui recaleraient tout le monde sans rien
lire seraient d'accord neuf fois sur dix, si neuf copies sur dix sont mauvaises.
L'accord brut ne mesure donc pas la compétence : il mesure surtout le
déséquilibre du paquet.

Alors prenons un cas. Deux correcteurs, cent copies, d'accord sur quatre-vingt-dix.

Chacun valide une copie sur cinq. Donc même en cochant au hasard, ils tomberaient
d'accord soixante-huit fois sur cent. Quatre fois sur un pass commun,
soixante-quatre fois sur un fail commun. Cet accord-là est gratuit.

Partant de soixante-huit, il ne restait que trente-deux points à conquérir. Ils en
ont pris vingt-deux.

Kappa égale vingt-deux sur trente-deux, soit zéro virgule soixante-neuf. Alors
que l'accord brut affichait quatre-vingt-dix pour cent.

Kappa, c'est la part conquise de ce qu'il restait à conquérir.
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
Et le piège marche dans les deux sens.

Sur mon critère le plus fréquent : soixante-dix-huit pour cent d'accord brut, et
un kappa de zéro virgule trente-neuf.

Là, le paquet est très déséquilibré. Donc le kappa paraît médiocre alors que les
deux correcteurs se trompent rarement.

Donner le kappa seul sous-estime l'accord. Donner le pourcentage seul le
surestime. Les deux vont ensemble, avec la répartition.

Un kappa bas ne veut donc pas toujours dire ce qu'on croit. Il faut regarder le
paquet avant de juger le chiffre.
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
Sur mes 50 items, **17 portent un désaccord sur au moins un contrôle, dont 15 que
le verdict masque.** Le verdict est reproductible ; les **raisons** le sont
beaucoup moins. Or c'est sur les raisons que le juge s'entraîne.

<!--
Et maintenant, deux kappas qu'on confond tout le temps.

Le premier mesure l'accord entre un humain et mes étiquettes de référence : il
répond à « mon étalon est-il fiable ? ». Il vaut zéro virgule quatre-vingt-huit.

Le second mesure l'accord entre mon juge et cet étalon : il répond à « mon juge
est-il aligné ? ». Il vaut zéro virgule quarante-quatre.

Présenter le premier à la place du second, c'est l'erreur la plus fréquente, et
la plus flatteuse : on annonce un alignement qu'on n'a jamais mesuré.

Et l'écart entre les deux est la vraie information. Zéro virgule quatre-vingt-huit
entre humains, zéro virgule quarante-quatre pour le juge. Le plafond n'est pas le
modèle — c'est ce que le corpus enseigne.

Pourquoi ? Sur mes cinquante items, dix-sept portent un désaccord sur au moins un
contrôle, et quinze d'entre eux sont masqués par le verdict. Le verdict est
reproductible ; les raisons le sont beaucoup moins. Or c'est sur les raisons que
le juge s'entraîne.
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
Avant de vous donner le résultat du fine-tuning, une mise en garde sur la façon
de lire un chiffre de justesse.

Un correcteur qui valide presque tout se trompe rarement. Il ne se trompe que sur
les copies qu'il aurait dû recaler.

Mon juge, sur vingt-sept mauvaises copies, en recale seize. Il en laisse passer
onze. Sur vingt-trois bonnes copies, il en valide vingt-deux.

Ça fait soixante-seize pour cent de décisions justes. Et quatre défauts sur dix
qui passent.

Le même juge, deux chiffres. Ne publiez jamais le premier sans le second.

Et pour OllamAssist, les deux erreurs n'ont pas le même prix : un défaut qui
passe, c'est une explication fausse sur ma codebase livrée à l'utilisateur. Un
bon code recalé, c'est juste une relecture inutile.

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

**12 items les départagent. 6 d'un côté, 6 de l'autre** — une pièce équilibrée.

Je ne peux pas dire que le fine-tuning n'apporte rien. Je peux dire que
**mes 50 items ne voient pas la différence** : en dessous de 15 points d'écart,
ils sont aveugles.

**Non concluant** — et cette issue était **écrite avant** de lancer la mesure.

<!--
Alors, le fine-tuning a-t-il amélioré mon juge ?

Trois variantes. L'invite nue : zéro pour cent de justesse, et surtout zéro pour
cent de JSON exploitable — elle ne rend rien d'utilisable. En ajoutant quatre
phrases de conventions écrites : soixante-seize pour cent. Et le modèle
fine-tuné, quatre-vingt-onze minutes d'entraînement : soixante-seize pour cent
aussi.

Sur les cinquante items, douze seulement départagent les deux juges. Et ils se
partagent six contre six. Une pièce équilibrée.

Je ne peux donc pas dire que le fine-tuning n'apporte rien. Je peux dire que mes
cinquante items ne voient pas la différence : en dessous de quinze points
d'écart, ils sont aveugles.

Non concluant. Et cette issue était écrite dans mon protocole avant que je lance
la mesure. C'est tout l'intérêt d'un pré-enregistrement : pouvoir dire « je ne
sais pas » sans que ce soit un échec, et sans redécouper les données jusqu'à
trouver un p flatteur.

⚠ NE PAS dire « ça n'améliore pas ». Dire : mes 50 items ne voient pas la
différence.
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

C'est ça qui rend deux exécutions comparables — et **vérifiables** :
le `<thinking>` **aide le modèle à décider**, les `checks` me permettent de
**vérifier** sa décision.

**Le contre-chiffre : la stabilité du verdict baisse, 76 % → 58 %.**
La baseline est stable parce qu'elle **décide avant de regarder.**

<!--
Mais alors, qu'est-ce que ces quatre-vingt-onze minutes ont acheté ?

Regardez. La baseline décompose déjà — elle rend bien un objet de contrôles. Mais
sous son propre nom de clé, et avec le verdict écrit avant.

Le fine-tuning ne lui a donc pas appris à décomposer. Il lui a appris le contrat
exact : les bons noms, et les contrôles avant le verdict. Cent cinquante fois sur
cent cinquante.

C'est ça qui rend deux exécutions comparables — et vérifiables. Le bloc de
raisonnement aide le modèle à décider ; les contrôles, eux, me permettent de
vérifier sa décision.

C'est une leçon d'intégration, pas d'intelligence. Un juge sert dans une chaîne
automatisée, et une chaîne a besoin d'un contrat, pas de bonne volonté.

Et le contre-chiffre, dans la même phrase : la stabilité du verdict baisse, de
soixante-seize à cinquante-huit pour cent. La baseline est stable parce qu'elle
décide avant de regarder.
-->
---

## Qui décide quoi

```
  déterministe ?     →  le compilateur, le parseur, le linter
                        ni juge, ni humain

  juge d'accord      →  automatique
  avec lui-même ?       PASS si et seulement si tous les contrôles sont vrais

  juge instable ?    →  un humain
                        déclencheur mesurable, pas une impression
```

Et le signal fonctionne : **83 %** de verdicts justes sur les items stables,
**67 %** sur les instables.

**Mais la stabilité mesure la répétabilité, pas la justesse.**
Un verdict stable reste faux une fois sur six.
Les enjeux, le hors-domaine, les critères qui se contredisent sont **d'autres
motifs** de relecture — l'instabilité est le seul que je sache mesurer.

<!--
Reste la question la plus pratique : qui décide quoi.

Ce qui est déterministe part au compilateur, au parseur, au linter. Ni juge, ni
humain.

Quand le juge est d'accord avec lui-même, c'est automatique : pass si et seulement
si tous les contrôles sont vrais.

Et quand le juge est instable — quand il se contredit d'une passe à l'autre —
c'est là qu'un humain intervient. C'est un déclencheur mesurable, pas une
impression.

Et le signal fonctionne : quatre-vingt-trois pour cent de verdicts justes sur les
items stables, soixante-sept pour cent sur les instables.

Mais attention : la stabilité mesure la répétabilité, pas la justesse. Un verdict
stable reste faux une fois sur six. Les enjeux, les questions hors-domaine, les
critères qui se contredisent sont d'autres motifs de relecture — l'instabilité
est simplement le seul que je sache mesurer.

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
Et quand il n'y a pas d'humain ? Parce que c'est le cas par défaut. On ne
demande pas une relecture humaine à chaque fois — personne ne fait vérifier ses
tests unitaires par un collègue à chaque échec.

Alors ça dépend de ce que le juge garde.

Si c'est une porte — la CI, la non-régression — l'item instable compte comme un
échec. On bloque. Un doute doit coûter, sinon il ne sert à rien.

Si c'est une mesure — un échantillonnage descriptif — l'item instable est exclu
du taux, et compté à part. On ne le force pas, on le déclare.

Même signal, deux politiques, parce que se tromper ne coûte pas pareil.

Et le piège, dans les deux cas : compter l'item douteux comme un succès. C'est le
seul choix qui se retourne toujours contre vous.
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
Dernière chose sur le triage, et c'est le chiffre qui referme tout.

Mon filtre de recevabilité exigeait quatre-vingt-quinze pour cent de verdicts
stables. Ce seuil avait l'air arbitraire quand je l'ai écrit. Il ne l'est pas.

Quatre-vingt-quinze pour cent de stabilité, ça veut dire un item sur vingt à
relire. Si vous pouvez en relire un sur vingt, il vous faut quatre-vingt-quinze
pour cent. Ce n'est pas un seuil statistique, c'est votre budget humain.

Mon juge est à cinquante-huit pour cent. Soit vingt-et-un items sur cinquante.
Quatre fois mon budget.

C'est pour ça qu'il n'est pas prêt pour la production. Et le raisonnement
s'inverse pour vous : partez de ce qu'un humain peut relire par semaine, ça vous
donne le taux de stabilité à atteindre, et donc si votre juge est utilisable.

⚠ Réserve à énoncer : 29 items stables contre 21 instables. C'est une tendance,
pas un effet établi — mais elle va dans le même sens sur les deux variantes
mesurées, baseline comprise (79 % contre 67 %), ce qui la rend défendable.

Et ça referme la partie 2 : c'est un humain qui a trouvé la fuite que douze
mesures avaient manquée, parce qu'il a changé d'avis sur un item. L'instabilité
est un signal, chez le juge comme chez le relecteur.

L'objectif n'est pas de retirer l'humain de la boucle. C'est d'arrêter de lui
faire relire ce qui est évident, pour qu'il regarde ce qui ne l'est pas.
 
Ça ne s'invente pas, ça se lit dans le harnais : je fais déjà trois passes pour
mesurer la répétabilité. Le même chiffre sert à trier.
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
Je termine là-dessus.

Le corpus devait mesurer la qualité : il contenait trois fuites. Le script que
j'avais écrit pour trouver les fuites avait lui-même deux bugs. Mon relevé de
coût était faux trois fois. Le correctif d'une fuite en a créé une pire. Et mon
banc d'essai a mesuré le vide cinq fois.

Regardez la colonne de droite. Un test de permutation. Un humain. La relecture du
code devant un chiffre absurde. Une comparaison avec le journal. Une sonde avant
de lire les chiffres.

Chacun a été corrigé parce qu'on a regardé. Jamais parce qu'une métrique a
protesté.

C'est la phrase que je veux que vous reteniez : on construit un juge pour arrêter
d'avancer à l'aveugle, mais le juge est lui-même un instrument. Et un instrument,
ça se vérifie. Sinon on a simplement déplacé l'aveuglement d'un cran.
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
Trois choses, applicables lundi, sans rien installer.

Un : écrivez vos conventions avant de fine-tuner. Quatre phrases m'ont rapporté
soixante-seize points. Le fine-tuning, zéro.

Deux : décomposez en critères atomiques, et mettez les contrôles avant le
verdict. Un modèle génère de gauche à droite — l'ordre des champs change le
comportement, et ça ne coûte rien.

Trois : exigez une preuve positive avant de dépenser du calcul. Un banc qui ne
sait pas prouver qu'il a mesuré la bonne chose ne mesure rien, et il le fait
silencieusement.

Tout est dans le dépôt : le corpus, le protocole avec ses amendements datés, et
les générations écartées avec la raison de leur mise à l'écart.

Merci.
-->
