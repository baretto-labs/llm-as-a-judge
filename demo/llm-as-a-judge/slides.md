---
theme: default
colorSchema: light
layout: cover
title: RAGots et Hallucinations
info: |
  ## RAGots et Hallucinations : votre chatbot passe devant le juge
  Mehdi Elketroussi · DevFest Paris, 27 novembre 2026
fonts:
  sans: Bricolage Grotesque
  serif: Caveat
  mono: JetBrains Mono
  weights: '400,600,700,800'
themeConfig:
  primary: '#d62839'
drawings:
  persist: false
transition: slide-left
comark: true
duration: 20min
---

<div class="abs-tr mt-14 mr-16">
  <Tampon :angle="10">Copie à corriger</Tampon>
</div>

# RAGots et <span class="rouge">Hallucinations</span>

<p class="sous-titre">votre chatbot <span class="fluo">passe devant le juge</span></p>

<p class="mt-10">
  <a href="https://fr.linkedin.com/in/melketroussi" target="_blank" class="inline-flex items-center gap-2">
    <carbon:logo-linkedin class="text-2xl" /> Mehdi Elketroussi
  </a>
</p>

<div class="abs-bl ml-18 mb-10">
  <span class="etiquette-logo">
    <img src="./img/devfest-paris-logo.svg" class="h-6" alt="GDG Paris">
    DevFest Paris · 27 novembre 2026
  </span>
</div>

<!--
Bonjour à tous, merci d'être à tous là pour assister à ma présentation.

Je m'appelle Mehdi, je suis développeur/tech lead indépendant, j'apprécie travailler sur les sujets de perf, de tests, et comme pas mal de développeur, je m'interesse à un petit sujet depuis quelques années, que je pense aura de l'avenir, vous avez entendu parlé de l'IA ? 


la journée à été longue et riche en talks, c'est pour ça que je vais essayer de rendre le sujet digeste.

LA PROMESSE (trois phrases, à dire telles quelles) :
J'ai un assistant de code. Pour savoir s'il s'améliore, j'ai construit un banc d'essai.
Mon banc m'a dit « aucune différence ». Je ne l'ai pas cru.
Pendant vingt minutes : comment on juge le juge.

On va pouvoir commencer la dernière ligne droite ...
-->

---
transition: fade-out
---
# Imaginez…

<div class="scotch mx-auto w-[92%]">
  <img src="./img/imaginez-attente.jpg" class="h-80 w-full object-cover" alt="Une voyageuse seule attend dans un terminal d'aéroport">
</div>

<p class="ref text-right mt-3">« The Long Lonely Wait », Anne Worner, CC BY-SA 2.0</p>

<!--
Imaginer, vous traversez une épreuve dans la vie, la perte d'un membre de votre famille, vous devez les rejoindre, après quelques minutes d'échanges avec le chatbot, vous prenez connaissance des conditions suite à un deuil, vous pouvez vous charger de tout après votre retour ... 

vous effectuez, le déplacement, faites ce que vous avez à faire, mais après votre retour quand vous voulez clore ce dossier,
le service administratif refuse, pretextant que c'est une erreur d'une chatbat ...



-->

---
transition: fade-out
---
# Un chatbot n'est pas un POC

Air Canada plaide : le chatbot est
**« une entité juridique distincte, responsable de ses propres actes »**.

<div v-click>

Le tribunal :

> « This is a remarkable submission. While a chatbot has an interactive
> component, it is still just a part of Air Canada's website. »

<span class="ref">Moffatt v. Air Canada, 2024 BCCRT 149</span>

</div>

<div v-click class="abs-br mb-20 mr-20">
  <Tampon :angle="-10">650,88 $ CA</Tampon>
</div>

<!--
et bien, certains n'ont pas eu à l'imaginer, c'est ce qu'a subi Jake Moffatt en 2022,

vous avez bien compris leur chatbot avait "halluciné" une réponse

et il ne s'est pas laissé faire et à porté l'affaire au tribunal.

 pour Air Canada le
chatbot est une entité juridique distincte, responsable de ses propres actes, et
l'utilisateur doit vérifier les informations sur le site.

[clic] Et c'est la réponse du tribunal qui est importante, je vous l'affiche (laisse 3 ou 4 secondes pour que le public lise)

Le chatbot fait partie du site, et l'entité responsable du site
est donc légalement responsable des réponses du chat. Ce n'est pas juste un POC,
c'est un engagement.

[clic] Ici, six cent cinquante dollars.

Petite question pour le public : qui a déployé un LLM, ou un RAG, en production ?
Autre question : et qui a mis en place un système d'évaluation des réponses de
son système ?
Et ce n'est pas un cas isolé.

RÉSERVE (conclusion ou questions) : NYC MyCity. L'administration annonçait 95 à 99 %
d'exactitude ; l'audit établit que ce calcul excluait les réponses jugées perfectibles.
Une mesure qui ment. Bureau du Contrôleur de New York, audit IT25PAR20028, 30 décembre 2025.


-->
---
transition: fade-out
---
# Pourquoi personne n'a rien vu ?

<div class="scotch extrait mx-auto mt-14">
  <span class="source">Mémoire déposé devant un tribunal fédéral américain, 2023</span>
  <p class="citation"><em>Varghese v. China Southern Airlines Co.</em>,<br>925 F.3d 1339 (11th Cir. 2019)</p>
  <div v-click="1" class="tampon-faux"><Tampon :angle="-9" taille="1.5rem">Cet arrêt n'existe pas</Tampon></div>
</div>

<p v-click="1" class="text-center mt-6"><span class="ref">Mata v. Avianca, S.D.N.Y., 22-cv-1461, juge P. Kevin Castel, 22 juin 2023</span></p>

<p v-click="2" class="text-center" style="margin-top: 2.5rem"><span class="fluo font-bold">Avec un LLM, le faux a exactement la forme du vrai.</span></p>

<style>
.extrait { position: relative; width: 640px; padding: 1.6rem 2rem; }
.extrait .source {
  font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
  letter-spacing: 0.05em; color: var(--encre-douce);
}
.extrait .citation { font-family: Georgia, serif; font-size: 1.6rem; line-height: 1.4; margin: 0.6rem 0 0; }
.tampon-faux { position: absolute; right: -1.5rem; bottom: 0.2rem; transition: opacity 0.3s ease; }
</style>

<!--
Alors pourquoi personne n'a rien vu ?

Regardez cet extrait. Il vient d'un vrai mémoire, déposé devant un vrai tribunal.
Les parties, le numéro de recueil, la cour, l'année. Il a tout.
Un avocat ne relit pas une citation bien formatée, et c'est tout ce que notre œil vérifie.

[clic] Cet arrêt n'existe pas.
Mata v. Avianca, 2023. L'avocat a demandé à ChatGPT : six décisions de justice inventées,
toutes avec des citations d'apparence normale. Le juge constate « conscious avoidance ».
5 000 $ de sanction.

[clic] Avec un LLM, le faux a exactement la forme du vrai.

Et nos outils ne nous aident pas davantage. Un test unitaire vérifie une valeur
de retour, pas un raisonnement. Et comparer mot à mot la réponse attendue et la
réponse obtenue, ça pénalise une bonne réponse formulée autrement, et ça laisse
passer une mauvaise réponse bien écrite.

Donc on livre en se fiant à l'impression qu'on a en relisant trois sorties à la
main.
-->
---
transition: fade-out
---
# OllamAssist
<div class="carte">
<div class="texte">

**Un assistant de code dans IntelliJ,
entièrement local. Mon labo.**

<p v-click>D’abord un <strong>chatbot</strong> : il répond avec ce qu’il sait.</p>

<p v-click>Puis un <strong>agent</strong> : il lit mon workspace,
et répond sur <strong>mon</strong> code.</p>

<p v-click><strong>Sa réponse ne dépend plus surtout du modèle.
Elle dépend de ce qu’il a trouvé.</strong></p>

</div>
<img src="./img/ollamassist-marketplace.png" width="480" height="316" alt="OllamAssist ouvert dans IntelliJ">
</div>

<!--
Moi, mon terrain de jeu, c'est OllamAssist. 
C'est un assistant de code dans mon IDE, tournant en local, avec de "petits modèles" qu'on deploie sur sa machine ou son serveur, d'ailleurs il y de vrais sujets de securité, de souverainté, 
mais ça sera pour un autre moment.




[clic] Au début, c'est un chatbot integré dans mon ide: je pose une question, il répond avec ce qu'il sait.
[clic] Et petit à petit c'est devenu un agent : il lit mon workspace, et il répond sur mon code, genere des messages de commite, refactor du code, créé des classes ...

[clic] Et là, tout change. Sa réponse ne dépend plus surtout du modèle utilisé. Elle dépend de
ce qu'il a trouvé.


Mais pourquoi, j'ai fais ça ? pour comprendre comment fonctionne les llms et avoir mon labo, je l'ai partagé et j'ai quelques utilisateurs finalement.
-->

---
transition: fade-out
---
# Comment savoir si j'améliore mon assistant ?

 Deux stratégies de RAG, Lucene et Neo4j.
  **Aucun moyen de les départager.**

<v-clicks>

- Trois rôles, une seule personne : **j'écris, je choisis, je juge.** **Un dispositif qui ne peut pas me contredire ne mesure rien.**

- Ma crainte : **avancer à l'aveugle.**

</v-clicks>

<p v-click><span class="fluo font-bold">Il me faut un juge.</span></p>

<!--
Comment mesurer la qualité des réponses de mon assistant ?

Je reçois un pr pour améliore le RAG, deux issues sur les reponses retournées ...
Je voulais travailler dessus et modifier le RAG utilisé

J'avais deux stratégies de récupération possible en tête: la RAG assez classique se basant sur une db vectorielle et calculant une distance sémantique pour rmeonter les documents le plus pertinents
, et une autre utilisant des graphs de connaissances à parcourir pour retrouver les information les intéressantes pour la réponse.

Et aucun moyen de les départager dans mon implementation

[clic] Le seul juge disponible, c'était moi. Sur quelques exemples. Choisis par moi.
Trois rôles en conflit ...

[clic] Ma crainte, c'était d'avancer à l'aveugle. 

Modifier, livrer, et ne jamais savoir
si j'ai amélioré ou dégradé. 

je ne voualis pas rentrer dans ce tunnel : pas de retour, donc
chaque modification est un pari, et les paris s'accumulent.

[clic] En recherchant un peu dans l'état de l'art, je tombe sur une notion intéressante, le llm-as-a-judge.

Note pour moi : c'est la question PRÉTEXTE, on y répond diapo 14.
La vraie question est celle de la couverture : « est-ce que je peux croire mon juge ? ».
C'est elle que la copie corrigée referme à la fin.
-->

---
transition: fade-out
---
# LLM-as-a-Judge

Écrire un livre est difficile. Le juger, beaucoup moins.

<JugeTheorie />

<!--
La théorie, pas encore mon juge.

[base] Un LLM ne rédige pas la réponse. Il corrige la copie.
Il lit la question, le contexte, la réponse. Il rend un verdict et une raison.
Pas une note : un oui ou un non, sur des critères précis.

[clic 1] Le barème : les critères, écrits avant de lire.
[clic 2] Le filtre : ce qu'une règle sait trancher n'arrive pas au LLM.
  Trois niveaux dans la littérature, du moins cher au plus cher :
  L0  des règles : regex, schéma JSON, compilation. Immédiat, gratuit.
      Chez moi, L0 sert aussi à MESURER, pas seulement à filtrer : le hint coverage
      (symboles attendus présents dans le contexte, un contains). Il n'écarte aucune copie,
      il donne un second avis sans LLM. En réserve dans les notes de la diapo 15.
  L1  un LLM juge avec un barème. Rapide, peu cher.
  L2  un jury de LLM, ou une vérification par étapes. Lent, cher.
  Pas pour économiser le juge : il est moins bon que le compilateur à ça.
  Moi : L0 + L1. Le doute part chez un humain (clic 5), pas chez un jury.
  Le jury, je l'ai essayé : c'est la fin de l'histoire (diapo 16).
  En local, un modèle à la fois : trois juges, c'est trois fois le temps.
[clic 3] La sortie : un format imposé, qu'un programme vérifie.
[clic 4] L'étalon : des copies corrigées à la main. Le juge aussi est noté.
[clic 5] Le juge hésite ? La copie part chez un humain. La double correction.
  L'humain ne relit pas tout : seulement les doutes.

Voilà les pièces. Je vais les construire une par une.
-->
---
transition: fade-out
---
# Rapide à coder ... 


```java {7-9}
ChatModel juge = OllamaChatModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("qwen2.5-coder:32b")
    .temperature(0.0)
    .build();

ChatResponse r = juge.chat(
    SystemMessage.from(BAREME),                // les trois contrôles + les conventions
    UserMessage.from(contexte + question));

Judgement j = parse(r.aiMessage().text());     // {checks, verdict, reason}
```

<!--
Voila quelques lignes de code en java pour constituer son propre juge ...
c'est assez rapide finalement ... sauf qu'on sait déjà que les llms ont des biais et des erreurs, sinon je ne serai pas en train de chercher à évaluermon système
-->
---
transition: fade-out
---
# Quelques biais des LLM ...

Ce que je crains de mon juge.

- **Biais de verbosité** : est-ce qu'il se laisse impressionner par une réponse longue ?
- **Biais de position** : est-ce que l'ordre des extraits change son verdict ?
- **Biais d'indulgence** : est-ce qu'il valide trop facilement ?

<p v-click class="mt-8"><span class="fluo font-bold">Pour le savoir, il me faut un corrigé.</span></p>

<!--
Trois questions, pas encore de réponses : je n'ai rien pour mesurer mon juge.

Premier biais, la verbosité (l'épaisseur de la copie). Un correcteur se laisse impressionner
par une copie de quatre pages. Si mon juge valide plus souvent la version bavarde d'un même
défaut, il note la forme et pas le fond.

Deuxième biais, la position (la place dans la pile). Pour un juge, c'est l'ordre des extraits
que ramène mon RAG.

Troisième biais, l'indulgence (leniency). Un correcteur qui valide presque tout a l'air
fiable : il se trompe rarement, seulement sur les copies qu'il aurait dû recaler.

[clic] Pour répondre, il me faut des copies dont je connais déjà la note. → l'étalon.

RÉSERVE (questions uniquement, mesuré après l'étalon et les conventions) :
- Verbosité : 46 % de faux PASS sur défauts bavards contre 40 % sur défauts secs. L'écart
  est petit, c'est le NIVEAU qui est mauvais. Ne pas vendre l'écart, vendre le niveau.
- Position : extraits mélangés avec une graine tirée de la question (mesure rejouable).
  12 verdicts sur 60 basculent au seul réordonnancement, à contenu identique.
  Le dénominateur (60) est le nombre de questions ; à contenu identique c'est 12/39.
  Ne pas confondre avec « A contre B puis B contre A ».
- Indulgence : 10 mauvaises réponses sur 27 passent → raconté diapo 11.
⚠ Ne pas confondre : l'indulgence, c'est laisser passer les mauvaises copies. « Plus gentil avec
  sa propre famille de modèles », c'est l'auto-préférence, un autre biais. Et la position, ici,
  c'est l'ordre des extraits ; pas l'attention qui faiblit au milieu d'une longue invite.
Source : demo/CONFERENCE-V2.md, diapos biais du juge.

L'abstract promet « les biais des systèmes RAG » : la position, c'est l'ordre des extraits
que ramène mon RAG ; et la diapo « Aucune différence » montre un biais de mon banc RAG.
-->

---
transition: fade-out
---
# Qui juge le juge ?

Avant de lui confier mon RAG, je lui fais passer un examen dont j'ai le corrigé.

<div class="deux mt-6">
<div class="lecon">
  <span class="etiquette">l'examen · l'étalon</span>
  <div class="chiffre">50 <small>réponses</small></div>
  <p>dont je connais le bon verdict.</p>
</div>
<div v-click class="lecon">
  <span class="etiquette">sa limite</span>
  <div class="chiffre">15 <small>points</small></div>
  <p>Un écart plus petit, je ne peux pas le voir.</p>
  <span class="annotation">50 copies, c'est peu</span>
</div>
</div>

<p v-click class="mt-8"><span class="fluo font-bold">Avant d'écrire le juge, écris le corrigé.</span></p>

<!--
ACTE 1. Le point de départ de l'histoire.

Je veux noter mon RAG. Il me faut un juge.
Mais comment je sais que mon juge note juste ? Je lui fais passer un examen.
50 réponses dont je connais déjà le bon verdict : 27 fausses, 23 justes.
Si le juge retrouve mes verdicts, je peux lui faire confiance. Ça, c'est l'étalon.
[clic] Sa limite : avec 50 copies, je ne vois que les gros écarts, 15 points ou plus.
Ce n'est pas un choix : c'est le calcul de puissance, fait AVANT les résultats
(judge-finetune/PREENREGISTREMENT.md, § 5). À 50 copies, le hasard seul fait bouger
le score de plusieurs points ; ≥ 15 points se détecte, ≤ 10 points non.
Exemple réel : 14B → 32B, +14 points, p = 0,0654 → non concluant (diapo « Deux raccourcis »).
Si on demande d'où sort 15 : méthode standard (McNemar exact, calcul de puissance), chiffre
estimé pour mon cas. Recalcul exact (2026-10-21), n = 50, α = 0,05, puissance selon le
taux de désaccords en sens inverse (0 / 2 / 5 / 10 %) :
  10 points : 38 / 32 / 24 / 18 %   ·   15 points : 78 / 62 / 48 / 36 %
  20 points : 95 / 83 / 70 / 55 %
→ 15 points, c'est le plancher, pas une garantie : sous 15, presque jamais tranché ;
au-dessus, souvent. La règle usuelle (puissance 80 %) demanderait plutôt ~20 points.
Écart minimal pour 80 % de chances de le voir, selon la taille de l'étalon
(désaccords inverses 2 % / 5 %) :
  50 copies : 19 / 23 points · 100 copies : 11 / 15 points · 200 copies : 7 / 9 points
À l'oral : « Mon étalon ne voit que les gros écarts. Pour voir 10 points, il faudrait
200 copies. » Répond d'avance à « pourquoi pas plus de copies ? ».
On compare bien les juges copie par copie (McNemar ne regarde que les désaccords) ;
sur peu de copies, quelques désaccords tombés au hasard suffisent à fabriquer un écart.
Dire « points », pas « % » : 76 → 90 %, c'est +14 points.
[clic] Avant d'écrire le juge, écris le corrigé.

Si la question vient : κ 0,880 contre des étiquettes écrites par un modèle, relues par
un relecteur. JAMAIS « entre humains ».
Triage (une des quatre preuves) : 12 relectures au lieu de 50.
⚠ Ne pas dire « la littérature dit 50 à 200 questions » : aucune source. Dire : « Mon étalon ne
voit que les gros écarts. »
-->

---
transition: fade-out
---
# Mon juge ne rend pas de verdict

Première invite : rien d'exploitable.

<div class="lecon mt-10 items-center text-center">
  <span class="etiquette">même modèle · quatre conventions dans l'invite</span>
  <div class="chiffre grand"><span class="barre">0 %</span> → 76 %</div>
  <p>de verdicts justes sur l'étalon</p>
</div>

<p v-click class="mt-10 text-center"><span class="fluo font-bold">Le plus gros levier m'a coûté quatre règles.</span></p>


<!--
ACTE 2. Chiffres vérifiés le 2026-10-23 : Qwen2.5-Coder-14B (MLX, 4 bits), 0/50 → 38/50.
« Quatre règles » : 4 conventions numérotées, 173 mots (judge-finetune/configs/conventions.md).
Dire 76 %, pas 77.

Ma première invite : zéro verdict lisible. 150 sorties sur 150 inutilisables.
Il raisonne, il nomme les bons contrôles, et il s'arrête avant le verdict.
J'écris quatre conventions : ce que veut dire PASS, ce qui compte comme étayé…
Même modèle, rien à réentraîner : 76 %.
[clic] Le plus gros levier du projet m'a coûté quatre règles.

Mais 76 %, regarde dans quel sens il se trompe (le biais d'indulgence, diapo 9) :
27 mauvaises copies, il en recale 17, en laisse passer 10. 23 bonnes, il en valide 21.
76 % de décisions justes, et près de 4 défauts sur 10 qui passent.
Ses erreurs penchent du même côté : il laisse passer. Un juge indulgent, c'est
Air Canada : la réponse fausse passe, et personne ne la voit (diapo 3).

Réponse prête : « tes conventions n'ont réparé que le format ? » Pour le 0 %, oui :
150/150 INVALID, rien de tronqué (WIP.md:289). Le levier, c'est « écrire le format attendu ».
Le dire avant qu'on le dise. Le jugement se mesure ensuite : 76 %, et dans quel sens il se trompe.

Si la question vient : p = 0,0000 sur 38 paires discordantes.
Few-shot : à la poubelle, 3 erreurs corrigées pour 8 nouvelles, 415 jetons contre 237.
-->

---
transition: fade-out
---
# Noter sur dix ?

Onze notes possibles. Combien en utilise-t-il ?

<div class="deux mt-6">
<div class="lecon">
  <span class="etiquette">« note de 0 à 10 »</span>
  <div class="chiffre">3 <small>/ 11</small></div>
  <p>valeurs utilisées par le juge.</p>
</div>
<div v-click class="lecon">
  <span class="etiquette">avec des critères</span>
  <div class="chiffre">92,2 <small>%</small></div>
  <p>d'accord entre la note et le oui / non.</p>
  <span class="annotation">demande le booléen</span>
</div>
</div>

<p v-click class="mt-8"><span class="fluo font-bold">L'échelle fine est un interrupteur déguisé en potentiomètre.</span></p>


<!--
ACTE 2 bis. Transition : le format est réparé. Tentation suivante : une échelle plus fine.
Ouverture, à l'oral : « J'aurais pu lui demander une note sur dix. »
Source : benchmarks/PREENREGISTREMENT_NOTE_BC.md, bras B (note seule, sans critères) :
3 valeurs vivantes sur 11 (0, 2, 8), validé pour l'écran. Confirmé par un premier banc
(PREENREGISTREMENT_ECHELLE.md, note demandée en plus des contrôles) : 4 valeurs sur 11. 92,2 % : PREENREGISTREMENT_NOTE_BC.md, bras C.

J'ai demandé une note de 0 à 10. Le juge n'utilise que 3 cases sur 11.
Zéro dans 128 cas sur 180.
[clic] Avec des critères, la note colle au oui / non : κ 0,841, 92,2 % d'accord.
Vous payez une échelle pour obtenir un booléen. Demandez le booléen.
[clic] L'échelle fine est un interrupteur déguisé en potentiomètre.
Le coût n'est pas en jetons : tu paies une échelle à onze crans, tu obtiens un interrupteur.
⚠ Ne pas dire « la note coûte plus cher en jetons » : non mesuré, et mes données ne montrent
pas d'écart (~33 s par jugement, l'ordre de grandeur du juge à verdict ; raisons de même longueur). La phrase
« coûte plus cher et décide pareil » était prévue, puis interdite : sans critères, la note
classe les bras autrement que le verdict.

Réserve : mesuré sur les réponses de la campagne RAG ; le classement des bras change selon l'échelle.
Honnête : la littérature n'est pas unanime, un papier trouve l'échelle 0–5 mieux alignée
sur l'humain. Mon résultat vaut pour mon juge et mon barème.
-->

---
transition: fade-out
---
# Deux raccourcis

Entraîner mon juge, ou en prendre un plus gros ?

<div class="bulletin mt-6">
  <div v-click class="ligne">
    <span class="candidat">J'entraîne <small>QLoRA, 91 min, sur le MacBook</small></span>
    <span class="note">76 → 76 %</span>
    <Tampon couleur="encre" taille="0.9rem" :angle="3">rien gagné</Tampon>
  </div>
  <div v-click class="ligne">
    <span class="candidat">Je prends plus gros <small>Qwen 14B → 32B, quantifié</small></span>
    <span class="note">76 → 90 %</span>
    <Tampon couleur="vert" taille="0.9rem" :angle="-4">retenu</Tampon>
  </div>
</div>

<div v-click class="deux mt-8">
  <p><span class="annotation">le format, pas le jugement</span></p>
  <p class="text-right"><span class="fluo font-bold">L'instrument est prêt.</span></p>
</div>


<!--
ACTE 3 (+ acte 4). Chiffres vérifiés le 2026-10-23 : 14B puis Qwen2.5-Coder-32B (MLX, 4 bits).

[clic] Premier réflexe : j'entraîne. QLoRA, 91 minutes sur mon MacBook.
Le jugement : 76 → 76 %. Rien.
Ce qu'il a gagné : le format strict (schéma checks imbriqué) 0 → 100 %.
Le JSON exploitable était déjà à 100 % avec les conventions. Et il est moins stable : 76 → 58 %.
[clic] Si ce n'est pas la méthode, c'est le juge. 14B → 32B : 76 → 90 %.
Quantifié en 4 bits, il tourne sur le MacBook. Pas besoin de cloud.
Honnête : +14 points sur 50 copies, sous le seuil de 15. Je le retiens, je ne le prouve pas.
[clic] Le fine-tuning achète la structure, pas le jugement.
Fin de la première moitié : l'instrument est prêt. Maintenant, je m'en sers.

Si la question vient : adaptateur 43,8 Mo, 0,078 % des paramètres ; p = 1 sur le jugement.
Le format sans entraîner : décodage contraint, 0 sortie invalide sur 360 (37 sans).
⚠ Les 37 sont surtout un effet de budget (35 reviennent avec 2048 jetons) : ne pas le
vendre comme preuve de format. Et sous schéma, le juge ne raisonne pas.
Raisonner d'abord, contraindre ensuite (Tam et al., « Let Me Speak Freely? », 2024).
κ 0,48 (14B) → 0,801 (32B) ; M3 Pro 36 Go.
Génération passée de llama à qwen3 : on ne fait pas juger la famille qui a généré
(Panickssery et al., NeurIPS 2024 ; décision, pas mesurée chez moi).
-->

---
transition: fade-out
---
# Premier verdict

Alors, est-ce que j'améliore mon assistant ?

<div class="barres mt-8">
  <div v-click class="barre-ligne">
    <span>GraphRAG <small>Neo4j</small></span>
    <div class="piste"><div class="plein rouge" style="--v: 16.7"></div></div>
    <strong>16,7 %</strong>
  </div>
  <div v-click class="barre-ligne">
    <span>Vectoriel <small>Lucene</small></span>
    <div class="piste"><div class="plein" style="--v: 60"></div></div>
    <strong>60,0 %</strong>
  </div>
</div>

<div v-click class="deux mt-10">
  <p><span class="annotation">un écart pareil ? c’est ton code</span></p>
  <p class="text-right"><span class="fluo font-bold">Un juge sert d'abord à trouver tes bugs.</span></p>
</div>


<!--
ACTE 5. Chiffres vérifiés le 2026-10-23 : qwen2.5-coder:32b (Ollama, schéma), sans plafond,
num_ctx 20480. Barres = part de verdicts PASS (10/60, 36/60). À rejuger si la relance a lieu.

La question de départ (diapo 6) : est-ce que j'améliore mon assistant ?
[clic] Le GraphRAG : 16,7 %. Je l'avais fait pour ça.
[clic] Le vectoriel : 60 %.
Dire « plus de trois fois », ou les deux chiffres ; pas « quatre fois » (60 / 16,7 = 3,6).
[clic] Un écart pareil sur son propre code, ce n'est pas la technique. C'est mon code.
Exemple : « What does DocumentIndexingPipeline implement? »
Le vectoriel ramène la déclaration de classe : « implements AutoCloseable ». PASS.
Le graphe ramène la classe, mais pas ce qu'elle implémente. FAIL.
La réponse était dans le code, pas dans le contexte. Ce n'était pas une hallucination : un bug.
(Sources : rag-campaign.jsonl, AutoCloseable absent du contexte graphrag ;
plafond/sans-plafond.jsonl, FAIL graphrag / PASS vectoriel.
Ne PAS prendre ContextRetriever : la question sur son interface passe sur les trois bras.)
Un juge sert d'abord à trouver tes bugs.

Si la question vient : face au vectoriel affiché, −43,3 points (29 contre 3 discordantes ;
calculé a posteriori, non pré-déclaré). Le −61,7 points (p < 0,0001, pré-déclaré) est face
à vectoriel + BM25 : diapo suivante.
-->

---
transition: fade-out
---
# « Aucune différence »

Vectoriel, ou vectoriel + BM25 ? 55 % contre 48 % : non concluant.

<div class="fiches mt-6">
<div v-click class="fiche">
  <span class="etiquette">01 · la panne</span>
  <strong>Copies coupées</strong>
  <p>Mon banc coupait chaque contexte à 6&nbsp;000&nbsp;caractères : 46 sur 60 côté BM25.</p>
  <span class="annotation">copies arrachées</span>
</div>
<div v-click class="fiche">
  <span class="etiquette">02 · contextes entiers</span>
  <strong>60 % → 78,3 %</strong>
  <p>Vectoriel, puis vectoriel + BM25.</p>
  <span class="annotation">+18 points</span>
</div>
</div>

<p v-click class="text-right mt-10"><span class="fluo font-bold">Vérifie ce que ton juge lit.</span></p>


<!--
ACTE 6. Chiffres vérifiés le 2026-10-23 : qwen2.5-coder:32b (Ollama). À rejuger si la relance a lieu.
Source : benchmarks/PREENREGISTREMENT_PLAFOND.md.
Ici, le juge note le CONTEXTE récupéré, pas la réponse de l'agent. Le dire.
Simplifiée le 2026-10-24 : trois temps, le hint coverage passe en réserve.

Vectoriel contre vectoriel + BM25 : 55 % contre 48 %, non concluant.
Le vectoriel est même un peu devant. J'ai failli conclure : BM25 ne sert à rien.
Mon banc m'a dit « aucune différence ». Je ne l'ai pas cru.
[clic] La panne : mon banc coupait chaque contexte à 6000 caractères avant le juge.
BM25 ramène des contextes longs : 46 sur 60 coupés, contre 10 sur 60 en vectoriel.
Le juge lisait des copies arrachées.
[clic] Contextes entiers : en ajoutant BM25 au vectoriel, je passe de 60 à 78 % : 18 points.
L'ordre s'inverse : BM25 passe devant.
[clic] Vérifie ce que ton juge lit. Avant de croire un « aucune différence »,
vérifie que les deux bras lui montrent la même chose.
Et la modification qui gagne, c'est la moins sexy : une recherche par mots-clés
des années 90. Pas le graphe.

Si la question vient : BM25 +18,3 points, p = 0,0010 ; 11 questions où seul BM25 passe, 0 dans l'autre sens.
Côté BM25 seul : 48,3 → 78,3 %, 18 verdicts FAIL → PASS, aucun dans l'autre sens.
(Sur les trois bras : 21 FAIL → PASS sur 57 contextes tronqués, PLAFOND.md:116.)
Et chez moi : avant de reconstruire le RAG, j'ai ajouté BM25.
RÉSERVE, hint coverage (mesure sans LLM) : chaque question de l'étalon liste les symboles
Java attendus ; on compte ceux présents dans le contexte (un contains). Sur le contexte
coupé, aussi aveugle que le juge : 68,6 %. Sur le contexte entier : 87,4 % (76,7 % en
vectoriel). Le juge et la mesure avaient le même angle mort : ils lisaient la même entrée.
Piège voisin : num_ctx non fixé (défaut Ollama) tronque l'invite en silence ; fixé à 20480.
Les sondes (une des quatre preuves) : je l'ai attrapé cinq fois, un banc qui mesure le
vide en affichant BUILD SUCCESS. Depuis : un appel sondé avant d'en lancer cent.
-->

---
transition: fade-out
---
# Un juge se trompe. Que faire ?

<div class="bulletin mt-6">
  <div v-click class="ligne">
    <span class="candidat">Le relancer trois fois <small>erreurs rendues à l'identique</small></span>
    <span class="note">8 / 12</span>
    <Tampon couleur="rouge" taille="0.9rem" :angle="-3">mêmes erreurs</Tampon>
  </div>
  <div v-click class="ligne">
    <span class="candidat">Un jury de trois familles <small>mon juge seul : 45 / 50</small></span>
    <span class="note">47 / 50</span>
    <Tampon couleur="encre" taille="0.9rem" :angle="3">non concluant</Tampon>
  </div>
  <div v-click class="ligne">
    <span class="candidat">Relire là où il hésite <small>verdicts qui changent d'une passe à l'autre</small></span>
    <span class="note">12 / 50</span>
    <Tampon couleur="vert" taille="0.9rem" :angle="-4">à relire</Tampon>
  </div>
</div>

<p v-click class="mt-8"><span class="fluo font-bold">Ne relis que les doutes.</span></p>

<p v-click class="mt-2 text-right"><span class="annotation">et tout ça, mesuré sur… l'étalon ↺</span></p>


<!--
ACTE 8, puis la boucle. Chiffres vérifiés le 2026-10-23. DEUX JUGES sur cette diapo :
lignes 1 et 3 = le 14B à 76 % (TRIAGE_POSTHOC.md, POST HOC) ; ligne 2 = le 32B à 90 % (JURY2).
Le dire à l'oral à chaque changement.

Mon juge se trompe encore. Que faire ?
[clic] Mon premier juge, celui à 76 %. Je le relance trois fois : sur ses 12 erreurs,
8 reviennent trois fois, identiques. Il se trompe pareil.
(Ne pas confondre avec 2/8 : c'est le premier jury, Mistral seul, JURY_RESULTAT.md.)
[clic] Changement de juge : le 32B, à 90 %. Trois familles qui votent (Qwen, Mistral, Gemma) :
47 sur 50, contre 45 seul.
Deux copies sur 50 : non concluant. Mon étalon ne voit pas en dessous de 15 points.
(Pas « un écart-type », pas « 5 % » : deux copies sur 50.)
Un jury t'assure contre un mauvais tirage. Il ne dispense pas de mesurer.
[clic] Retour au juge à 76 %. Ce qui a marché : les trois passes ne corrigent pas, mais elles montrent où il hésite.
12 copies sur 50 changent de verdict. Je ne relis que celles-là : 76 % du travail en moins.
C'est le « doute → humain » de la théorie (diapo 7, clic 5), en vrai.
[clic] Ne relis que les doutes.
Honnête : ça rattrape 4 erreurs sur 12. Les 8 autres sont rendues trois fois, identiques
et fausses. Un juge sûr de lui peut avoir tort : le triage réduit la relecture, il ne la
remplace pas.
[clic] Et tout ça, je ne le sais que grâce à mes 50 copies. Retour à la case départ.
Chaque raccourci m'a ramené à l'étalon. C'est la seule chose du pipeline
que je n'ai pas pu déléguer à un modèle.

⚠ Piège : 76 % de justesse = 38 copies justes, et 38 copies stables. Deux 38 sans rapport :
les 38 stables contiennent 8 copies fausses.
Si la question vient : p = 0,5000 ; discordantes 2 contre 0 ; les 3 erreurs du jury
sont indulgentes (encore le sens de la diapo 9). Mistral seul 35/50 : un juré faible pèse autant que les autres au vote.
⚠ Gemma seul 49/50 : NON PRÉSENTABLE (WIP.md, 2026-10-21). Question non déclarée,
4–0, p = 0,1250, sous le seuil de 15 points. Ne pas dire « mon meilleur juré bat le jury »
sans nouveau pré-enregistrement.
Littérature : PoLL (Verga et al., Cohere, 2024) ; Condorcet ;
Kohli, « Nine Judges, Two Effective Votes », arXiv 2605.29800, mai 2026 (vérifié) :
9 juges, 7 familles ≈ 2 votes indépendants ; le meilleur juge seul égale ou bat le panel.
-->

---
layout: center
class: text-center
transition: fade-out
---

<CopieCorrigee />

<!--
La couverture disait « copie à corriger ». La voici corrigée.
[clic 1] Écris tes 50 copies d'abord. Personne ne le fera pour toi, aucun modèle non plus.
[clic 2] Écris ton barème. Quatre règles, le plus gros levier.
[clic 3] Vérifie ce que ton juge lit. Mon banc coupait 46 contextes BM25 sur 60.
[clic 4] Ne relis que les doutes. 12 copies au lieu de 50.
[clic 5] Entraîner, grossir, voter : chaque raccourci m'a ramené à l'étalon.
  C'est la seule chose du pipeline que je n'ai pas pu déléguer à un modèle.
  Mon juge se trompe encore. Mais maintenant, je le vois.
-->



---
layout: center
class: text-center
transition: fade-out
---
# Les sources

<div class="scotch qr-cadre mx-auto mt-4"><span>QR sources</span></div>

<p class="ref mt-4">lien à venir</p>

<!--
TODO : générer le QR des sources (repo, articles, données) et le mettre à la place du cadre.
-->

---
layout: center
class: text-center
transition: fade-out
---
# Votre avis

<div class="scotch qr-cadre mx-auto mt-4"><img src="./img/openfeedback.png" alt="QR code OpenFeedback" /></div>

<p class="mt-4"><span class="annotation">merci ! des questions ?</span></p>

<!--
QR OpenFeedback (img/openfeedback.png). ⚠ Le scanner une fois avant le jour J pour vérifier qu'il ouvre bien ce talk.
Cette diapo reste à l'écran pendant les questions : le QR a le temps d'être scanné.

Merci. Vos questions.
-->
