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
  il faut un étalon → le juge ne sait pas juger → deux raccourcis → je m'en sers (bug, banc
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

1 couverture · 2 Imaginez… · 3 un chatbot n'est pas un POC (Air Canada) · 4 pas un cas isolé ·
5 pourquoi personne n'a rien vu · 6 OllamAssist · 7 comment savoir si j'améliore ·
8 LLM-as-a-Judge (théorie) · 9 4 façons · 10 rapide à coder (LangChain4j) ·
11 biais des LLM (verbosité, position, indulgence — mesurés sur mon juge) ·
**REX en actes** : 12 qui juge le juge ? (l'étalon, acte 1) · 13 mon juge ne sait pas juger
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

1. **Abstract** (« biais des systèmes RAG ») : couvert par la position (ordre des extraits,
   diapo 11) et le banc qui tronquait (diapo 16) ; la littérature est coupée (archivée).
2. **Diapos 13–18** : confirmer les chiffres après la relance, retirer les annotations rouges.
   « 3 valeurs sur 11 » : **tranché**, c'est le bras B de `PREENREGISTREMENT_ECHELLE.md` (les
   « 4 valeurs vivantes » sont un autre banc).
   « Quatre phrases » (récit) contre « quatre paragraphes » (WIP.md) — trancher.
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
   sources à générer ; `img/qr-feedback.png` est un **placeholder** (« QR à remplacer ») à écraser ;
   la diapo 21 reste à l’écran pendant les questions.
5. Renommer la diapo 11 « Les biais de mon juge » (proposé, pas tranché).
6. Images : PNG OllamAssist magenta à remplacer ; `judge_dredd_casque.jpeg` inutilisé (ce
   serait une 2ᵉ métaphore) ; le logo est celui du GDG Paris, pas un logo DevFest officiel.
7. Intensité de la grille Seyès à vérifier sur un vrai projecteur.

## Fait

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
  AutoCloseable absent du contexte graphrag dans `rag-campaign.jsonl`). M3 (couper diapo 4)
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
