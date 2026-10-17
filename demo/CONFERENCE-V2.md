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
Bonjour à tous, merci de prendre un peu de votre temps pour discuter des chatbots,
mais aussi des agents.

Je m'appelle Mehdi Elketroussi, je suis marié et père de 2 petites princesses,
et quand tout le monde est à l'école ou au travail, je suis software engineer.
J'aime beaucoup les sujets liés à la perf et à la qualité, et depuis la popularisation des LLM
une question m'est venue : comment savoir si mon RAG s'améliore ? Et surtout :
comment faire confiance à une mesure, quand la même question peut donner deux
réponses différentes ?
-->
---

## Air Canada, 2024

Le chatbot invente une politique de tarif deuil.

Air Canada plaide : le chatbot est
**« une entité juridique distincte, responsable de ses propres actes »**.

Le tribunal :

> « This is a remarkable submission. While a chatbot has an interactive
> component, it is still just a part of Air Canada's website. »

**650,88 $ CA**

<span class="ref">Moffatt v. Air Canada, 2024 BCCRT 149</span>

<!--
Mais avant de commencer, j'aimerais vous raconter une histoire, celle de Jake
Moffatt, qui en novembre 2022 a dû réserver un vol pour les funérailles de sa
grand-mère. Il se renseigne et après un court échange avec l'assistant du site,
il voit qu'il peut effectuer les demandes après le voyage.

Sauf que non, le chatbot avait « halluciné » cette réponse, la vraie règle
présente sur le site exige que la demande se fasse avant le voyage.

Cette affaire passe devant le tribunal, pour Air Canada le
chatbot est une entité juridique distincte, responsable de ses propres actes, et
l'utilisateur doit vérifier les informations sur le site.

Et c'est la réponse du tribunal qui est importante, je vous l'affiche (laisse 3 ou 4 secondes pour que le public lise)

Le chatbot fait partie du site, et l'entité responsable du site
est donc légalement responsable des réponses du chat. Ce n'est pas juste un POC,
c'est un engagement.

Ici, six cent cinquante dollars.

Petite question pour le public : qui a déployé un LLM, ou un RAG, en production ?
Autre question : et qui a mis en place un système d'évaluation des réponses de
son système ?
==============================================================

⚠ Vérifié sur la décision : membre Christopher C. Rivers, 14 février 2024,
650,88 $ CA, au titre de la NÉGLIGENCE DANS LA PRÉSENTATION D'INFORMATIONS
(negligent misrepresentation) — le motif a quitté l'écran le 2026-10-13 pour
alléger, le dire si on demande sur quel fondement Air Canada a été condamnée.
Ne pas citer de mémoire le délai annoncé par le chatbot ni le total avec frais —
non vérifiés, volontairement absents de l'écran.

⚠ Si on demande la défense exacte : Air Canada a aussi plaidé que Moffatt
n'avait pas suivi la procédure. Détail vérifié et utile pour une salle de devs —
la réponse du chatbot contenait elle-même un lien vers la page « Bereavement
travel », qui disait le contraire. Sources : McCarthy Tétrault, CTV News.
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
Mais derrière chacune de ces lignes, il y a aussi une histoire, un Jake Moffatt blessé,
des citoyens dans le doute, des ventes irrégulières ...
Et en réalité, j'aurais pu en remplir beaucoup plus ...
Mais je ne garde que ce que je peux prouver — à droite, ceux que je n'ai pas
pu vérifier sur source primaire.
Vous voyez où je veux en venir ?

==============================================================

⚠ Mata v. Avianca : SIX décisions inventées (Varghese, Shaboon, Petersen,
Martinez, Estate of Durden, Miller), pas neuf. Les trois autres noms qui
circulent (Zicherman, Ehrlich, In re Air Crash Disaster) sont de VRAIES
décisions citées à l'intérieur des fausses. Ne pas se tromper en public.

⚠ NYC MyCity : l'audit du Contrôleur est une source primaire, VÉRIFIÉE. Mais il
ne documente PAS le conseil d'enfreindre la loi — ça, c'est The Markup, mars
2024, donc de la presse. Ne citer de l'audit que ce qu'il contient : les réponses
incohérentes, et le taux d'exactitude annoncé qui excluait les mauvais cas.
C'est le meilleur exemple du talk : une administration publie 95 % avec une
métrique qui écarte les cas gênants, et c'est un auditeur public qui le relève.

⚠ Deloitte descend chez les cas rapportés : concordant sur AP, Fortune et CFO
Dive, mais la source primaire du DEWR n'a jamais pu être ouverte. Si tu la
vérifies, la ligne peut remonter.

⚠ Deux secondes minimum à l'écran : en dessous, la salle ne perçoit pas que la
diapositive est dense et l'effet de volume tombe.
-->
---

## Pourquoi personne n'a rien vu

**Le faux avait exactement la forme du vrai.**

> *Varghese v. China Southern Airlines Co., 925 F.3d 1339 (11th Cir. 2019)*

**Cet arrêt n'existe pas.**

- Un test unitaire vérifie une valeur, **pas un raisonnement**

- Comparer mot à mot : une réponse **juste** formulée
  autrement est pénalisée, une **fausse** bien écrite passe

<!--
Alors pourquoi personne n'a rien vu ?

Parce que le faux avait exactement la forme du vrai. Regardez la référence à
l'écran : les parties, le numéro de recueil, la cour, l'année. Elle a tout. Un
avocat ne relit pas une citation bien formatée — et c'est tout ce que notre œil
vérifie.

Cet arrêt n'existe pas.

Et nos outils ne nous aident pas davantage. Un test unitaire vérifie une valeur
de retour, pas un raisonnement. Et comparer mot à mot la réponse attendue et la
réponse obtenue, ça pénalise une bonne réponse formulée autrement, et ça laisse
passer une mauvaise réponse bien écrite.

Donc on livre en se fiant à l'impression qu'on a en relisant trois sorties à la
main.

==============================================================

⚠ Varghese v. China Southern Airlines, 925 F.3d 1339 (11th Cir. 2019) : c'est la
référence réellement déposée dans Mata v. Avianca, pour un arrêt qui n'existe
pas. Concordant sur Volokh et Simon Willison, qui citent le dépôt — pas vérifié
sur l'ordonnance elle-même.

⚠ Si on demande : à cette page du recueil, le vrai arrêt voisin est A.D. v.
Azar, 925 F.3d 1291. Le modèle n'a pas tiré un numéro au hasard, il en a produit
un plausible juste à côté d'un vrai. C'est exactement le propos de la diapo.

⚠ « La même question admet dix bonnes réponses » n'est écrite nulle part dans le
support ; le deuxième point la porte implicitement. À dire explicitement sur
« Comment mesurer… » si on demande « pourquoi ne pas comparer à la réponse
attendue ? ».
-->
---

## OllamAssist

<div class="carte">
<div class="texte">

**Un assistant de code dans IntelliJ,
entièrement local. Mon labo.**

D'abord un **chatbot** — il répond avec ce qu'il sait.

Puis un **agent** — il lit mon workspace,
et répond sur **mon** code.

**Sa réponse ne dépend plus surtout du modèle.
Elle dépend de ce qu'il a trouvé.**

</div>
<img src="img/ollamassist-marketplace.png" width="384" height="319" alt="Carte OllamAssist sur la JetBrains Marketplace">
</div>

<!--
Moi, mon terrain, c'est OllamAssist. C'est un assistant de code dans mon IDE,
qui tourne entièrement sur ma machine. Je l'ai écrit pour comprendre ce que l'IA
fait vraiment, plutôt que de le lire. C'est mon labo, que j'ai partagé.
La codebase qu'il indexe fait 162 fichiers Java, et c'est la mienne — donc je
vois quand il se trompe.

Au début, c'est un chatbot : je pose une question, il répond avec ce qu'il sait.
Puis c'est devenu un agent : il lit mon workspace, et il répond sur mon code.

Et là, tout change. Sa réponse ne dépend plus surtout du modèle. Elle dépend de
ce qu'il a trouvé.

C'est ce déplacement qui justifie de mesurer la récupération, et pas seulement le
modèle.

==============================================================

⚠ À FAIRE LA VEILLE : l'image de droite est un gabarit. Prendre une capture de
la carte sur plugins.jetbrains.com/plugin/26388 et ÉCRASER le fichier
demo/img/ollamassist-marketplace.png — même nom, idéalement 768 x 638. Puis
relancer le rendu. Aucune modification du markdown.
Un iframe a été écarté : il exigeait du réseau pendant la présentation et ne
s'exportait pas en PDF.

⚠ Les faits, si on demande : plugin JetBrains publié sur la Marketplace, propulsé
par Ollama, avec un mode entièrement hors-ligne. Chat dans l'IDE, autocomplétion
expérimentale, messages de commit générés depuis le diff.

⚠ Les 162 fichiers Java sont désormais dits à voix haute. Le prolongement, si on
demande : sur du code que je ne connais pas, je n'aurais aucun moyen de juger le
juge.

⚠ « Elle dépend de ce qu'il a trouvé » est la charnière de tout l'exposé. Tant
que c'est un chatbot, la qualité vient du modèle ; dès qu'il lit le workspace,
elle vient d'abord de ce que la récupération a rapporté. Ralentir sur cette
phrase.

⚠ OllamAssist PEUT faire une recherche internet : optionnelle, désactivée par
défaut. Dire « peut tourner entièrement hors-ligne », jamais « tourne entièrement
hors-ligne et ne sort jamais ».

⚠ Le tunnel et la peur d'avancer à l'aveugle appartiennent à la diapo suivante
(« Comment mesurer… »), qui est construite dessus. Ne pas les dire ici.
-->
---

## Comment mesurer la qualité des réponses de mon assistant ?

- Deux stratégies de RAG, Lucene et Neo4j —
  **aucun moyen de les départager**

- Trois rôles, une seule personne : **j'écris, je choisis, je juge** —
  **un dispositif qui ne peut pas me contredire ne mesure rien**

- Ma crainte : **avancer à l'aveugle.**

**Comment savoir que mon RAG s'améliore,
sans croire mon juge sur parole ?**

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

Écrire un livre est difficile. 
Le lire et dire s'il est bon, beaucoup moins.


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

**1. Deux copies côte à côte** — laquelle est la meilleure ?
Je sais les classer. **Pas si l'une mérite la moyenne.**

**2. Le corrigé type** — fiable, mais il faut
**écrire le corrigé de chaque question.**

**3. Le barème seul** — une liste de points à vérifier.
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

Avant de lire, le correcteur vérifie qu'elle est **signée**,
dans la **bonne matière**, pas **hors-sujet**.

Il ne lit pas pour ça. **Il écarte.**

```
  Ça compile ?             →  le compilateur
  Le JSON est valide ?     →  un parseur
  Le style tient ?         →  le linter
```

**Tout ce qui est déterministe ne passe pas par le juge** —
pas pour l'économiser, **parce qu'il est moins bon que le compilateur à ça.**

Chez moi : l'équilibrage des parenthèses. **Pas un filtre, un début.**

```
   [ FILTRE L0 ] ───►  ( LE JUGE )
    écarte sans lire
```

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

[AJOUT AU SCHÉMA : la naissance du schéma, et DEUX boîtes d'un coup. À gauche,
ce qui entre : la CI, qui rejoue les MÊMES questions à chaque modification.
Puis, avant le juge, un filtre déterministe qui écarte sans lire — rien de ce
qu'il recale n'atteint le LLM. La brique CI venait de la diapositive « quand
évaluer ? », supprimée le 2026-10-14.]

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

<!-- _class: dense -->

## Ce que le juge rend

Pas une note sur 10 — **« 13/20 » ne dit pas si on livre.**
Des **contrôles, un par critère**, vrai ou faux.

```
  ✗  {                        ✓  <thinking> … </thinking>
       "verdict": "PASS",         {
       "checks": { … }              "checks": { … },
     }                              "verdict": "FAIL"
                                  }

     décide, puis justifie       raisonne, constate, conclut
```

Un modèle génère **de gauche à droite**, il ne revient pas en arrière.
Verdict en premier : les contrôles sont écrits pour **lui donner raison**.

**PASS si et seulement si tous les contrôles sont vrais.**

```
   CI ─► [ L0 ] ─►  ( LE JUGE ) ─►  thinking · checks · verdict
```

<!--
[À REFORMULER AVEC TES MOTS]

Maintenant, sous quelle forme il rend son verdict. Et là il y a deux décisions
qui ne coûtent rien et qui changent tout.

La première : pas de note sur dix. « Treize sur vingt », ça ne me dit pas si je
livre. Des contrôles, un par critère, vrai ou faux. Et le verdict est vrai
seulement si tous les contrôles le sont — pas de demi-mesure.

La seconde, et c'est la moins intuitive du talk : l'ordre des champs.

Un modèle génère de gauche à droite. Il ne revient jamais en arrière. Donc si le
verdict est écrit en premier, tout ce qui suit est écrit pour lui donner raison.
Il décide, puis il justifie. Dans l'autre sens, il constate, puis il conclut.

Deux caractères dans un schéma JSON. Aucun modèle, aucun prompt ne rattrape un
mauvais ordre de champs.

==============================================================

[AJOUT AU SCHÉMA : la sortie du juge n'est plus une note, c'est une liste de
contrôles puis un verdict.]

⚠ D'où viennent mes critères, si on demande : trois sont génériques pour toute
analyse de code, trois dépendent du type de tâche, et neuf sont LUS DANS LA
REQUÊTE — « sans dépendance externe » devient un critère nommé, sinon il
n'existe pas. Je ne les choisis pas pour la troisième catégorie.

⚠ Je n'ai PAS mesuré l'écart entre les deux ordres : j'ai choisi le bon dès le
départ. C'est un raisonnement sur le fonctionnement de la génération, pas un
résultat expérimental. Le dire tel quel.

⚠ Ce que j'ai mesuré en revanche : le verdict correspond bien à ses propres
contrôles 99,3 % du temps. Donc je peux le recalculer et détecter un juge qui se
contredit.

⚠ Un bon critère tient trois tests : décidable — la réponse se lit dans ce qui
est fourni ; falsifiable — je sais dire ce qui le rendrait faux ; reproductible —
deux personnes répondent pareil. Le troisième se mesure, et c'est le seul qui
tranche.
-->

---

## Le correcteur se laisse impressionner par l'épaisseur

Quatre pages, c'est sérieux. Une réponse courte, ça fait négligé.

**Le même défaut, écrit deux fois** — une version bavarde, une version sèche.
Si le juge valide plus souvent la bavarde, il note la forme, pas le fond.

**Le test répond : 46 % de faux PASS sur les défauts bavards.**

```
   CI ─► [ L0 ] ─►  ( LE JUGE ) ─►  thinking · checks · verdict
                         ▲
                 le même défaut, bavard ET sec
```

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

⚠ Le chiffre exact : 46 % de faux PASS sur défauts verbeux contre 40 % sur
défauts concis — l'écart lui-même est petit, c'est le NIVEAU qui est mauvais.
Ne pas vendre l'écart, vendre le niveau.
-->

---

## Le même devoir, selon sa place dans la pile

La première copie et la vingtième ne sont pas notées pareil.

Pour un juge, c'est **l'ordre des extraits** qu'on lui donne.

**Je mélange le contexte — avec une graine tirée de la question**, pour que la
mesure se rejoue à l'identique.

La parade atténue. **Et je sais de combien il reste :**
**12 verdicts sur 60 basculent au seul réordonnancement.**

```
   RÉCUPÉRATION ─► [ mélange grainé ] ─┐
                                       ▼
   CI ─► [ L0 ] ───────────────► ( LE JUGE ) ─► thinking · checks · verdict
```

<!--
[À REFORMULER AVEC TES MOTS]

Deuxième biais : la place dans la pile. Un correcteur ne note pas la première
copie comme la vingtième. Pour un juge LLM, ce n'est pas la pile, c'est l'ordre
des extraits qu'on lui donne dans le contexte.

Ma parade : je mélange les extraits. Mais attention — avec une graine tirée de la
question, sinon la mesure n'est plus rejouable.

Et je peux chiffrer ce qui reste. Douze verdicts sur
soixante basculent au seul réordonnancement, à récupération strictement
identique.

==============================================================

[AJOUT AU SCHÉMA : c'est ici que la RÉCUPÉRATION apparaît sur le schéma — elle
est le préalable. Puis une boîte « mélange grainé » entre elle et le juge.]

⚠ Sans graine, les exécutions de la veille faisaient bouger le même bras de
55,9 % à 43,3 %. Une mesure qui ne se rejoue pas n'est pas une mesure.

⚠ SOURCE DU 12/60, recalculée le 2026-10-17. Comparaison du bras **Lucene**, qui
était configuré à l'identique dans les deux scénarios du run non graîné
(`benchmarks/non-reproductible-20260923-melange-non-graine/`) :
    contextes stockés identiques  60/60   (la récupération ne bouge pas)
    hintCoverage identique        39/60   (les 21 autres : la troncature à 6000
                                           après mélange ne garde pas les mêmes extraits)
    bascules de verdict           24/60   dont **12 à hintCoverage identique**
Ce sont ces 12 que la diapositive annonce : contenu strictement inchangé, ordre
seul modifié. Le dénominateur affiché (60) est le nombre de questions, pas les 39
à contenu identique — donc le chiffre **sous-estime** le biais (12/39 = 31 %).
Si on est challengé, c'est l'argument : la formulation est conservatrice.

⚠ LE TÉMOIN, et il est net : rejoué AVEC la graine, le même bras Lucene donne
**0 bascule sur 60** et 60/60 hintCoverage identiques entre les deux scénarios
(48,3 % des deux côtés). C'est ce qui prouve que la graine a tenu — et c'est le
même témoin que celui invoqué diapositive 25.

⚠ Ne pas confondre avec le « A contre B puis B contre A » de la comparaison par
paires : là c'est l'ordre de DEUX RÉPONSES, ici c'est l'ordre des EXTRAITS.
-->

---

## Un correcteur indulgent a l'air fiable

Il valide presque tout, donc il se trompe rarement —
seulement sur les copies qu'il aurait dû recaler.

```
   27 mauvaises copies   →  il en recale 17.  Il en laisse passer 10.
   23 bonnes copies      →  il en valide 21.
```

**76 % de décisions justes. Et près de 4 défauts sur 10 qui passent.**

Le même juge, deux chiffres. **Ne publiez jamais le premier sans le second.**

```
   RÉCUPÉRATION ─► [ mélange grainé ] ─┐
                                       ▼
   CI ─► [ L0 ] ───────────────► ( LE JUGE ) ─► [ LE BANC ]
                                                 justes · attrapées
```

<!--
[À REFORMULER AVEC TES MOTS]

Troisième biais, et c'est celui qu'aucun tableau ne montre : l'indulgence.

Un correcteur qui valide presque tout se trompe rarement. Forcément : il ne se
trompe que sur les copies qu'il aurait dû recaler.

Mon juge, sur vingt-sept mauvaises réponses, en recale dix-sept. Il en laisse
passer dix. Sur vingt-trois bonnes, il en valide vingt et une.

Ça fait soixante-seize pour cent de décisions justes — et quatre défauts sur dix
qui passent. Le même juge, deux chiffres.

Et pour moi les deux erreurs n'ont pas le même prix : un défaut qui passe, c'est
une explication fausse sur ma codebase livrée à l'utilisateur. Un bon code
recalé, c'est juste une relecture inutile.

==============================================================

[AJOUT AU SCHÉMA : ce n'est pas le juge qui sort deux chiffres, c'est le BANC
qui le mesure — une boîte en aval, avec deux cadrans : les décisions justes, et
les erreurs attrapées.]

⚠ TOUT LE SUPPORT PARLE DU JUGE À CONVENTIONS, de bout en bout. Ne pas mélanger
les deux variantes d'une diapositive à l'autre. Mesuré sur results/runs/ :

  |                        | fine-tuné | À CONVENTIONS |
  | matrice                | 16/11/22  | 17/10/21      |
  | défauts qui passent    | 11/27 41% | 10/27 37%     |
  | verbosité verbeux/concis | 46/42 % | 46/40 %       |
  | taux de PASS (150 passes)| 64 %    | 65 %          |
  | justesse               | 76 %      | 76 %          |

Aucun chiffre ne bouge de plus de 4 points : l'indulgence est la même. Ce qui
diffère VRAIMENT entre les deux juges, c'est κ 0,48 contre 0,44 et la stabilité.

⚠ LE BANC RAG A TOURNÉ AVEC LE JUGE FINE-TUNÉ, et la diapositive « Le résultat »
le dit à l'écran. Les deux juges rendent 76 % contre 76 %, p = 1,0000 :
indiscernables EN JUSTESSE, pas en alignement (κ 0,48 contre 0,44).
⚠ Rejouer le banc avec le juge à conventions — rejouer le banc RAG avec le juge à conventions — est
IMPOSSIBLE hors-ligne, mesuré le 2026-10-17. `RetrievalBenchmark.java:447-449`
stocke `generated` **non mélangé et tronqué à 3000** caractères, là où le juge
recevait l'ordre mélangé par `question.hashCode()` tronqué à **6000**. Le prompt
réellement jugé n'est donc pas reconstituable. Et la perte est asymétrique :
**118/120 contextes Lucene amputés (98 %)** contre 4/120 côté Neo4j — rejuger ne
comparerait plus que 2 items Lucene à 116 Neo4j. Il faudrait rejouer la
RÉCUPÉRATION entière (Java + Lucene + Neo4j), hors chemin critique.
→ La phrase à l'écran n'est donc pas une commodité : c'est la seule option.

⚠ QUEL ESTIMATEUR, si on ouvre le dépôt — vérifié le 2026-10-17. L'écran dit
76 % ; `results/report.md` affiche DEUX chiffres pour la même variante :
« Exactitude 73 % » (ligne 11, moyenne des trois passes : 70, 76, 74) et
« Justesse stricte du verdict (vote majoritaire) 76,0 % » (ligne 69). Le support
prend le second, et il est correctement sourcé : la matrice 27/23 → 17/10/21
affichée ici EST le vote majoritaire, et (17+21)/50 = 76 %. Les deux sont justes,
ce sont deux estimateurs. Réponse courte si on la demande : « 76 %, c'est le vote
majoritaire des trois passes ; la moyenne passe par passe donne 73 %. »

⚠ Le n, si on demande — et c'est LA question qui viendra sur cette diapositive :
les 46 % portent sur **8 items verbeux à défaut caché**, contre 19 concis
(results/report.md §2). Un pourcentage à deux chiffres sur 8 cas. Le dire avant
qu'on le demande vaut mieux que de le défendre après.

⚠ Un juge qui répondrait PASS à tout sur un corpus où 95 % des réponses sont
bonnes afficherait 95 % d'exactitude et attraperait zéro erreur. C'est l'exemple
à donner si quelqu'un doute.

⚠ Ce biais recoupe les deux autres : 46 % de faux PASS sur les défauts verbeux,
et un juge qui rend PASS 65 % du temps là où l'étalon en compte 46 %. Trois
mesures indépendantes, un même diagnostic.
-->

---

## Le quatrième, je le cite — je ne le mesure pas

**L'auto-préférence** : un modèle préfère ce qui ressemble à ce qu'il aurait
écrit.

Je ne l'ai **pas mesuré chez moi**. Je le cite.

La parade connue : **ne pas faire juger un modèle par sa propre famille.**

*Et je vous dis ça alors que mon juge, lui, est tout seul. J'y reviens à la fin.*

<!--
[À REFORMULER AVEC TES MOTS]

Il y en a un quatrième, et je vais être clair sur son statut : l'auto-préférence.
Un modèle préfère ce qui ressemble à ce qu'il aurait écrit lui-même.

Celui-là, je ne l'ai pas mesuré. Je le cite. La parade connue, c'est de ne pas
faire juger un modèle par un modèle de sa propre famille.

Je le dis parce que mélanger ce qu'on a mesuré et ce qu'on a lu, c'est la
meilleure façon de perdre la confiance de la salle sur tout le reste.

Et puisque j'y suis : je vous donne cette parade alors que mon juge, lui, est
tout seul. Gardez-le en tête, j'y reviens à la fin.

==============================================================

⚠ LA DETTE OUVERTE ICI SE PAIE EN CONCLUSION — PAR UNE MESURE, PAS PAR UN PLAN.
Dix mots posés tôt pour que la fin soit un remboursement et pas une idée qui
tombe du ciel. La conclusion la rembourse en parlant TOUJOURS DE FAMILLE — « je
vous l'ai dit, alors je l'ai fait, et ce n'est pas la famille ». Ne retirer cette
phrase que si la conclusion cesse de parler de famille.

⚠ « VOTRE JUGE EST-IL DE LA MÊME FAMILLE QUE CE QU'IL JUGE ? » — NON, pas dans
les résultats publiés.
Le juge est Qwen2.5-Coder-14B. Le seul autre Qwen du pipeline est
`rag.hyde.model = qwen2.5:7b` (Neo4jGraphRagStrategy.java:87), et il N'A PAS
TOURNÉ : ligne 246, le modèle HyDE n'est branché que si le reranking est actif,
or les deux scénarios du banc (`hybrid|hybrid-graph` et `hybrid|hybrid`)
n'activent ni le reranking ni HyDE (FeatureFlags). Aucun recouvrement de
familles dans la mesure.

⚠ Trouvé au passage, à NE PAS mettre dans le talk mais à savoir : le preset
`hybrid-graph-hyde` pose hydeEnabled=true ET rerankingEnabled=false, donc
ligne 246 lui passe un modèle null et ligne 1718 rend la requête d'origine sans
rien dire. Ce preset tournerait SANS HyDE en annonçant son nom. Jamais publié,
donc rien d'invalidé — mais ce serait un sixième « BUILD SUCCESS » sur du vide.

⚠ Ne PAS dire « la littérature montre qu'un jury est plus stable » : Verga et al.
ont mesuré l'accord avec l'humain, le biais intra-modèle et le coût, PAS la
stabilité. Formulation sûre : « un jury corrige une autre classe d'erreur —
l'angle mort partagé — et mécaniquement il lisse le bruit. »

⚠ C'est la diapositive qui protège les trois précédentes. Si on ne distingue pas
mesuré et cité, la salle a raison de douter de tout. Référence pour les biais de
position, verbosité et auto-préférence : Zheng et al., NeurIPS 2023, MT-Bench.

⚠ Possible de la fusionner avec la précédente si le temps manque — mais ne pas la
supprimer : c'est elle qui rend les trois autres crédibles.
-->

---

## Et le RAG a ses propres pièges

Trois cas, tirés de **vraies extractions** sur ma codebase.

**Le quasi-homonyme** — je demande `OllamaService`, le moteur rend
`OllamaSettings`. Le contexte **ressemble** à une réponse.

**Les corps tronqués** — dix extraits, aucun corps de méthode,
pour une question en « comment ».

**Le vrai mais non étayé** — réponse exacte dans ma codebase,
absente du contexte fourni. **Elle doit tomber.**

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

Donc mon juge ne rend pas **un** verdict. Il répond séparément :

```
   le contexte est-il pertinent ?
   permet-il de répondre sans rien supposer ?
   la réponse s'appuie-t-elle sur lui ?
```

**Le moteur n'a rien trouvé d'utile, ou le modèle a mal utilisé ce qu'il avait.
Sans cette distinction : un taux d'échec, et aucune idée de quoi corriger.**

```
   RÉCUPÉRATION ─► [ mélange ] ─┐ le contexte entre AUSSI
                                ▼
   CI ─► [ L0 ] ──────► ( LE JUGE ) ─► pertinent ? suffisant ? étayé ?
                        question + contexte + réponse  └─► [ LE BANC ]
```

<!--
[À REFORMULER AVEC TES MOTS]

Vous vous souvenez, je vous ai dit que mon juge reçoit le contexte en plus de la
réponse. Voilà pourquoi.

Il ne rend pas un verdict, il répond séparément à trois questions. Est-ce que le
contexte est pertinent ? Est-ce qu'il permet de répondre sans rien supposer ?
Est-ce que la réponse s'appuie dessus ?

Parce que ça distingue deux pannes très différentes : le moteur n'a rien trouvé
d'utile, ou le modèle a mal utilisé ce qu'il avait. Sans ça, j'ai un taux
d'échec et aucune idée de quoi corriger.

==============================================================

[AJOUT AU SCHÉMA : le contexte récupéré entre DANS le juge, pas seulement dans
l'assistant. Et la sortie du juge se décompose.]

⚠ Ne pas réintroduire ici les trois ENTRÉES du juge : déjà montrées et dites
diapositive 7. Cette diapositive ne porte que ses trois QUESTIONS.

⚠ C'est ce qui permettra, plus tard, de dire que Neo4j souffre d'un défaut de
rappel — 66 % de contextes jugés insuffisants contre 40 % — et pas d'un problème
de bruit. Sans cette décomposition : 25 points d'écart sans explication.
-->

---

## Tout ça, écrit, fait quatre paragraphes

**1. Verdict** — PASS si et seulement si tous les contrôles sont vrais.

**2. Préférence ou obligation** — « si tu as le temps » non suivi :
contrôle vrai, écart noté dans le `<thinking>`.
Verbeux mais correct : **jamais pénalisé.**

**3. Un contrôle, un critère.** Pas de double sanction.

**4. Citations** — on ne sanctionne que ce qui **déforme** le contexte.

**Avant : 0 % de JSON exploitable. Après : 100 %, et 76 % de justes.**

```
  ╔═ LES 4 CONVENTIONS ═════════════════════════════════════╗
  ║  RÉCUP ─► [mélange] ─┐                                  ║
  ║  CI ─► [L0] ─────────► ( LE JUGE ) ─► checks ─► [ BANC ]║
  ╚═════════════════════════════════════════════════════════╝
```

<!--
[À REFORMULER AVEC TES MOTS]

Vous venez de me voir construire ce juge pendant neuf diapositives. Le filtre
avant le juge, le format de sortie, les contrôles avant le verdict, les parades
contre les biais, le contexte qui entre dedans.

Tout ça, une fois écrit, ça fait quatre paragraphes.

Le premier, vous le connaissez déjà : PASS seulement si tous les contrôles sont
vrais. Le deuxième règle le cas de la consigne polie — « si tu as le temps » —
et il interdit de pénaliser une réponse juste parce qu'elle est longue. C'est là
qu'on dit au juge où consigner ce qu'il a laissé passer : dans son bloc de
raisonnement. Le troisième évite qu'un même défaut soit puni deux fois. Le
quatrième dit qu'on ne sanctionne la citation que si elle déforme.

Et voilà le chiffre. Avant ces quatre paragraphes, mon juge ne rendait aucun
JSON exploitable. Zéro sur cent cinquante. Après, cent pour cent de JSON
exploitable, et soixante-seize pour cent de réponses justes.

Avant d'envisager quoi que ce soit de plus sophistiqué — écrivez vos conventions.

==============================================================

[AJOUT AU SCHÉMA : les conventions ne sont pas une boîte de plus, c'est le cadre
qui entoure tout le schéma — elles s'appliquent à chaque contrôle.]

⚠ Les chiffres : 0 % → 100 % de JSON exploitable, 0 % → 76 % de réponses justes.
Le texte intégral est dans judge-finetune/configs/conventions.md.

⚠ Cette diapositive ferme la section construction. C'est le paiement des neuf
diapositives précédentes : ne pas l'expédier, c'est elle qui leur donne un sens.

⚠ Elle rend l'action n°1 de la conclusion redondante : là-bas, une ligne de
rappel suffit désormais, pas une explication.
-->

---

## L'étalon, et la signature que j'y ai trouvée

Il faut des réponses **dont je connais déjà le verdict**.
200 exemples, 50 **relus en aveugle** : 47 verdicts identiques sur 50.
**Un relecteur contre mes étiquettes** — pas deux humains entre eux.

**17 requêtes portaient la même incise** —
*« si tu as le temps, dis un mot de X »*. **Les 17 étaient PASS.**

Il n'apprend pas à juger. Il apprend à **repérer ma signature.**

Correctif : ajouter l'incise à des réponses en échec, **en paragraphe isolé**.
Nouvelle règle apprise : *paragraphe isolé ⇒ échec*. **30 sur 30.**

**Corriger un corpus, c'est l'écrire encore — et toute écriture signe.**

<!--
[À REFORMULER AVEC TES MOTS]

Pour vérifier un juge, il me faut des réponses dont je connais déjà le verdict.
Donc un étalon : deux cents exemples, cinquante relus en aveugle, quarante-sept
verdicts identiques sur cinquante.

Un point d'attention tout de suite : à partir d'ici il y a DEUX jeux, et je ne
veux pas que vous les confondiez. Cinquante copies déjà corrigées, qui servent à
vérifier le juge. Et soixante questions sur ma codebase, qui serviront à comparer
les deux moteurs. Deux jeux, deux rôles.

Sa limite, je vous la dois tout de suite : UN relecteur, contre des étiquettes
écrites par un modèle. C'est la faiblesse la plus sérieuse de tout ce que je vous
montre.

Et c'est là que le corpus m'a piégé.

Dix-sept requêtes de mon corpus portaient la même incise : « si tu as le temps,
dis un mot de X ». Les dix-sept étaient étiquetées PASS. Sans que je m'en rende
compte, j'avais associé une tournure de politesse à des réponses que je trouvais
bonnes.

Un juge n'a plus qu'à détecter cette chaîne pour marquer dix-sept points. Il
n'apprend pas à juger, il apprend à repérer ma signature.

Le correctif était évident : la même incise sur des réponses en échec. Sauf que
je l'ai mise en paragraphe isolé, là où les dix-sept d'origine la portaient au
fil du texte. Nouvelle règle apprise : paragraphe isolé, donc échec. Trente sur
trente.

J'avais aggravé le problème en le réparant. Et ça a traversé une régénération,
une validation à zéro erreur, trois mesures et un commit.

==============================================================

⚠ C'est aussi la diapositive qui introduit le corpus : sans elle, le « κ du
corpus » deux diapos plus loin tombe du ciel.

⚠ Toute correction d'un corpus est une nouvelle écriture, et toute écriture
laisse une signature. C'est la leçon, pas l'anecdote.

⚠ Ne pas appeler ces 50 items « golden set » ni les confondre avec les 60
questions du banc. Deux jeux, deux rôles.
-->

---

## Ce qui l'a trouvée : un humain

Les métriques ont trouvé **ce que je leur avais demandé de chercher.**

L'humain a trouvé **ce que je ne savais pas chercher.**

Un relecteur a répondu **différemment** sur un item, après avoir appliqué la
règle correctement quatre fois de suite.

Ce n'était pas un relâchement. **Le stimulus était réellement différent.**

<!--
[À REFORMULER AVEC TES MOTS]

Alors qu'est-ce qui l'a trouvée ?

Les métriques ont trouvé ce que je leur avais demandé de chercher. L'humain a
trouvé ce que je ne savais pas chercher.

Concrètement : un relecteur a répondu différemment sur un item, après avoir
appliqué la règle correctement quatre fois de suite. Ce n'était pas un
relâchement — le stimulus était réellement différent, et c'est en creusant ce
désaccord que la règle est apparue.

Un balayage automatique cherche les régularités qu'on a listées. Il ne peut pas
signaler celle à laquelle on n'a pas pensé. Et une fuite, par définition, c'est
celle à laquelle on n'a pas pensé.

==============================================================

⚠ Ralentir. C'est la diapositive qui porte la conclusion du talk, et c'est aussi
la première ligne de son tableau final.

⚠ Si le temps manque vraiment, c'est celle-ci qui se fusionne avec la précédente
— mais on y perd la phrase, et c'est une des deux ou trois que la salle peut
retenir.
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

```
  ╔═ LES 4 CONVENTIONS ═════════════════════════════════════╗
  ║  RÉCUP ─► [mélange] ─┐                                  ║
  ║  CI ─► [L0] ─────────► ( LE JUGE ) ─► checks ─► [ BANC ]║
  ║                           ▲                        │    ║
  ║                           └── aligné ? stable ? ───┘    ║
  ╚═════════════════════════════════════════════════════════╝
```

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

[AJOUT AU SCHÉMA : une BOUCLE DE RETOUR sur le juge lui-même. Jusqu'ici le
schéma était une chaîne qui va dans un sens ; à partir d'ici il se vérifie.
Cet ajout change sa nature. Le corpus viendra encore s'ajouter deux diapos plus loin.]

⚠ C'est la bascule du talk. Ralentir, marquer un temps.

⚠ Ne pas annoncer la réponse ici. Le fait que mon juge échoue son propre seuil
arrive plus tard, et ça n'a de force que si la question est posée franchement
d'abord.
-->

---

## Est-ce qu'il marche, oui ou non ?

| | justesse | accord | stabilité | schéma |
|---|---|---|---|---|
| **invite nue** | 0 % | 0,00 | 0 % | 0 % |
| **+ 4 conventions** | **76 %** | 0,48 | **76 %** | 0 % |
| **+ entraînement** | **76 %** | 0,44 | 58 % | **100 %** |
| **+ un modèle 32B** | **90 %** | **0,80** | **92 %** | 0 % |

**Quatre paragraphes achètent l'essentiel de la justesse.
91 minutes d'entraînement n'achètent qu'une colonne — la dernière.**

κ, c'est l'accord une fois retiré ce que le hasard donne.
**Ni les conventions ni l'entraînement n'ont amélioré cette colonne.**

**Je ne lui fais pas confiance sur une copie.
Je lui fais confiance sur soixante.**

*Et vous, vous la connaissez, la précision de votre évaluateur ?*

```
  [ LE CORPUS ] ─────────── étalon ──────┐
  ╔════════════════════════════════════╗ │
  ║  RÉCUP ─► [mélange] ─┐             ║ ▼
  ║  CI ─► [L0] ─────────► ( LE JUGE ) ─► checks ─► [ BANC ]
  ║                           ▲                        │
  ║  LES 4 CONVENTIONS        └── aligné ? stable ? ───┘
  ╚════════════════════════════════════╝
```

<!--
[À REFORMULER AVEC TES MOTS]

Alors est-ce qu'il marche ? Voilà les quatre versions de mon juge, et ce que
chacune a acheté.

Première ligne, l'invite nue : le modèle, ma question, rien d'autre. Zéro. Et pas
zéro de justesse — zéro JSON exploitable. Cent cinquante générations, aucune
lisible par une machine.

Deuxième ligne : j'ajoute mes quatre paragraphes de conventions. Rien d'autre ne
change — même modèle, même question, le suffixe d'invite et c'est tout.
Soixante-seize pour cent.

Troisième ligne : je l'entraîne. Quatre-vingt-onze minutes sur mon corpus.
Soixante-seize pour cent. Le même chiffre.

Maintenant lisez les colonnes, pas les cases.

La justesse ne bouge plus entre la deuxième et la troisième ligne. L'accord — le kappa, c'est
l'accord une fois retiré ce que le hasard donne tout seul — ne s'améliore pas
non plus : zéro quarante-huit, puis zéro quarante-quatre. Et la stabilité, elle,
BAISSE : soixante-seize, puis cinquante-huit.

La seule colonne que l'entraînement a achetée, c'est la dernière. Le schéma
imbriqué, cent cinquante fois sur cent cinquante — donc un accord mesurable
contrôle par contrôle. De l'auditabilité. Pas du jugement.

Quatrième ligne. Pas pour gagner des points : pour poser à mon banc la question
que vous devriez poser au vôtre. Est-ce que je mesure encore mon juge, ou
est-ce que je mesure mes copies ?

Le contrôle tient en une phrase : faites passer un modèle que vous attendez
meilleur, et regardez si l'aiguille bouge. Mêmes copies, mêmes conventions, un
modèle deux fois plus gros. Trente-huit copies justes chez moi, quarante-cinq
chez lui.

Elle a bougé. Mon banc a de la marge : mes soixante-seize pour cent parlent de
mon juge, pas de mon corpus.

Et la dernière colonne : zéro. La taille n'achète pas le schéma. L'entraînement,
lui, l'achète en entier.

Et ça compte pour la suite : c'est la troisième ligne qui a tourné sur le banc
que je vais vous montrer.

Donc je ne lui fais pas confiance sur une copie. Si je lui en soumets une seule
et qu'il répond PASS, je ne sais pas si c'est son jugement ou son tirage. Sur
soixante questions, le bruit se moyenne — et c'est comme ça que je l'utilise.

Et vous, vous la connaissez, la précision de votre évaluateur ?

==============================================================

[AJOUT AU SCHÉMA : le corpus sort de l'ombre et devient une boîte à part, avec
son propre cadran. Et DEUX cadrans sur le juge, pas un : l'alignement et la
stabilité.]

⚠ NE PAS RÉINTRODUIRE LE κ COMME SUJET. Il se donne en une phrase, en réponse à
la question posée juste avant — jamais enseigné. Il est faible et mesuré contre
un étalon fragile : en faire un sujet donne à tout l'exposé une couleur d'excuse.

⚠ LE TABLEAU, posé le 2026-10-17. Source : REX_TRAME.md:257 — banc du juge du
2026-09-24, 450 générations, 50 items, 3 passes, T = 0,2, bootstrap 10 000.
`invite nue` et `+ conventions` ne diffèrent QUE par le suffixe d'invite, les
quatre conventions reprises mot pour mot. C'est ce qui autorise à lire la ligne 2
comme un effet de l'invite seule.

⚠ POURQUOI un tableau et plus trois lignes : un chiffre faible tout seul est une
note, le même chiffre entouré de ses voisins de même nature est une information.
Le 0,44 n'est plus un bulletin — c'est la cellule qui PROUVE que l'entraînement
n'a pas acheté le jugement.

⚠ NE PAS ajouter le κ du corpus (0,880) à la colonne accord. Ce n'est pas la même
mesure — UN relecteur contre des étiquettes écrites par un modèle — et le
pré-enregistrement de la seconde relecture a tranché : « il ne peut pas servir de
plafond » (PREENREGISTREMENT_RELECTURE2.md). L'y mettre réintroduirait à l'écran
l'erreur corrigée le 2026-10-13.

⚠ hintCoverage n'est pas ici : il vit sur « Le résultat », avec la comparaison
des deux moteurs. Il y corrobore un CLASSEMENT — ne jamais dire qu'il valide
le juge.

⚠ Les chiffres hors écran, si on demande : κ 0,48 IC [0,29 — 0,66] pour la
variante À CONVENTIONS, celle que raconte le support depuis l'arbitrage du
2026-10-17 ; κ 0,44 [0,27 — 0,60] pour le fine-tuné, celui qui a tourné sur le
banc RAG — ne pas les mélanger. Les intervalles se chevauchent largement :
aucun des deux n'est meilleur que l'autre à cet effectif. Justesse
76,0 % contre 76,0 %, Δ = 0,0 %, IC apparié [-14 %, +14 %], McNemar exact
p = 1,0000 sur 12 paires discordantes, 6 de chaque côté. À n = 50 l'étude ne
détecte pas moins de ~15 points, et cette limite était écrite AVANT les
résultats. Accord par contrôle, DISPONIBLE POUR LE FINE-TUNÉ SEULEMENT — le dire tel quel
si on demande, ne pas le présenter comme celui du juge décrit à l'écran :
validation_entree 100 %,
contexte_pertinent 89 %, absence_invention 83 %, format_impose 33 %,
bruit_maitrise 50 %.

⚠ LA QUATRIÈME LIGNE. `32B-baseline-conventions` : même invite, mêmes
conventions, mêmes 50 items, 3 passes — seule la TAILLE change. Paire
pré-déclarée dans configs/variants.json, « effet de la taille, à conventions
identiques », et la lecture pré-déclarée est appliquée telle quelle.

  justesse stricte (vote majoritaire)   90 %   contre 76 %
  accord κ moyen                        0,80   contre 0,48   IC95 [0,64 ; 0,93]
  stabilité du verdict                  92 %   contre 76 %
  format strict (le « schéma »)          0 %   contre 0 %

  Écart apparié produit par le harnais : Δ justesse = +14,0 points,
  IC95 bootstrap [+2,0 ; +26,0], McNemar p = 0,0654, 11 paires discordantes.

CE QUI EST DIT SUR SCÈNE : **le contrôle de
plafond, pas la comparaison de justesse.** « Le corpus plafonne à 76 % » est une
affirmation UNIVERSELLE ; un seul contre-exemple la détruit, et 90 % sur le même
corpus avec la même invite en est un. **Cela ne demande aucun test** — on ne
teste pas l'existence, on la constate. C'est pourquoi le script ne prononce ni
valeur-p ni « non concluant » : il n'en a pas besoin.

NE PAS DIRE, en revanche : « la taille améliore la justesse », « un modèle plus
gros est meilleur ». Ça, c'est la question générale, elle n'est PAS tranchée, et
ce n'est pas le sujet. Dire les comptes : **38 copies justes sur 50 contre 45**.
Un décompte n'a pas d'intervalle de confiance.

⚠ SI ON POUSSE SUR LA STATISTIQUE — tout donner, jamais un seul test. Les paires
discordantes sont 9 contre 2 en faveur du gros modèle, et le test se comporte
comme ceci :

  McNemar exact (PRÉ-ENREGISTRÉ, §5 l.68)    p = 0,0654   ne rejette pas
  McNemar mid-p                              p = 0,0386   rejette
  McNemar asymptotique, sans correction      p = 0,0348   rejette
  McNemar asymptotique, avec correction      p = 0,0704   ne rejette pas

Deux sur quatre franchissent le seuil. Le pré-enregistrement avait déclaré le
plus conservateur des quatre. **Réponse honnête, et c'est la seule : « le
résultat est posé sur la frontière, et le côté où il tombe dépend du test. C'est
exactement pour ça que je ne fonde rien dessus. »** La littérature déconseille
d'ailleurs le test exact conditionnel, trop conservateur. Ne PAS s'en servir pour
changer de test après coup : ce serait choisir le test après avoir vu le
résultat, et quelqu'un dans la salle le dira.

  ✓ RÉFÉRENCE VÉRIFIÉE le 2026-10-17 (Europe PMC, enregistrement complet) :
  Fagerland M. W., Lydersen S., Laake P., « The McNemar test for binary
  matched-pairs data: mid-p and asymptotic are better than exact conditional »,
  BMC Medical Research Methodology, 2013, vol. 13, article 91.
  DOI 10.1186/1471-2288-13-91 — PMID 23848987.
  FORMULATION SÛRE, parce qu'elle est portée par le TITRE lui-même : « le mid-p
  et l'asymptotique font mieux que l'exact conditionnel ». L'article recommande
  le mid-p et l'exact inconditionnel en toute situation, et l'asymptotique si de
  petites violations du niveau nominal sont acceptables ; le mid-p n'a violé le
  niveau dans aucun des 9 595 scénarios étudiés.
  ⚠ Ne PAS dire « l'article dit que l'exact conditionnel est trop conservateur » :
  le résumé qualifie d'« overly conservative » les méthodes EXACTES en général,
  et ne juge l'exact conditionnel que par comparaison. Dire le titre, pas plus.

⚠ Pour mémoire, et à ne pas plaider : la table de conclusion du
PREENREGISTREMENT (§7) a un TROU. Elle prévoit « p < 0,05 ET intervalle excluant
0 », et « intervalle CONTENANT 0 ». Notre cas — IC [+2 ; +26] excluant zéro mais
p = 0,065 — ne tombe dans aucune ligne. Le « non concluant » employé plus tôt
venait d'une grille écrite le matin même, pas du pré-enregistrement. C'est une
raison de plus de ne rien fonder sur la statistique ici, et de s'en tenir au
contre-exemple, qui lui est inattaquable.

⚠ LE PIÈGE DU κ 0,80, armé le 2026-10-17. La quatrième ligne affiche κ = 0,80.
Deux rapprochements vont venir, et ce sont deux erreurs :
  — « 0,80, c'est le seuil de reproductibilité entre humains de
    PREENREGISTREMENT_RELECTURE2.md » — non : ce seuil porte sur κ(relecteur 1,
    relecteur 2), un accord ENTRE DEUX HUMAINS. Ici κ mesure juge contre étalon.
    Deux quantités différentes qui portent le même nom.
  — « 0,80, c'est presque le 0,880 de la relecture du corpus » — non, et c'est le
    rapprochement le plus dangereux du support : ce 0,880 est l'accord d'UN
    relecteur avec des étiquettes écrites par un MODÈLE, il a déjà été rétrogradé
    pour cette raison. Le comparer au κ du juge ferait dire au support qu'un juge
    automatique atteint le niveau humain, ce qu'aucune mesure du dépôt n'établit.
Réponse courte si on insiste : « les deux s'appellent kappa et ne mesurent pas la
même chose ; l'accord entre deux humains sur cette grille, je ne l'ai pas encore —
la seconde relecture est pré-enregistrée. »

⚠ À RELIRE QUAND TU REFORMULERAS : il y a QUATRE versions, pas trois, et les
conventions achètent « l'essentiel de » la justesse, pas « toute » (76 sur 90).
L'hypothèse de plafond est ABANDONNÉE : le corpus ne plafonne pas à 76 %,
puisqu'un modèle plus gros atteint 90 % sur le même corpus. Mais l'écart n'est pas
déclarable à n = 50. Les deux phrases tiennent ensemble, et c'est tout le propos.

⚠ Si on demande comment faire mieux sur l'étalon : une seconde relecture est
PRÉ-ENREGISTRÉE et le paquet aveugle est prêt (judge-finetune/data/relecture2/),
il manque seulement un relecteur disponible. Le dire comme un fait, pas comme une
excuse.
-->

---

## Et son hésitation, elle, me sert

Les copies où il **change d'avis** entre trois lectures, je les relis.

```
   50 copies
   ├─ 38 stables     →  je n'y touche pas
   └─ 12 instables   →  je relis
```

**12 relectures au lieu de 50** — les trois quarts du travail écartés.

**Mais l'hésitation n'attrape que 4 de ses 12 erreurs.** Les 8 autres, il les
rend trois fois identiques et fausses — **rejouer le même modèle fait varier
l'échantillonnage, jamais la compréhension.**

<!--
[À REFORMULER AVEC TES MOTS]

Bon. Mon juge hésite sur une copie sur quatre. Mais cette hésitation, je peux
m'en servir.

L'idée est simple : les copies où il rend trois fois le même verdict, je lui fais
confiance. Celles où il change d'avis, je les relis moi-même.

Résultat : je relis douze copies au lieu de cinquante. Les trois quarts du
travail, c'est lui qui les a écartés — et il a gardé ce qu'il y avait de plus
ambigu.

Et sur les douze fois où il n'est pas d'accord avec mon étalon, l'hésitation m'en
signale quatre. Un tiers. Les huit autres, il les a rendues trois fois de suite,
identiques, et fausses. Il ne doutait pas. Il se trompait.

Les trois plus coriaces ont la même forme : une phrase fausse entourée de
paragraphes justes. « Arrays.asList renvoie une liste immuable » — faux, et tout
le reste de la copie est impeccable. Mon juge a noté l'entourage.

==============================================================

⚠ LES CHIFFRES SONT CEUX DU JUGE À CONVENTIONS : 12 relectures, 4 désaccords
rattrapés. Ne pas confondre avec le fine-tuné, qui donne 21 et 7 — vrais aussi,
mais d'un autre juge. Si on demande pourquoi moins : voir le curseur, plus bas.

⚠ MESURE A POSTERIORI, pas pré-enregistrée. Le dire si on insiste. Tout est
consigné dans judge-finetune/TRIAGE_POSTHOC.md, méthode et limites comprises.
« Erreur » veut dire « désaccord avec l'étalon », pas faute objective.

⚠ LA QUESTION QUI VIENT : « comment en attraper plus ? » Trois réponses, dans
cet ordre.
  1. Pas en routant sur les contrôles plutôt que sur le verdict : MESURÉ, ça
     fait relire 16 copies au lieu de 12 et rattrape exactement les mêmes 4.
     Perte sèche.
  2. Un contrôle déterministe, sans LLM — hintCoverage existe déjà et ne partage
     aucune erreur systématique avec le juge. Ne PAS dire qu'il valide le juge :
     il corrobore un classement.
  3. Un JURY plutôt qu'un juge : des modèles de familles disjointes, et on route
     sur leur désaccord. C'est le seul levier qui attaque la part systématique.
     Verga et al., « Replacing Judges with Juries », arXiv:2404.18796, Cohere
     2024 : un panel de petits modèles bat un seul gros juge, moins de biais
     intra-modèle, plus de sept fois moins cher. Et c'est cohérent avec ma
     parade contre l'auto-préférence.

⚠ LE PIÈGE DES DEUX 38, vérifié le 2026-10-17. La diapositive 21 annonce
**76 % de justesse**, soit **38 copies justes sur 50**. Celle-ci annonce
**38 stables**. Ce sont **deux 38 différents**, et leur coïncidence est un
hasard arithmétique : les 38 stables se décomposent en 30 justes + **8 FAUSSES**,
les 38 justes en 30 stables + 8 instables. Ne jamais dire ni laisser entendre
que « les stables sont les bonnes » — c'est précisément l'inverse du propos de la
diapositive. Si quelqu'un fait le rapprochement, la réponse est : « les deux font
38 par hasard ; huit copies stables sont fausses, et c'est tout mon problème. »
Recoupement : 50 − 38 justes = 12 erreurs, et le triage compte 12 désaccords
(8 stables + 4 instables). Les deux lectures se referment exactement.

⚠ POURQUOI les 8 échappent : rejouer le même modèle ne fait varier que
l'échantillonnage, pas la compréhension. Une convention mal lue est mal lue
pareil aux trois passes. Ces erreurs sont systématiques — c'est structurel,
aucun rejeu du même modèle ne les exposera.

⚠ LES TROIS ITEMS, LUS LE 2026-10-17 — matière de la phrase dite sur scène, et
réponse à « quelles erreurs rate-t-il, concrètement ? ». Sur les 8 désaccords,
trois sont rendus PASS par les QUATRE configurations essayées (juge, fine-tuné,
32B, jury 24B d'une autre famille). Ils ont été ouverts : l'étalon a raison dans
les trois cas, ce n'est PAS un défaut de corpus. Tracé dans
judge-finetune/JURY_RESULTAT.md.

  b04-002 — « Arrays.asList renvoie une liste immuable ». FAUX. Autour : l'idiome
     toArray(new String[0]) le plus rapide, l'exposition de la représentation
     interne sur un return hosts, le coût de la copie défensive. Trois
     développements exacts.
  b06-008 — « ajouter T00:00:00 force une lecture cohérente ». FAUX, et le
     correctif CRÉE le décalage. Autour : getMonth() indexé à zéro, le
     remplissage manquant. Exacts, mais hors sujet.
  b07-002 — « c'est de la contention, passez en verrou équitable ». FAUX, c'est
     un interblocage. Autour : tryLock, lockInterruptibly, Condition, le
     unlock() dans le finally. Tout exact.

  LE MOTIF, et c'est lui le propos : l'erreur centrale est enrobée de
  développements annexes exacts et bien écrits. Le juge valide une copie
  d'expert sans peser la phrase qui compte plus lourd que celles qui l'entourent.
  C'est le biais de l'épaisseur (diapo 11) dans sa forme adulte : il ne joue pas
  sur la LONGUEUR, il joue sur la DENSITÉ DE VRAI AUTOUR DU FAUX. Le test apparié
  de la 11 fait varier la longueur à défaut égal — il ne peut donc pas couvrir
  ces trois-là, et les 46 % ne parlent pas d'eux.

  ⚠ SI ON TE REPREND SUR Arrays.asList — « c'est une vue de taille fixe, pas une
  liste immuable » : c'est la BONNE réponse, et elle te sert. Dire exactement :
  « Oui, et c'est précisément l'erreur. add et remove lèvent bien, mais set
  passe : Arrays.asList("a","b").set(0,"z") réussit et la liste devient
  [z, b]. Là où List.of lève. La copie a dit immuable, et mon juge a validé. »
  NE PAS improviser cette réponse : la dire comme ça.

  ⚠ Limites, si on insiste : n = 3, post hoc. La lecture tranche « corpus ou
  modèle » — c'est le modèle — mais elle ne mesure pas la fréquence du motif.
  Aucun test ne le couvre aujourd'hui. Piste outillable : un jeu apparié
  erreur bien entourée / erreur nue. C'est une piste, pas un chiffre.

⚠ Le curseur, si on demande : la variante fine-tunée est plus instable, elle
envoie 21 copies à l'humain au lieu de 12, et rattrape 7 désaccords sur 12 au
lieu de 4. Plus on relit, plus on attrape. Ce n'est pas une qualité du triage,
c'est sa couverture.
-->

---

## Le banc : 60 questions sur ma codebase

| niveau | ce qu'il teste |
|---|---|
| **LOCAL** | une méthode précise, dans un seul fichier |
| **STRUCTURAL** | héritage, interfaces, ce qui implémente quoi |
| **CROSS_MODULE** | une chaîne qui traverse plusieurs paquets |

Les **mêmes** 60 questions pour les deux stratégies, dans la **même** exécution.

Mélange du contexte **grainé par la question** → la mesure se rejoue à
l'identique.

<!--
[À REFORMULER AVEC TES MOTS]

Maintenant le banc. Soixante questions sur ma codebase, en trois niveaux.

Et c'est lui qui tourne dans ma CI, à chaque modification. Toujours les mêmes
questions — c'est la seule façon de savoir si ce que je viens de changer améliore
ou dégrade. C'est ça qui ferme le tunnel dont je vous parlais au début.

Local : une méthode précise, dans un seul fichier. Structural : héritage,
interfaces, ce qui implémente quoi. Et inter-modules : une chaîne qui traverse
plusieurs paquets — c'est là qu'on attend le graphe.

Deux choses qui comptent plus qu'elles n'en ont l'air.

Les deux stratégies répondent aux mêmes questions, dans la même exécution. C'est
ce qui autorise une comparaison appariée, et une comparaison appariée est
beaucoup plus puissante à effectif égal.

Et le mélange du contexte est tiré de la question. Sans ça, la mesure ne se
rejoue pas : les exécutions de la veille faisaient
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

Et une mesure **sans aucun LLM** les classe **dans le même ordre**.

<span class="ref">Sur ce corpus, selon ma variante entraînée — 76 % de justesse, comme celle décrite.</span>

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

Une précision : le banc a tourné avec ma variante entraînée, pas celle que je
viens de décrire. Les deux rendent soixante-seize pour cent sur l'étalon. Je
vous ai décrit la plus simple.

==============================================================

⚠ LES QUATRE CHIFFRES VIENNENT D'UNE SEULE LIGNE : `benchmarks/rag-quality.jsonl`,
scénario `hybrid|hybrid`, `difficulty ALL`, invalides EXCLUS.
    lucene  n=58  invalid=2  justes 0,483  ctx insuffisant 0,397  hint 0,697
    neo4j   n=59  invalid=1  justes 0,237  ctx insuffisant 0,661  hint 0,596
Ne jamais recalculer depuis `rag-quality-detail.jsonl` sans exclure les
invalides : `ligneSynthese` divise par `valides`, jamais par `js`, et compter les
60 lignes donne 43/67 au lieu de 40/66.

⚠ UN ITEM NON RÉCONCILIÉ, à dire si on insiste. Recompté à la main sur le détail,
Neo4j tombe pile (39/59 = 0,661) mais Lucene donne 24/58 = 0,414 contre 23/58 =
0,397 à la synthèse. Un item sur 58 : ne change ni le classement ni « quatre fois
sur dix ». Ne pas afficher 41 % tant que l'item n'est pas trouvé.

⚠ « VINGT-CINQ POINTS » DANS LE SCRIPT EST JUSTE, ne pas le « corriger » en 24.
Sur les taux bruts : 0,483 − 0,237 = 24,6 points. Le 24 vient des arrondis
affichés. Idem pour « L'écart de 25 points » de la diapositive suivante.

⚠ « quatre fois sur dix » pour 39,7 % et « deux fois sur trois » pour 66,1 % :
les deux sont justes. Garder le script tel quel.

⚠ p = 0,0066. hintCoverage 0,697 contre 0,596.

⚠ Ne PAS dire que hintCoverage valide le juge : il corrobore un CLASSEMENT et
mesure une autre propriété.

⚠ LA RÉSERVE EST MAINTENANT À L'ÉCRAN, et elle dit quel juge a tourné. Preuve
directe : dans `benchmarks/rag-quality-detail.jsonl`, les **120** lignes du
scénario portent `judgeModel` =
`…Qwen2.5-Coder-14B-Instruct-4bit+adapters/14b-judge-ckpt200`. C'est la variante
ENTRAÎNÉE, pas celle décrite jusqu'ici.

⚠ LE PIÈGE κ, à connaître avant qu'on le tende. Les deux variantes sont
indiscernables EN JUSTESSE (76 % contre 76 %), pas en alignement : la variante à
conventions affichée diapo 21 est à κ 0,48, celle qui a tourné le banc à κ 0,44.
Donc dire « même justesse », jamais « même juge ». Si on demande pourquoi le banc
n'a pas tourné avec la meilleure : parce qu'il a tourné avant, et que rejouer est
impossible — `RetrievalBenchmark.java:447` stocke `generated` tronqué à 3000
caractères là où le juge en recevait 6000 mélangés (cf. notes diapo 13).

⚠ Un écart de 25 points est large, mais c'est une comparaison, pas une vérité
sur GraphRAG.
-->

---

## Moteur, ou traversée de graphe ?

Les chiffres d'avant mettent les deux moteurs sur le **même réglage**.
Mais Neo4j, lui, sait traverser le graphe.

Je l'ai donc rejoué **avec** l'expansion K-hop :
**22,0 % au lieu de 23,7. Il perd 1,7 point — une question sur 59.**

Et **Lucene ne bouge pas d'une décimale** : 48,3 %, sur les trois niveaux.
C'est ce témoin qui valide la comparaison.

**L'écart de 25 points vient du moteur de récupération,
pas du parcours de graphe.**

<!--
[À REFORMULER AVEC TES MOTS]

Mais attention. Mon pipeline Neo4j fait deux choses : il cherche, puis il étend
la recherche en suivant les liens du graphe. Lequel des deux pose problème ?

Les chiffres que je viens de vous montrer comparent les deux moteurs sur le même
réglage, sans expansion des deux côtés. Je les ai donc rejoués une seconde fois,
en rendant à Neo4j son expansion de graphe. Et surtout, j'ai laissé Lucene
strictement identique dans les deux exécutions. Son taux doit donc être le même.

Il l'est. Quarante-huit virgule trois pour cent, à la décimale, et sur chacun des
trois niveaux. Le témoin n'a pas bougé — et c'est ça qui rend l'attribution
possible. S'il avait bougé, je n'aurais rien pu conclure du tout.

Neo4j, lui, passe de vingt-trois virgule sept à vingt-deux pour cent. Il perd un
virgule sept point. Une question sur cinquante-neuf. Du bruit.

Donc l'écart vient du moteur de récupération, pas de la traversée. Et la nuance
compte : je ne dis pas « le graphe est mal implémenté ». Je dis que ce
pipeline-là rapporte moins de matière. Ce n'est pas la même critique, et ce n'est
pas le même correctif.

==============================================================

⚠ LE SENS DE L'ABLATION, facile à inverser. « Le résultat » affiche 23,7 % —
c'est `hybrid|hybrid`, le contrôle d'équité, SANS expansion des deux côtés. Ici
on AJOUTE l'expansion, on ne la retire pas, et Neo4j PERD 1,7 point. Les deux
lignes de REX_TRAME :
  hybrid|hybrid-graph  (avec K-hop)  22,0 %  +26,3 pts  p 0,0041  25 discordantes
  hybrid|hybrid        (sans K-hop)  23,7 %  +24,6 pts  p 0,0066  24 discordantes
Les 22,0 % sont à l'écran : sans eux, la salle ne peut pas calculer le 1,7.

⚠ C'est la diapositive qui rend tout le reste défendable. Le bras témoin
invariant est la seule chose qui autorise à attribuer l'écart.
-->

---

## Ce qui conclut, et ce qui ne conclut pas

Sur les trois niveaux, **un seul écart tient** : les questions inter-modules.
Sur les 8 où ils divergent, **Lucene gagne les 8.**

Sur les deux autres : **5 piles sur 7, et 6 sur 9. Banal.**

**Deux écarts sur trois ne concluent pas** — limite
**annoncée avant** la mesure, pas une surprise.

<!--
[À REFORMULER AVEC TES MOTS]

Et voilà ce qui conclut.

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

## Cinq fois, j'ai pris mon banc à mesurer le vide

Et cinq fois, il a affiché **BUILD SUCCESS**.

La pire : une option **acceptée, puis ignorée** — le serveur a répondu
avec un autre modèle que celui demandé.
Deux heures de calcul. 150 réponses plausibles. Et un rapport annonçant
**une dégradation de 76 %**, intervalle de confiance compris.

**Publiable tel quel. Entièrement faux.**

Aucune erreur, aucun avertissement.
**Ce qui l'a trahi : un détail de style.**

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
script, un mélange non grainé. Ne pas les énumérer à l'écran — cinq bugs
cryptiques enterrent le signal, qui est le NOMBRE.
-->

---

## Ce qui a rattrapé chaque instrument

| ce qui l'a rattrapé | ce qui était faux |
|---|---|
| un test de permutation, puis **un humain** | le corpus |
| une comparaison avec le journal | le relevé de coût — faux **trois fois** |
| le désaccord d'un relecteur | le correctif d'une fuite |
| une sonde avant de lire les chiffres | le banc d'essai — **cinq fois** |

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

Et je vous dois une réponse. Tout à l'heure je vous ai dit de ne pas faire juger
un modèle par sa propre famille, alors que mon juge, lui, est tout seul. Voilà
où ça m'a mené : quand il hésite, je le vois. Quand il se trompe avec aplomb,
non — et c'est huit fois sur douze. Rejouer le même modèle ne fait varier que
l'échantillonnage, jamais la compréhension.

C'est la phrase que je veux que vous reteniez : on construit un juge pour arrêter
d'avancer à l'aveugle. Mais le juge est lui-même un instrument. Et un instrument,
ça se vérifie. Sinon on a simplement déplacé l'aveuglement d'un cran.

==============================================================

⚠ Ralentir. C'est la conclusion.
-->

---

## Trois choses pour vous, une pour moi

**1. Écrivez vos conventions avant tout le reste.**
Vous l'avez vu : quatre paragraphes, 0 % → 76 %.

**2. Décomposez en critères, les contrôles avant le verdict.**
Un modèle génère de gauche à droite. L'ordre des champs change tout.

**3. Exigez une preuve positive avant de dépenser du calcul.**
Un banc qui ne prouve pas ce qu'il mesure ne mesure rien — silencieusement.

**Et moi, ensuite ?** Je vous ai dit de ne pas faire juger un modèle par sa
famille. Je l'ai fait : **2 erreurs sur 8**, et la même complaisance.

**Ce n'est pas la famille** — c'est l'erreur bien entourée.

<!--
[À REFORMULER AVEC TES MOTS]

Trois choses applicables lundi, sans rien installer. Et une que je garde pour moi.

Un. Écrivez vos conventions avant tout le reste. Vous les avez vues tout à
l'heure : quatre paragraphes, et mon juge passait de zéro à soixante-seize pour
cent.

Deux. Décomposez en critères, et mettez les contrôles avant le verdict. Un modèle
génère de gauche à droite — l'ordre des champs change son comportement, et ça ne
coûte rien à corriger.

Trois. Exigez une preuve positive avant de dépenser du calcul. Un banc qui ne
sait pas prouver qu'il a mesuré la bonne chose ne mesure rien, et il le fait
silencieusement.

Et moi, ensuite ? Je vous ai dit de ne pas faire juger un modèle par sa propre
famille, et mon juge est tout seul.

Alors je l'ai fait. Un juge d'une autre famille, sur mes huit erreurs
systématiques. Il en attrape deux. Et sur six d'entre elles, il se trompe comme
le mien : trop indulgent. Deux familles sans ancêtre commun, la même
complaisance, sur les mêmes copies.

Donc ce n'est pas la famille. Les trois copies que rien ne corrige ont toutes la
même forme : une phrase fausse, entourée de paragraphes justes.

Voilà ce que je vais apprendre à mesurer. Pas un modèle de plus — un test de
plus.

Tout est dans le dépôt : le corpus, le protocole avec ses amendements datés, et
les générations écartées avec la raison de leur mise à l'écart.

==============================================================

⚠ Les trois sont applicables sans budget et sans installation. C'est ce qui en
fait des actions et pas des conseils.

⚠ Le quatrième bloc n'est pas une action pour la salle, et ce n'est pas un PLAN
mais un RÉSULTAT : deux leviers écartés par la mesure (jury, entraînement), un
troisième non déclarable (taille), une seule piste retenue. Ne jamais le dire
comme « il reste du travail » : le sujet de la phrase est celui qui a mesuré,
pas celui qui a raté.

⚠ LE JURY A TOURNÉ, et il est la raison de cette réécriture.
`Mistral-Small-3.2-24B-Instruct-2506-4bit`, banc terminé le 2026-10-17 à 15 h 44,
lecture appliquée telle qu'écrite dans PREENREGISTREMENT_JURY.md AVANT toute
génération. **2 sur 8**, bande ≤ 3/8 — conclusion déclarée d'avance : « le jury
ne fait pas mieux qu'un entraînement de plus » (l'entraînement en corrigeait 3).
Appliquée sans renégociation. Détail complet dans judge-finetune/JURY_RESULTAT.md.
  Le « six » dit sur scène : 7 des 8 items sont étalon FAIL / juge PASS — le juge
  n'erre pas au hasard, il est TROP INDULGENT — et Mistral partage cette
  indulgence sur 6 d'entre eux. C'est le chiffre le plus fort du bloc.
  ⚠ Ne PAS dire « une famille juge mieux qu'une autre » : cette variante confond
  famille et taille (24B contre 14B), c'est écrit dans le pré-enregistrement.
  ⚠ Si on demande ce que le jury gagne quand même : l'union triage ∪ jury couvre
  6 des 12 désaccords pour 18 relectures, contre 4 pour 12 au triage seul.
  Descriptif, et ce n'était pas la question posée.

⚠ « L'ERREUR BIEN ENTOURÉE » est un terme maison. Le mot est choisi pour être
défini par la phrase qui le suit sur scène — « une phrase fausse, entourée de
paragraphes justes » — donc raconter d'abord, nommer ensuite. Ne PAS le
présenter comme un concept établi.
  OÙ ÇA SE SITUE DANS LA LITTÉRATURE, vérifié le 2026-10-17. Le phénomène
  appartient à une famille déjà nommée et mesurée :
    · « style over substance » — un juge préfère une réponse bien écrite et
      fausse à une réponse moins soignée et juste. Feuer et al. 2024 (SOS-Bench),
      Doddapaneni et al. 2024.
    · « authority bias » — un juge récompense les références et les tournures
      formelles.
    · le plus proche : un juge favorise les DÉTAILS CONCRETS (chiffres, termes
      techniques, identifiants) SANS vérifier qu'ils sont corrects. C'est
      exactement ce que les trois items exploitent : toArray(new String[0]),
      lockInterruptibly, getMonth() indexé à zéro — tout exact, et c'est ça qui
      fait passer le faux.
  CE QUI RESTE PROPRE À CE TRAVAIL, et c'est la position à tenir : aucune de ces
  études ne fait varier la JUSTESSE DE L'ENTOURAGE. Elles font varier le style,
  le ton, la longueur. Donc : « je n'invente pas un phénomène, j'ajoute un
  mécanisme à une famille connue. » Ne jamais revendiquer la découverte du biais
  lui-même — quelqu'un dans la salle connaît SOS-Bench. Ce qu'il désigne est mesuré et lu :
les trois items que les QUATRE configurations ratent portent une affirmation
centrale fausse entourée de développements annexes exacts. Lus le 2026-10-17,
l'étalon a raison dans les trois cas — ce n'est pas un défaut de corpus. Détail,
contre-exemples et limites dans judge-finetune/JURY_RESULTAT.md, et matière
parlée dans les notes de la diapositive 22.
  La distinction qui tient le terme : le biais de la diapositive 11 joue sur la
  LONGUEUR, celui-ci sur la DENSITÉ DE VRAI AUTOUR DU FAUX. Le test apparié
  actuel fait varier la longueur à défaut égal, il ne peut donc pas couvrir ces
  trois-là. Piste outillable annoncée sur scène : un jeu apparié erreur bien
  entourée / erreur nue. ⚠ C'est une piste, pas un chiffre. n = 3, post hoc,
  fréquence non mesurée.

⚠ « VOS MODÈLES SONT TROP PETITS POUR LA TÂCHE » — l'objection la plus forte du
talk, et ce sont tes propres chiffres qui l'alimentent : dans la table post hoc,
la taille corrige 5 items sur 8, l'entraînement 3, le jury 2. La taille est le
levier dominant. Cinq réponses, dans cet ordre.
  1. C'EST LA QUESTION, PAS UNE LIMITE. OllamAssist tourne dans IntelliJ, en
     local. Un juge qui exige un 70B ne peut pas juger un assistant local : il a
     perdu la prémisse. Qwen2.5-Coder-14B en 4 bits, c'est ce qui tient à côté de
     l'IDE sur 36 Go.
  2. TU L'AS VÉRIFIÉ — c'est l'argument qui ferme la question. Le 32B a tourné :
     90 %, Δ +14 points, IC95 [+2 ; +26], McNemar p = 0,0654. NON CONCLUANT à
     n = 50. « J'ai regardé, et à mon échantillon je ne peux pas le déclarer »
     vaut mieux que ne pas avoir regardé. Détail : notes de la diapositive 21.
  3. LA TAILLE N'ACHÈTE PAS LE SCHÉMA. Dernière colonne : zéro. Le 32B sans
     conventions ne respecte pas le format. La thèse n'est pas touchée.
  4. DANS TES CHIFFRES, LES CONVENTIONS PÈSENT PLUS QUE LA TAILLE : 0 % → 76 %
     pour quatre paragraphes, +14 points pour un modèle deux fois plus gros.
     C'est la réponse en une phrase si le temps manque.
  5. ET ÇA NE SAUVE PAS LE JURY : le juge de l'autre famille était un **24B,
     plus gros que le 14B**, et il n'attrape que 2 sur 8. « Trop petit »
     n'explique pas ce résultat-là.
  CE QUI SE CONCÈDE, franchement et sans détour : 76 % ne suffit pas pour un
  contrôle automatique sans relecture, et une part de cet écart EST de la
  capacité. Le concéder est ce qui rend les quatre points précédents crédibles.
  ⚠ La dernière ligne dite sur scène — « pas un modèle de plus, un test de
  plus » — pose cette réponse AVANT la question. Ne pas la couper.

⚠ LA LIGNE « PAS UN PLUS GROS MODÈLE » NE REVIENT PAS, et c'est la règle
pré-déclarée qui le dit : elle ne devait revenir que sur un résultat détectable,
or 90 % contre 76 % donne Δ +14 points, IC95 [+2 ; +26], McNemar p = 0,0654 —
NON CONCLUANT à n = 50. Détail dans les notes de la diapositive 21.
Et ne jamais gager cette ligne sur 76,0 contre 76,0 : ce sont deux variantes de
MÊME taille (`14B-baseline-conventions` contre `14B-finetuned`). Le 32B n'a
jamais été entraîné (REX_TRAME.md:431, lignes 32B-* gelées sans données).
⚠ Ce qui change quand même, et qui n'est pas sur cette diapositive : l'hypothèse
« c'est le corpus qui plafonne » est abandonnée. Un modèle plus gros atteint 90 %
sur le MÊME corpus. L'écart n'est pas déclarable, le plafond n'est plus défendable.
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

Ce talk raconte **cinq mesures prises en flagrant délit** — parce que quelqu'un
a fini par les regarder.

Alors regardez celle-ci.

Ce qui n'était pas clair, ce qui vous a semblé faux, ce que vous auriez fait
autrement : **c'est ce qui me sert.**

</div>
<img src="img/qr-feedback.png" width="300" height="300" alt="QR code de retour">
</div>

<!--
[À REFORMULER AVEC TES MOTS]

Une dernière chose, et c'est une demande.

Ce talk raconte cinq mesures prises en flagrant délit, parce que quelqu'un a
fini par les regarder. Alors regardez celle-ci.

Ce qui n'était pas clair, ce qui vous a paru faux, ce que vous auriez fait
autrement — c'est exactement ce qui me sert. Le QR code est là, il y restera
pendant les questions.

Merci.

==============================================================

⚠ À FAIRE AVANT : générer le QR vers ton formulaire et écraser
demo/img/qr-feedback.png — même nom, 620 x 620, puis relancer le rendu.

⚠ C'est bien la DERNIÈRE diapositive : la laisser affichée pendant les
questions, c'est le moment où les gens dégainent leur téléphone. Les questions
qui peuvent tomber sont en pistes de réponse plus bas, hors écran.

⚠ L'angle « vous avez vu un talk sur la vérification, vérifiez-moi » est
cohérent avec le propos. Éviter le « n'hésitez pas à me faire un retour » neutre.

==============================================================
LES QUESTIONS QUI PEUVENT TOMBER — pistes de réponse, pas de script.
Toutes les valeurs sont vérifiées ; les sources sont nommées.

❓ COMMENT L'EMPÊCHER DE SE TROMPER TROIS FOIS DE SUITE, AVEC APLOMB ?
   1. D'abord soupçonner l'étalon, pas le juge. REX_TRAME l.205 : 16 désaccords
      sur 22 vont dans le MÊME sens, l'humain plus sévère que l'étiquette écrite
      par le LLM. Une partie des 8 sont peut-être des erreurs d'étiquette.
   2. Corriger les RAISONS, pas le volume : 17 items sur 50 portent un désaccord
      sur au moins un contrôle, dont 15 que le verdict masque. Ajouter 200
      exemples de plus reproduit l'ambiguïté au lieu de la lever.
   3. Puis un JURY : des familles disjointes, on relit là où elles divergent.
      Seul levier contre l'angle mort partagé. Verga et al., arXiv:2404.18796.
   4. Un plus gros modèle : mesuré le 2026-10-17, 90 % contre 76 %, mais
      Δ +14 points NON CONCLUANT à n = 50 (McNemar p = 0,0654). Et 0 % de
      format strict : il n'achète pas le schéma. ⚠ Ne plus dire « PAS un plus
      gros modèle — 76,0 % contre 76,0 % » : ce chiffre-là mesurait
      l'entraînement, pas la taille.
   ⚠ Levier mesuré et NÉGATIF, à sortir si on le propose : router sur « un
     contrôle a bougé » au lieu du verdict fait relire 16 copies au lieu de 12
     et rattrape exactement les mêmes 4. Détail dans TRIAGE_POSTHOC.md.

❓ κ = 0,44, C'EST FAIBLE. COMMENT CONCLUEZ-VOUS QUOI QUE CE SOIT ?
   Je ne conclus pas sur une réponse isolée. Je compare deux moteurs sur les
   mêmes 60 questions, dans la même exécution : le bruit tombe des deux côtés.
   Témoin invariant : Lucene identique à la décimale sur les trois strates.
   hintCoverage, SANS aucun LLM, les classe pareil (0,697 contre 0,596).
   McNemar p = 0,0066 sur 24 paires discordantes, 19-5.
   La réserve à énoncer : sur ce corpus, selon ce juge.

❓ VOTRE ÉTALON EST ÉCRIT PAR UN MODÈLE ET RELU PAR UNE SEULE PERSONNE.
   Oui. C'est la limite la plus sérieuse du travail — la reconnaître, ne pas la
   défendre. C'est écrit en en-tête de data/REVUE_GOLDEN.md.
   Ce que je n'en tire PAS : un plafond humain. 47/50 et κ 0,880, c'est un
   contrôle de cohérence de MA règle, pas un accord entre deux humains.
   Et le biais est documenté ET orienté : 16/22 désaccords dans le même sens,
   ma référence est plus indulgente qu'un humain. Je le dis avant qu'on le
   trouve.

❓ POURQUOI PAS UN PLUS GROS MODÈLE, OU PLUS DE FINE-TUNING ?
   ⚠ RÉPONSE REFAITE LE 2026-10-17 : l'ancienne répondait « 76,0 % contre
   76,0 %, p = 1,0000 », qui est la mesure du FINE-TUNING, et l'appliquait à la
   TAILLE — deux questions, une seule mesure. Elle concluait « le plafond n'est
   pas la taille du modèle » : le banc 32B dit le contraire.
   Le fine-tuning : 76,0 % contre 76,0 %, p = 1,0000. Il a acheté le CONTRAT DE
   SORTIE — 100 % de format strict — pas la justesse. Et il a DÉGRADÉ la
   stabilité : 76 % à 58 %.
   Un plus gros modèle : MESURÉ, et c'est le seul levier qui ait bougé les trois
   premières colonnes. 90 % contre 76 %, κ 0,80 contre 0,48, stabilité 92 %
   contre 76 %. Δ = +14 points, IC95 [+2 ; +26], McNemar p = 0,0654 —
   NON CONCLUANT à n = 50, et c'est le mot pré-déclaré. Il n'achète toujours
   pas le schéma : 0 % de format strict.
   Ce qui reste vrai sans réserve : AUCUN des deux leviers que j'ai payés
   n'a amélioré l'accord. Et le corpus, lui, n'a pas bougé d'un item.

❓ DONC LUCENE BAT GRAPHRAG ? EN GÉNÉRAL ?
   Non. Sur ma codebase, 162 fichiers Java, avec CE pipeline Neo4j.
   Et ce n'est pas la traversée de graphe : l'expansion K-hop ne pèse que
   1,7 point. C'est le moteur de récupération lui-même.
   Le mécanisme est lisible : contexte jugé insuffisant 66 % contre 40 % — un
   défaut de rappel, pas un problème de bruit.
   Un seul niveau conclut : CROSS_MODULE, 8-0, p = 0,0078. Les deux autres non,
   et c'était annoncé avant la mesure.

❓ LE BLOC DE RAISONNEMENT, IL SERT VRAIMENT À QUELQUE CHOSE ?
   Mesuré chez moi, fidelite/RESULTAT.md, pré-enregistré.
   Le verdict bascule 53 % du temps si on lui impose un raisonnement étranger,
   IC [38 %, 68 %] — NON CONCLUANT selon mes propres bandes déclarées.
   Mais 23 bascules sur 24 suivent le raisonnement imposé : c'est une cause
   réelle, pas une cause unique.
   Et thinking vide : 74 % contre 72 %, p = 1,0000, alors qu'il coûte 73 % des
   jetons. Donc : auditabilité démontrée, gain en justesse NON démontré.
   Ne pas prétendre l'inverse — c'est exactement le genre de glissement que le
   talk dénonce.
-->
