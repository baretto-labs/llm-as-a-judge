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

# RAGots et <span class="rouge">Hallucinations</span>

<p class="sous-titre">votre chatbot <span class="entoure">passe devant le juge</span></p>

<p class="mt-10">
  <a href="https://fr.linkedin.com/in/melketroussi" target="_blank" class="inline-flex items-center gap-2">
    <carbon:logo-linkedin class="text-2xl" /> Mehdi Elketroussi
  </a>
  <span class="mx-3 text-gray-400">·</span>
  <a href="https://www.baretto.fr" target="_blank" class="inline-flex items-center gap-2">
    <img src="./img/baretto-symbole.svg" class="h-6" alt=""> Baretto
  </a>
</p>

<div class="abs-bl ml-18 mb-10">
  <span class="etiquette-logo">
    <img src="./img/devfest-paris-logo.png" class="h-10 rounded-full" alt="DevFest Paris 2026">
    DevFest Paris · 27 novembre 2026
  </span>
</div>

<!--
⏱ 0:00. Cible : 18 min max. ⏱ = budget de la diapo (cumul).
- Silence, puis « Imaginez ».
- Je raconte ce que j'ai fait, avec mes chiffres.
- Détails et questions : NOTES-QUESTIONS.md
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
⏱ 0:40 (0:40)
- Un deuil, un voyage en urgence.
- Le chatbot : « partez, demandez le tarif réduit au retour ».
- Au retour : « c'était une erreur du chatbot ».
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

<div v-click class="abs-br mb-20 mr-20 coup-de-tampon">
  <Tampon :angle="-10">650,88 $ CA</Tampon>
</div>

<!--
⏱ 0:50 (1:30)
- Jake Moffatt l'a vécu. 2022.
- Air Canada : « le chatbot est responsable de ses actes ».
- [click] Le tribunal : il fait partie du site. (laisser lire)
- [click] 650,88 $. (laisser le tampon) Un chatbot n'est pas un POC.
-->

---
layout: cover
transition: fade-out
---
<div v-click class="abs-tr mt-14 mr-16 coup-de-tampon">
  <Tampon :angle="10">Copie à corriger</Tampon>
</div>

# RAGots et <span class="rouge">Hallucinations</span>

<p class="sous-titre">votre chatbot <span class="entoure">passe devant le juge</span></p>

<p class="mt-10">
  <a href="https://fr.linkedin.com/in/melketroussi" target="_blank" class="inline-flex items-center gap-2">
    <carbon:logo-linkedin class="text-2xl" /> Mehdi Elketroussi
  </a>
  <span class="mx-3 text-gray-400">·</span>
  <a href="https://www.baretto.fr" target="_blank" class="inline-flex items-center gap-2">
    <img src="./img/baretto-symbole.svg" class="h-6" alt=""> Baretto
  </a>
</p>

<div class="abs-bl ml-18 mb-10">
  <span class="etiquette-logo">
    <img src="./img/devfest-paris-logo.png" class="h-10 rounded-full" alt="DevFest Paris 2026">
    DevFest Paris · 27 novembre 2026
  </span>
</div>

<!--
⏱ 0:45 (2:15)
- Mehdi Elketroussi, software engineer.
- Un assistant de code : comment savoir s'il s'améliore ?
- Aujourd'hui : comment on juge le juge.
- [click] Tampon. 1 s de silence.
- Mains levées : qui a un LLM en prod ? (2 s) Qui l'évalue ? (2 s, un mot de réaction)
-->
---
transition: fade-out
---
# Pourquoi personne n'a rien vu ?

<div class="scotch extrait mx-auto mt-14">
  <span class="source">Mémoire déposé devant un tribunal fédéral américain, 2023</span>
  <p class="citation"><em>Varghese v. China Southern Airlines Co.</em>,<br>925 F.3d 1339 (11th Cir. 2019)</p>
  <div v-click="1" class="tampon-faux coup-de-tampon"><Tampon :angle="-9" taille="1.5rem">Cet arrêt n'existe pas</Tampon></div>
</div>

<p v-click="1" class="text-center mt-6"><span class="ref">Mata v. Avianca, S.D.N.Y., 22-cv-1461, juge P. Kevin Castel, 22 juin 2023</span></p>

<p v-click="2" class="text-center" style="margin-top: 2.5rem"><span class="entoure font-bold">Avec un LLM, le faux a exactement la forme du vrai.</span></p>

<style>
.extrait { position: relative; width: 640px; padding: 1.6rem 2rem; }
.extrait .source {
  font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
  letter-spacing: 0.05em; color: var(--encre-douce);
}
.extrait .citation { font-family: Georgia, serif; font-size: 1.6rem; line-height: 1.4; margin: 0.6rem 0 0; }
.tampon-faux { position: absolute; right: -1.5rem; bottom: 0.2rem; }
</style>

<!--
⏱ 1:00 (3:15)
- Regardez ce jugement. Tout a l'air juste.
- [click] Mata contre Avianca, New York, 2023. Six jugements cités, aucun n'existe : ChatGPT. 5 000 dollars.
- Test unitaire, comparaison mot à mot : ils ne voient rien.
- [click] « Avec un LLM, le faux a exactement la forme du vrai. »
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
⏱ 0:40 (3:55)
- OllamAssist : assistant de code, en local. Mon labo.
- [click] D'abord un chatbot.
- [click] Puis un agent : il lit mon code.
- [click] RAG : on lui donne des extraits, il répond à partir d'eux.
-->

---
transition: fade-out
---
# Comment savoir si j'améliore mon assistant ?

 Deux stratégies de RAG : vectorielle ou graphe.
  **Aucun moyen de les départager.**

<v-clicks>

- Trois rôles, une seule personne : **j'écris, je choisis, je juge.** **Un dispositif qui ne peut pas me contredire ne mesure rien.**

- Ma crainte : **avancer à l'aveugle.**

</v-clicks>

<p v-click><span class="entoure font-bold">Il me faut un juge.</span></p>

<!--
⏱ 0:45 (4:40)
- Deux RAG : vectoriel ou graphe. Lequel est meilleur ?
- [click] J'écris, je choisis, je juge : rien ne me contredit.
- [click] Ma crainte : que mes utilisateurs le voient avant moi.
- [click] Il me faut un juge.
-->

---
transition: fade-out
---
# LLM-as-a-Judge

Écrire un livre est difficile. Le juger, beaucoup moins.

<JugeTheorie />

<!--
⏱ 2:00 (6:40)
- Un LLM qui ne rédige pas : il corrige la copie (question, contexte, réponse).
- Il rend un verdict et une raison.
- [click] Barème : des critères explicites, écrits avant.
- [click] Filtre sans LLM : la copie est signée ? Chez moi : ça compile ?
- [click] Format imposé : il coche d'abord, il tranche ensuite.
- [click] Étalon : 50 copies que j'ai corrigées. L'expert d'OllamAssist, c'est moi.
- [click] Le doute part chez un humain. (détail diapo 17)
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
⏱ 0:40 (7:20)
- Vingt lignes de LangChain4j.
- Température 0 : il juge pareil à chaque fois.
- Facile à coder. Mais un LLM a des biais.
-->
---
transition: fade-out
---
# Quelques biais des LLM ...

Ce que je crains de mon juge.

- **Biais de verbosité** : est-ce qu'il se laisse impressionner par une réponse longue ?
- **Biais de position** : est-ce que l'ordre des extraits change son verdict ?
- **Biais d'indulgence** : est-ce qu'il valide trop facilement ?

<p v-click class="mt-8"><span class="entoure font-bold">Pour le savoir, il me faut un corrigé.</span></p>

<!--
⏱ 0:45 (8:05)
- Verbosité : le long l'impressionne ?
- Position : l'ordre des extraits change le verdict ?
- Indulgence : il laisse passer le faible ?
- [click] Pour le savoir, il me faut un corrigé.
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

<p v-click class="mt-8"><span class="entoure font-bold">Avant d'écrire le juge, écris le corrigé.</span></p>

<!--
⏱ 1:00 (9:05)
- 50 copies dont je connais le verdict.
- [click] 50, c'est peu : je ne conclus qu'au-delà de 15 points.
- Hasard : si 90 % des copies sont bonnes, un juge « toujours oui » fait 90 %. Mon étalon : moitié-moitié.
- [click] Avant d'écrire le juge, écris le corrigé.
-->

---
transition: fade-out
---
# Mon juge ne rend pas de verdict

Premier prompt : rien d'exploitable.

<div class="grid gap-10 mt-8 items-center" style="grid-template-columns: auto 1fr">
<div class="lecon items-center text-center">
  <span class="etiquette">même modèle</span>
  <div class="chiffre grand whitespace-nowrap"><span class="barre">0 %</span> → 76 %</div>
  <p>de verdicts justes sur l'étalon</p>
</div>
<ol v-click class="conventions">
  <li>Une seule case rouge, et la copie est recalée.</li>
  <li>« Si possible », c'est un bonus, pas une obligation.</li>
  <li>Chaque faute se note à un seul endroit.</li>
  <li>Ne rien citer, ce n'est pas mal citer : l'invention est punie ailleurs.</li>
</ol>
</div>

<p v-click class="mt-8 text-center"><span class="entoure font-bold">Le plus gros levier m'a coûté quatre règles.</span></p>


<!--
⏱ 1:00 (10:05)
- Premier prompt : 0 %. Pas faux : illisible. Il s'arrête avant le verdict.
- [click] Quatre règles dans le prompt, même modèle : 76 %. (je laisse l'écran parler)
- [click] Le plus gros levier : quatre règles.
- Mon étalon me montre qu'il est indulgent : 10 mauvaises copies sur 27 passent.
- Si question, règle 3 : Optional&lt;String&gt; demandé, String rendu. Seule la case signature est rouge.
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

<p v-click class="mt-8"><span class="entoure font-bold">L'échelle fine est un interrupteur déguisé en potentiomètre.</span></p>


<!--
⏱ 0:50 (10:55)
- J'aurais pu demander une note sur 10.
- Il n'utilise que 3 notes sur 11.
- [click] Avec des critères, la note colle au oui/non : 92 %.
- [click] Un interrupteur déguisé en potentiomètre. Demandez le booléen.
- Si question : les quatre raisons du booléen (NOTES-QUESTIONS.md).
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
  <p class="text-right"><span class="entoure font-bold">L'instrument est prêt.</span></p>
</div>


<!--
⏱ 0:35 (11:30)
- Une phrase par clic.
- 76 %. Comment monter ?
- [click] J'entraîne : rien ne bouge.
- [click] Plus gros, 32 milliards : 90 %. Et les mauvaises copies qui passent tombent de 10 à 4.
- [click] L'instrument est prêt.
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
  <p class="text-right"><span class="entoure font-bold">Un juge sert d'abord à trouver tes bugs.</span></p>
</div>


<!--
⏱ 1:00 (12:30)
- Alors, j'améliore ?
- [click] Graphe : 16,7 %.
- [click] Vectoriel : 60 %.
- [click] Un tel écart, c'est mon code : le graphe perd des liens. Il ramène la classe, pas ce qu'elle implémente.
- Je m'attendais à l'inverse.
- Un juge sert d'abord à trouver tes bugs.
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

<p v-click class="text-right mt-10"><span class="entoure font-bold">Vérifie ce que ton juge lit.</span></p>


<!--
⏱ 1:15 (13:45)
- Vectoriel + BM25 (mots-clés) : 55 contre 48. Aucune différence.
- Je ne l'ai pas cru.
- [click] Mon banc coupait les contextes à 6 000 caractères : 46 sur 60.
- [click] Contextes entiers : 60 → 78 %.
- [click] « Vérifie ce que ton juge lit. »
- J'ai corrigé mon banc, pas le juge. En prod le jour même.
-->

---
transition: fade-out
---
# Un juge se trompe. Que faire ?

<div class="bulletin mt-6">
  <div v-click class="ligne">
    <span class="candidat">Le relancer trois fois <small>juge à 76 %</small></span>
    <span class="note">8 / 12</span>
    <Tampon couleur="rouge" taille="0.9rem" :angle="-3">mêmes erreurs</Tampon>
  </div>
  <div v-click class="ligne">
    <span class="candidat">Un jury de trois familles <small>juge à 90 % : 45 / 50 seul</small></span>
    <span class="note">47 / 50</span>
    <Tampon couleur="encre" taille="0.9rem" :angle="3">non concluant</Tampon>
  </div>
  <div v-click class="ligne">
    <span class="candidat">Relire là où il hésite <small>juge à 76 %</small></span>
    <span class="note">12 / 50</span>
    <Tampon couleur="vert" taille="0.9rem" :angle="-4">à relire</Tampon>
  </div>
</div>

<p v-click class="mt-8"><span class="entoure font-bold">Ne relis que les doutes.</span></p>

<p v-click class="mt-2 text-right"><span class="annotation">et tout ça, mesuré sur… l'étalon ↺</span></p>


<!--
⏱ 1:15 (15:00)
- Mon juge se trompe encore. Que faire ?
- [click] Juge à 76 %, relancé trois fois : 8 erreurs sur 12 reviennent identiques.
- [click] Juge à 90 % : un jury de trois familles fait 47 contre 45. Sous 15 points : non concluant.
- [click] Juge à 76 % : là où il change d'avis, il hésite : 12 copies sur 50.
- [click] Je ne relis que celles-là. J'attrape 4 erreurs sur 12. Les 8 autres, il les répète trois fois : ce sont ses angles morts.
- [click] Je ne le sais que grâce à mes 50 copies.
- Si question sur la température : ce banc tournait à 0,2, pour voir ses hésitations.
- Si question « et les erreurs sûres d'elles ? » : un jury de familles différentes, la seule piste qui vise ces angles morts. Pas encore mesuré.
-->

---
layout: center
class: text-center
transition: fade-out
---

<CopieCorrigee />

<!--
⏱ 1:00 (16:00)
- La couverture disait « copie à corriger ». La voici.
- Pour chaque règle : je la lis, je lis l'annotation rouge, je clique.
- [click] Écris tes 50 copies d'abord.
- [click] Écris ton barème.
- [click] « Vérifie ce que ton juge lit. » (mot pour mot)
- [click] Ne relis que les doutes.
- [click] Dernière phrase : « Jake Moffatt a dû aller jusqu'au tribunal pour qu'on vérifie la réponse du chatbot. Vérifiez-la avant lui. »
- 2 s de silence. Puis « Merci ».
-->



---
transition: fade-out
---
# Les sources

<div class="deux mt-8 sources">
<div>
  <span class="etiquette">le code</span>
  <p><b>OllamAssist</b><br><span class="ref">github.com/baretto-labs/OllamAssist</span></p>
  <p><b>Le banc et le juge</b><br><span class="ref">github.com/baretto-labs/llm-as-a-judge</span></p>
  <span class="etiquette mt-6 block">les affaires</span>
  <p><b>Moffatt v. Air Canada</b><br><span class="ref">2024 BCCRT 149 · canlii.org</span></p>
  <p><b>Mata v. Avianca</b><br><span class="ref">S.D.N.Y., 22-cv-1461, 22 juin 2023 · courtlistener.com</span></p>
</div>
<div>
  <span class="etiquette">les articles</span>
  <p><b>Using LLM-as-a-Judge For Evaluation</b><br><span class="ref">Hamel Husain · hamel.dev/blog/posts/llm-judge</span></p>
  <p><b>Judging LLM-as-a-Judge</b><br><span class="ref">Zheng et al. · NeurIPS 2023 · arXiv:2306.05685</span></p>
  <p><b>CheckEval</b><br><span class="ref">Lee et al. · 2024 · arXiv:2403.18771</span></p>
  <p><b>SelfCheckGPT</b><br><span class="ref">Manakul, Liusie, Gales · EMNLP 2023 · arXiv:2303.08896</span></p>
  <span class="etiquette mt-6 block">le jury</span>
  <p><b>Replacing Judges with Juries</b> <span class="annotation text-base">pour</span><br><span class="ref">Verga et al. · 2024 · arXiv:2404.18796</span></p>
  <p><b>Nine Judges, Two Effective Votes</b> <span class="annotation text-base">contre</span><br><span class="ref">Kohli · 2026 · arXiv:2605.29800</span></p>
</div>
</div>

<!--
⏱ 0:15 (16:15)
- Le code, le banc et les articles : tout est ici.
-->

---
layout: center
class: text-center
transition: fade-out
---
# Votre avis

<div class="scotch qr-cadre mx-auto mt-4"><img src="./img/openfeedback.png" alt="QR code OpenFeedback" /></div>

<p class="mt-4"><span class="annotation">merci ! des questions ?</span></p>

<div class="abs-br mr-14 mb-10 text-center">
  <a href="https://www.baretto.fr" target="_blank">
    <img src="./img/baretto-logo.png" class="h-24 mx-auto" alt="Baretto">
    <span class="ref">www.baretto.fr</span>
  </a>
</div>

<!--
⏱ 0:15 (16:30)
- Merci. Vos questions ?
- Laisser cette diapo pendant les questions.

-->
