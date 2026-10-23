# talk_v3 — support de travail

**Écrit le 2026-10-18.** Suit `demo/PLAN-DEVFEST-2026.md` (13 diapos, 16:55 annoncées,
créneau de 20 min questions comprises). Ce n'est pas le deck rendu : c'est ce depuis quoi
le deck s'écrit.

**Ce que contient chaque diapo ici** : le titre, ce qui va **à l'écran**, et quelques lignes
de **scénario** — ce qui se dit. Les diapos 1, 2 et 4 sont **reprises de la v2** et portent
donc leur contenu entier ; les suivantes ne portent que des mots-clés, à mettre en scène.

**Règles qui gouvernent toute réécriture** (inchangées depuis le 2026-09-30) :

- C'est un **REX**, pas un exposé de méthodes. La méthode se coupe, les quatre preuves restent.
- Phrases courtes, une idée par phrase, rien de pompeux. **Raconter avant de nommer.**
- Une seule famille de métaphores : **le correcteur de copies et son barème**.
- **L'aveu est une preuve, jamais le propos.** Le sujet de la phrase est celui qui *détecte*.
- Les chiffres exacts, les σ et les intervalles descendent dans les notes orateur.
- On est en **phase de coupe** : une idée nouvelle **remplace** quelque chose, ou vit hors écran.

**Les quatre preuves qui ne se coupent jamais** : les conventions (0 % → 76 %), le banc RAG,
le triage (12 relectures au lieu de 50), les sondes (cinq fois un banc qui mesure le vide en
affichant BUILD SUCCESS).

> ⚠ **Deux diapos attendent des chiffres en cours de production** — la campagne RAG à trois
> bras tourne au moment où ce fichier est écrit. Voir les diapos **10** et **12**. Rien n'y
> est à figer avant que `scripts/rapport_campagne.py` ait rendu.

---

## Diapo 1 — Bonjour `0:40`

*Reprise de la v2, sans changement.*

**À l'écran**

> # RAGots et Hallucinations
> ## votre chatbot passe devant le juge
>
> Mehdi Elketroussi — Novembre 2026

**Scénario**

Bonjour à tous, merci de prendre un peu de votre temps pour parler des chatbots, et aussi
des agents. Je m'appelle Mehdi Elketroussi, je suis marié, père de deux petites princesses,
et quand tout le monde est à l'école ou au travail, je suis software engineer. J'aime les
sujets de perf et de qualité. Depuis que les LLM se sont répandus, une question me suit :
comment savoir si mon RAG s'améliore ? Et surtout, comment faire confiance à une mesure,
quand la même question peut donner deux réponses différentes ?

---

## Diapo 2 — La thèse, et Air Canada `0:50`

*Reprise de la v2. Absorbe l'ancienne diapo 3 : « Et ce n'est pas un cas isolé » et
« Pourquoi personne n'a rien vu » ne sont plus des diapos — ce qu'elles portaient descend
en notes orateur et ressort seulement si on pose la question.*

**À l'écran**

> ## Air Canada, 2024
>
> Le chatbot invente une politique de tarif deuil.
>
> Air Canada plaide : le chatbot est **« une entité juridique distincte, responsable de ses
> propres actes »**.
>
> Le tribunal :
> > « This is a remarkable submission. While a chatbot has an interactive component, it is
> > still just a part of Air Canada's website. »
>
> **650,88 $ CA**
>
> <span class="ref">Moffatt v. Air Canada, 2024 BCCRT 149</span>

**Scénario**

En novembre 2022, Jake Moffatt doit réserver un vol pour les funérailles de sa grand-mère.
Il interroge l'assistant du site, qui lui dit qu'il peut faire sa demande après le voyage.
C'était faux : la vraie règle, sur le site, exige la demande avant. L'affaire passe devant
le tribunal. Air Canada plaide que le chatbot est une entité distincte, responsable de ses
propres actes, et que l'utilisateur devait vérifier. *(laisser la réponse du tribunal à
l'écran trois ou quatre secondes)* Le chatbot fait partie du site ; le responsable du site
répond de ce que le chat dit. Ce n'est pas un POC, c'est un engagement. Ici, six cent
cinquante dollars.

Deux questions pour la salle : qui a déployé un LLM ou un RAG en production ? Et qui a mis
en place un système d'évaluation des réponses ?

> ⚠ Fondement exact : négligence dans la présentation d'informations, membre Christopher C.
> Rivers, 14 février 2024. Ne pas citer de mémoire le délai annoncé par le chatbot.
> ⚠ Si on demande d'autres cas : Mata v. Avianca (six décisions inventées, 5 000 $), audit
> NYC MyCity (95–99 % annoncés, calcul qui excluait les réponses jugées perfectibles).
> Deloitte Australie et Chevrolet de Watsonville sont **rapportés par la presse**, pas
> vérifiés sur source primaire — le dire si on les cite.
> ⚠ Si on demande pourquoi personne n'a rien vu : le faux avait la forme du vrai. Un test
> unitaire vérifie une valeur, pas un raisonnement ; et comparer mot à mot pénalise une
> bonne réponse formulée autrement.

---

## Diapo 4 — OllamAssist, les deux stratégies, et l'annonce du renversement `1:35`

*Reprise de la v2 pour les deux premiers tiers. Le troisième — **l'annonce du
renversement** — est neuf et reste à écrire mot pour mot.*

**À l'écran**

> ## OllamAssist
>
> **Un assistant de code dans IntelliJ, entièrement local. Mon labo.**
>
> D'abord un **chatbot** — il répond avec ce qu'il sait.
> Puis un **agent** — il lit mon workspace, et répond sur **mon** code.
>
> **Sa réponse ne dépend plus surtout du modèle. Elle dépend de ce qu'il a trouvé.**
>
> Deux stratégies de récupération : **Lucene** et **un graphe Neo4j**. Aucun moyen de les
> départager.
>
> *(place réservée : la phrase du renversement)*

**Scénario**

Mon terrain, c'est OllamAssist : un assistant de code dans mon IDE, qui tourne entièrement
sur ma machine. Je l'ai écrit pour comprendre ce que l'IA fait vraiment plutôt que de le
lire. La codebase qu'il indexe fait 162 fichiers Java, et c'est la mienne — donc je vois
quand il se trompe.

Au début c'est un chatbot : je pose une question, il répond avec ce qu'il sait. Puis c'est
devenu un agent : il lit mon workspace, et il répond sur mon code. Et là tout change.
*(ralentir)* Sa réponse ne dépend plus surtout du modèle. Elle dépend de ce qu'il a trouvé.

J'avais deux stratégies de récupération, Lucene et un graphe Neo4j, et aucun moyen de les
départager. Le seul juge disponible, c'était moi. Sur quelques exemples. Choisis par moi.
Trois rôles en conflit : j'écris le système, je choisis les cas de test, et je juge.

Puis **l'annonce du renversement** — la phrase que la diapo 14 viendra refermer.

> ⚠ **À RÉDIGER MOT POUR MOT.** C'est la première des trois phrases porteuses. Elle arme
> tout le reste. Forme visée, sans la dire encore : j'ai construit le graphe *pour* la
> traversée inter-modules, et c'est exactement là qu'il perd. La salle doit repartir d'ici
> avec une question ouverte, pas avec le résultat.
> ⚠ « Elle dépend de ce qu'il a trouvé » est la charnière de tout l'exposé. Ralentir.
> ⚠ Dire « peut tourner entièrement hors-ligne », jamais « ne sort jamais » : la recherche
> internet existe, optionnelle et désactivée par défaut.
> ⚠ L'image marketplace est encore un gabarit magenta. À remplacer la veille.

---

## Diapo 5 — Le principe du juge `2:15`

**À l'écran**

- un correcteur de copies · **le barème avant la copie**
- trois contrôles, pas une note sur 10
- `{checks, verdict, reason}` — **PASS ⇔ tous les contrôles vrais**
- le schéma du juge *(dix états, à dessiner)*

**Scénario**

Je vais donc construire un juge. Pas un modèle qui donne une note sur dix — un correcteur
qui applique un barème. La différence est tout le talk : une note sur dix, deux correcteurs
ne la donnent jamais pareille ; un barème, on peut vérifier s'ils cochent les mêmes cases.

Mon barème tient en trois contrôles. Le contexte est-il pertinent, est-il suffisant, le
bruit est-il maîtrisé. Le juge répond par trois vrai/faux, puis un verdict, puis une
raison. Et la règle est stricte : **PASS seulement si les trois contrôles sont vrais.**
Pas de moyenne, pas d'arrondi bienveillant.

J'avais commencé par la note sur dix. Je l'ai abandonnée : je n'arrivais pas à dire ce que
7 voulait dire, et encore moins à vérifier que mon juge et moi mettions 7 pour la même
raison.

> ⚠ C'est la diapo la plus coupable de dériver vers l'exposé de méthode. Si ça déborde, la
> réserve de coupe la ramène à 2:00.
> ⚠ Le schéma en dix états est l'une des trois tâches du chemin critique. Échafaudage ASCII
> dans `demo/CONFERENCE-V2.md`, versions longues dans `demo/SCHEMA-ETATS.md`.

---

## Diapo 6 — L'implémentation, en LangChain4j `1:30`

**À l'écran**

- **douze lignes de code au maximum, une seule surlignée**
- LangChain4j + Ollama, tout en local
- **« Le code n'est pas le problème. »**

**Scénario**

Voilà à quoi ça ressemble. *(ne pas lire le code à voix haute ; laisser la salle balayer)*
Un modèle, une invite, une réponse parsée. C'est tout. Il y a des bibliothèques qui font ça
très bien, et en une après-midi vous avez un juge qui tourne.

*(temps)*

Et c'est précisément le piège. **Le code n'est pas le problème.** Tout ce qui a été difficile
dans ce projet est arrivé après cette ligne-là : trouver l'expert, écrire le jeu de données,
et savoir si le juge a raison. Le reste du talk, c'est ces trois choses.

> ⚠ **À RÉDIGER MOT POUR MOT** : « Le code n'est pas le problème. » C'est la deuxième phrase
> porteuse, et la bascule du talk.
> ⚠ Douze lignes maximum, une seule surlignée. **S'il faut faire défiler, le point est mort.**
> ⚠ Ne pas toucher à cette diapo dans la réserve de coupe.

---

## Diapo 7 — L'expert, et le jeu de données `1:30`

**À l'écran**

- **« L'expert, c'était moi. »**
- un barème écrit avant de regarder les copies
- le corpus : des exemples, pas des règles
- **le triage : 12 relectures au lieu de 50**

**Scénario**

Un juge, ça s'étalonne contre quelqu'un. Et quelqu'un, dans ce projet, c'était moi — sur ma
propre codebase, que je connais assez pour voir quand l'assistant se trompe. C'est une
faiblesse, je la déclare ici et je dirai plus loin comment je l'ai bornée.

Ce que j'ai écrit d'abord, ce n'est pas du code : c'est le barème, avant de regarder les
copies. Puis le jeu de données — des exemples étiquetés, un par un.

Et c'est là qu'arrive la première preuve. Relire cinquante items à la main, c'est une
journée. J'ai trié avant : les cas où le juge et moi étions évidemment d'accord, je ne les
relis pas. **Douze relectures au lieu de cinquante**, et le triage est écrit avant d'avoir
vu les résultats, pas après.

> ⚠ Réserve de coupe n° 3 : descendre à 1:20 en gardant « l'expert, c'était moi » sans
> développer.
> ⚠ Le corpus n'est jamais édité à la main : tout passe par ses générateurs. Le dire
> seulement si on demande.

---

## Diapo 8 — Le banc : vectoriel contre graphe `0:50`

**À l'écran**

- 60 questions sur **ma** codebase, les mêmes pour tous les bras
- **vectoriel** · **vectoriel + BM25** · **graphe**
- un index par bras, aucun état qui traverse
- mesure appariée : la même question part dans les trois

**Scénario**

Le dispositif tient en une phrase : soixante questions sur ma codebase, posées à l'identique
à trois stratégies de récupération. Le vectoriel seul. Le vectoriel plus BM25. Et le graphe.

Chaque stratégie a son propre index, construit à part : aucune ne peut hériter de ce qu'une
autre a trouvé. Et comme la même question part dans les trois, je peux comparer question par
question plutôt que moyenne contre moyenne. C'est ce qui rend la comparaison tenable à
soixante.

> ⚠ Réserve de coupe n° 2 : descendre à 0:40 en resserrant le dispositif.
> ⚠ Ancienne version du banc : deux bras, deux scénarios. La campagne du talk en a trois,
> en une seule exécution. Ne pas mélanger les deux descriptions.

---

## Diapo 9 — Juger le juge `1:30`

**À l'écran**

- l'étalon : **50 items, relus un par un**
- **0 % → 76 %** de justesse, pour quatre paragraphes de conventions
- l'accord κ, **rétrogradé au rang de diagnostic**
- ce que 50 items **ne tranchent pas** : ~15 points

**Scénario**

Mon juge rend des verdicts. Rien ne dit qu'ils sont bons. Alors j'ai monté un étalon :
cinquante items, relus un par un, et je compare le juge à cette relecture.

Premier résultat, et c'est la preuve que je trouve la plus utile. Le juge sans consignes :
**zéro pour cent** de justesse. J'ai ajouté quatre paragraphes de conventions — ce que PASS
veut dire, ce qu'est une citation exacte, comment arbitrer un cas limite. **Soixante-seize
pour cent.** Quatre paragraphes. Pas un entraînement, pas un plus gros modèle.

Deuxième résultat, et celui-là est inconfortable : à cinquante items, mon banc ne détecte
pas un écart en dessous d'une quinzaine de points. Ça veut dire que plusieurs comparaisons
que j'aurais bien aimé trancher, il ne les tranche pas. Je préfère le dire que l'arrondir.

> ⚠ **L'étalon, c'est UN relecteur, pas deux.** Les étiquettes de départ sont produites par
> un modèle ; la relecture en aveugle est la mienne. Le κ de 0,880 mesure mon accord avec
> ces étiquettes-là. **Ne jamais dire « accord entre humains ».** La seconde relecture par
> un collègue est pré-enregistrée et pas encore rendue.
> ⚠ Le κ ne porte plus deux diapos : il donnait à l'ensemble une couleur d'excuse. Une
> mention, en diagnostic.

---

## Diapo 10 — Les résultats, la surprise, et mon bug `2:15`

**À l'écran**

- le tableau des trois bras *(chiffres en cours de production)*
- **la surprise : le graphe perd**
- le témoin sans LLM, qui dit la même chose
- **« puis j'ai découvert que le bug était à moi »**

**Scénario**

Voilà les résultats. *(laisser lire)* Le graphe perd. Nettement. Et je rappelle que je suis
allé au graphe en y croyant — c'est moi qui l'ai construit.

Premier réflexe : accuser le juge. Donc j'ai regardé si quelque chose d'autre, qui n'est pas
un LLM du tout, disait la même chose. Un simple décompte : est-ce que les identifiants que
j'attendais dans la réponse s'y trouvent ? Ce témoin ne sait rien juger, mais il classe les
stratégies — et il les classe dans le même ordre. Le juge n'invente pas le résultat.

Deuxième réflexe, le bon : regarder *pourquoi*. Et la réponse est désagréable. Mes nœuds de
graphe portent la signature des méthodes, pas leur corps. Le graphe ramène la structure et
pas le contenu. **Ce n'est pas une limite du GraphRAG, c'est une limite de mon code de
projection.** Je l'ai attrapée en regardant les items un par un, pas en lisant la moyenne.

> ⚠ **CHIFFRES EN ATTENTE.** La campagne à trois bras tourne au moment où ce fichier est
> écrit. Les 48,3 % / 23,7 % publiés viennent de la campagne du 2026-09-24, dont le juge et
> le générateur ont tous deux changé : le pré-enregistrement **interdit** de présenter les
> deux côte à côte. Attendre `scripts/rapport_campagne.py`.
> ⚠ Posture : le sujet de la phrase est celui qui **détecte**. « J'ai trouvé mon bug », pas
> « je me suis trompé ».
> ⚠ Ne pas toucher à cette diapo dans la réserve de coupe.

---

## Diapo 11 — Trois biais, constatés sur mes runs `1:15`

**À l'écran**

- **ce n'est pas le bruit, c'est le manque** — le contrôle qui échoue le moins est `bruit_maitrise`
- **le graphe ramène la structure, pas le corps** — 22 % contre 7 %
- **l'angle mort est là où j'attendais le gain** — cross-module : graphe 10 %, Lucene 50 %
- l'exemple travaillé : `ContextRetriever`

**Scénario**

Trois choses que mes mesures m'ont apprises, et qu'aucune ne vient d'un article.

La première casse un réflexe. On dit « le RAG ramène n'importe quoi ». Chez moi, c'est faux :
le bruit est le contrôle qui échoue **le moins**, et identiquement pour les deux stratégies.
Le contexte n'est pas hors sujet, il est **incomplet**. Ce n'est pas le bruit, c'est le manque.

La deuxième : le graphe ramène la structure et pas le corps. Trois fois plus d'items
pertinents mais insuffisants que le vectoriel.

La troisième : sur les questions qui traversent les modules, le graphe tombe à dix pour cent
et le vectoriel tient à cinquante. Je suis allé au GraphRAG **pour** la traversée
inter-modules. C'est son pire terrain.

*(temps)* Et maintenant la phrase qui vaut mieux que les trois prises séparément : j'ai nommé
trois biais à partir de mes mesures, puis j'ai découvert que deux n'en faisaient qu'un — et
qu'il était à moi.

L'exemple, en dix secondes. « Quelle interface `ContextRetriever` implémente-t-il, et que
redéfinit-il ? » Le graphe rend le nom de l'interface et aucune méthode. Contexte tronqué,
réponse fausse. Contexte complet, réponse juste. **Ce n'était pas une hallucination.**

> ⚠ L'exemple travaillé reste à préparer : dix minutes, et il ne dépend d'aucun run.
> ⚠ Ne pas toucher à cette diapo dans la réserve de coupe.

---

## Diapo 12 — BM25, le rerun, en production dans l'heure `1:15`

**À l'écran**

- une ligne de configuration : **BM25 à côté du vecteur**
- le banc rejoué *(chiffres en cours de production)*
- **en production dans l'heure**
- ce que le banc ne tranche pas, il le dit

**Scénario**

Et c'est là que le dispositif sert à quelque chose. J'ai une hypothèse : si le problème est
le manque et pas le bruit, alors ajouter une recherche par mots-clés à côté du vecteur
devrait récupérer ce que le vecteur rate. Une ligne de configuration.

Je rejoue le banc. *(chiffres)* Et je livre dans l'heure — pas parce que je suis rapide,
parce que **j'ai enfin un retour**. Avant, chaque modification était un pari. Là, j'ai un
avis motivé avant de livrer.

Un mot sur l'honnêteté de la mesure : si le banc ne tranche pas, il le dit. J'ai fixé les
seuils avant de lancer, pas après avoir vu les chiffres. Un résultat non concluant reste
non concluant, même quand il m'arrangerait.

> ⚠ **CHIFFRES EN ATTENTE** — c'est le trou connu du plan. Ils sortent de la campagne qui
> tourne. La lecture est fixée d'avance dans `benchmarks/PREENREGISTREMENT_REPONSE.md` :
> p < 0,05 **et** ≥ 15 points → le chiffre va à l'écran ; sinon **« non concluant »**, et
> c'est ce mot-là qui est dit, pas l'estimation ponctuelle.
> ⚠ Si « non concluant » sort, cette diapo **se raconte quand même** : « j'ai posé la
> question proprement, mon banc ne sait pas trancher à cette taille » est un enseignement.
> ⚠ Ne pas toucher à cette diapo dans la réserve de coupe.

---

## Diapo 13 — Ouverture : le fine-tuning, et le dépôt `0:45`

**À l'écran**

- j'ai entraîné un juge — **il n'a pas gagné**
- le levier que la littérature recommande, essayé : **non concluant**
- tout est dans le dépôt : corpus, bancs, pré-enregistrements
- QR code

**Scénario**

Deux pistes que j'ai suivies et qui n'ont pas donné ce que j'espérais, parce qu'elles valent
mieux dites que tues.

J'ai entraîné un juge — quatre-vingt-onze minutes sur ma machine. Il ne fait pas mieux que
les quatre paragraphes de conventions. Et j'ai essayé le levier que la littérature désigne
comme principal, mettre des exemples commentés dans l'invite : non concluant à cinquante
items. Ce qui a payé reste la chose la moins chère : écrire le barème.

Tout est dans le dépôt — le corpus, les bancs, et les pré-enregistrements écrits avant
chaque mesure, y compris ceux qui m'ont donné tort.

> ⚠ Réserve de coupe n° 4 : descendre à 0:30, simple pointeur vers le dépôt.
> ⚠ Le QR code est encore un gabarit magenta. À remplacer la veille.

---

## Diapo 14 — Conclusion `0:45`

**À l'écran**

- *(la phrase qui referme la boucle ouverte en 4)*
- un barème écrit avant de regarder les copies
- un étalon, et ce qu'il ne tranche pas
- **mesurer la récupération, pas le modèle**

**Scénario**

*(refermer la boucle ouverte diapo 4)*

Ce que je retiens tient en trois choses. Écrire le barème avant de regarder les copies —
c'est ce qui a fait passer mon juge de zéro à soixante-seize pour cent, et ça ne coûte rien.
Se donner un étalon, et accepter qu'il ne tranche pas tout. Et mesurer ce que le système
**récupère**, pas seulement le modèle qui parle — parce que depuis le jour où l'assistant
lit mon workspace, sa réponse dépend d'abord de ce qu'il a trouvé.

Merci.

> ⚠ **À RÉDIGER MOT POUR MOT** : la troisième phrase porteuse. Elle doit répondre à la diapo
> 4 de façon reconnaissable — la salle doit entendre que la boucle se ferme.
> ⚠ Ne pas toucher à cette diapo dans la réserve de coupe.

---

