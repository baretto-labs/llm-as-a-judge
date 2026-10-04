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

<!--
▸ Lire le titre à voix haute. « RAGots » se perd à l'écrit.
 _class: title -->

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
▸ Raconter : les funérailles, le chatbot, la politique qui n'existe pas. Puis laisser la phrase du tribunal.

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

<!--
▸ Survoler — 2 secondes minimum. « J'aurais pu en remplir beaucoup plus. Je ne garde que ce que je peux prouver. »
 _class: dense -->

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
▸ Le faux avait la forme du vrai. Un avocat ne relit pas une citation bien formatée.

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
▸ Ma codebase, donc je vois quand il se trompe. Appuyer sur la dernière ligne : la réponse dépend de ce qu'il a trouvé.

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
▸ Trois rôles en conflit : auteur, sélectionneur, juge. Le mot à dire, c'est TUNNEL.

Trois rôles en conflit : auteur du système, sélectionneur des cas de test, et
juge.

Le mot exact, c'est TUNNEL. Pas de boucle de retour, donc chaque modification
est un pari, et les paris s'accumulent sans qu'on sache lequel a coûté quoi.

La dernière ligne est la promesse du talk, et c'est elle qu'il faut tenir : les
deux moitiés comptent. Mesurer le RAG, et ne pas faire confiance à l'instrument
sans l'avoir mesuré lui aussi.

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
▸ Trois entrées, pas une. Il ne génère pas la réponse, il la juge.

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
▸ Le corrigé type est ce que je n'ai pas : si je savais écrire la réponse, je n'aurais pas besoin de RAG.

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
▸ Un compilateur répond en 50 ms et n'a pas d'humeur. Puis l'aveu : mon filtre à moi est mince.

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
▸ C'est l'offline qui ferme le tunnel. Moi : 100 % CI, aucun échantillonnage.

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

Et elle convient **à mon cas** : des critères qu'on tranche un par un, une
décision de livraison, et des erreurs dont le coût n'est pas le même des deux
côtés.

Mesuré ailleurs : douze modèles évaluateurs notent les mêmes textes.
Avec une échelle, leur accord vaut **0,09** — autant dire rien.
Avec des questions binaires, **0,48**.

<span class="ref">CheckEval, EMNLP 2025 — Lee et al.</span>

<!--
▸ « 13/20, ça ne veut rien dire. » Et dire que ce point-là vient de la littérature, pas de ma mesure.

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

Et le raisonnement affiché, est-il suivi ? **Je l'ai remplacé par celui d'un
autre item :** le verdict bascule **une fois sur deux** — et quand il bascule,
il suit le raisonnement imposé **23 fois sur 24**.

**Le `<thinking>` est une cause réelle de la décision. Pas sa cause unique.**

<!--
▸ La chose la moins intuitive du talk, et ça tient en deux caractères. Puis : « et le raisonnement, est-il suivi ? » — je l'ai mesuré.

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

Les deux conditionnements sont mesurés. Contrôles → verdict : 99,3 % de
cohérence. Thinking → décision : l'expérience de fidélité, 46 paires, 92
générations, température 0, pré-enregistrée avant la mesure.

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
▸ Je ne choisis pas la troisième catégorie : je la lis dans la requête.

Le modèle n'apprend pas mon domaine, il apprend à suivre un barème — et c'est le
barème qui porte le domaine. C'est pour ça que mes trois types de tâche partagent
le même moteur : un seul correcteur, trois barèmes. Changer de domaine, c'est
changer de barème, pas réentraîner.

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

Le test a désigné le plus faible des miens : **`respect_consignes`.**

**Le diagnostic :** c'est le seul **sans définition propre** — il hérite de la
requête, donc il change de sens à chaque question.

**Le correctif :** quand la contrainte est explicite, je la sors en critère
nommé. *« sans dépendance externe »*, *« sans changer la signature »*.
**Neuf fois dans mon corpus.**

<!--
▸ Test, diagnostic, correctif. Le message est que le test a fonctionné — pas que j'ai un mauvais critère.

Les deux premiers tests sont des règles d'écriture. Le troisième est une mesure,
et c'est le seul qui tranche.

Ce n'est pas un aveu, c'est une démonstration que le test fonctionne : il m'a
désigné un critère, le critère avait une cause, et la cause avait un correctif.

Les chiffres si on demande : κ = 0,386 pour 78 % d'accord brut entre relecteurs.
Et attention à ne pas s'auto-accabler — je montre deux diapositives plus loin
qu'un κ bas sur des marges déséquilibrées SOUS-ESTIME l'accord. Les deux
relecteurs se trompent rarement ; c'est simplement mon critère le moins net.

Ce qui reste, et qu'il faut dire si on insiste : les requêtes dont la consigne est
elle-même vague. Là, aucune décomposition n'est possible sans réécrire la
question. Je garde le critère plutôt que de ne rien évaluer sur cette dimension —
c'est un choix, pas un oubli.
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
▸ Un correcteur honnête fatigué par 200 copies. La quatrième m'est arrivée.

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

Quatre de ces cinq, je les ai **mesurés chez moi**. Le cinquième, non — je le **cite**.

<!--
▸ Quatre mesurés chez moi, un seul cité. Le dire à voix haute.

La règle, à dire plutôt qu'à afficher : ne jamais présenter un biais cité comme
un biais mesuré.

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
▸ C'est un PARI, pas une conclusion. La partie 4 dira s'il était bon — et la réponse m'a surpris.

C'est l'accroche qui manquait : jusqu'ici personne n'a dit qu'on entraînait quoi
que ce soit. Sans elle, les trois diapositives qui suivent parlent d'un corpus et
d'un modèle qui apprend une signature, sans qu'on sache pourquoi il y a un
modèle.

Annoncer le pari comme un pari, pas comme une conclusion : la partie 4 dira s'il
était bon, et la réponse n'est pas celle que j'attendais.

Chaque exemple : une requête, un contexte, une réponse à évaluer, et le jugement
attendu — contrôles, verdict, raison.

L'accord entre relecteurs vaut κ = 0,880, IC 95 % [0,720 — 1,000]. Je ne mets pas
le κ à l'écran ici : il n'est expliqué qu'en partie 4, et un chiffre qu'on ne sait
pas lire ne sert à rien. « 47 sur 50 » se comprend tout de suite.

Et c'est la phrase à faire porter : le modèle s'entraînera en 91 minutes, le
corpus a pris des semaines. Le coût n'est pas le GPU, c'est l'étalon.
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
▸ Marquer un temps sur la dernière ligne : c'est le chiffre que j'ai annoncé, et il était faux.

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
▸ Le tireur qui mitraille un mur puis dessine la cible. De l'overfitting, mais sur une statistique.

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
▸ Toute correction d'un corpus est une nouvelle écriture, et toute écriture laisse une signature.

La fuite corrigée était à 17 sur 17. Celle que le correctif a créée est à 30 sur
30. J'ai aggravé le problème en le réparant, et aucune de mes vérifications ne
l'a vu — tout un dispositif conçu exprès pour l'attraper.

Toute correction d'un corpus est une nouvelle écriture, et toute écriture
introduit une signature.

C'est une fuite déterministe, pas un biais statistique. La différence est
importante : un biais déforme, une fuite dispense d'apprendre.

Et elle vient de moi. En rédigeant le corpus, j'ai associé sans y penser une
tournure de politesse à des réponses que je considérais bonnes.

C'est le risque propre à un corpus écrit par une seule personne — et c'est
exactement mon cas.
-->

---

## Ce qui l'a trouvée : un humain

Les métriques ont trouvé ce que je leur avais demandé de chercher.

**L'humain a trouvé ce que je ne savais pas chercher.**

Un relecteur a répondu **différemment** sur un item, après avoir appliqué la
règle correctement quatre fois de suite.

Ce n'était pas un relâchement : le stimulus était réellement différent.

<!--
▸ La diapositive qui compte de toute la partie. Ralentir.

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

Le corpus a pris des semaines. **Le modèle, lui : une soirée.**

**Entraîner un juge n'est pas un projet d'infrastructure.**

<!--
▸ Le message est le prix d'entrée, pas la performance. Tout le monde ici a la machine qu'il faut.

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

## Le banc d'essai : 60 questions, 3 niveaux

| Niveau | Ce qu'il teste |
|---|---|
| **LOCAL** | une méthode précise, dans un seul fichier |
| **STRUCTURAL** | héritage, interfaces, ce qui implémente quoi |
| **CROSS_MODULE** | une chaîne qui traverse plusieurs paquets |

Les **mêmes** 60 questions pour les deux stratégies, dans la **même** exécution.

Mélange du contexte **graîné par la question** → la mesure est reproductible.

<!--
▸ Mêmes questions, même boucle : c'est ce qui autorise la comparaison appariée.

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

Le hasard seul donnerait 12 – 12. Obtenir 19 – 5, c'est tirer **19 fois pile
sur 24 lancers.** → **p = 0,0066**

Une mesure **sans aucun LLM** — compter les identifiants attendus dans le
contexte récupéré — **les classe dans le même ordre** : 0,697 contre 0,596.

Elle ne valide pas les verdicts, **elle mesure autre chose.** Mais deux
instruments indépendants qui classent pareil, c'est mieux qu'un seul.

<span class="ref">Sur ce corpus, selon ce juge.</span>

<!--
▸ La deuxième ligne donne le mécanisme : défaut de rappel, pas de bruit. Et la mesure sans LLM confirme.

Chiffre retiré de l'écran mais disponible : la cohérence du juge, c'est-à-dire la
part des verdicts qui correspondent bien à ses propres contrôles, est de 100 %
pour Lucene et 98,3 % pour Neo4j.
Les 36 autres questions ne sont pas perdues : elles disent que les deux
stratégies se valent là-dessus. Elles ne peuvent simplement pas servir à
trancher. Le test apparié n'est rien d'autre qu'une pièce lancée autant de fois
qu'il y a de questions qui départagent — ni boîte noire, ni magie.

Conséquence pratique, et c'est pour ça que je donne toujours le nombre de
questions qui départagent : doubler le nombre de questions ne sert à rien si
elles sont faciles. Ce qui compte, c'est combien font diverger les deux systèmes.

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
▸ Le témoin n'a pas bougé d'une décimale. Sans ça, aucune attribution n'était possible.

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
▸ Dire « non concluant » sur deux niveaux donne du poids au troisième.

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
▸ Ce qui l'a révélé n'est pas une métrique, c'est un détail de style.

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
▸ Suivre le tableau du doigt. κ, c'est ce qu'on a gagné sur ce qu'il restait à gagner.

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
▸ Ici c'est le κ qui accable à tort. Regarder la répartition avant de juger le chiffre.

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
Sur mes 50 items, **17 portent un désaccord sur au moins un contrôle, dont 15 que
le verdict masque.** Le verdict est reproductible ; les **raisons** le sont
beaucoup moins. Or c'est sur les raisons que le juge s'entraîne.

<!--
▸ L'écart entre 0,880 et 0,44 est l'information. Le plafond, c'est le corpus.

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
▸ Ne jamais donner l'exactitude sans le taux d'erreurs attrapées.

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

**12 items les départagent. 6 d'un côté, 6 de l'autre** — une pièce équilibrée.

Je ne peux pas dire que le fine-tuning n'apporte rien. Je peux dire que
**mes 50 items ne voient pas la différence** : en dessous de 15 points d'écart,
ils sont aveugles.

**Non concluant** — et cette issue était **écrite avant** de lancer la mesure.

<!--
▸ NE PAS dire « ça n'améliore pas ». Dire : mes 50 items ne voient pas la différence.

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

Troisième : ce qu'il a acheté est ailleurs, c'est la diapositive d'après.

« Pas de différence détectée » et « pas de différence » sont deux affirmations
différentes : la première parle de mon dispositif, la seconde parlerait du monde.
Traduire l'intervalle à voix haute — la vérité peut être une perte de 14 points
comme un gain de 14. Pour trancher il faudrait plus d'items, pas un autre calcul.
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

**Le contre-chiffre : la stabilité du verdict baisse, 76 % → 58 %.**
La baseline est stable parce qu'elle **décide avant de regarder.**

<!--
▸ Une leçon d'intégration, pas d'intelligence. Une chaîne a besoin d'un contrat.

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

Sur la stabilité qui baisse, si on demande : les deux chiffres ne mesurent pas le
même objet. D'un côté la constance d'un seul jeton écrit tôt ; de l'autre celle
d'une conjonction de trois contrôles, dont n'importe lequel qui bascule fait
basculer le verdict. Mesuré : le verdict du fine-tuné ne bouge jamais sans qu'un
contrôle bouge — 0 item sur 50 — et 8 fois la conjonction absorbe la variation.
La stabilité de la baseline est donc moins chère, et elle n'achète aucune
justesse : les deux sont à 76,0 %.

Et aucune des trois variantes ne passe le filtre de recevabilité fixé d'avance :
au mieux 76 % de stabilité pour un seuil à 95 %.
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
▸ Un humain n'intervient pas « parfois ». Il intervient quand le juge s'est contredit — c'est mesuré.

« Parfois un humain » n'est pas une politique : il faut un déclencheur mesurable,
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
▸ Le seul choix qui se retourne toujours contre vous : compter le douteux comme un succès.

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
▸ Partir du budget humain, pas du seuil. Finir sur : mon juge n'est pas prêt pour la production.

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
▸ La conclusion. Ralentir. « Corrigé parce qu'on a regardé, jamais parce qu'une métrique a protesté. »

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
▸ Les trois s'appliquent sans rien installer. Le dépôt permet de tout rejouer.

Les trois sont applicables sans rien installer et sans budget.

La troisième est celle que j'aurais voulu entendre il y a six mois : elle m'a
coûté cinq mesures nulles et une conclusion publiable entièrement fausse.

Le dépôt contient tout ce qui permet de rejouer les chiffres de ce talk — le
corpus, le protocole pré-enregistré avec ses amendements datés, et les
générations écartées avec la raison de leur mise à l'écart.
-->
