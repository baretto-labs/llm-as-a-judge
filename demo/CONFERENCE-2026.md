---
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
  strong { font-weight: 600; }
  .ref { font-size: 0.85rem; color: #666; }
  section.title { justify-content: center; }
---

<!--
Support de la conférence de novembre 2026.

ÉTAT : introduction seule (4 diapositives). Les parties 1 à 4 restent à écrire.
Le contenu de référence — chiffres, réserves, formulations à ne pas employer —
est dans judge-finetune/REX_TRAME.md, qui fait foi. Ce fichier-ci en est la mise
en scène, pas la source.

ATTENTION : demo/SLIDES.md est un AUTRE deck, celui du talk précédent sur le
benchmark RAG. Il note la qualité sur 10, avec le juge gradué abandonné le
2026-09-13. Ne pas y reprendre de chiffres.

RENDU (marp-cli via docker, voir demo/SUPPORT.md) :
  docker run --rm -v "$(pwd)/demo:/home/marp/app" marpteam/marp-cli \
    CONFERENCE-2026.md --html --output CONFERENCE-2026.html

Les blocs en commentaire HTML sous chaque diapositive sont les notes orateur :
Marp les exporte en notes, elles ne s'affichent pas à l'écran.
-->

<!-- _class: title -->

# RAGots et Hallucinations

## votre chatbot passe devant le juge

Mehdi El Ketroussi
Novembre 2026

<!--
Titre figé par l'abstract retenu (REX_TRAME.md, section « Titre »).

Validé le 2026-09-24 : pas de logo ni de nom de conférence pour l'instant —
à revoir seulement si l'organisateur impose un gabarit.

À dire : lire le titre à voix haute dès la première seconde. « RAGots » est un
jeu de mots qui se perd à l'écrit — la moitié de la salle ne le verra pas.
Et « passe devant le juge » porte les deux sens du talk : le juge automatique
qu'on construit, et le tribunal — ce que la diapositive 3 vient refermer.
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
Validé le 2026-09-24. Citation gardée EN ANGLAIS (choix assumé) : c'est
l'original, donc vérifiable, et « remarkable » dans la bouche d'un juge est sec
d'une façon qu'une traduction perd. La traduire à l'oral en la commentant.

À dire — c'est ici qu'on raconte, la diapositive ne raconte pas :
novembre 2022, Jake Moffatt réserve un vol pour les funérailles de sa
grand-mère. Le chatbot lui indique qu'il peut demander le tarif deuil après le
voyage. La politique réelle exige de le demander avant. Il paie le plein tarif
et se retourne contre la compagnie.

Le récit humain est plus fort dit que lu, et il ne prend pas de place à l'écran.
La diapositive ne tient que la confrontation — la défense, puis la réponse du
tribunal — parce que la phrase du tribunal est la seule chose que la salle doit
pouvoir relire : c'est la punchline, elle n'est pas de nous, elle est opposable.

État de vérification (2026-09-24) : la phrase est celle de la décision. Membre
Christopher C. Rivers, 14 février 2024, 650,88 $ CA de dommages — l'écart entre
le tarif deuil et ce qui a été payé.
NON vérifiés sur pièce, donc volontairement absents de l'écran : le délai exact
annoncé par le chatbot (90 jours selon plusieurs sources secondaires) et le
total incluant intérêts et frais de tribunal, légèrement supérieur. CanLII
renvoie un 403 et les PDF ne s'extraient pas. Pour les ajouter, lire la décision
directement : canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html
-->

---

## Et ce n'est pas un cas isolé

**DOCUMENTÉ** — décision de justice ou document public

- **Mata v. Avianca, 2023** — un avocat dépose **six décisions de justice
  inventées** par ChatGPT, citations d'apparence normale. Le juge constate
  « conscious avoidance ». 5 000 $ de sanction.
  <span class="ref">S.D.N.Y., 22-cv-1461 (PKC), juge P. Kevin Castel, 22 juin 2023</span>

- **Deloitte Australie, 2025** — rapport à 440 000 AUD remis au *Department of
  Employment and Workplace Relations*. Références fabriquées, dont une citation
  attribuée à un juge fédéral. ~97 000 AUD remboursés. La version corrigée
  mentionne l'usage d'Azure OpenAI.

**RAPPORTÉ PAR LA PRESSE** — non vérifié sur source primaire

- **NYC MyCity, 2024** — le chatbot municipal conseille des pratiques contraires
  au droit du travail.

- **Chevrolet de Watsonville, 2023** — chatbot détourné par injection de prompt,
  accepte de vendre un véhicule pour **1 $**.

<!--
Validé le 2026-09-24. DIAPOSITIVE À SURVOLER, deux secondes minimum à l'écran —
en dessous, la salle ne perçoit pas qu'elle est dense et l'effet de volume tombe.

Densité assumée : celle-ci est faite pour être LUE APRÈS COUP, dans le deck
partagé. C'est la seule du talk où la densité est un choix et non un défaut,
donc elle doit être auto-suffisante — références complètes, compréhensible sans
nous avoir entendu.

Phrase de survol : « J'aurais pu en remplir beaucoup plus — mais je ne garde que
ceux que je peux prouver. » Le survol doit être ASSUMÉ, pas subi : « je ne
m'arrête pas, vous les retrouverez » et non « je n'ai pas le temps ». Le premier
est un choix, le second dit à la salle qu'elle rate quelque chose.

La séparation documenté / rapporté est le vrai moment de l'introduction : un
talk sur la mesure rigoureuse qui range ses propres anecdotes par niveau de
preuve fait la démonstration avant l'argument.

État de vérification (2026-09-24) :
- Mata v. Avianca : VÉRIFIÉ sur le texte de l'opinion. Caption, docket, juge,
  date, sanction de 5 000 $ solidairement contre LoDuca, Schwartz et le cabinet
  Levidow, Levidow & Oberman. Mauvaise foi constatée en ces termes : « acts of
  conscious avoidance and false and misleading statements to the Court ».
  Le compte est SIX décisions inventées (Varghese, Shaboon, Petersen, Martinez,
  Estate of Durden, Miller) — pas neuf : les trois autres noms qui circulent
  (Zicherman, Ehrlich, In re Air Crash Disaster) sont de VRAIES décisions,
  citées à l'intérieur des fausses. Ne pas se tromper là-dessus en public.
- Deloitte : concordant sur AP, Fortune et CFO Dive. La source primaire — le
  rapport révisé et sa mention d'Azure OpenAI — est sur le site du DEWR et n'a
  pas pu être ouverte le 2026-09-24 (timeout deux fois). À confirmer avant
  l'oral, sinon basculer la ligne dans la section RAPPORTÉ.
- NYC MyCity et Chevrolet : presse et captures d'écran seulement, d'où
  l'étiquette. Le « 1 $ » est gardé parce qu'il est parlant, et il est couvert
  par l'étiquette.
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
Validé le 2026-09-24.

Titre retitré : c'était « Nos tests ne voient pas les erreurs qui comptent », une
thèse à défendre. Placée APRÈS les exemples, la diapositive répond à la question
que la salle se pose déjà au lieu de l'asséner.

BLEU / ROUGE volontairement RETIRÉS et remplacés par la formulation en clair :
les nommer coûte plus qu'il ne rapporte — qui connaît n'apprend rien, qui ne
connaît pas paie vingt secondes d'acronyme qui ne resservira pas dans le talk.

À dire : un avocat ne relit pas une citation bien formatée. « 925 F.3d 1339
(11th Cir. 2019) » a la forme d'une vraie référence, et c'est tout ce que notre
œil vérifie. La conséquence pratique : on livre en se fiant à l'impression qu'on
a en relisant trois sorties à la main.

Le gain du réordonnancement : les six citations inventées SONT la démonstration
de la deuxième puce. Plus besoin d'argumenter que la forme trompe — on vient de
le montrer sur un avocat, un ministère et une compagnie aérienne.
-->

---

## Pourquoi j'ai voulu mesurer

**OllamAssist**, mon assistant de code

- J'avais deux stratégies de RAG — Lucene et un graphe Neo4j —
  et **aucun moyen de les départager**

- Le seul juge disponible, c'était moi,
  sur quelques exemples **choisis par moi**

- Ma crainte : **avancer à l'aveugle.**
  Modifier, livrer, et ne jamais savoir si j'ai amélioré ou dégradé.

<!--
Validé le 2026-09-24. La crainte est la formulation de Mehdi : « comment être sûr
que j'améliore mon assistant et que je ne le dégrade pas ? Je ne veux pas avancer
à l'aveugle dans mes modifications et me créer un tunnel et ne pas avoir de
feedback. » Gardée en question à l'oral, en affirmation à l'écran.

Pourquoi elle porte : c'est une crainte de DÉVELOPPEUR, pas de chercheur —
l'instinct du test de non-régression appliqué à un système non déterministe. La
salle n'a pas besoin qu'on la lui explique, elle la vit.

« choisis par moi » n'est pas un détail : trois rôles en conflit — auteur du
système, sélectionneur des cas de test, et juge.

À dire : le mot exact, c'est TUNNEL. Pas de boucle de retour, donc chaque
modification est un pari, et les paris s'accumulent sans qu'on sache lequel a
coûté quoi.

CALLBACK À PRÉPARER POUR LA CONCLUSION : cette crainte se vérifie à la fin du
talk. 91 minutes de fine-tuning pour une justesse de 76,0 % contre 76,0 % —
exactement « j'ai modifié sans savoir si j'améliorais ». La différence, c'est que
cette fois on l'a su. L'introduction pose la peur, la conclusion montre que
l'outillage l'a attrapée sur notre propre modification. Le talk se referme sur
nous, pas sur une leçon abstraite.

Transition vers la Partie 1 : « Avant d'écrire une ligne de juge, il y a quatre
questions à se poser — et la première, c'est ce qu'il ne faut surtout pas lui
donner à évaluer. »
-->

---

<!--
PARTIE 1 (4 min) — La méthode : les questions à se poser avant de construire
son juge.

Les deux diapositives qui suivent ont été ajoutées le 2026-09-24 : le plan
attaquait « les questions à se poser » sans avoir montré ce qu'était un juge.
On ne peut pas poser de bonnes questions sur un objet qu'on n'a pas présenté.

BUDGET : elles coûtent 60 à 75 s, et le plan tombait à 20 min pile sans marge
(3+4+4+6+3). Dépassement assumé — Mehdi taillera après la présentation à ses
associés. Ne pas l'oublier au moment de la répétition chronométrée.
-->

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
Validé le 2026-09-24.

TROIS entrées, pas une. Si on ne montre que « réponse → juge », on perd ce qui
fait tout le talk : le juge voit aussi LE CONTEXTE RÉCUPÉRÉ, et c'est ce qui lui
permet de dire « cette réponse est peut-être vraie, mais rien dans le contexte ne
l'étaye ». Tout le banc Lucene/Neo4j repose là-dessus.

La sortie est PASS / FAIL, jamais une note sur 10 : le juge gradué a été
abandonné le 2026-09-13. Annoncer une note ici contredirait la Partie 2 dès la
sixième diapositive.

« Il ne génère pas, il juge » est la ligne la plus utile : c'est la confusion
numéro un dans la salle. On croit qu'on demande au modèle de refaire le travail,
alors qu'on lui demande de VÉRIFIER — deux tâches d'une difficulté très
différente. L'analogie du livre porte le même argument, et la conséquence
économique en découle au lieu d'être un point séparé.

À dire : l'idée tient en une phrase, et c'est précisément pour ça qu'elle est
dangereuse — elle a l'air gratuite.
-->

---

## Trois façons de juger

**1. Comparaison par paires**
A contre B, puis B contre A pour neutraliser l'ordre
→ classe deux systèmes. **Ne dit pas si l'un des deux est bon.**

**2. Évaluation unique, avec référence**
On fournit le corrigé attendu
→ fiable, mais il faut **produire un corrigé par question**.

**3. Évaluation unique, sans référence** ← *mon choix*
Le juge applique une **grille de critères**
→ pas de corrigé à écrire. **Tout repose sur la grille.**

<!--
Validé le 2026-09-24.

À dire : sur du code, le corrigé est exactement ce que je n'ai pas — si je savais
écrire la bonne réponse à mes 60 questions, je n'aurais pas besoin de RAG.

Pourquoi ce découpage sert le plan : la troisième approche déplace le problème
sur la grille, et « l'ingénierie des rubriques » est le titre de la Partie 2.
Cette diapositive pose donc la question à laquelle la Partie 2 répond, sans
avoir à l'annoncer.

PRÉCISION À NE PAS CONFONDRE EN PUBLIC : le « A contre B, puis B contre A » de
l'approche 1 neutralise le biais de position ENTRE DEUX RÉPONSES. Ce qui a été
mesuré dans ce projet est un biais de position SUR L'ORDRE DES CONTEXTES
RÉCUPÉRÉS — 12 verdicts sur 60 basculent au seul réordonnancement. Même
phénomène de fond, dispositif différent. Le rapprochement est permis à condition
de dire lequel a été mesuré.
-->

---

## Première question : que ne PAS lui donner à juger

Avant de dépenser un seul jeton :

```
  Est-ce que ça compile ?           →  le compilateur
  Est-ce que le JSON est valide ?   →  un parseur
  Est-ce que le style tient ?       →  le linter
```

Déterministe. Gratuit. Instantané. **Et ça ne se trompe jamais.**

Mon filtre à moi : l'équilibrage des parenthèses et des accolades.
C'est tout. **Ce n'est pas un filtre L0, c'est un début.**

<!--
Validé le 2026-09-24.

Renversement assumé : on attend d'un talk sur les juges qu'il explique ce qu'on
peut leur confier, et on ouvre sur ce qu'il faut leur RETIRER. C'est l'argument
le plus solide de la partie, parce qu'il tient à la fois sur le prix et sur la
fiabilité, sans compromis entre les deux.

À dire : un compilateur répond en cinquante millisecondes, ne coûte rien et n'a
pas d'humeur. Demander ça à un LLM, c'est payer pour une réponse moins fiable.

À dire — l'aveu, et c'est là qu'il devient utile : si mon filtre est aussi mince,
c'est que ce que je fais juger n'est pas du code compilable. Ce sont des
explications en prose qui contiennent du code. « Est-ce que ça compile » ne
s'applique donc pas directement — il faudrait extraire les blocs et les compiler
à part. Je ne l'ai pas fait. C'est une raison, pas une excuse.

Pourquoi l'aveu vaut mieux que le principe seul : un principe énoncé sans coût
vécu s'écoute poliment ; suivi de « et moi je ne l'ai pas appliqué, voilà
pourquoi », il se retient — la salle est dans la même situation. Même registre
que l'aveu sur l'échelle 0-10 (quatrième point de la Partie 1).

ACTION CONCRÈTE à proposer, ce qui manque souvent aux talks de méthode : extraire
les blocs de code de la réponse et les passer au compilateur avant le juge.
Faisable en une après-midi, mesurable, et personne dans la salle ne le fait.

CARTE À REJOUER EN PARTIE 3 : la même idée reparaît sous une autre forme —
hintCoverage, contrôle déterministe SANS LLM, qui classe Lucene et Neo4j dans le
même ordre que le juge. Le filtre déterministe n'est donc pas seulement un
économiseur de jetons en amont, c'est un instrument de validation croisée en
aval. Poser l'idée proprement ici fait gagner la seconde occurrence.
-->

---

## Deuxième question : quand évaluer ?

**OFFLINE** — dans la CI, sur un jeu de questions figé
Rejoue les **mêmes** questions à chaque modification.
→ détecte la régression. **Exige un corpus.**

**ONLINE** — en production, par échantillonnage
Juge un échantillon des vraies conversations.
→ détecte l'imprévu. **Ne compare rien.**

Moi : **100 % offline.** Aucun échantillonnage de production.

<!--
Validé le 2026-09-24.

La vraie opposition n'est pas le moment, c'est LE COÛT — d'où les deux lignes en
« → ». L'offline exige un jeu figé, donc un corpus à construire, et c'est là que
part tout l'effort de ce projet : 200 exemples, un golden set de 50. L'online ne
demande aucun corpus mais ne donne aucune comparabilité — les conversations de
mardi ne sont pas celles de lundi, donc rien ne s'attribue à la modification.

AVEU, même registre que le L0 : ce projet est entièrement offline, il n'y a aucun
échantillonnage de production. Le dire coûte deux secondes et évite qu'on le
demande.

À dire : c'est l'offline qui ferme le tunnel de la diapositive 5. Rejouer les
MÊMES questions est la seule façon de savoir si une modification améliore ou
dégrade — et la seule façon de comparer deux stratégies, puisque Lucene et Neo4j
doivent répondre aux mêmes 60 questions pour être comparables.

Un rappel oral d'une demi-phrase vers la crainte du tunnel suffit à faire le
lien, et c'est ce qui donne au talk sa structure : la peur est posée en
introduction, le mécanisme qui la lève est nommé ici.
-->

---

## Troisième question : quel format de verdict ?

Pas une note sur 10. **PASS / FAIL.**

Chez un juge LLM, les échelles graduées donnent un **faible accord entre juges**
et une **forte variance** des notes.

Décomposer en questions binaires : **+0,45 d'accord moyen** entre 12 modèles
évaluateurs. <span class="ref">CheckEval, EMNLP 2025 — Lee et al.</span>

Biais de position, de verbosité, d'auto-préférence.
<span class="ref">Zheng et al., NeurIPS 2023 — MT-Bench</span>

**Ça, je ne l'ai pas mesuré. Je m'appuie sur la littérature.**

<!--
Validé le 2026-09-24. Resserré de 11 à 8 lignes plutôt que découpé : les
références SONT la justification, les séparer de l'affirmation l'affaiblirait.

RÉFÉRENCES VÉRIFIÉES le 2026-09-24 :
- CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation
  using checklists. Yukyung Lee, JoongHoon Kim, Jaehee Kim, Hyowon Cho,
  Jaewook Kang, Pilsung Kang, Najoung Kim. EMNLP 2025.
  aclanthology.org/2025.emnlp-main.796/
  L'abstract attribue explicitement les incohérences de notation aux « subjective
  evaluation criteria combined with Likert scale scoring », et mesure
  « improves the average agreement across evaluator models by 0.45 and reduces
  the score variance » sur 12 modèles évaluateurs. C'est précisément
  l'affirmation qu'on voulait pouvoir faire.
- Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. Lianmin Zheng et al.
  NeurIPS 2023, Datasets and Benchmarks Track. arxiv.org/abs/2306.05685
  Référence canonique des biais de position, de verbosité et d'auto-préférence.

LA DERNIÈRE LIGNE EST LA PLUS IMPORTANTE DE LA DIAPOSITIVE. C'est la seule du
talk où l'on s'appuie sur la littérature plutôt que sur sa propre mesure, et on
l'affiche. Dans un exposé qui passe vingt minutes à distinguer ce qui est mesuré
de ce qui est cru, cette ligne vaut plus que les deux références au-dessus :
elle prouve que la séparation n'est pas un slogan.

À dire : je n'ai pas fait combattre le gradué contre le binaire chez moi. J'ai
abandonné le gradué, je ne l'ai pas battu en duel — la nuance compte, et
quelqu'un dans la salle la verra.
-->

---

## Le verdict n'est pas une opinion, c'est une conjonction

```json
<thinking>
  1. …   2. …   3. …
</thinking>
{
  "checks": {
    "exactitude_technique": true,
    "absence_de_bugs":      false,
    "respect_consignes":    true
  },
  "verdict": "FAIL",
  "reason":  "Diagnostic exact mais correctif faux : …"
}
```

**PASS ⟺ tous les contrôles vrais.** Un seul `false` ⇒ FAIL.

<!--
Validé le 2026-09-24. Découpée en deux : cette diapositive porte le schéma et la
règle de conjonction, la suivante porte l'ordre des champs, qui se démontre
visuellement.

À dire : pas de demi-mesure, pas de « globalement acceptable ». Le verdict n'est
pas jugé, il est CALCULÉ — donc vérifiable : on peut recalculer chaque verdict
depuis les contrôles et détecter un juge qui se contredit. C'est exactement
comme ça que la cohérence du juge est mesurée (coherenceRate du banc RAG).

LE VRAI GAIN DE LA DÉCOMPOSITION N'EST PAS LA FIABILITÉ. Une note globale dit
QU'une réponse échoue ; les contrôles atomiques disent LEQUEL échoue. C'est ce
qui a permis en Partie 3 de conclure que Neo4j souffre d'un défaut de rappel —
66 % de contextes jugés insuffisants contre 39,7 % — et non d'un problème de
bruit mal maîtrisé. Sans contrôles atomiques : un écart de 25 points sans
explication. À dire ici, ça prépare la Partie 3.

`reason` vient en DERNIER et ce n'est pas un détail : le champ existe pour
l'humain qui relira, pas pour la machine, et venant après le verdict il ne peut
pas l'influencer. Cohérent avec la règle de la diapositive suivante.

CONTRE-CHIFFRE À NE PAS TAIRE, il appartient à la Partie 4 mais c'est ici qu'il
devient compréhensible : la conjonction ABSORBE les désaccords. Sur les 50 items
du golden set, 17 portent un désaccord sur au moins un contrôle, dont 15 que le
verdict masque — dès qu'un contrôle échoue des deux côtés, un désaccord sur un
autre devient invisible. Le verdict est reproductible, les raisons beaucoup
moins, et c'est un plafond sur ce que le fine-tuning peut apprendre.
-->
