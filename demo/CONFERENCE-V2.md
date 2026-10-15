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

⚠ « La même question admet dix bonnes réponses » a été retiré d'ici : c'est un
argument tourné vers l'avant, pas une explication de ce qui s'est passé. VÉRIFIÉ
le 2026-10-13 : l'idée n'est désormais écrite NULLE PART ailleurs dans le
support. Elle reste portée implicitement par le deuxième point (« une réponse
juste formulée autrement est pénalisée »). À remettre explicitement sur la diapo
« Comment mesurer… » si la question « pourquoi ne pas juste comparer à la réponse
attendue ? » revient.
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

⚠ TRANCHÉ le 2026-10-14 : OllamAssist PEUT faire une recherche internet, mais
c'est OPTIONNEL et désactivé par défaut. Formulation exacte à employer partout :
« peut tourner entièrement hors-ligne », jamais « tourne entièrement hors-ligne
et ne sort jamais ». Retiré du script parlé parce que, dit vingt secondes après
« il tourne entièrement en local », ça se lisait comme une contradiction.

⚠ Le tunnel et la peur d'avancer à l'aveugle appartiennent à la diapo suivante
(« Comment mesurer… »), qui est construite dessus. Ne pas les dire ici.
-->
---

## Comment mesurer la qualité des réponses de mon assistant ?

- Deux stratégies de RAG, Lucene et Neo4j —
  **aucun moyen de les départager**

- Le seul juge disponible, c'était **moi**,
  sur des exemples **choisis par moi**

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

**Chez moi : 46 % de faux PASS sur les défauts bavards.**

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
question, sinon la mesure n'est plus rejouable, et j'en ai fait les frais.

Et je veux être honnête : ça atténue, ça ne supprime pas. Douze verdicts sur
soixante basculent au seul réordonnancement, à récupération strictement
identique.

==============================================================

[AJOUT AU SCHÉMA : c'est ici que la RÉCUPÉRATION apparaît sur le schéma — elle
est le préalable. Puis une boîte « mélange grainé » entre elle et le juge.]

⚠ Sans graine, les exécutions de la veille faisaient bouger le même bras de
55,9 % à 43,3 %. Une mesure qui ne se rejoue pas n'est pas une mesure.

⚠ Ne pas confondre avec le « A contre B puis B contre A » de la comparaison par
paires : là c'est l'ordre de DEUX RÉPONSES, ici c'est l'ordre des EXTRAITS.
-->

---

## Un correcteur indulgent a l'air fiable

Il valide presque tout, donc il se trompe rarement —
seulement sur les copies qu'il aurait dû recaler.

```
   27 mauvaises copies   →  il en recale 16.  Il en laisse passer 11.
   23 bonnes copies      →  il en valide 22.
```

**76 % de décisions justes. Et 4 défauts sur 10 qui passent.**

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

Mon juge, sur vingt-sept mauvaises réponses, en recale seize. Il en laisse passer
onze. Sur vingt-trois bonnes, il en valide vingt-deux.

Ça fait soixante-seize pour cent de décisions justes — et quatre défauts sur dix
qui passent. Le même juge, deux chiffres.

Et pour moi les deux erreurs n'ont pas le même prix : un défaut qui passe, c'est
une explication fausse sur ma codebase livrée à l'utilisateur. Un bon code
recalé, c'est juste une relecture inutile.

==============================================================

[AJOUT AU SCHÉMA : ce n'est pas le juge qui sort deux chiffres, c'est le BANC
qui le mesure — une boîte en aval, avec deux cadrans : les décisions justes, et
les erreurs attrapées.]

⚠ TRANCHÉ le 2026-10-14 : tout le talk parle du juge FINE-TUNÉ, parce que c'est
LUI qui a tourné sur le banc RAG (REX_TRAME l.110, « juge 14B fine-tuné au
checkpoint 200 »). Cette matrice (16 recalés, 11 passés, 22 validés) est donc la
bonne, ainsi que les 46 % / 42 % de verbosité et les 64 % de PASS ci-dessous.
Ne pas réintroduire les chiffres de la variante à conventions (κ 0,48,
stabilité 76 %, 40 % de faux PASS concis) : ils appartiennent à un juge qui n'a
pas produit le résultat.

⚠ Le n, si on demande — et c'est LA question qui viendra sur cette diapositive :
les 46 % portent sur **8 items verbeux à défaut caché**, contre 19 concis
(results/report.md §2). Un pourcentage à deux chiffres sur 8 cas. Le dire avant
qu'on le demande vaut mieux que de le défendre après.

⚠ Un juge qui répondrait PASS à tout sur un corpus où 95 % des réponses sont
bonnes afficherait 95 % d'exactitude et attraperait zéro erreur. C'est l'exemple
à donner si quelqu'un doute.

⚠ Ce biais recoupe les deux autres : 46 % de faux PASS sur les défauts verbeux,
et un juge qui rend PASS 64 % du temps là où l'étalon en compte 46 %. Trois
mesures indépendantes, un même diagnostic.
-->

---

## Le quatrième, je ne l'ai pas mesuré — et je vous le dis

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

⚠ LA DETTE OUVERTE ICI SE PAIE EN CONCLUSION (« un jury, pas un juge »). Dix mots
posés tôt pour que la fin soit un remboursement et pas une idée qui tombe du
ciel. Si la conclusion change, retirer cette phrase.

⚠ RÉSOLU le 2026-10-14 — la question « votre juge est-il de la même famille que
ce qu'il juge ? » a une réponse nette : NON, pas dans les résultats publiés.
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

⚠ RÉDUITE le 2026-10-15 à ses trois questions : les trois entrées du juge
étaient déjà montrées ET dites à la diapositive 7, neuf diapositives plus tôt.
Ne pas les réintroduire ici.

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

## L'étalon, et le biais que j'y ai mis moi-même

Il faut des réponses **dont je connais déjà le verdict**.
200 exemples, 50 **relus en aveugle** : 47 verdicts identiques sur 50.
**Un relecteur contre mes étiquettes** — pas deux humains entre eux.

**17 requêtes portaient la même incise** —
*« si tu as le temps, dis un mot de X »*. **Les 17 étaient PASS.**

Il n'apprend pas à juger. Il apprend à **repérer ma signature.**

Correctif : ajouter l'incise à des réponses en échec.
Je l'ai mise **en paragraphe isolé**. Nouvelle règle apprise :
*paragraphe isolé ⇒ échec*. **30 sur 30.**

<!--
[À REFORMULER AVEC TES MOTS]

Pour vérifier un juge, il me faut des réponses dont je connais déjà le verdict.
Donc un étalon : deux cents exemples, cinquante relus en aveugle, quarante-sept
verdicts identiques sur cinquante.

Et je vous préviens tout de suite : à partir d'ici il y a DEUX jeux, et je ne
veux pas que vous les confondiez. Cinquante copies déjà corrigées, qui servent à
vérifier le juge. Et soixante questions sur ma codebase, qui serviront à comparer
les deux moteurs. Deux jeux, deux rôles.

Sa limite, je vous la dois tout de suite : UN relecteur, contre des étiquettes
écrites par un modèle. C'est la faiblesse la plus sérieuse de tout ce que je vous
montre.

Et c'est là que je me suis fait avoir.

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

```
  d'accord avec une référence ?          κ = 0,44
  d'accord avec lui-même ?               même verdict 3 fois sur 5
  une mesure SANS LLM dit-elle pareil ?  oui, même classement
```

**κ, c'est l'accord une fois retiré ce que le hasard donne.** 0,44, c'est moyen —
et c'est mesuré contre l'étalon dont je viens de vous dire la limite.

**Je ne lui fais pas confiance sur une copie.
Je lui fais confiance sur soixante.**

<span class="ref">Ce juge est entraîné sur mon corpus : ça lui donne le format, pas la justesse.</span>

**Assez net pour départager deux moteurs de 25 points** — et une mesure
qui ne contient aucun LLM les classe pareil.

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

Alors est-ce qu'il marche ? Trois réponses.

Une précision d'abord, parce qu'elle compte pour la suite : ce juge-là, je l'ai
aussi entraîné sur mon corpus. Ça lui a donné le format — du JSON exploitable à
tous les coups — pas la justesse. Et c'est lui qui a tourné sur le banc que je
vais vous montrer.

Est-il d'accord avec une référence ? Kappa zéro virgule quarante-quatre —
l'accord une fois retiré ce que le hasard donne tout seul. C'est moyen.

Est-il d'accord avec lui-même ? Je lui donne la même copie trois fois. Il ne rend
le même verdict que trois fois sur cinq.

Ce qui veut dire une chose très concrète : je ne lui fais pas confiance sur une
copie. Si je lui en soumets une seule et qu'il répond PASS, je ne sais pas si
c'est son jugement ou son tirage. Mais sur soixante questions, le bruit se
moyenne — et c'est comme ça que je l'utilise.

Mais la troisième compte plus que les deux autres. J'ai vérifié mon juge avec une
mesure qui ne contient aucun LLM — compter les identifiants attendus dans le
contexte. Elle classe les deux moteurs dans le même ordre que lui.

Les deux ne partagent aucun mode de défaillance. C'est ça qui tient l'écart de
vingt-cinq points.

Et vous, vous la connaissez, la précision de votre évaluateur ?

==============================================================

[AJOUT AU SCHÉMA : le corpus sort de l'ombre et devient une boîte à part, avec
son propre cadran. Et DEUX cadrans sur le juge, pas un : l'alignement et la
stabilité.]

⚠ DÉMOTION DU κ, 2026-10-14. La diapositive de pédagogie du κ (« mesurer un
accord, c'est enlever le hasard ») a été SUPPRIMÉE, et celle-ci ne l'enseigne
plus : elle le donne en une phrase, comme réponse à une question posée juste
avant. Motif : le κ portait deux diapositives, il est faible, et il est mesuré
contre un étalon fragile — il donnait à tout l'exposé une couleur d'excuse. Ne
pas le réintroduire comme sujet.

⚠ C'est hintCoverage qui porte la réponse, pas le κ. Pour une salle de devs,
« j'ai vérifié mon juge LLM avec une mesure sans aucun LLM » est plus fort qu'un
coefficient. Mais ne PAS dire qu'il valide le juge : il corrobore un CLASSEMENT.

⚠ Les chiffres, si on demande : κ du juge 0,44 IC [0,27 — 0,60] pour le juge
fine-tuné, CELUI QUI A TOURNÉ SUR LE BANC. La variante à conventions est à 0,48
[0,29 — 0,66] mais elle n'a pas produit le résultat — ne pas les mélanger. κ du
corpus 0,880 IC [0,720 — 1,000], et c'est UN relecteur contre des étiquettes
écrites par un modèle, jamais deux humains. Stabilité 76 % (conventions) contre
58 % (fine-tuné). hintCoverage 0,697 contre 0,596.

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
   ├─ 29 stables     →  je n'y touche pas
   └─ 21 instables   →  je relis
```

**21 relectures au lieu de 50.** Et ça rattrape **7 de ses 12 erreurs.**

**Les 5 autres, il les a rendues trois fois de suite, identiques et fausses.**
Il n'a pas hésité. **L'hésitation ne les signale pas.**

<!--
[À REFORMULER AVEC TES MOTS]

Bon. Mon juge hésite une fois sur quatre. Mais cette hésitation, je peux m'en
servir.

L'idée est simple : les copies où il rend trois fois le même verdict, je lui fais
confiance. Celles où il change d'avis, je les relis moi-même.

Résultat : je relis vingt et une copies au lieu de cinquante. La moitié du
travail, c'est lui qui l'a trié — et il a trié ce qu'il y avait de plus ambigu.

Et sur les douze fois où il n'est pas d'accord avec mon étalon, l'hésitation m'en
signale sept. Plus de la moitié. Les cinq
autres, il les a rendues trois fois de suite, identiques, et fausses. Il ne
doutait pas. Il se trompait.

Et c'est exactement ce que je vous disais tout à l'heure : un juge qui change
d'avis n'est pas un juge, mais un juge constant et faux non plus.

==============================================================

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

⚠ POURQUOI les 8 échappent : rejouer le même modèle ne fait varier que
l'échantillonnage, pas la compréhension. Une convention mal lue est mal lue
pareil aux trois passes. Ces erreurs sont systématiques — c'est structurel,
aucun rejeu du même modèle ne les exposera.

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

Et une mesure **sans aucun LLM** les classe **dans le même ordre**.

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

⚠ CORRIGÉ le 2026-10-14 après audit : le sens de l'ablation était inversé. La
diapositive « Le résultat » affiche 23,7 % — c'est `hybrid|hybrid`, le contrôle
d'équité, SANS expansion des deux côtés. Donc ici on AJOUTE l'expansion, on ne
la retire pas, et Neo4j PERD 1,7 point. Les deux lignes de REX_TRAME :
  hybrid|hybrid-graph  (avec K-hop)  22,0 %  +26,3 pts  p 0,0041  25 discordantes
  hybrid|hybrid        (sans K-hop)  23,7 %  +24,6 pts  p 0,0066  24 discordantes
Avant correction, la salle ne pouvait pas calculer le 1,7 : les 22,0 % n'étaient
affichés nulle part.

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

La pire : une option **acceptée, puis ignorée** — le serveur a répondu
avec un autre modèle que celui demandé.
Deux heures de calcul. 150 réponses plausibles. Et un rapport annonçant
**une dégradation de 76 %**, intervalle de confiance compris.

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
script, un mélange non grainé. Ne pas les énumérer à l'écran — cinq bugs
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

Et je vous dois une réponse. Tout à l'heure je vous ai dit de ne pas faire juger
un modèle par sa propre famille, alors que mon juge, lui, est tout seul. Voilà
où ça m'a mené : quand il hésite, je le vois. Quand il se trompe avec aplomb,
non — et c'est huit fois sur douze. Rejouer le même modèle ne fait varier que
l'échantillonnage, jamais la compréhension.

Donc ce que je ferais ensuite, ce n'est pas un plus gros modèle. J'ai aussi
essayé d'entraîner le mien sur mon corpus : ça lui a donné le format, pas la
justesse. C'est un jury plutôt qu'un juge — des modèles de familles différentes,
et on relit là où ils se contredisent.

C'est la phrase que je veux que vous reteniez : on construit un juge pour arrêter
d'avancer à l'aveugle. Mais le juge est lui-même un instrument. Et un instrument,
ça se vérifie. Sinon on a simplement déplacé l'aveuglement d'un cran.

==============================================================

⚠ Ralentir. C'est la conclusion.
-->

---

## Trois choses à faire lundi

**1. Écrivez vos conventions avant tout le reste.**
Vous l'avez vu : quatre paragraphes, 0 % → 76 %.

**2. Décomposez en critères, les contrôles avant le verdict.**
Un modèle génère de gauche à droite. L'ordre des champs change tout.

**3. Exigez une preuve positive avant de dépenser du calcul.**
Un banc qui ne prouve pas ce qu'il mesure ne mesure rien — silencieusement.

<span class="ref">Corpus, protocole et mesures : le dépôt est partagé.</span>

<!--
[À REFORMULER AVEC TES MOTS]

Trois choses, applicables lundi, sans rien installer.

Un. Écrivez vos conventions avant tout le reste. Vous les avez vues tout à
l'heure : quatre paragraphes, et mon juge passait de zéro à soixante-seize pour
cent.

Deux. Décomposez en critères, et mettez les contrôles avant le verdict. Un modèle
génère de gauche à droite — l'ordre des champs change son comportement, et ça ne
coûte rien à corriger.

Trois. Exigez une preuve positive avant de dépenser du calcul. Un banc qui ne
sait pas prouver qu'il a mesuré la bonne chose ne mesure rien, et il le fait
silencieusement.

Tout est dans le dépôt : le corpus, le protocole avec ses amendements datés, et
les générations écartées avec la raison de leur mise à l'écart.

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
   4. PAS un plus gros modèle : mesuré, 76,0 % contre 76,0 %, p = 1,0000.
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
   Mesuré : 76,0 % contre 76,0 %, p = 1,0000. Le fine-tuning a acheté le
   CONTRAT DE SORTIE — 100 % de format strict — pas la justesse.
   Et il a DÉGRADÉ la stabilité : 76 % à 58 %.
   Le plafond n'est pas la taille du modèle, c'est ce que le corpus enseigne.

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
