# Notes détaillées et réponses aux questions

Archive des notes du présentateur au 2026-10-25, avant leur remplacement par des phrases clés.
On y trouve les chiffres vérifiés, leurs sources et les réponses prêtes (« Si la question vient »).
Les numéros de diapo suivent le deck à 20 diapos.

## Diapo 1 · Titre (écran d'attente)

ÉCRAN D'ATTENTE, pendant que la salle s'installe. Je ne parle pas dessus.
Pas de tampon : la copie arrive sur la table au second titre (diapo 4), avec la promesse.
Quand je commence : je passe directement à « Imaginez… », sans bonjour.

## Diapo 2 · Imaginez…

PREMIÈRE PHRASE DU TALK. Pas de bonjour avant : on entre directement dans l'histoire.
Je me présente après Air Canada, sur la couverture.

Imaginez, vous traversez une épreuve dans la vie, la perte d'un membre de votre famille, vous devez les rejoindre, après quelques minutes d'échanges avec le chatbot, vous prenez connaissance des conditions suite à un deuil, vous pouvez vous charger de tout après votre retour ... 

vous effectuez, le déplacement, faites ce que vous avez à faire, mais après votre retour quand vous voulez clore ce dossier,
le service administratif refuse, pretextant que c'est une erreur du chatbot ...

## Diapo 3 · Un chatbot n'est pas un POC

Jake Moffatt, lui, n'a pas eu à l'imaginer : c'est ce qu'il a vécu en 2022.

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

Et ce n'est pas un cas isolé.

RÉSERVE (conclusion ou questions) : NYC MyCity. L'administration annonçait 95 à 99 %
d'exactitude ; l'audit établit que ce calcul excluait les réponses jugées perfectibles.
Une mesure qui ment. Bureau du Contrôleur de New York, audit IT25PAR20028, 30 décembre 2025.

## Diapo 4 · Titre (présentation)

Second titre, APRÈS l'histoire : c'est le moment où je me présente.
Le tampon « Copie à corriger » n'est que sur ce titre-ci (la conclusion y répond).

Bonjour à tous, et merci d'être là.
Je m'appelle Mehdi Elketroussi, je suis software engineer, et je vais vous parler de
l'évaluation des systèmes RAG.

LA PROMESSE (trois phrases, à dire telles quelles) :
J'ai un assistant de code. Pour savoir s'il s'améliore, j'ai construit un banc d'essai.
Mon banc m'a dit « aucune différence ». Je ne l'ai pas cru.
[clic] Le tampon tombe : « Copie à corriger ». Laisser une seconde de silence.

Petite question pour le public : qui a déployé un LLM, ou un RAG, en production ?
Autre question : et qui a mis en place un système d'évaluation des réponses de son système ?

## Diapo 5 · Pourquoi personne n'a rien vu ?

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

## Diapo 6 · OllamAssist

Moi, mon terrain de jeu, c'est OllamAssist. 
C'est un assistant de code dans mon IDE, tournant en local, avec de "petits modèles" qu'on deploie sur sa machine ou son serveur, d'ailleurs il y de vrais sujets de securité, de souverainté, 
mais ça sera pour un autre moment.




[clic] Au début, c'est un chatbot integré dans mon ide: je pose une question, il répond avec ce qu'il sait.
[clic] Et petit à petit c'est devenu un agent : il lit mon workspace, et il répond sur mon code, genere des messages de commite, refactor du code, créé des classes ...

[clic] Et là, tout change. Sa réponse ne dépend plus surtout du modèle utilisé. Elle dépend de
ce qu'il a trouvé.


Mais pourquoi, j'ai fais ça ? pour comprendre comment fonctionne les llms et avoir mon labo, je l'ai partagé et j'ai quelques utilisateurs finalement.

## Diapo 7 · Comment savoir si j'améliore mon assistant ?

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

Note pour moi : c'est la question PRÉTEXTE, on y répond diapo 15.
La vraie question est celle de la couverture : « est-ce que je peux croire mon juge ? ».
C'est elle que la copie corrigée referme à la fin.

## Diapo 8 · LLM-as-a-Judge

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
      il donne un second avis sans LLM. En réserve dans les notes de la diapo 16.
  L1  un LLM juge avec un barème. Rapide, peu cher.
  L2  un jury de LLM, ou une vérification par étapes. Lent, cher.
  Pas pour économiser le juge : il est moins bon que le compilateur à ça.
  Moi : L0 + L1. Le doute part chez un humain (clic 5), pas chez un jury.
  Le jury, je l'ai essayé : c'est la fin de l'histoire (diapo 17).
  En local, un modèle à la fois : trois juges, c'est trois fois le temps.
[clic 3] La sortie : un format imposé, qu'un programme vérifie.
[clic 4] L'étalon : des copies corrigées à la main. Le juge aussi est noté.
[clic 5] Le juge hésite ? La copie part chez un humain. La double correction.
  L'humain ne relit pas tout : seulement les doutes.

Voilà les pièces. Je vais les construire une par une.

## Diapo 9 · Rapide à coder ... 

Voila quelques lignes de code en java pour constituer son propre juge ...
c'est assez rapide finalement ... sauf qu'on sait déjà que les llms ont des biais et des erreurs, sinon je ne serai pas en train de chercher à évaluermon système

## Diapo 10 · Quelques biais des LLM ...

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
- Indulgence : 10 mauvaises réponses sur 27 passent → raconté diapo 12.
⚠ Ne pas confondre : l'indulgence, c'est laisser passer les mauvaises copies. « Plus gentil avec
  sa propre famille de modèles », c'est l'auto-préférence, un autre biais. Et la position, ici,
  c'est l'ordre des extraits ; pas l'attention qui faiblit au milieu d'une longue invite.
Source : demo/CONFERENCE-V2.md, diapos biais du juge.

L'abstract promet « les biais des systèmes RAG » : la position, c'est l'ordre des extraits
que ramène mon RAG ; et la diapo « Aucune différence » montre un biais de mon banc RAG.

## Diapo 11 · Qui juge le juge ?

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

## Diapo 12 · Mon juge ne rend pas de verdict

ACTE 2. Chiffres vérifiés le 2026-10-23 : Qwen2.5-Coder-14B (MLX, 4 bits), 0/50 → 38/50.
« Quatre règles » : 4 conventions numérotées, 173 mots (judge-finetune/configs/conventions.md).
Dire 76 %, pas 77.

Ma première invite : zéro verdict lisible. 150 sorties sur 150 inutilisables.
Il raisonne, il nomme les bons contrôles, et il s'arrête avant le verdict.
J'écris quatre conventions : ce que veut dire PASS, ce qui compte comme étayé…
Même modèle, rien à réentraîner : 76 %.
[clic] Le plus gros levier du projet m'a coûté quatre règles.

Mais 76 %, regarde dans quel sens il se trompe (le biais d'indulgence, diapo 10) :
27 mauvaises copies, il en recale 17, en laisse passer 10. 23 bonnes, il en valide 21.
76 % de décisions justes, et près de 4 défauts sur 10 qui passent.
Ses erreurs penchent du même côté : il laisse passer. Un juge indulgent, c'est
Air Canada : la réponse fausse passe, et personne ne la voit (diapo 3).

Réponse prête : « tes conventions n'ont réparé que le format ? » Pour le 0 %, oui :
150/150 INVALID, rien de tronqué (WIP.md:289). Le levier, c'est « écrire le format attendu ».
Le dire avant qu'on le dise. Le jugement se mesure ensuite : 76 %, et dans quel sens il se trompe.

Si la question vient : p = 0,0000 sur 38 paires discordantes.
Few-shot : à la poubelle, 3 erreurs corrigées pour 8 nouvelles, 415 jetons contre 237.

## Diapo 13 · Noter sur dix ?

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

## Diapo 14 · Deux raccourcis

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

## Diapo 15 · Premier verdict

ACTE 5. Chiffres vérifiés le 2026-10-23 : qwen2.5-coder:32b (Ollama, schéma), sans plafond,
num_ctx 20480. Barres = part de verdicts PASS (10/60, 36/60). À rejuger si la relance a lieu.

La question de départ (diapo 7) : est-ce que j'améliore mon assistant ?
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

## Diapo 16 · « Aucune différence »

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

## Diapo 17 · Un juge se trompe. Que faire ?

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
C'est le « doute → humain » de la théorie (diapo 8, clic 5), en vrai.
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
sont indulgentes (encore le sens de la diapo 10). Mistral seul 35/50 : un juré faible pèse autant que les autres au vote.
⚠ Gemma seul 49/50 : NON PRÉSENTABLE (WIP.md, 2026-10-21). Question non déclarée,
4–0, p = 0,1250, sous le seuil de 15 points. Ne pas dire « mon meilleur juré bat le jury »
sans nouveau pré-enregistrement.
Littérature : PoLL (Verga et al., Cohere, 2024) ; Condorcet ;
Kohli, « Nine Judges, Two Effective Votes », arXiv 2605.29800, mai 2026 (vérifié) :
9 juges, 7 familles ≈ 2 votes indépendants ; le meilleur juge seul égale ou bat le panel.

## Diapo 18 · Conclusion (copie corrigée)

La couverture disait « copie à corriger ». La voici corrigée.
[clic 1] Écris tes 50 copies d'abord. Personne ne le fera pour toi, aucun modèle non plus.
[clic 2] Écris ton barème. Quatre règles, le plus gros levier.
[clic 3] Vérifie ce que ton juge lit. Mon banc coupait 46 contextes BM25 sur 60.
[clic 4] Ne relis que les doutes. 12 copies au lieu de 50.
[clic 5] Entraîner, grossir, voter : chaque raccourci m'a ramené à l'étalon.
  C'est la seule chose du pipeline que je n'ai pas pu déléguer à un modèle.
  Mon juge se trompe encore. Mais maintenant, je le vois.

## Diapo 19 · Les sources

TODO : générer le QR des sources (repo, articles, données) et le mettre à la place du cadre.

## Diapo 20 · Votre avis

QR OpenFeedback (img/openfeedback.png). ⚠ Le scanner une fois avant le jour J pour vérifier qu'il ouvre bien ce talk.
Cette diapo reste à l'écran pendant les questions : le QR a le temps d'être scanné.

Merci. Vos questions.

## Questions pointues (réponses courtes, préparées le 2026-10-31)

**« 50 copies, c'est assez ? »**
C'est limite, je le sais. C'est pour ça que je ne conclus qu'au-delà de 15 points d'écart. En dessous, je dis « non concluant ». Pour mesurer finement, il en faudrait plus.

**« Un seul relecteur, c'est fiable ? »**
À mon niveau, oui : je suis l'expert d'OllamAssist. La bonne pratique, c'est de faire valider par d'autres. Sur un métier qui n'est pas le vôtre, c'est obligatoire.

**« Tes règles ont été écrites en regardant les mêmes copies que celles qui mesurent ? »**
Oui, et j'ai compris ensuite que ça pèse lourd sur le résultat. Le 76 % est donc sans doute optimiste. Pour le valider, il me faudrait d'autres copies, que le juge n'a jamais vues.

Référence si besoin : Hamel Husain, « Using LLM-as-a-Judge For Evaluation » (hamel.dev). Même démarche : un expert, PASS/FAIL, itérer le prompt contre ses étiquettes, et un jeu de test séparé.

**« Pourquoi pas le kappa de Cohen ? »**
Je l'ai mesuré : κ 0,48 pour le 14B, 0,80 pour le 32B. À l'écran, je montre le pourcentage parce qu'il se lit sans explication. Le kappa corrige le hasard : si 70 % des copies sont bonnes, un juge qui dit toujours PASS fait 70 % de justesse, mais κ 0.
Ne jamais dire « κ entre humains » : c'est l'accord avec mon étalon.
Référence : J. Cohen, « A Coefficient of Agreement for Nominal Scales », Educational and Psychological Measurement, 20(1), 1960, p. 37-46.

**« Pourquoi un booléen plutôt qu'une note ? »**
1. Je ne perds rien : 3 notes sur 11 utilisées, la note collait déjà au oui/non.
2. Je peux le vérifier : oui/non se compare à l'étalon. Un 6 sur 10 n'est ni juste ni faux.
3. Le barème m'oblige à être clair : dire ce qui fait échouer.
4. Je peux agir dessus : une note impose un seuil, qui redevient un booléen (et on finit par baisser le seuil).
