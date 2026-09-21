# REX — trame de l'exposé (novembre 2026)

> **Titre, abstract et objectifs : figés.** L'abstract a été retenu, il engage.
> **Plan arrêté le 2026-09-21**, avec quatre retouches appliquées le même jour — détaillées en fin
> de document, avec leur motif.
> Durée : **20 min**. Le décompte du plan tombe à 20 pile (3+4+4+6+3), sans marge : toute
> respiration se prend sur du contenu, pas sur du temps qui n'existe pas.

---

## Titre

> **RAGots et Hallucinations : votre chatbot passe devant le juge**

## Abstract — retenu, verbatim, ne pas retoucher

> Lorsqu'un assistant IA répond à côté de la plaque, le premier réflexe est d'accuser le modèle
> d'« halluciner ». Pourtant, la réponse dépend avant tout de la vue qu'on lui donne : le contexte. Si les
> informations récupérées par le RAG sont incomplètes ou bruitées, même le meilleur LLM ne peut que deviner
> la vérité. À travers le développement d'un système utilisant le RAG, cette session propose de sortir du
> « pifomètre » pour entrer dans l'ingénierie de la mesure. Nous passerons au banc d'essai les différentes
> stratégies de récupération d'information en utilisant un protocole de LLM-as-a-judge. En sortie, vous allez
> comprendre quelques biais des systèmes RAG, comprendre l'intérêt de mesurer la « pertinence » de vos
> chatbot et une implémentation de l'approche LLM-as-a-judge.

**Ce que l'abstract engage**, et qu'il faut tenir : (1) des **biais des systèmes RAG**, pas seulement des
biais de juge ; (2) un **banc d'essai des stratégies de récupération** ; (3) **une implémentation**.

## Objectifs

1. Pourquoi mesurer/quantifier la qualité des réponses de son chat.
2. Présenter l'approche LLM-as-a-judge.
3. Présenter une implémentation — *promesse de l'abstract retenu*.
4. Avantages et limitations.
5. REX.

---

# Plan — 20 min

## Introduction (3 min) — Pourquoi évaluer ses systèmes LLM / Agents ?

- **Le constat** : tests unitaires et métriques lexicales (BLEU/ROUGE) sont aveugles aux erreurs
  sémantiques.
- **Quand l'IA dérape en production.** Trois cas d'école :
  - **Air Canada** — hallucination RAG entraînant une responsabilité juridique. *Décision de tribunal :
    source primaire disponible, la citer.*
  - **NYC Bot** — conseils réglementaires illégaux, risque métier.
  - **Chevy Chatbot** — injection de prompt, perte de contrôle commercial.
  - ⚠️ Les deux derniers reposent sur de la presse. Vérifier et attribuer — la règle « pas de chiffre sans
    source primaire » vaut aussi pour les anecdotes.
- **REX OllamAssist** : pourquoi j'ai voulu évaluer mon assistant de code, et ma crainte initiale.

## Partie 1 (4 min) — La méthode : les questions à se poser avant de construire son juge

- **Que faut-il évaluer, et ne PAS évaluer ?** La règle du filtre déterministe (L0) : compilation, types
  JSON, linter — par du code classique, avant de consommer le moindre jeton.
- **Quand évaluer ?** Offline (CI/CD, non-régression) contre online (échantillonnage de production).
- **Quel format de verdict ?** Abandonner les échelles 1-10 vagues au profit du **binaire PASS/FAIL**.
  - Règle dure retenue : **PASS ⟺ tous les contrôles vrais.** Pas de demi-mesure.
  - Et **contrôles avant verdict** dans le JSON : la génération est séquentielle, le modèle pose les faits
    avant de trancher. L'ordre inverse le laisserait décider puis justifier.
- **REX** : mon filtre L0 en amont, et mon choix du binaire pour la suite de tests.
  - Moment d'honnêteté à assumer : **mon propre harnais RAG utilisait une échelle 0-10** — celle que je
    vous dis d'abandonner. La migration vers le binaire est en cours, et c'est un REX, pas une leçon.

## Partie 2 (4 min) — L'ingénierie des rubriques & la maîtrise des biais

- **Rédiger une rubrique fiable** : *reasoning-then-scoring* — le juge raisonne dans `<thinking>` avant de
  noter — et décomposition en **critères atomiques vrai/faux**.
- **L'approche modulaire** : séparer le moteur de jugement neutre des rubriques spécifiques au domaine. Un
  seul modèle entraîné à être *fiable* et à **coller à une grille** ; c'est la grille qui porte le domaine.
- **Les biais systématiques.** Distinguer nettement ce que **je mesure** de ce que **la littérature
  documente** :
  - **Verbosité — mesuré chez moi.** Taux de faux PASS sur défauts verbeux contre défauts concis.
  - **Position, auto-préférence — littérature.** Le biais de position est *mitigé* chez moi (mélange des
    extraits) mais **jamais quantifié**. L'auto-préférence n'est pas mesurée du tout. À citer comme connus,
    jamais comme mes résultats.
- **REX — une seule fuite, racontée en entier** : voir « La fuite retenue » plus bas.

## Partie 3 (6 min) — Le choix de l'infrastructure & l'implémentation (cas d'étude local)

- **Les options** : modèles frontier en cloud, modèles distillés, SLM fine-tunés en local — arbitrages
  coût, latence, confidentialité.
- **Constitution du jeu de données (principe LIMA)** : un golden set de 100–150 exemples d'experts
  rédigés à la main suffit à **enseigner la posture** de juge.
  - ⚠️ **Et voici ce que mes données ajoutent** : à 150 exemples, le surapprentissage est **reproductible**.
    Trois runs, même courbe. LIMA enseigne la posture, *et* le modèle commence à mémoriser avant la fin.
    Détail à donner : le minimum de validation tombe à l'itération 250, et mes points de contrôle sont à
    100/200/300/400 — **le meilleur modèle n'a jamais été sauvegardé.**
- **REX OllamAssist** :
  - Pourquoi un **SLM 14B en local sur Mac M3** : confidentialité du code, zéro coût de jetons.
  - La démarche **QLoRA via `mlx-lm`**, et le juge servi par **`mlx_lm.server`** sur une API
    OpenAI-compatible, interrogé depuis le harnais Java.
  - **Un seul modèle, plusieurs grilles d'évaluation** : on entraîne le juge à être fiable et à coller à
    une grille ; la grille évalue le domaine.
  - Précision à ne pas sur-vendre : **le RAG lui-même tourne toujours sur Ollama** — génération,
    embeddings, reranker. Le juge passe par MLX, le système jugé reste sur Ollama. Les deux sont locaux,
    la promesse « tout en local » tient — mais la démo fait tourner les deux **plus** Neo4j embarqué sur
    36 Go. À répéter avant le jour J.
- **Le banc d'essai** : Lucene contre GraphRAG-Neo4j, jugés par le même juge, sur les mêmes questions.

## Partie 4 & Conclusion (3 min) — Calibration & triage humain dans la boucle

- **Mesurer la fiabilité du juge — et distinguer deux κ qu'on confond tout le temps :**

  | κ | ce qu'il mesure | état |
  |---|---|---|
  | **κ du corpus** | accord entre l'annotateur humain et les étiquettes de référence | **mesuré : 0,880, IC 95 % [0,720 — 1,000]**, accord de verdict 47/50 sur les 50 items |
  | **κ du juge** | accord entre le juge et l'étalon | **n'existe pas encore** — il sort du benchmark, pas de la relecture |

  Ne pas présenter le premier comme le second. Le premier dit *« mon étalon est-il fiable ? »*, le second
  *« mon juge est-il aligné ? »*.

- **Le chiffre qui dit l'inverse, et qu'il faut donner juste après** : **17 items sur 50 portent un
  désaccord sur au moins un contrôle, dont 15 que le verdict absorbe.** Le verdict est une conjonction :
  dès qu'un contrôle échoue des deux côtés, un désaccord sur un autre devient invisible.
  **Le verdict est reproductible ; les raisons le sont beaucoup moins** — or le juge est entraîné sur les
  raisons. C'est un plafond sur ce que le fine-tuning peut apprendre, une propriété du corpus, pas un
  défaut de la méthode.

- **Et un κ bas qui ne veut pas dire ce qu'on croit** : le contrôle le plus fréquent, `respect_consignes`,
  tombe à **κ = 0,386 pour 78 % d'accord brut**. Marges très déséquilibrées. Publier le κ seul sous-estime
  l'accord, publier les 78 % seuls le surestime. Les deux vont ensemble, avec les marges.

- **Une asymétrie qui n'est pas du bruit** : **16 désaccords sur 22 vont dans le même sens**, l'annotateur
  humain plus sévère que l'étiquette rédigée par le LLM. Une vérité de référence écrite par un LLM puis
  relue est **plus indulgente** que ce que l'humain aurait produit seul.

- **Le triage par niveau de confiance** : automatiser les décisions nettes, router les cas ambigus vers
  l'humain.
  - Le signal de confiance existe déjà dans le harnais : **la stabilité du verdict sur plusieurs passes**.
    Un item instable est un item à router. Le rattacher à cette mesure, ne pas l'inventer.

- **Takeaways** : les 3 étapes clés pour concevoir son propre évaluateur dès demain.

---

# Matière

## Les chiffres, mesurés et non estimés

| | |
|---|---|
| Durée d'entraînement | **90 min 58 s** (13,65 s/itération) — dont 76 min d'itérations et 14,7 min de validation |
| Pic mémoire | **11,32 Go** sur 36 Go |
| Itérations | 400, batch 1 |
| Jetons entraînés | 169 513 |
| Adaptateur | **43,8 Mo** — 11,5 M paramètres sur 14,77 Md, soit **0,078 %** |
| Coût en jetons facturés | **zéro** |

**91 minutes sur un portable.** C'est l'argument « le fine-tuning n'est pas si coûteux », mesuré.

Et une correction à raconter : j'ai d'abord publié **76 minutes**. La méthode de substitution déclarée ne
dérivait la durée que des itérations d'entraînement et **excluait les 9 passes de validation**, soit
14,7 minutes. L'utilisateur attend 91 minutes, pas 76. Corriger rendait le chiffre **moins** flatteur —
c'est précisément ce qui rend la correction crédible.

⚠️ **À dire, parce que c'est un REX** : ce relevé était **faux** au premier jet. L'horloge annonçait
690 minutes — un facteur **9,1** — la machine ayant été suspendue pendant l'entraînement. Pour la
troisième fois, et **rien ne l'a signalé** : le script n'a aucune détection, il écrit la valeur brute dans
le champ qui fait foi. La correction est manuelle, comme les deux précédentes.

**Courbe de validation** — troisième reproduction quasi identique :

```
1: 1,816 → 50: 1,259 → 100: 1,164 → 150: 1,131 → 200: 1,124
→ 250: 1,103  ← minimum
→ 300: 1,200 → 350: 1,199 → 400: 1,183
```

## La fuite retenue — le correctif qui aggrave

*Une seule fuite est racontée, en entier. Les deux autres sont en note plus bas, permutables.*

- 17 requêtes portaient « si tu as le temps, dis un mot de X ». **Les 17 étaient PASS. 17/17.**
- Déterministe, pas statistique : un juge n'a qu'à détecter la chaîne pour marquer 17 sur 17.
- Correctif : ajouter la clause à des FAIL existants. Règle de surface ramenée à 57 %.
- **Sauf que le correctif plaçait la clause en paragraphe isolé**, là où les 17 d'origine la portaient en
  incise. Nouvelle règle apprise : « paragraphe isolé ⇒ FAIL », **30 items sur 30**.
- Elle a traversé **une régénération, une validation à 0 erreur, trois mesures et un commit**.
- **Ce qui l'a révélée : un humain.** Le relecteur a répondu différemment sur un item, après avoir appliqué
  la règle correctement quatre fois. Ce n'était pas un relâchement — le stimulus était réellement différent.

> **La diapositive qui compte :** les métriques ont trouvé ce que je leur avais demandé de chercher.
> L'humain a trouvé ce que je ne savais pas chercher.

**Les deux autres fuites, coupées faute de temps** — à permuter si l'audience est plus statisticienne :

- **Verbosité** : longueur prédisant le verdict à 75 % pour une base de 53 %, annoncé **+8,8 σ**.
  Spectaculaire et faux : la statistique avait été maximisée sur 145 seuils et deux directions, puis
  comparée à un taux de base. Test de permutation : **+1,3 σ, p = 0,132**. Du bruit.
  *Règle acquise : tout seuil choisi après coup se compare à un tirage de permutation du même maximum.*
- **Mise en forme** : balayage systématique de 22 traits. Le nombre de titres `##` sépare les verdicts —
  **0 PASS contre 24 FAIL** chez les non verbeux, puis les tableaux à **0/18**. J'écrivais les réponses
  fausses en documents soignés et les justes en prose directe, quatorze lots durant.
  *Le point piquant : la littérature 2026 documente le biais inverse — les juges notent plus haut les
  réponses à titres. Mon corpus enseignait à contredire l'a priori du modèle de base.*

## Les biais RAG, sur données réelles — la promesse de l'abstract

Trois cas tirés d'**extractions réelles** sur ma propre codebase, gardées telles quelles :

1. **Le quasi-homonyme.** Requête sur `OllamaService` ; le moteur rend `OllamaSettings` — même forme, classe
   voisine, interface sans rapport. Le contexte *ressemble* à une réponse et invite à répondre faux.
2. **Les corps tronqués.** Dix extraits, aucun corps de méthode, pour une question en « comment ». Les noms
   annoncent une intention, ils ne livrent pas la mécanique.
3. **Le vrai mais non étayé.** Une réponse exacte dans la codebase réelle, mais absente du contexte fourni.
   **Elle doit tomber** — c'est le test décisif de la posture en monde fermé. L'accepter au motif qu'elle
   est vraie reviendrait à valider, sur un autre dossier, une hallucination indiscernable.

## Ce qu'il ne faut pas dire

- « Notre corpus ne contient pas de fuite. » Invérifiable, et probablement faux.
- « Tendance à l'amélioration », « non significatif mais encourageant ». Interdit par le pré-enregistrement.
- Les chiffres de blogs d'éditeurs, du type « un juge est d'accord avec l'humain 85 % du temps, plus que
  deux humains entre eux ». Aucune source primaire.
- Présenter un résultat de la littérature comme une mesure maison.

## Questions à préparer

- *Pourquoi pas GPT-4 / Gemini comme juge ?* → coût, reproductibilité (une API change sous vous, un
  adaptateur LoRA est figé), confidentialité du code.
- *Votre vérité de référence a été écrite par un LLM — est-ce surprenant qu'un LLM y réussisse ?*
  → c'est la limite la plus sérieuse, d'où le κ humain et son intervalle.
- *Combien de temps au total ?* → chiffrer honnêtement, y compris les trois tours de correction.
- *Votre benchmark conclut sur combien de questions ?* → ~30, en design apparié. Ne détecte que de gros
  écarts, et la compétence du juge sur cette tâche précise repose sur **6 items** du golden set. À dire
  avant le résultat, pas après.

---

## Fil conducteur, formulé par l'utilisateur le 2026-09-20

> **« Même le harnais d'évaluation ne doit pas être construit sans observation ni réflexion. »**

| ce qui devait mesurer | ce qui n'allait pas | ce qui l'a révélé |
|---|---|---|
| le corpus | trois fuites de surface, dont une déterministe | un test de permutation, puis un humain, puis un balayage |
| `sweep_surface.py`, écrit pour trouver les fuites | deux bugs : direction non rapportée, coupes dans les ex æquo | relecture du code au moment d'interpréter un chiffre absurde |
| le relevé de coût | durée et mémoire fausses, machine suspendue — **trois fois**, jamais détecté | une comparaison avec le débit relevé dans le journal |
| le protocole de relecture | convention d'attribution ambiguë | suspension de la mesure plutôt qu'accumulation |
| le correctif de la fuite n°2 | il a créé une fuite pire — 30/30 au lieu de 17/17 | le désaccord d'un relecteur humain, après douze mesures muettes |
| le parseur du κ | rendait **42 items sur 50** en silence, et manquait les 3 désaccords d'un contrôle | des recoupements contre des décomptes notés pendant la relecture |
| le tirage « déterministe » | ordre des lignes dépendant du processus : adaptateurs non rejouables à graine égale | un contrôle d'empreintes avant l'entraînement final |
| **deux documents normatifs divergents** | le plus ancien restait exécutable, et le code le suivait fidèlement | la confrontation du code au protocole écrit **avant** lui |

**Aucun instrument de ce projet n'a été juste du premier coup.** Chacun a été corrigé parce qu'on a
regardé — jamais parce qu'une métrique a protesté. **C'est la diapositive de conclusion.**

---

## Les quatre retouches du 2026-09-21

1. **Ollama retiré de la Partie 3.** L'export GGUF est bloqué : `mlx_lm.fuse` refuse `qwen2` (seuls
   `llama`/`mixtral`/`mistral`) et refuse les modèles quantifiés. Le contournement par llama.cpp
   produirait un **artefact différent** de celui mesuré. Le juge est servi par `mlx_lm.server` en
   OpenAI-compatible ; le RAG reste sur Ollama, et c'est dit.
2. **Les deux κ séparés en Partie 4.** Le κ mesuré qualifie le **corpus**, pas le juge. Le κ du juge
   n'existera qu'après le benchmark. Les confondre serait annoncer un alignement qu'on n'a pas mesuré.
3. **LIMA assorti de sa réserve.** Le surapprentissage à 150 exemples est reproductible sur trois runs, et
   le minimum de validation tombe là où aucun point de contrôle n'est écrit.
4. **Une fuite au lieu de trois.** Les 4 minutes de la Partie 2 ne peuvent pas porter trois fuites *plus*
   l'ingénierie des rubriques. Le correctif qui aggrave est retenu : c'est celui qui porte le fil
   conducteur. Les deux autres restent rédigées ci-dessus, permutables sans recherche.

## Ce qui n'est pas encore construit

- **Le juge Java au schéma binaire** — parseur tolérant (le bloc `<thinking>` interdit la sortie
  structurée), contrat d'invite, agrégation en taux de PASS, McNemar apparié. **C'est la pièce dont dépend
  la démo promise par l'abstract.**
- **Le benchmark lui-même**, donc le κ du juge et le verdict Lucene / Neo4j.
- Piste gratuite à ne pas oublier : `hintCoverage` est **déterministe, sans LLM**. S'il désigne le même
  gagnant que le juge, c'est une validation croisée qui ne coûte rien ; s'il diverge, c'est encore plus
  intéressant.
