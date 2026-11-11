# WIP-SLIDES — mémoire de travail du support

*Dernière mise à jour : 2026-10-21.* À lire avant de toucher au deck. Le contexte du projet
(juge, bancs, chiffres) vit dans `../../WIP.md` ; ce fichier ne couvre que le **support**.

## Contexte

- Talk **« RAGots et Hallucinations — votre chatbot passe devant le juge »**, DevFest Paris,
  **27 novembre 2026**, 20 min, ~400 personnes mélangées.
- Le support final est **`slides.md`** (Slidev 53). Les autres `.md` de `demo/` sont des
  brouillons. Plan d'ensemble : `../PLAN-DEVFEST-2026.md` ; texte par diapo : `../talk_v3.md`.
- **Démo interne vendredi 2026-10-23** : recueillir l'avis sur les choix ouverts (voir plus bas).

## Ligne éditoriale (ne pas la revisiter sans raison)

- Un **REX**, pas un exposé de méthodes : construire l'instrument, l'auditer, s'en servir.
- **Fil retenu le 2026-10-19** : une phase de **théorie** qui pose les questions (diapos 8–9),
  puis l'**implémentation** qui y répond pièce par pièce (principes, pas lignes de code),
  jusqu'au banc RAG qui **aide à un choix d'archi** (Lucene / Neo4j). Construction en miroir :

  | Théorie (la question) | Mon implémentation (la réponse) |
  |---|---|
  | que filtrer avant le juge ? | L0 : parenthèses |
  | quel format de verdict ? | binaire, PASS ⟺ tous les checks |
  | quels biais ? | mélange à graine, conventions (0 % → 76 %) |
  | lui faire confiance ? | étalon de 50 copies, triage (12 relectures au lieu de 50) |
  | à quoi ça sert ? | le banc RAG → un choix d'archi |

- **Une seule métaphore** : le correcteur de copies et son barème. Copie, barème, tampon,
  double correction, copie hors-sujet écartée avant lecture.
- Phrases courtes, rien de pompeux, **raconter avant de nommer**. Les chiffres exacts vont
  dans les notes, pas à l'écran.
- **Phase de coupe** : un ajout remplace quelque chose ou vit dans les notes.
- Jamais « κ 0,880 entre humains » : écrire « 50 relus · un relecteur ».
- Niveaux de juge (littérature fournie par Mehdi) : **L0** règles · **L1** un LLM + barème ·
  **L2** jury / vérification par étapes. Mehdi est en **L0 + L1** ; le doute part chez un
  humain. Le jury a été **essayé** (non concluant) : c'est l'acte final du REX.
- **Le REX est une histoire, pas une liste** (arbitré le 2026-10-21) : je veux noter mon RAG →
  il faut un étalon → le juge ne rend pas de verdict → deux raccourcis → je m'en sers (bug, banc
  menteur) → un jury → pour le choisir… l'étalon. **La boucle** est la chute : « chaque
  raccourci m'a ramené à l'étalon, la seule chose que je n'ai pas pu déléguer à un modèle ».
  Une phrase-chute surlignée par acte à l'écran ; κ, p et citations dans les notes.

## Thème : « Copie corrigée »

**Pourquoi.** Inspiré des exemples aimés par Mehdi (PayFit DevLille, Julien Topçu,
Hubert Sablonnière) : fond clair, typo affirmée, illustrations dessinées, révélation au clic.
Consigne : **« du sel, pas un copier-coller : d'autres teintes, d'autres motifs »**. Le motif
retenu prolonge le titre (« passe devant le juge ») : la diapo est **une copie qu'on corrige**.

**Direction artistique.**

| Élément | Choix | Où |
|---|---|---|
| Fond | papier Seyès (grille 32 px + lignes fines 8 px) + marge rouge | `style.css` `.slidev-layout` |
| Encre | `--encre #1c2541` (bleu-noir de stylo plume), `--encre-douce #4a5573` | `style.css` |
| Correcteur | `--rouge #d62839` : mots-clés, soulignés, annotations | `.rouge`, `h1::after` |
| Validé | `--vert #2f7d4f` (PASS) | `Tampon couleur="vert"` |
| Surligneur | `--fluo` jaune, trait penché | `.fluo` |
| Code | ardoise `--ardoise #23332d`, thème shiki `vitesse-dark` | `setup/shiki.ts` |
| Typo | Bricolage Grotesque (texte), **Caveat** (écriture du correcteur), JetBrains Mono | headmatter `fonts` |
| Titres | weight 800 + trait de stylo rouge ondulé dessous | `h1::after` |

**Motifs réutilisables** (classes dans `style.css`) : `.fluo` · `.annotation` (remarque
manuscrite rouge, penchée) · `.etiquette` (libellé mono majuscules) · `.ref` (source sous un
fait) · `.scotch` (photo scotchée) · `.carte` · `.deux` · `.etiquette-logo` ·
`.fiches` / `.fiche` (fiches bristol 2×2, liseré rouge, une par `v-click`, annotation du
correcteur en bas à droite — diapo « Aucune différence » ; né sur la diapo biais RAG, coupée).

**Composants** (`components/`, auto-importés) :
- `Tampon.vue` — tampon encreur (`couleur: rouge|vert|encre`, `angle`), texture SVG turbulence.
- `JugeTheorie.vue` — diapo 8, le LLM juge **générique** : copie → juge → verdict, puis au clic
  barème · filtre sans LLM · format imposé · étalon · renvoi à l'humain si doute (5 clics).
- `QuatreFacons.vue` — diapo 9, les 4 façons de juger (redessiné d'après la figure DataCamp,
  pas copié) ; une carte par clic, le verdict « tamponne » ; clic 5 entoure la classification.
- `JudgeSchema.vue` — **le juge de Mehdi complet** (état 11 de `../SCHEMA-ETATS.md`).
  **Inutilisé exprès** : réservé au récapitulatif de fin d'implémentation, pour ne pas gâcher
  la construction.
- `global-top.vue` — barre de progression « barème » : une case par diapo, cochée en rouge,
  compteur `NN / NN` ; masquée sur la couverture.

**Animation** : `v-click` sur des `<g>` SVG ; entrée en glissé (`translate`) + verdict qui
tombe comme un tampon (`scale` + rotation, rebond) ; trait rouge qui se dessine
(`stroke-dashoffset`). Transition de diapo `slide-left` / `fade-out`.

## Pièges techniques

- Images : toujours `./img/...` (un `img/...` nu casse le build rolldown).
- `global-bottom.vue` est caché par le fond opaque des diapos → utiliser `global-top.vue`.
- Le thème default grise `h1 + p` : surchargé dans `style.css`.
- Vérifier : `npx slidev build --out <scratch>/dist`, et captures headless
  `Chrome --headless=new --screenshot=… --window-size=1280,720 --virtual-time-budget=9000
  "http://localhost:3031/N?clicks=K"` (dev server `npx slidev --port 3031`).
  `slidev export` échoue : Playwright absent.
- zsh : ne jamais nommer une variable `path`.

## Carte du deck (21 diapos au 2026-10-21)

1 couverture · 2 Imaginez… · 3 un chatbot n'est pas un POC (Air Canada) · ~~4 pas un cas isolé~~ (coupée le 2026-10-24, numéros suivants -1) ·
5 pourquoi personne n'a rien vu · 6 OllamAssist · 7 comment savoir si j'améliore ·
8 LLM-as-a-Judge (théorie) · ~~9 4 façons~~ (coupée le 2026-10-24) · 10 rapide à coder (LangChain4j) ·
11 biais des LLM (verbosité, position, indulgence — mesurés sur mon juge) ·
**REX en actes** : 12 qui juge le juge ? (l'étalon, acte 1) · 13 mon juge ne rend pas de verdict
(0 → 76 %, acte 2) · 14 deux raccourcis (entraîner 76 → 76 %, plus gros 76 → 90 % ; actes 3+4,
« l'instrument est prêt ») · 15 premier verdict (GraphRAG 16,7 % vs vectoriel 60 % : c'est ton
code, acte 5) · 16 « aucune différence » (détecteur / panne / plafond retiré 60 → 78,3 %,
acte 6 ; refaite le 2026-10-21 : panne / hint coverage 68,6 → 87,4 % / ~~48,3~~ → 78,3 %,
chute « Ton juge ne voit que ce que ton banc lui montre ») · 17 noter sur dix ? (acte 7, **à l'essai**) · 18 un juge se trompe, que faire ?
(relancer 2/8 · jury 47/50 non concluant · triage 12/50 « Ne relis que les doutes » → « l'étalon ↺ »,
acte 8 + boucle) · 19 conclusion
« Copie corrigée » (`CopieCorrigee.vue`) · 20 les sources (QR à générer) · 21 votre avis
(QR feedback + « merci — des questions ? »)

Coupées le 2026-10-21 : les deux diapos littérature sur les biais RAG et leurs parades,
archivées telles quelles dans `coupes/biais-rag-litterature.md`.

Les diapos 13–17 portent l'annotation rouge « chiffres à confirmer ». Acte 7 (note sur dix) dans le
fil à l'essai (diapo 17). Few-shot, famille qui génère, κ, p,
triage (12/50) et sondes (cinq fois) : dans les notes.

## Ouvert

- [ ] **Démo : capture d'écran dans la diapo 15 (décidé le 2026-10-28, pas de vidéo tant que le passage dépasse 16 min)** : voir `DEMO-DEROULE.md`, script `scripts/demo_juge.py` (rejoue le banc plafond, mêmes verdicts au mot près). Question : « What does DocumentIndexingPipeline implement? » : 45-60 s, placée juste avant « Premier verdict » (diapo 15). Une vraie question de l'étalon où le graphe échoue et le vectoriel réussit : les deux contextes, `hintCoverage`, les deux verdicts (cases, PASS/FAIL, raison). Capture de secours. Comble la minute de marge (budget 16:30 → ~17:30).
1. **Abstract** (« biais des systèmes RAG ») : couvert par la position (ordre des extraits,
   diapo 11) et le banc qui tronquait (diapo 16) ; la littérature est coupée (archivée).
2. **Diapos 13–18** : chiffres vérifiés le 2026-10-23 (voir Fait). Reste : titre de la diapo 13
   tranché le 2026-10-24 : « Mon juge ne rend pas de verdict » ; si la relance a lieu, rejuger 15 à 18.
   « 3 valeurs sur 11 » : **tranché**, c'est le bras B de `PREENREGISTREMENT_NOTE_BC.md` (les
   « 4 valeurs vivantes » sont `PREENREGISTREMENT_ECHELLE.md`, un autre banc).
   « Quatre phrases » : tranché, « quatre règles » (4 conventions, 173 mots).
   Diapo 13 : préparer la réponse à « les conventions n'ont réparé que le format ? ».
   Diapo 14 : 14B → 32B = +14 points, sous le seuil de 15 → tampon « retenu », pas « prouvé ».
   Diapo 15 : exemple `ContextRetriever` à préparer.
   Diapo 18 : **Gemma seul 49/50 est non présentable** (WIP.md 2026-10-21) → la chute écran
   est « Il ne dispense pas de mesurer », pas « il ne bat pas un juge choisi en le mesurant ».
   Kohli vérifiée (arXiv 2605.29800, « Nine Judges, Two Effective Votes », 28 mai 2026).
   Durée : 21 diapos ; premier candidat à la coupe côté REX : l’acte 7 (diapo 17) ; puis fusion 4–5 ?
3. **Diapo 10** : le code montre `qwen2.5-coder:32b` ; Mehdi relance tout avec un modèle plus
   récent (~26–27B, nom exact à obtenir) → mettre à jour la ligne `modelName`. Le surlignage
   couvre 3 lignes (7–9), le plan en veut une.
4. **Diapos 20–21** : QR des
   sources à générer ; QR feedback fait (`img/openfeedback.png`, à scanner une fois avant le jour J) ;
   la diapo 21 reste à l’écran pendant les questions.
5. Renommer la diapo 11 « Les biais de mon juge » (proposé, pas tranché).
6. Images : PNG OllamAssist magenta à remplacer ; `judge_dredd_casque.jpeg` inutilisé (ce
   serait une 2ᵉ métaphore) ; le logo est le badge officiel DevFest Paris 2026 (`img/devfest-paris-logo.png`).
7. Intensité de la grille Seyès à vérifier sur un vrai projecteur.

## Fait

- **2026-11-11** : Baretto dans le deck. Logo et symbole récupérés sur baretto.fr (`img/baretto-logo.png`, `img/baretto-symbole.svg`). Diapos 1 et 4 : « Mehdi Elketroussi · [symbole] Baretto » (lien www.baretto.fr). Diapo 20 (reste pendant les questions) : logo complet + www.baretto.fr en bas à droite. Vérifié en capture diapos 1 et 20.
- **2026-11-11** : diapo 19 complétée : Zheng et al. (biais, NeurIPS 2023, arXiv:2306.05685), CheckEval (Lee et al., arXiv:2403.18771, vérifié), liens canlii.org et courtlistener.com pour les deux affaires. URL complètes dans SOURCES.md. Vérifié en capture.
- **2026-11-11** : diapo 19, le QR des sources est remplacé par la liste directe (deux colonnes, classe `.sources`) : OllamAssist et le banc (github.com/baretto-labs, vérifiés publics), Moffatt v. Air Canada, Mata v. Avianca, Hamel Husain, SelfCheckGPT, Verga et al. Cohen et Kohli restent dans SOURCES.md (questions). Vérifié en capture.
- **2026-11-11** : `SOURCES.md` créé, page cible du QR de la diapo 19 : Moffatt v. Air Canada, Mata v. Avianca, Hamel Husain, Cohen 1960, SelfCheckGPT (Manakul et al., EMNLP 2023, arXiv:2303.08896, vérifié : l'auto-cohérence de la diapo 17), Verga et al. 2024, Kohli 2026. Reste : publier la page et générer le QR.
- **2026-11-09** : diapo 17, le triage raconté avec son prix (`judge-finetune/TRIAGE_POSTHOC.md`, variante à conventions) : 12 relues sur 50, 4 erreurs sur 12 rattrapées, 8 angles morts répétés trois fois. Note : « Sur mon premier juge » (le triage est mesuré sur le juge à 76 %, le jury sur le 32B), réponse prête « jury de familles, pas encore mesuré ». Annotation de la règle 4 (`CopieCorrigee.vue`) : « 12 au lieu de 50 » devient « 12 relues : 4 erreurs sur 12 ». Vérifié en capture. Écran de la diapo 17 : chaque ligne dit sur quel juge elle est mesurée (« juge à 76 % », « juge à 90 % : 45 / 50 seul »), notes alignées, vérifié en capture.
- **2026-11-06** : indulgence racontée en fil : diapo 12 « Mon étalon me montre qu'il est indulgent : 10 mauvaises copies sur 27 passent », diapo 14 « Et les mauvaises copies qui passent tombent de 10 à 4 » (WIP.md, tableau JURY2 : conventions 10 indulgentes, 32B 4).
- **2026-11-06** : passage complet ~22:30 (fatigue ; dépassement sur les diapos 8, 14, 15, 17, 18). Notes reformulées en consignes positives, sans « ✂ Pas… » (Mehdi préfère des notes sur ce qu'il faut faire) : 5 lignes négatives réécrites ou retirées, ajout « une phrase par clic » (diapo 14) et « je lis la règle, l'annotation, je clique » (diapo 18). Sauvegarde : scratchpad `slides.avant-positif.md`.
- **2026-11-06** : logo officiel DevFest Paris 2026 (PNG 500×500) : lien `.svg` cassé corrigé en `.png` dans les deux étiquettes, taille `h-10` arrondie pour que le badge reste lisible. Vérifié en capture diapo 1. L'ancien SVG GDG est supprimé (2026-11-11).
- **2026-11-01** : boucle finale choisie (option C) : « Jake Moffatt a dû aller jusqu'au tribunal pour qu'on vérifie la réponse du chatbot. Vérifiez-la avant lui. » Elle referme l'ouverture (Jake) et la crainte de la diapo 7. À l'écran, diapo 18 dernier clic : « Jake Moffatt a dû aller au tribunal. Vérifiez avant lui. » (`components/CopieCorrigee.vue`), note alignée, puis 2 s de silence et « Merci ». Vérifié en capture.
- **2026-11-01** : passage complet ~17:20. Notes des 20 diapos réécrites en puces courtes (sauvegarde scratchpad `slides.avant-puces.md`), marqueur `[click]` (et non `[clic]`) : le mode présentateur surligne la ligne du clic en cours, vérifié diapo 8. Conclusion à l'écran : « Chaque raccourci m'a ramené à l'étalon » remplacé par « 650,88 $ : ce n'était pas le montant, c'était la direction. » (`components/CopieCorrigee.vue`). Les quatre raisons du booléen passent dans NOTES-QUESTIONS.md.
- **2026-11-01** : diapo 11, note : phrase sur le hasard (un juge « toujours PASS » fait 90 % si 90 % des copies sont bonnes ; étalon 23 bonnes / 27 mauvaises ; on regarde les mauvaises qui passent). Le kappa reste hors écran, réponse prête dans NOTES-QUESTIONS.md (κ 0,48 → 0,80, Cohen 1960). Diapo 14 resserrée à une phrase par clic (0:50 → 0:35), diapo 11 0:45 → 1:00, cumul inchangé à 11:30. Diapo 13 : « plus de 90 % d'accord » rétabli, c'est le 92,2 % affiché.
- **2026-11-01** : passage complet 24:05 (v3 : 31:09). Notes corrigées d'après la transcription : phrase Mata contre Avianca prête, « critères explicites », 12/50 ≠ 47/50 expliqué, plus de « température à zéro » en diapo 17 (le banc du juge tournait à 0,2, `judge-finetune/results/report.md`), 76 → 90, chiffres non sourcés en ✂ (80-90 %, « alignées à 90 % », « coûte moins cher »), « je corrige mon banc, pas le juge », boucle Air Canada en dernière phrase. Lignes obsolètes retirées (spoiler diapo 4, « on avisera », etc.). Surligneur jaune `.fluo` remplacé par un entourage rouge tracé à la main `.entoure` (12 usages), vérifié en capture diapos 1, 5, 12, 16. Sauvegardes : scratchpad `slides.avant-entoure.md`, `slides.avant-notes-v6.md`.
- **2026-10-31** : diapo 7, « Lucene et Neo4j » remplacé par « vectorielle ou graphe » (l'écran soufflait le jargon à l'oral, v5). Diapo 15 garde les petites étiquettes Neo4j / Lucene. Note diapo 5 : nom de l'affaire en tête.
- **2026-10-30** : boucle Air Canada. Diapo 3, note : « 650,88 $. (laisser le tampon) Un chatbot n'est pas un POC. », plus de « c'est la direction ». Conclusion (diapo 18), après « je le vois » : « Air Canada : 650,88 $. Ce n'était pas le montant, c'était la direction… Alors jugez-le, et jugez votre juge. » Idée venue du deck de Bruno Verachten (« Et le bus ? »).
- **2026-10-28** : passage 3 = 31:04 (budget 16:30), jugé plus fluide. Diapo 12, note : ne pas lire les règles, exemple concret de la règle 3 (Optional<String> exigé, String rendu : seule la case signature est rouge, la case consignes reste verte ; tiré de `judge-finetune/configs/conventions-fewshot.md`).
- **2026-10-28** : notes diapo 8, l'étalon : « l'expert d'OllamAssist, c'est moi ; sur votre métier, allez chercher l'expert ». Diapo 16 : « en production le jour même (le temps de la publication sur la marketplace) », pas « dans l'heure ».
- **2026-10-27** : diapo 12, règles en version humaine : une seule case rouge recale · « si possible » = bonus · chaque faute notée à un seul endroit · ne rien citer n'est pas mal citer. « invite » remplacé par « prompt » (sous-titre et note), le public dit prompt.
- **2026-10-27** : diapo 12, les quatre règles réécrites en langage concret (la 2 « une préférence non suivie » était obscure) : contrôles cochés · « si possible » ignoré · erreur comptée une fois · réponse inventée échoue même sans citation.
- **2026-10-25** : cible 17 min (questions comprises dans les 20). Chaque note commence par un budget ⏱ et le cumul (somme 16:30). Lignes ✂ là où le passage 2 a débordé : rappels de contexte, RAG redéfini, « la littérature dit », récap de la diapo 14, « c'est-à-dire » de la conclusion. Diapo 8 : « il coche d'abord, il tranche ensuite ». Diapo 4 : « Aujourd'hui » remplace « Pendant vingt minutes ». Sauvegarde : scratchpad `slides.avant-budget.md`.
- **2026-10-25** : après le 2e passage (25:33). Notes réduites à des phrases clés, une ligne par [clic], plus de scénario. Les anciennes notes complètes (chiffres vérifiés, sources, « Si la question vient ») sont archivées dans `NOTES-QUESTIONS.md`, pointé en tête de la note 1. Diapo 12 : les quatre conventions s’affichent au clic à droite du 0 % → 76 % (classe `.conventions`), étiquette réduite à « même modèle ». Corrige l’erreur du passage 2 (« c’est la sortie structurée ou l’entraînement »). Sauvegarde : scratchpad `slides.avant-phrases-cles.md`.
- **2026-10-25** : le tampon « Copie à corriger » du second titre (diapo 4) tombe au clic, après la promesse. Classe `.coup-de-tampon` dans style.css (part de scale 1.8, rebond à l'atterrissage), appliquée aussi à « 650,88 $ CA » (diapo 3) et « Cet arrêt n'existe pas » (diapo 5). Les petits tampons des diapos 14 et 17 arrivent avec leur ligne, inchangés.
- **2026-10-25** : double titre. 1 titre SANS tampon (écran d'attente, silencieux) · 2 Imaginez… (fondu retrouvé) · 3 Air Canada · 4 titre AVEC le tampon « Copie à corriger », où je me présente + la promesse · 5 Pourquoi personne n'a rien vu ? Deck : 20 diapos, renvois « diapo N » des notes décalés de un. Sauvegarde : scratchpad `slides.avant-double-titre.md`.
- **2026-10-25** : ouverture à froid. Ordre : 1 Imaginez… · 2 Air Canada (« Jake Moffatt, lui, n'a pas eu à l'imaginer ») · 3 couverture, où je me présente (« Je m'appelle Mehdi Elketroussi, software engineer… »), puis la promesse et les mains levées · 4 Pourquoi personne n'a rien vu ? `layout: cover` sorti de la headmatter vers la diapo 3. La bio (perf, tests, « l'IA ») et « la journée a été longue » sont retirées. La diapo 1 prend la transition par défaut (slide-left) au lieu de fade-out. Sauvegarde : scratchpad `slides.avant-cold-open.md`.
- **2026-10-24** : diapo 15 « Aucune différence » simplifiée en trois temps : 55 vs 48 non concluant → la panne (46/60 coupés) → contextes entiers 60 → 78,3 % (+18 points) → « Vérifie ce que ton juge lit. » (même mot que la conclusion). Hint coverage passé en RÉSERVE dans les notes. Chute orale : « la modification qui gagne, c'est la moins sexy : une recherche par mots-clés des années 90. Pas le graphe. » À éprouver au deuxième déroulé.
- **2026-10-24** : notes mises à jour après vérification des chiffres du premier passage : « plus de trois fois » (pas quatre), BM25 60 → 78,3 % (+18 points, c'est le contexte qui est jugé), jury « deux copies sur 50 », pas de « 50 à 200 selon la littérature », pas de « la note coûte plus cher en jetons » (non mesuré), 76 % pas 77, indulgence ≠ auto-préférence. Commentaires obsolètes retirés (« quatre phrases », « à l'essai », renvoi à l'acte « J'en prends trois ? », « la moitié des copies » → 46 contextes BM25 sur 60).
- **2026-10-24** : « Noter sur dix ? » déplacée entre « Mon juge ne rend pas de verdict » (11) et « Deux raccourcis » (devient 12) : elle coupait l'acte RAG, calage au premier passage. Notes : transition « le format est réparé, tentation suivante : une échelle plus fine » ; « le classement des bras change » passe en réserve (le public ne connaît pas encore les bras) ; doublon retiré des notes de la 11. Renvois « diapo N » recalés. Ordre : … 11 verdict · 12 noter sur dix · 13 deux raccourcis · 14 premier verdict · 15 aucune différence · 16 un juge se trompe · 17 conclusion.
- **2026-10-24** : diapo « 4 façons » (QuatreFacons) coupée : taxonomie générique, sautée d'instinct au premier passage. Le choix oui/non passe dans les notes de « LLM-as-a-Judge » ; « Noter sur dix ? » s'ouvre seule à l'oral (« J'aurais pu lui demander une note sur dix. »). Renvois « diapo N » décalés. Composant `QuatreFacons.vue` conservé, non utilisé. Deck : 19 diapos. Sauvegarde : scratchpad `slides.avant-coupe-d8.md`.
- **2026-10-24** : diapo 4 « pas un cas isolé » coupée (M3), après le premier passage chronométré (30:51 pour 20 min). « Et ce n'est pas un cas isolé » se dit à l'oral ; MyCity passe en RÉSERVE dans les notes de la diapo 3. Renvois « diapo N » des notes décalés de un. Sauvegarde : scratchpad `slides.avant-coupe-d4.md`.
- **2026-10-23** — vérification des chiffres des diapos 13–18 (deux sous-agents, recomptes
  JSONL). Relance non faite : juges = 14B (13, 14, triage 18), 32B MLX (14, jury 18),
  32B Ollama à schéma (15–17). Corrigé : diapo 16 « 18 FAIL → PASS » (21 = trois bras) ;
  diapo 18 ligne 1 « 8 / 12 erreurs rendues à l'identique » (le 2/8 était le jury Mistral) ;
  diapo 13 « quatre règles » (+ CopieCorrigee) ; notes : 0 % = échec de format (WIP.md:289),
  « format strict » et non « JSON valide », 37/360 = effet de budget, −61,7 pts = face à
  BM25 (−43,3 face au vectoriel, a posteriori), source 3/11 = NOTE_BC.md bras B, « 11 questions
  où seul BM25 passe ». Annotations « chiffres à confirmer » retirées sauf diapo 13.
- **2026-10-23** — diapo 21 : QR OpenFeedback (`img/openfeedback.png`) à la place du placeholder.
- **2026-10-23** — tirets cadratins (—) supprimés de tout le deck (écran, notes, commentaires
  CSS/Vue) : remplacés selon le cas par « : », « , », « . », « · » ou des parenthèses. Règle :
  plus de « — » dans le deck, ça fait réponse de LLM. Copie avant : scratchpad
  `slides.avant-tirets.md`.
- **2026-10-23** — passage « révélation progressive » sur tout le deck. Ajouté : diapo 3
  (plaidoirie, puis clic tribunal + citation, puis clic tampon 650,88 $) ; diapo 7 (deux puces
  puis le surligné, un par clic). Déjà progressives : 5, 6, 9, 11 à 19. Laissées entières : 4
  (liste de cas, M3 en suspens), 8 (schéma de trois boîtes), 10 (code surligné). `[clic]` posés
  dans les notes.
- **2026-10-23** — diapo 6 : capture IntelliJ d'OllamAssist en place (480 × 316, le placeholder
  indiquait à tort `demo/img/`) ; chatbot, agent et chute révélés un par clic, `[clic]` dans
  les notes.
- **2026-10-23** — diapo 5 mise en scène : l'extrait du mémoire (Mata v. Avianca) en papier
  scotché, clic 1 tampon « Cet arrêt n'existe pas », clic 2 surligné « Avec un LLM, le faux a
  exactement la forme du vrai. » Les deux puces (test unitaire, mot à mot) retirées de l'écran,
  gardées à l'oral dans les notes.
  Puis : Mata v. Avianca retiré de la diapo 4 (il grillait le tampon) et raconté seulement en
  diapo 5 ; étiquette neutre « Mémoire déposé devant un tribunal fédéral américain, 2023 » ;
  la référence S.D.N.Y. apparaît avec le tampon (clic 1). La diapo 4 garde MyCity, Deloitte,
  Chevrolet ; M3 (la couper) reste à trancher après vendredi.
- **2026-10-21** — diapo 11 sans chiffres : les trois biais posés en questions (« Ce que je
  crains de mon juge »), surligné « Pour le savoir, il me faut un corrigé. » → étalon. Raison :
  les mesures supposaient l'étalon (diapo 12) et les conventions (diapo 13). Indulgence 10/27
  et « regarde dans quel sens il se trompe » déplacés dans les notes de la diapo 13 ;
  46 % et 12/60 en réserve dans les notes de la diapo 11.
- **2026-10-21** — audit externe M1/M2/M4 appliqué. M1 : la promesse en trois phrases dans
  les notes de couverture (« Mon banc m'a dit "aucune différence". Je ne l'ai pas cru. »).
  M2 : diapo 7 ne pose plus que la question prétexte ; surligné « Il me faut un juge. » ;
  la vraie question (croire mon juge) vit sur la couverture et la conclusion. M4 : exemple
  de la diapo 15 remplacé — ContextRetriever passe sur les trois bras, DocumentIndexingPipeline
  « implements AutoCloseable » : FAIL graphrag / PASS vectoriel (`plafond/sans-plafond.jsonl`,
  AutoCloseable absent du contexte graphrag dans `rag-campaign.jsonl`). M3 (couper diapo 4, fait le 2026-10-24)
  et M5 (retirer les six marqueurs) reportés après la démo de vendredi.
- **2026-10-19** — nettoyage du starter Slidev, headmatter, coquilles ; logo + LinkedIn ;
  code réduit à LangChain4j ; illustration « Imaginez » (Anne Worner, CC BY-SA 2.0) ;
  thème « Copie corrigée » ; `QuatreFacons` (diapo 9) ; `JugeTheorie` à la place de
  `JudgeSchema` en diapo 8, sous-titre « Écrire un livre est difficile. Le juger, beaucoup
  moins. » ; notes des `@mehdi` réécrites (courtes, un repère par clic) ; niveaux L0/L1/L2 et
  « pourquoi pas de jury » en notes ; diapo 14 « Les biais de mon RAG » en squelette ;
  diapo 12 (biais RAG, littérature) remise dans la DA : FR, 4 fiches, texte EN en notes.
- **2026-10-20** — diapo 13 remise dans la DA : « Et quelques parades », 3 fiches, texte EN
  en notes ; annotations des fiches calées en bas de carte.
- **2026-10-20** — bascule REX, diapos 14–17 (remplacent le squelette « biais de mon RAG ») ;
  texte à l'écran réduit au minimum, détail en notes. Nouveaux motifs dans `style.css` :
  `.lecon` + `.chiffre` + `.barre` (ancien chiffre barré en rouge), `.bulletin` (candidats +
  tampons), `.barres` (barres qui se remplissent au clic). `Tampon` prend une prop `taille`.
- **2026-10-20** — fin du deck : 18 conclusion `CopieCorrigee.vue` (répond au tampon « Copie à
  corriger » de la couverture ; 3 règles cochées au clic — barème, étalon, mesure sans LLM —
  appréciation « Il se trompe encore. Mais maintenant, je le vois. », tampon « Copie
  corrigée ») · 19 sources (QR à venir) · 20 votre avis (QR feedback, reste pendant les questions).
- **2026-10-21** — REX réécrit en histoire (proposition de Mehdi, 8 actes ramenés à 6 diapos) :
  14 étalon · 15 barème · 16 raccourcis · 17 premier verdict · 18 « aucune différence » ·
  19 jury + boucle ; conclusion `CopieCorrigee` alignée (50 copies d'abord, la boucle en
  appréciation). Note « pourquoi pas de jury » de la diapo 8 corrigée (le jury a été essayé).
  Nouvelle classe `.chiffre.grand` (5rem).
- **2026-10-21** — acte 7 remis en **annexe A** (diapo 23, après « Votre avis ») ; référence
  Kohli vérifiée et complétée dans les notes de la diapo 19.
- **2026-10-21** — acte 7 sorti de l'annexe et remis dans le fil (diapo 19, entre « aucune
  différence » et le jury), à l'essai selon la réception.
- **2026-10-21** — diapo 11 : biais nommés (verbosité, position, indulgence), allégories
  renvoyées à l'oral et rappelées entre parenthèses dans les notes.
- **2026-10-21** — diapos 12–13 (littérature biais RAG) coupées, archivées dans
  `coupes/biais-rag-litterature.md` ; pont vers l'étalon et réponse à l'abstract dans les notes de la 11.
- **2026-10-21** — diapo 16 corrigée sur les sources (`PREENREGISTREMENT_PLAFOND.md`) : avec
  plafond 55 % contre 48,3 % (pas « 60 % partout ») ; le hint coverage, calculé sur le contexte
  coupé, avait le même angle mort que le juge (68,6 % vu, 87,4 % réel) ; il est nommé à l'écran.
  Chute transposable « Ton juge ne voit que ce que ton banc lui montre » ; BM25 en notes.
  Conclusion, règle 3 : « Vérifie ce que ton juge lit. » Diapo 12 : notes de puissance (15 points).
- **2026-10-21** — deux leçons transposables ajoutées sans nouvelle diapo : « Regarde dans quel
  sens il se trompe » (chute de la 11, lien Air Canada en notes) ; le triage « Ne relis que les
  doutes » (12/50, `TRIAGE_POSTHOC.md`, post hoc, mesuré sur le juge à 76 % — à refaire) dans la
  18, retitrée « Un juge se trompe. Que faire ? ». Conclusion : 4ᵉ règle « Ne relis que les doutes ».
