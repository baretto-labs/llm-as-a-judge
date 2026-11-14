# Paquet de relecture en aveugle — golden set, 50 items

Merci de prendre ce temps. Voici ce qu'on mesure et comment.

## Ce qu'on cherche

On veut savoir si **deux personnes appliquant la même grille tombent d'accord**.
Ce n'est pas toi qui es évalué : c'est la grille. Si elle est ambiguë, c'est elle
qu'il faut réécrire — et c'est exactement ce que ce passage doit révéler.

## Comment faire

1. Pour chaque item : lis le contexte, la requête, la sortie à évaluer, et les
   critères.
2. **Tranche chaque critère séparément**, vrai ou faux.
3. **Ne calcule pas le verdict** : il en découle mécaniquement — PASS si et
   seulement si TOUS les critères sont vrais. Une seule case à faux ⇒ FAIL.
4. Reporte tes réponses dans `reponses.csv`, colonne `valeur` : `V` ou `F`.

## Règles d'application — à lire avant de commencer

Ce sont les conventions que le juge automatique doit suivre. Applique-les toi
aussi, sinon on ne compare pas la même chose.

1. **Verdict.** PASS si et seulement si tous les critères sont vrais. Aucune
   exception.
2. **Consigne obligatoire contre préférence.** Une consigne formulée comme une
   préférence (« si possible », « si tu as le temps ») et non suivie : le critère
   reste **vrai**. Une sortie verbeuse mais correcte n'est **jamais** pénalisée
   pour sa seule longueur. Une exigence explicite et vérifiable non respectée —
   signature, version, dépendance interdite, format, périmètre : critère **faux**.
3. **Un critère, une chose.** Si un critère dédié couvre déjà un point, ne le
   sanctionne pas une seconde fois dans `respect_consignes`.
4. **Citations.** Ne sanctionner que la **déformation** d'un élément réellement
   repris du contexte. Si la sortie invente de bout en bout sans rien citer, il
   n'y a aucune citation à déformer : ce critère-là est vrai, et c'est un autre
   qui porte le rejet.

## Deux consignes de protocole

- **Les dix premiers items sont les plus durs**, c'est volontaire : ce sont les
  cas limites, là où un seul critère sépare PASS de FAIL. Ne te décourage pas.
- **N'en discute avec personne avant d'avoir fini les 50.** Une seule phrase
  échangée sur un item, et la mesure ne vaut plus rien.

---


## 1/50 — `b03-012`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Explique la différence entre `merge` et `rebase`, et dis lequel utiliser dans notre workflow de pull requests. Sans obligation, dis aussi un mot de `git rebase --onto`.

### SORTIE À ÉVALUER
## La différence de fond

**`merge`** crée un nouveau commit de fusion qui a deux parents. L'historique conserve la trace exacte de ce qui s'est passé : votre branche a divergé, puis a été réintégrée. Aucun commit existant n'est modifié.

**`rebase`** rejoue vos commits, un par un, au sommet de la branche cible. Le contenu final peut être identique, mais ce ne sont plus les mêmes commits : ils ont de nouveaux identifiants, puisqu'un identifiant dépend du parent. L'historique devient linéaire, comme si vous aviez travaillé à partir de la dernière version depuis le début.

## Ce que ça implique au quotidien

- **Lisibilité** : un historique rebasé se lit de haut en bas. Avec beaucoup de fusions, le graphe devient rapidement illisible.
- **Traçabilité** : la fusion conserve le contexte réel, notamment le moment où la branche a été créée.
- **Résolution de conflits** : en fusion, on résout une fois. En rebase, potentiellement à chaque commit rejoué.
- **La règle d'or** : ne jamais rebaser des commits déjà partagés avec d'autres. Vous réécrivez un historique sur lequel vos collègues ont construit, et leur prochain `pull` fabriquera des doublons.

## Recommandation pour un workflow de PR

Rebase en local sur votre branche tant qu'elle n'est pas partagée, pour garder une série de commits propre et à jour. Intégration par merge ou squash côté serveur, ce qui préserve la trace de la revue.

Et si vous devez republier une branche rebasée après un `push`, utilisez `--force-with-lease` plutôt que `--force` : la commande refuse d'écraser des commits que vous n'aviez pas vus.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 2/50 — `b04-015`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Explique la différence entre verrouillage optimiste et pessimiste, et dis lequel choisir pour notre back-office où deux gestionnaires éditent rarement la même fiche. **Contrainte : 5 lignes maximum**, c'est pour une note interne au format court.

### SORTIE À ÉVALUER
## Verrouillage pessimiste

On pose un verrou sur la ligne dès la lecture, typiquement avec un `SELECT ... FOR UPDATE`. Les autres transactions qui veulent la même ligne attendent, ou échouent sur un délai d'attente. La cohérence est garantie par construction, mais on sérialise les accès : sous forte contention, le débit s'effondre, et le risque d'interblocage augmente dès que plusieurs lignes sont verrouillées dans des ordres différents.

## Verrouillage optimiste

On ne verrouille rien. On lit la ligne avec un numéro de version, et au moment d'écrire on vérifie que la version n'a pas changé :

```sql
UPDATE fiche SET valeur = ?, version = version + 1
WHERE id = ? AND version = ?;
```

Si l'ordre affecte zéro ligne, quelqu'un est passé avant : on remonte le conflit à l'utilisateur, qui recharge et rejoue. Le coût est nul tant qu'il n'y a pas de conflit, et c'est là tout l'intérêt.

## Que choisir pour votre back-office

Vous décrivez des conflits rares : le verrouillage optimiste est clairement adapté. Vous évitez de tenir des verrous pendant qu'un gestionnaire réfléchit devant son formulaire, ce qui est le principal défaut du pessimiste dans une application web où le temps de réflexion humain se compte en minutes.

Réservez le pessimiste aux cas où un conflit coûte cher à rejouer, par exemple un décrément de stock en fin de tunnel d'achat.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées, à l'exception de celles couvertes par un contrôle dédié ci-dessous, qui les évalue séparément.
4. format_impose: La sortie respecte la limite de longueur chiffrée fixée par la requête.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F
- `format_impose` : V / F

---


## 3/50 — `b05-008`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
On instancie plusieurs millions de ces objets et la mémoire explose. Optimise.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

### SORTIE À ÉVALUER
## Pourquoi ça coûte cher

Chaque instance Python porte par défaut un dictionnaire `__dict__` qui stocke ses attributs. C'est ce qui permet d'ajouter un attribut à la volée, mais pour un objet à deux champs, le dictionnaire pèse bien plus lourd que les données elles-mêmes.

## La correction

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y
```

`__slots__` remplace le dictionnaire par des descripteurs et un emplacement fixe par attribut.

## L'ordre de grandeur

Sur une instance à deux attributs, on passe d'environ 344 octets, en comptant l'objet et son dictionnaire, à 48 octets, soit un facteur sept. Sur cinq millions d'instances, cela représente environ 1,5 Go économisés.

## Ce que vous perdez

- Plus d'attribut dynamique : `p.z = 3` lève désormais `AttributeError`.
- Pas de `__dict__`, ce qui gêne certaines bibliothèques de sérialisation qui l'inspectent directement.
- En cas d'héritage, chaque classe de la hiérarchie doit déclarer ses propres `__slots__`, sinon le dictionnaire réapparaît.

## Alternatives

Selon votre usage, un `dataclass(slots=True)` donne le même bénéfice avec la syntaxe des dataclasses, un `NamedTuple` convient si les points sont immuables, et pour des tableaux de plusieurs millions de points, un `array` NumPy à deux colonnes serait encore bien plus compact et plus rapide à parcourir.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 4/50 — `b06-013`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Pour pousser des notifications du serveur vers le navigateur, WebSocket ou *Server-Sent Events* ? Si tu as le temps, dis un mot du passage à l'échelle derrière un répartiteur de charge.

### SORTIE À ÉVALUER
Pour de la notification, c'est-à-dire un flux **unidirectionnel** du serveur vers le client, les *Server-Sent Events* sont le choix par défaut.

- Ils passent par du HTTP ordinaire : pas de protocole distinct à faire accepter par les proxys d'entreprise, et la compression comme l'authentification par cookie ou en-tête fonctionnent sans adaptation.
- La reconnexion automatique est intégrée au protocole, avec reprise là où le client s'était arrêté grâce à l'identifiant de dernier événement reçu. Avec WebSocket, cette logique est à écrire.
- L'API navigateur est minimale, `EventSource` tient en quelques lignes.

WebSocket devient justifié dès que le client doit lui aussi émettre à haute fréquence, typiquement une édition collaborative ou un jeu, ou si vous avez besoin de transmettre du binaire, que SSE ne gère pas nativement.

Un point à connaître avec SSE en HTTP/1.1 : chaque flux occupe une connexion, et le navigateur en limite le nombre par domaine, aux alentours de six. En HTTP/2, le multiplexage supprime cette contrainte.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 5/50 — `b07-011`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Le double-checked locking est-il correct en Java ? **Réponds en trois points maximum**, c'est pour une fiche de revue de code.

### SORTIE À ÉVALUER
Le double-checked locking est correct en Java **à condition** que le champ soit déclaré `volatile`. Voici pourquoi, et comment le reconnaître en revue.

**1. Le motif.** On teste le champ hors verrou, on ne prend le verrou que s'il est nul, puis on re-teste à l'intérieur — d'où le nom. L'objectif est d'éviter le coût du verrou sur le chemin nominal, une fois l'instance construite.

**2. Ce qui casse sans `volatile`.** L'écriture `instance = new Holder()` n'est pas atomique : allocation, exécution du constructeur, affectation de la référence. Rien n'interdit au compilateur ou au processeur de rendre la référence visible avant la fin du constructeur. Un autre thread voit alors un champ non nul, saute le verrou, et manipule un objet partiellement initialisé.

**3. Ce que `volatile` garantit.** Depuis Java 5 et la refonte du modèle mémoire par la JSR-133, une écriture volatile établit une relation happens-before avec les lectures suivantes : aucune opération du constructeur ne peut être réordonnée après l'affectation, et la visibilité est assurée.

**4. En pratique.** Pour un singleton, l'idiome de l'initialisation à la demande par classe interne est préférable : le chargeur de classes garantit l'unicité et la sûreté, sans `volatile` ni verrou explicite.

**5. En revue.** Cherchez le couple `if (champ == null)` hors verrou et un champ **non** `volatile` : c'est la signature du défaut.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées, à l'exception de celles couvertes par un contrôle dédié ci-dessous, qui les évalue séparément.
4. format_impose: La sortie respecte la limite de longueur chiffrée fixée par la requête.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F
- `format_impose` : V / F

---


## 6/50 — `b07-015`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre client réessaie les appels échoués toutes les secondes, jusqu'à cinq fois. Lors de la dernière panne, cela a aggravé la situation. Explique pourquoi et que faire. Si tu as le temps, dis un mot du disjoncteur.

### SORTIE À ÉVALUER
Parce que des réessais à intervalle fixe **synchronisent** vos clients. Quand le service tombe, tous échouent en même temps, donc réessaient en même temps, une seconde plus tard, puis encore. Le service qui tentait de se rétablir reçoit alors des vagues régulières de charge, exactement au moment où il en a le moins la capacité : c'est ce qu'on appelle une tempête de réessais.

Deux corrections vont ensemble.

**Attente exponentielle.** Doublez le délai à chaque tentative — 1 s, 2 s, 4 s, 8 s — pour laisser au service une fenêtre de rétablissement qui s'élargit au lieu de rester constante.

**Gigue aléatoire.** L'exponentielle seule ne suffit pas : elle espace les vagues sans les désynchroniser, puisque tous les clients doublent en même temps. Tirez le délai au hasard dans l'intervalle, par exemple uniformément entre zéro et le plafond courant. C'est la gigue qui étale réellement la charge.

Deux garde-fous complémentaires : ne réessayez que ce qui est idempotent, sans quoi vous dupliquez des effets de bord ; et plafonnez le délai comme le nombre total de tentatives, faute de quoi un client attend indéfiniment.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 7/50 — `b09-009`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Rends cette méthode de notre bibliothèque tolérante à une liste nulle. **La signature publique est figée**, des applications tierces compilées contre cette version doivent continuer à fonctionner.

```java
public static int total(List<Integer> valeurs) {
    return valeurs.stream().mapToInt(Integer::intValue).sum();
}
```

### SORTIE À ÉVALUER
```java
public static int total(Optional<List<Integer>> valeurs) {
    return valeurs.orElseGet(List::of).stream().mapToInt(Integer::intValue).sum();
}
```

Envelopper le paramètre dans un `Optional` rend l'absence explicite dans la signature, ce qui est plus propre qu'un test de nullité : l'appelant voit immédiatement que la valeur peut manquer, et le compilateur l'oblige à en tenir compte.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées, à l'exception de celles couvertes par un contrôle dédié ci-dessous, qui les évalue séparément.
4. signature_publique_inchangee: La signature publique de la méthode est inchangée, comme l'exige la requête.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F
- `signature_publique_inchangee` : V / F

---


## 8/50 — `b10-015`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Que fait l'en-tête `Strict-Transport-Security` et quels sont les pièges à son activation ? **Format imposé : prose uniquement, aucun bloc de code ni exemple d'en-tête**, le document cible n'en accepte pas.

### SORTIE À ÉVALUER
L'en-tête `Strict-Transport-Security` demande au navigateur de n'accéder au domaine qu'en HTTPS pendant une durée déterminée, y compris lorsque l'utilisateur saisit une adresse en clair ou suit un lien non sécurisé. Il supprime ainsi la fenêtre de redirection initiale, pendant laquelle une interception reste possible.

Concrètement, on l'active ainsi :

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Le premier piège tient à la durée : elle est mémorisée par le navigateur et ne peut pas être révoquée à distance. Un domaine dont le certificat expire pendant cette période devient inaccessible, sans possibilité pour l'utilisateur de passer outre. Il est donc prudent de commencer par une durée courte et de l'allonger une fois la chaîne de certificats fiabilisée.

Le second concerne la directive d'extension aux sous-domaines : elle s'applique à tous, y compris ceux qu'on avait oubliés — un environnement de recette, un outil interne encore en clair — qui deviennent inaccessibles du jour au lendemain.

Le troisième est l'inscription sur la liste de préchargement des navigateurs, dont la sortie est lente et manuelle. C'est un engagement durable, à ne prendre qu'une fois le reste stabilisé.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées, à l'exception de celles couvertes par un contrôle dédié ci-dessous, qui les évalue séparément.
4. format_impose: La sortie respecte exactement le format imposé par la requête, sans contenu proscrit.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F
- `format_impose` : V / F

---


## 9/50 — `b12-008`

<sub>tâche RAG_CONTEXT_RELEVANCE</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.WorkspaceContextRetriever.get() [...]

=== fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.HybridRetriever.safeGet(CompletableFuture<List<T>>) [...]

=== fr.baretto.ollamassist.chat.rag.ContextRetriever [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever -[IMPLEMENTS]-> ContentRetriever
Fields:
  - private contentRetriever
  - private NOTIFICATION_GROUP_ID
  - private duckDuckGoContentRetriever
  - private workspaceContextProvider
  - private executor
  - private LAST_SOURCES
  - private settings

=== fr.baretto.ollamassist.chat.ui.Context [Class] ===

=== ContentRetriever [Class] ===

### ENTREE / REQUÊTE
Which classes does ContextRetriever delegate to, and in what order are their results merged?

### SORTIE À ÉVALUER
(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de recherche a retournés pour cette requête)

### CRITÈRES DE VALIDATION
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `contexte_pertinent` : V / F
- `contexte_suffisant` : V / F
- `bruit_maitrise` : V / F

---


## 10/50 — `b13-013`

<sub>tâche RAG_FAITHFULNESS</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.conversation.ConversationMessage.assistant(String) [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.conversation.ConversationMessage
Parameters:
  - content: String
Graph paths:
  fr.baretto.ollamassist.chat.ui.OllamaContent.subscribe(MessageBusConnection) -[CALLS]-> fr.baretto.ollamas [...]

=== fr.baretto.ollamassist.completion.LightModelService.handleSuggestion(Editor) [Function] ===
Visibility: public
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.completion.LightModelService.handleSuggestion(Editor) -[CALLS]-> fr.baretto.ollamassist.completion.LightModelService.handleBasicSugg [...]

=== AnAction [Class] ===
Inheritance paths:
  fr.baretto.ollamassist.completion.InlineCompletionAction -[EXTENDS]-> AnAction
  fr.baretto.ollamassist.chat.ui.menu.AddToContextAction -[EXTENDS]-> AnAction
  fr.baretto.ollamassist.actions.refactor.ApplyRefactoringAction -[EXTENDS]-> AnAction [...]

=== fr.baretto.ollamassist.setting.OllamAssistSettings.getAuthMode() [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.auth.AuthMode
Graph paths:
  fr.baretto.ollamassist.setting.OllamAssistSettings.getAuthMode() -[CALLS]-> fr.baretto.ollamassist.setting.OllamaSettings.getInstance()

=== fr.baretto.ollamassist.setting.ConfigurationPanel.getAuthMode() [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.auth.AuthMode
Graph paths:
  fr.baretto.ollamassist.setting.OllamassistSettingsConfigurable.isModified() -[CALLS]-> fr.baretto.ollamassist.setting.ConfigurationPanel.getAuthMode() [...]

### ENTREE / REQUÊTE
What methods does the Assistant interface define?

### SORTIE À ÉVALUER
## Réponse courte

Le contexte fourni ne contient pas l'interface `Assistant`. Je ne peux donc pas énumérer ses méthodes.

## Ce que contient réellement le contexte

Les cinq extraits portent sur des éléments distincts :

- `ConversationMessage.assistant(String)` — une méthode de fabrique construisant un message de conversation. Le nom est proche, mais il s'agit d'une classe de message, pas de l'interface interrogée.
- `LightModelService.handleSuggestion(Editor)` — relève de la complétion de code.
- `AnAction` — le nœud d'une classe IntelliJ, avec la liste des actions du projet qui en héritent.
- Deux fonctions `getAuthMode()`, qui concernent les réglages d'authentification.

## Pourquoi je m'arrête là

Répondre supposerait de restituer une interface que je n'ai pas sous les yeux. Le seul extrait dont le nom évoque la requête est un homonyme, et s'en servir produirait une réponse fausse avec l'apparence d'un ancrage.

Il faudrait relancer la recherche sur le nœud de l'interface elle-même pour obtenir ses méthodes.

### CRITÈRES DE VALIDATION
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `affirmations_etayees` : V / F
- `absence_invention` : V / F
- `citations_exactes` : V / F

---


## 11/50 — `b12-005`

<sub>tâche RAG_CONTEXT_RELEVANCE</sub>

### CONTEXTE / RAG
Method: fr.baretto.ollamassist.setting.OllamaSettings#getInstance [...]

Method: fr.baretto.ollamassist.chat.ui.OllamaContent#createConversationPanel [...]

Method: fr.baretto.ollamassist.completion.SuggestionActionHandler#isEnabledForCaret [...]

Type: class fr.baretto.ollamassist.setting.OllamaSettings implements PersistentStateComponent [...]

### ENTREE / REQUÊTE
What interfaces does OllamaService implement?

### SORTIE À ÉVALUER
(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de recherche a retournés pour cette requête)

### CRITÈRES DE VALIDATION
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `contexte_pertinent` : V / F
- `contexte_suffisant` : V / F
- `bruit_maitrise` : V / F

---


## 12/50 — `b12-007`

<sub>tâche RAG_CONTEXT_RELEVANCE</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.WorkspaceContextRetriever.get() [...]

=== fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.HybridRetriever.safeGet(CompletableFuture<List<T>>) [...]

=== fr.baretto.ollamassist.chat.rag.ContextRetriever [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever -[IMPLEMENTS]-> ContentRetriever
Fields:
  - private contentRetriever
  - private NOTIFICATION_GROUP_ID
  - private duckDuckGoContentRetriever
  - private workspaceContextProvider
  - private executor
  - private LAST_SOURCES
  - private settings

=== fr.baretto.ollamassist.chat.ui.Context [Class] ===

=== ContentRetriever [Class] ===

### ENTREE / REQUÊTE
What does the retrieve method do in ContextRetriever?

### SORTIE À ÉVALUER
(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de recherche a retournés pour cette requête)

### CRITÈRES DE VALIDATION
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `contexte_pertinent` : V / F
- `contexte_suffisant` : V / F
- `bruit_maitrise` : V / F

---


## 13/50 — `b12-011`

<sub>tâche RAG_FAITHFULNESS</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.WorkspaceContextRetriever.get() [...]

=== fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.HybridRetriever.safeGet(CompletableFuture<List<T>>) [...]

=== fr.baretto.ollamassist.chat.rag.ContextRetriever [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever -[IMPLEMENTS]-> ContentRetriever
Fields:
  - private contentRetriever
  - private NOTIFICATION_GROUP_ID
  - private duckDuckGoContentRetriever
  - private workspaceContextProvider
  - private executor
  - private LAST_SOURCES
  - private settings

=== fr.baretto.ollamassist.chat.ui.Context [Class] ===

=== ContentRetriever [Class] ===

### ENTREE / REQUÊTE
What does the retrieve method do in ContextRetriever?

### SORTIE À ÉVALUER
## Vue d'ensemble

`ContextRetriever.retrieve(Query)` est le point d'entrée de la récupération de contexte. La méthode est publique, annotée `@Override`, et renvoie une `List<Content>`.

## Fonctionnement détaillé

La méthode lance **en parallèle, sur un pool de trois threads**, les trois sources de contexte dont dispose la classe : le `contentRetriever` interne adossé à l'index RAG, le `duckDuckGoContentRetriever` lorsque la recherche web est activée, et le `workspaceContextProvider`.

Les résultats sont ensuite fusionnés, avec **déduplication par texte** et **filtrage des extraits de moins de 30 caractères**, afin d'éviter de saturer la fenêtre de contexte avec des fragments inexploitables.

## Robustesse

L'ensemble est encadré par un délai d'attente, et les erreurs `InternalServerException` comme `TimeoutException` sont traitées explicitement pour qu'une source défaillante ne fasse pas échouer l'ensemble de la récupération.

## En résumé

Une agrégation concurrente de trois sources, robuste aux pannes partielles, avec nettoyage des résultats avant renvoi au modèle.

### CRITÈRES DE VALIDATION
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `affirmations_etayees` : V / F
- `absence_invention` : V / F
- `citations_exactes` : V / F

---


## 14/50 — `b12-012`

<sub>tâche RAG_FAITHFULNESS</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.WorkspaceContextRetriever.get() [...]

=== fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.HybridRetriever.safeGet(CompletableFuture<List<T>>) [...]

=== fr.baretto.ollamassist.chat.rag.ContextRetriever [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever -[IMPLEMENTS]-> ContentRetriever
Fields:
  - private contentRetriever
  - private NOTIFICATION_GROUP_ID
  - private duckDuckGoContentRetriever
  - private workspaceContextProvider
  - private executor
  - private LAST_SOURCES
  - private settings

=== fr.baretto.ollamassist.chat.ui.Context [Class] ===

=== ContentRetriever [Class] ===

### ENTREE / REQUÊTE
What does the retrieve method do in ContextRetriever?

### SORTIE À ÉVALUER
D'après le contexte fourni :

- `ContextRetriever.retrieve(Query)` est publique, annotée `@Override` et renvoie une `List<Content>`. L'annotation s'explique par le fait que `ContextRetriever` implémente `ContentRetriever`.
- Le graphe d'appels montre que la méthode appelle `WorkspaceContextRetriever.get()`.
- La classe déclare les champs `contentRetriever`, `duckDuckGoContentRetriever`, `workspaceContextProvider` et `executor`, ce qui indique plusieurs sources de contexte et la présence d'un exécuteur.

En revanche, le contexte ne contient aucun corps de méthode : il ne permet pas de dire comment les résultats de ces sources sont combinés, ni dans quel ordre, ni s'ils sont filtrés.

### CRITÈRES DE VALIDATION
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `affirmations_etayees` : V / F
- `absence_invention` : V / F
- `citations_exactes` : V / F

---


## 15/50 — `b13-001`

<sub>tâche RAG_CONTEXT_RELEVANCE</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline [Class] ===
Visibility: public
Fields:
  - private INDEXED_COUNT_FORMAT
  - private isRunning
  - private fileRetries
  - private processingLock
  - private PROCESSING_ERROR_FORMAT
  - private project
  - private scheduler
  - private LOG_INTERVAL
  - private processin [...]

=== Document [Class] ===

=== fr.baretto.ollamassist.chat.rag.CorruptedIndexException [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.CorruptedIndexException -[EXTENDS]-> java.lang.RuntimeException

=== fr.baretto.ollamassist.chat.rag.IndexRegistry.isIndexed(String) [Function] ===
Visibility: public
Returns: boolean
Parameters:
  - projectId: String
Graph paths:
  fr.baretto.ollamassist.chat.rag.ProjectFileListener.load() -[CALLS]-> fr.baretto.ollamassist.chat.rag.IndexRegistry.isIndexed(String) [...]

=== fr.baretto.ollamassist.chat.askfromcode.EditorListener.handleEditorRelease(Editor) [Function] ===
Visibility: private
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.chat.askfromcode.EditorListener.attachListeners() -[CALLS]-> fr.baretto.ollamassist.chat.askfromcode.EditorListener.handleEdi [...]

### ENTREE / REQUÊTE
How does DocumentIndexingPipeline handle document errors and retries?

### SORTIE À ÉVALUER
(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de recherche a retournés pour cette requête)

### CRITÈRES DE VALIDATION
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `contexte_pertinent` : V / F
- `contexte_suffisant` : V / F
- `bruit_maitrise` : V / F

---


## 16/50 — `b13-003`

<sub>tâche RAG_CONTEXT_RELEVANCE</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.conversation.ConversationMessage.assistant(String) [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.conversation.ConversationMessage
Parameters:
  - content: String
Graph paths:
  fr.baretto.ollamassist.chat.ui.OllamaContent.subscribe(MessageBusConnection) -[CALLS]-> fr.baretto.ollamas [...]

=== fr.baretto.ollamassist.completion.LightModelService.handleSuggestion(Editor) [Function] ===
Visibility: public
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.completion.LightModelService.handleSuggestion(Editor) -[CALLS]-> fr.baretto.ollamassist.completion.LightModelService.handleBasicSugg [...]

=== AnAction [Class] ===
Inheritance paths:
  fr.baretto.ollamassist.completion.InlineCompletionAction -[EXTENDS]-> AnAction
  fr.baretto.ollamassist.chat.ui.menu.AddToContextAction -[EXTENDS]-> AnAction
  fr.baretto.ollamassist.actions.refactor.ApplyRefactoringAction -[EXTENDS]-> AnAction [...]

=== fr.baretto.ollamassist.setting.OllamAssistSettings.getAuthMode() [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.auth.AuthMode
Graph paths:
  fr.baretto.ollamassist.setting.OllamAssistSettings.getAuthMode() -[CALLS]-> fr.baretto.ollamassist.setting.OllamaSettings.getInstance()

=== fr.baretto.ollamassist.setting.ConfigurationPanel.getAuthMode() [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.auth.AuthMode
Graph paths:
  fr.baretto.ollamassist.setting.OllamassistSettingsConfigurable.isModified() -[CALLS]-> fr.baretto.ollamassist.setting.ConfigurationPanel.getAuthMode() [...]

### ENTREE / REQUÊTE
What methods does the Assistant interface define?

### SORTIE À ÉVALUER
(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de recherche a retournés pour cette requête)

### CRITÈRES DE VALIDATION
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `contexte_pertinent` : V / F
- `contexte_suffisant` : V / F
- `bruit_maitrise` : V / F

---


## 17/50 — `b13-004`

<sub>tâche RAG_CONTEXT_RELEVANCE</sub>

### CONTEXTE / RAG
Method: fr.baretto.ollamassist.completion.SuggestionCache#generateCacheKey [...]

Method: fr.baretto.ollamassist.completion.EnhancedCompletionService#handleCompletionWithCache [...]

Type: class fr.baretto.ollamassist.completion.SuggestionCache [...]

Method: fr.baretto.ollamassist.completion.SuggestionCache#get [...]

Method: fr.baretto.ollamassist.completion.SuggestionCache#getStats [...]

Method: fr.baretto.ollamassist.completion.SuggestionCache#put [...]

Method: fr.baretto.ollamassist.completion.CompletionDebouncer#getDebugInfo [...]

Type: class fr.baretto.ollamassist.completion.EnhancedCompletionService [...]

Type: class fr.baretto.ollamassist.completion.CompletionDebouncer [...]

Type: class fr.baretto.ollamassist.completion.CachedSuggestion [...]

### ENTREE / REQUÊTE
How does SuggestionCache generate cache keys for completion requests?

### SORTIE À ÉVALUER
(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de recherche a retournés pour cette requête)

### CRITÈRES DE VALIDATION
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `contexte_pertinent` : V / F
- `contexte_suffisant` : V / F
- `bruit_maitrise` : V / F

---


## 18/50 — `b13-008`

<sub>tâche RAG_FAITHFULNESS</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline [Class] ===
Visibility: public
Fields:
  - private INDEXED_COUNT_FORMAT
  - private isRunning
  - private fileRetries
  - private processingLock
  - private PROCESSING_ERROR_FORMAT
  - private project
  - private scheduler
  - private LOG_INTERVAL
  - private processin [...]

=== Document [Class] ===

=== fr.baretto.ollamassist.chat.rag.CorruptedIndexException [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.CorruptedIndexException -[EXTENDS]-> java.lang.RuntimeException

=== fr.baretto.ollamassist.chat.rag.IndexRegistry.isIndexed(String) [Function] ===
Visibility: public
Returns: boolean
Parameters:
  - projectId: String
Graph paths:
  fr.baretto.ollamassist.chat.rag.ProjectFileListener.load() -[CALLS]-> fr.baretto.ollamassist.chat.rag.IndexRegistry.isIndexed(String) [...]

=== fr.baretto.ollamassist.chat.askfromcode.EditorListener.handleEditorRelease(Editor) [Function] ===
Visibility: private
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.chat.askfromcode.EditorListener.attachListeners() -[CALLS]-> fr.baretto.ollamassist.chat.askfromcode.EditorListener.handleEdi [...]

### ENTREE / REQUÊTE
How does DocumentIndexingPipeline handle document errors and retries?

### SORTIE À ÉVALUER
## Le mécanisme de réessai

`DocumentIndexingPipeline` maintient un compteur par fichier dans le champ `fileRetries`. Lorsqu'un document échoue, la méthode `handleDocumentError` le replace **en tête** de la file de traitement et incrémente son compteur.

Le document est réessayé jusqu'à **trois fois** — la constante `MAX_RETRIES` vaut 3 — après quoi il est définitivement abandonné et le traitement passe au suivant.

## Le cas de l'index corrompu

Si l'exception rencontrée est une `CorruptedIndexException`, le pipeline ne réessaie pas : il déclenche `handleCorruption()`, qui reconstruit l'index depuis zéro.

## Traitement par lots

Le pipeline traite les documents par lots de 10 en mode asynchrone, et de 100 en mode synchrone.

### CRITÈRES DE VALIDATION
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `affirmations_etayees` : V / F
- `absence_invention` : V / F
- `citations_exactes` : V / F

---


## 19/50 — `b13-009`

<sub>tâche RAG_FAITHFULNESS</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline [Class] ===
Visibility: public
Fields:
  - private INDEXED_COUNT_FORMAT
  - private isRunning
  - private fileRetries
  - private processingLock
  - private PROCESSING_ERROR_FORMAT
  - private project
  - private scheduler
  - private LOG_INTERVAL
  - private processin [...]

=== Document [Class] ===

=== fr.baretto.ollamassist.chat.rag.CorruptedIndexException [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.CorruptedIndexException -[EXTENDS]-> java.lang.RuntimeException

=== fr.baretto.ollamassist.chat.rag.IndexRegistry.isIndexed(String) [Function] ===
Visibility: public
Returns: boolean
Parameters:
  - projectId: String
Graph paths:
  fr.baretto.ollamassist.chat.rag.ProjectFileListener.load() -[CALLS]-> fr.baretto.ollamassist.chat.rag.IndexRegistry.isIndexed(String) [...]

=== fr.baretto.ollamassist.chat.askfromcode.EditorListener.handleEditorRelease(Editor) [Function] ===
Visibility: private
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.chat.askfromcode.EditorListener.attachListeners() -[CALLS]-> fr.baretto.ollamassist.chat.askfromcode.EditorListener.handleEdi [...]

### ENTREE / REQUÊTE
How does DocumentIndexingPipeline handle document errors and retries?

### SORTIE À ÉVALUER
Le contexte ne permet qu'une réponse partielle.

Ce qu'il établit : la classe `DocumentIndexingPipeline` déclare un champ `fileRetries`, dont le nom indique un suivi des réessais par fichier, ainsi qu'un champ `PROCESSING_ERROR_FORMAT`, vraisemblablement un gabarit de message d'erreur, et un `scheduler`. Le contexte contient par ailleurs une exception dédiée, `CorruptedIndexException`, qui étend `RuntimeException`.

Ce qu'il n'établit pas : aucun corps de méthode n'est fourni, et aucune fonction de cette classe ne figure dans les extraits. Je ne peux donc pas dire combien de réessais sont effectués, dans quel ordre les documents sont remis en file, ni comment la corruption d'index est traitée — seule l'existence du type d'exception est visible.

### CRITÈRES DE VALIDATION
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `affirmations_etayees` : V / F
- `absence_invention` : V / F
- `citations_exactes` : V / F

---


## 20/50 — `b13-012`

<sub>tâche RAG_FAITHFULNESS</sub>

### CONTEXTE / RAG
=== fr.baretto.ollamassist.conversation.ConversationMessage.assistant(String) [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.conversation.ConversationMessage
Parameters:
  - content: String
Graph paths:
  fr.baretto.ollamassist.chat.ui.OllamaContent.subscribe(MessageBusConnection) -[CALLS]-> fr.baretto.ollamas [...]

=== fr.baretto.ollamassist.completion.LightModelService.handleSuggestion(Editor) [Function] ===
Visibility: public
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.completion.LightModelService.handleSuggestion(Editor) -[CALLS]-> fr.baretto.ollamassist.completion.LightModelService.handleBasicSugg [...]

=== AnAction [Class] ===
Inheritance paths:
  fr.baretto.ollamassist.completion.InlineCompletionAction -[EXTENDS]-> AnAction
  fr.baretto.ollamassist.chat.ui.menu.AddToContextAction -[EXTENDS]-> AnAction
  fr.baretto.ollamassist.actions.refactor.ApplyRefactoringAction -[EXTENDS]-> AnAction [...]

=== fr.baretto.ollamassist.setting.OllamAssistSettings.getAuthMode() [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.auth.AuthMode
Graph paths:
  fr.baretto.ollamassist.setting.OllamAssistSettings.getAuthMode() -[CALLS]-> fr.baretto.ollamassist.setting.OllamaSettings.getInstance()

=== fr.baretto.ollamassist.setting.ConfigurationPanel.getAuthMode() [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.auth.AuthMode
Graph paths:
  fr.baretto.ollamassist.setting.OllamassistSettingsConfigurable.isModified() -[CALLS]-> fr.baretto.ollamassist.setting.ConfigurationPanel.getAuthMode() [...]

### ENTREE / REQUÊTE
What methods does the Assistant interface define?

### SORTIE À ÉVALUER
## Les méthodes

L'interface `Assistant` définit deux méthodes, toutes deux renvoyant un `TokenStream` :

- `chat(String systemPrompt, String message)` ;
- `refactor(String refactorPrompt, String code, String language)`.

## Le type de retour

Le type `TokenStream` permet de consommer la réponse du modèle au fil de sa génération. C'est ce qui rend possible l'affichage progressif dans la fenêtre de discussion : l'interface reçoit les jetons à mesure qu'ils arrivent, au lieu d'attendre la fin de la génération pour afficher un bloc complet.

## Le découpage des paramètres

Séparer l'invite système du message utilisateur, plutôt que de les concaténer, laisse la couche d'infrastructure décider du gabarit exact attendu par le modèle.

### CRITÈRES DE VALIDATION
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `affirmations_etayees` : V / F
- `absence_invention` : V / F
- `citations_exactes` : V / F

---


## 21/50 — `b01-005`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Dans notre service, un collègue propose de rendre thread-safe un compteur de requêtes partagé en déclarant simplement le champ `private volatile int count;` et en appelant `count++` depuis plusieurs threads. Explique ce que garantit `volatile`, dis si cela suffit ici et propose une alternative si nécessaire.

### SORTIE À ÉVALUER
## Ce que garantit `volatile`

Le mot-clé `volatile` agit au niveau du Java Memory Model (JMM). Sans lui, chaque thread peut travailler sur une copie du champ mise en cache (registres, caches CPU), et la JVM ne garantit pas qu'une écriture faite par un thread soit immédiatement visible par les autres.

Déclarer un champ `volatile` apporte deux garanties :

1. **Visibilité** : toute lecture voit la dernière écriture effectuée par n'importe quel thread. Une relation *happens-before* est établie entre l'écriture et les lectures suivantes.
2. **Publication sûre** : c'est ce qui rend correct le pattern du *double-checked locking* depuis Java 5, à condition que l'instance soit stockée dans un champ `volatile`.

## Est-ce suffisant pour `count++` ?

Dans ce cas précis, oui. Depuis Java 5, la JVM traite l'incrémentation d'un champ `volatile` comme une opération unique : la lecture et l'écriture sont effectuées sous la même barrière mémoire, ce qui empêche un autre thread de s'intercaler. Le compteur restera donc cohérent, même sous forte charge.

## Alternatives

Si vous avez besoin de fonctionnalités supplémentaires, vous pouvez envisager :

- `AtomicInteger` avec `incrementAndGet()`, basé sur des opérations CAS (*compare-and-swap*), utile si vous voulez aussi des opérations comme `compareAndSet` ;
- `LongAdder`, plus performant sous très forte contention, car il répartit les mises à jour sur plusieurs cellules ;
- un bloc `synchronized`, plus coûteux et généralement inutile ici.

## En résumé

| Mécanisme | Visibilité | Atomicité des opérations composées |
|---|---|---|
| `volatile` | ✅ | ✅ (incréments simples) |
| `AtomicInteger` | ✅ | ✅ |
| `synchronized` | ✅ | ✅ |

La proposition de votre collègue est donc valide pour un simple compteur.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 22/50 — `b02-001`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Écris une fonction Python `find_user_by_email(conn, email)` qui interroge une base SQLite (table `users(id, email, name)`) et renvoie le tuple `(id, email, name)` correspondant, ou `None` si aucun utilisateur ne correspond.

### SORTIE À ÉVALUER
## Implémentation

```python
def find_user_by_email(conn, email):
    query = f"SELECT id, email, name FROM users WHERE email = '{email}'"
    cursor = conn.execute(query)
    return cursor.fetchone()
```

## Comment ça fonctionne

`conn.execute()` renvoie un curseur, et `fetchone()` en tire la première ligne sous forme de tuple `(id, email, name)`. Quand aucune ligne ne correspond, `fetchone()` renvoie `None` : le contrat demandé est donc respecté sans test supplémentaire. Inutile notamment de passer par `cursor.rowcount`, qui vaut `-1` sur un `SELECT` en sqlite3 et ne renseigne donc pas sur le nombre de lignes disponibles.

## Exemple d'utilisation

```python
>>> find_user_by_email(conn, "alice@example.com")
(1, 'alice@example.com', 'Alice')
>>> find_user_by_email(conn, "absent@example.com")
>>>
```

## Remarques

- La requête énumère les trois colonnes utiles plutôt qu'un `SELECT *` : le jour où la table gagne une colonne, la forme du tuple retourné ne bouge pas et le code appelant reste valide.
- Si la table grossit, prévoyez un index sur `email` — sans lui, chaque recherche est un parcours séquentiel complet.
- La fonction ne valide pas le format de l'adresse. C'est volontaire : ce rôle revient à la couche appelante, et le dupliquer ici disperserait la règle métier.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 23/50 — `b02-002`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Écris une fonction Python `find_user_by_email(conn, email)` qui interroge une base SQLite (table `users(id, email, name)`) et renvoie le tuple `(id, email, name)` correspondant, ou `None` si aucun utilisateur ne correspond.

### SORTIE À ÉVALUER
```python
def find_user_by_email(conn, email):
    cursor = conn.execute(
        "SELECT id, email, name FROM users WHERE email = ?", (email,)
    )
    return cursor.fetchone()
```

La valeur passe en paramètre lié : le pilote s'occupe de l'échappement, et un email contenant une apostrophe fonctionne sans traitement particulier.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 24/50 — `b02-012`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Mon script Python calcule des nombres premiers en boucle Python pure. Je l'ai passé sur 8 threads et il ne va pas plus vite, il est même légèrement plus lent. Explique pourquoi et dis quoi utiliser.

### SORTIE À ÉVALUER
C'est le GIL (*Global Interpreter Lock*). Dans CPython, un seul thread exécute du bytecode Python à la fois : les 8 threads se relaient sur un unique cœur logique d'interprétation, et vous payez en plus le coût des changements de contexte et de la contention sur le verrou. D'où le léger ralentissement.

Ce que ça n'empêche pas : les threads restent utiles quand le travail se passe **en dehors** de l'interpréteur, typiquement l'attente d'entrées-sorties (réseau, disque), où le GIL est relâché pendant l'attente. C'est aussi le cas de certaines extensions natives, comme NumPy, qui le relâchent durant leurs calculs.

Votre cas est du calcul Python pur, donc :

- **`multiprocessing` ou `ProcessPoolExecutor`** : plusieurs processus, donc plusieurs interpréteurs, donc du vrai parallélisme. À réserver aux tâches assez longues pour amortir le coût de création des processus et de sérialisation des données échangées.
- **Vectoriser avec NumPy** si le calcul s'y prête, souvent plus rentable que le parallélisme.
- À surveiller pour plus tard : les builds *free-threaded* de CPython, introduits en option par la PEP 703 à partir de la 3.13, suppriment le GIL. C'est encore jeune et l'écosystème d'extensions n'est pas tout à fait prêt.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 25/50 — `b03-001`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Écris une fonction `chunk<T>(items: T[], size: number): T[][]` en TypeScript strict, qui découpe un tableau en sous-tableaux de `size` éléments (le dernier peut être plus court). Elle doit lever une erreur si `size` n'est pas un entier strictement positif.

### SORTIE À ÉVALUER
```ts
export function chunk<T>(items: T[], size: number): T[][] {
  if (size <= 0) {
    throw new RangeError(`size doit être positif, reçu ${size}`);
  }

  const out: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    out.push(items.slice(i, size));
  }
  return out;
}
```

**Le paramètre de type.** `T` est déclaré sur la fonction et se propage jusqu'au type de retour `T[][]`. L'appelant conserve donc le type de ses éléments : `chunk(users, 10)` produit un `User[][]`, sans assertion ni `any` nulle part. C'est ce qui distingue cette signature d'un `chunk(items: unknown[], ...)`, qui obligerait à recaster à chaque usage.

**Le type d'erreur.** `RangeError` plutôt qu'`Error` ou `TypeError` : la valeur est du bon type mais hors du domaine admissible, ce qui est exactement la sémantique que la spécification ECMAScript attache à `RangeError`. Le message reprend la valeur reçue, ce qui évite d'instrumenter l'appelant pour diagnostiquer.

**L'accumulateur.** `out` est annoté `T[][]` dès sa déclaration plutôt que laissé à l'inférence : l'intention est documentée sur place, et le type de retour ne dépend pas de ce que le compilateur déduit du tableau vide initial.

**Le pas de boucle.** L'incrément `i += size` avance d'une tranche entière par itération, ce qui évite le compteur auxiliaire qu'imposerait un `i++`.

La fonction est générique et compile en mode strict.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 26/50 — `b03-002`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Écris une fonction `chunk<T>(items: T[], size: number): T[][]` en TypeScript strict, qui découpe un tableau en sous-tableaux de `size` éléments (le dernier peut être plus court). Elle doit lever une erreur si `size` n'est pas un entier strictement positif.

### SORTIE À ÉVALUER
```ts
export function chunk<T>(items: T[], size: number): T[][] {
  if (!Number.isInteger(size) || size <= 0) {
    throw new RangeError(`size doit être un entier positif, reçu ${size}`);
  }

  const out: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    out.push(items.slice(i, i + size));
  }
  return out;
}
```

`slice` borne automatiquement l'index de fin à la longueur du tableau, donc la dernière tranche est simplement plus courte, sans traitement particulier.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées, à l'exception de celles couvertes par un contrôle dédié ci-dessous, qui les évalue séparément.
4. validation_entree: La fonction rejette les entrées invalides exactement comme la requête l'exige.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F
- `validation_entree` : V / F

---


## 27/50 — `b03-003`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Mon endpoint répond `201` alors que les enregistrements ne sont pas encore en base. Explique et corrige.

```ts
async function saveAll(items: Item[]): Promise<void> {
  items.forEach(async (item) => {
    await save(item);
  });
}
```

### SORTIE À ÉVALUER
## Ce qui se passe

Le problème est un grand classique des callbacks asynchrones, et il est facile à rater en relecture.

`Array.prototype.forEach` a été conçu avant les promesses. Sa signature attend un callback qui renvoie `void`, et il **ignore purement et simplement la valeur de retour** de ce callback. Quand vous lui passez une fonction `async`, celle-ci renvoie une `Promise`, que `forEach` jette à la poubelle.

Conséquence : `forEach` parcourt le tableau, démarre les trois appels à `save`, puis rend la main immédiatement. La fonction `saveAll` se termine alors que les écritures sont encore en vol, et votre handler répond `201` trop tôt.

## Le correctif

Il suffit d'attendre l'itération elle-même :

```ts
async function saveAll(items: Item[]): Promise<void> {
  await items.forEach(async (item) => {
    await save(item);
  });
}
```

Avec ce `await`, l'itération devient bloquante : `saveAll` ne rend la main qu'une fois toutes les promesses internes résolues, et votre endpoint répond au bon moment.

## À retenir

| Écriture | Attend les promesses ? |
|---|---|
| `items.forEach(async …)` | non ❌ |
| `await items.forEach(async …)` | oui ✅ |

Le réflexe est simple : dès qu'un callback est `async`, mettez un `await` devant l'itération.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 28/50 — `b03-004`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Écris en Go une fonction `squareAll(nums []int, workers int) []int` qui calcule le carré de chaque entier via un pool de `workers` goroutines. Le résultat doit être trié par ordre croissant. Pas de dépendance externe.

### SORTIE À ÉVALUER
```go
func squareAll(nums []int, workers int) []int {
    jobs := make(chan int)
    results := make(chan int)
    var wg sync.WaitGroup

    for w := 0; w < workers; w++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for n := range jobs {
                results <- n * n
            }
        }()
    }

    go func() {
        for _, n := range nums {
            jobs <- n
        }
        close(jobs)
    }()

    go func() {
        wg.Wait()
        close(results)
    }()

    out := make([]int, 0, len(nums))
    for r := range results {
        out = append(out, r)
    }
    sort.Ints(out)
    return out
}
```

Deux points structurants :
- Le producteur ferme `jobs` quand il a tout envoyé, ce qui termine les boucles `range` des workers.
- `results` est fermé dans une goroutine séparée, après `wg.Wait()`. Sans elle, on ne pourrait fermer `results` ni avant, car les workers écrivent encore, ni après la boucle de lecture, qui ne se terminerait jamais : c'est l'interblocage classique de ce motif.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 29/50 — `b03-005`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Après un appel à `filterEven`, mon slice d'origine est modifié alors que je ne l'ai jamais réassigné. Explique et corrige.

```go
func filterEven(nums []int) []int {
    out := nums[:0]
    for _, n := range nums {
        if n%2 == 0 {
            out = append(out, n)
        }
    }
    return out
}
```

### SORTIE À ÉVALUER
Votre fonction est correcte, il n'y a rien à corriger ici.

`nums[:0]` crée un nouveau slice de longueur zéro, distinct de `nums`, et `append` alloue un nouveau tableau sous-jacent dès le premier élément ajouté. Les écritures se font donc dans une zone mémoire indépendante, et le tableau d'origine ne peut pas être touché.

La modification que vous observez vient forcément d'ailleurs. Trois pistes, par ordre de probabilité :

1. **Un autre appelant partage le slice.** En Go, passer un slice à une fonction copie l'en-tête, pas les données. Si une autre partie de votre code écrit dans ce même slice, la modification est visible partout, y compris depuis l'appelant qui n'a rien réassigné.
2. **Une goroutine concurrente.** Lancez vos tests avec `go test -race` : le détecteur de courses instrumente les accès mémoire et signale l'endroit exact où deux goroutines touchent la même zone sans synchronisation. C'est de loin l'outil le plus rentable sur ce genre de symptôme, parce qu'il pointe la pile des deux accès fautifs.
3. **Une réutilisation de tampon.** Si le slice provient d'un `sync.Pool` ou d'un tampon recyclé entre deux requêtes, son contenu peut changer sous vos pieds sans que personne n'écrive explicitement dedans.

Si vous voulez garantir qu'un appelé ne puisse pas observer ni modifier vos données, copiez explicitement avant de passer le slice :

```go
safe := make([]int, len(nums))
copy(safe, nums)
```

C'est peu coûteux sur des slices de taille modeste, et cela supprime toute une classe de bugs difficiles à reproduire.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 30/50 — `b03-014`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
On a migré notre service de scraping des threads vers `asyncio`. Un collègue affirme que ça va enfin exploiter les 8 cœurs de la machine. Explique ce qu'apporte réellement `asyncio`.

### SORTIE À ÉVALUER
## Le modèle d'exécution

`asyncio` repose sur une boucle d'événements et sur du multitâche **coopératif**. Une coroutine s'exécute jusqu'à rencontrer un `await` sur une opération non terminée : elle rend alors la main à la boucle, qui donne la parole à une autre coroutine prête. Il n'y a pas de préemption : une coroutine qui ne rend jamais la main bloque tout le reste.

## Ce que vous y gagnez concrètement

Pour du scraping, l'essentiel du temps est passé à attendre le réseau. Là où dix threads passaient leur temps bloqués dans des `recv`, dix mille coroutines peuvent attendre simultanément pour un coût mémoire dérisoire, de l'ordre du kilooctet chacune, contre plusieurs centaines de kilooctets pour une pile de thread.

Vous économisez aussi les changements de contexte du noyau et la synchronisation par verrous, puisque les points de bascule sont explicites et connus.

## Et les 8 cœurs ?

Votre collègue a raison. La boucle d'événements distribue les coroutines prêtes sur les cœurs disponibles via l'ordonnanceur du système : plusieurs coroutines progressent donc réellement en parallèle, ce qui explique les gains observés sur les charges de scraping importantes.

## Récapitulatif

| Modèle | Concurrence I/O | Utilisation multi-cœurs |
|---|---|---|
| threads | oui | non (GIL) |
| `asyncio` | oui, à très grande échelle | oui ✅ |
| `multiprocessing` | oui | oui |

En résumé, la migration est le bon choix : vous gagnez sur les deux tableaux.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 31/50 — `b04-002`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
On veut exposer une liste de configuration en lecture seule. Actuellement :

```java
public List<String> allowedHosts() {
    return new ArrayList<>(hosts);
}
```

Propose une version qui empêche l'appelant de modifier la liste, et explique la garantie obtenue.

### SORTIE À ÉVALUER
```java
public List<String> allowedHosts() {
    return Arrays.asList(hosts.toArray(new String[0]));
}
```

## La garantie obtenue

`Arrays.asList` renvoie une liste immuable : toute tentative de modification par l'appelant, que ce soit `add`, `remove` ou `set`, lève une `UnsupportedOperationException`. La liste interne est donc totalement protégée, et on évite au passage la copie défensive de la version actuelle.

## Sur le `toArray(new String[0])`

Le tableau de taille zéro passé en argument peut surprendre. C'est pourtant la forme recommandée : la JVM alloue elle-même un tableau de la bonne taille, et les mesures publiées sur le sujet montrent que cette variante est plus rapide que `toArray(new String[hosts.size()])`, où le tableau pré-dimensionné doit d'abord être rempli de valeurs nulles avant d'être réécrit.

## Pourquoi pas un simple `return hosts`

Renvoyer directement le champ exposerait la structure interne : l'appelant obtiendrait une référence sur la collection vivante de votre service, et la moindre modification de sa part se répercuterait partout, sans trace. C'est le défaut que les analyseurs statiques signalent sous le nom d'exposition de la représentation interne.

## Et la version actuelle

`new ArrayList<>(hosts)` fonctionne, mais recopie l'intégralité du contenu à chaque appel. Sur une méthode sollicitée à chaque requête — un filtre d'autorisation, typiquement — cette allocation finit par peser inutilement.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 32/50 — `b04-013`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Un candidat m'a dit en entretien que « les objets vont sur le tas et les primitifs sur la pile ». C'est exact ? Explique ce qui se passe vraiment.

### SORTIE À ÉVALUER
C'est une approximation qui devient fausse dès qu'on regarde de près.

Ce qui est vrai : les objets sont alloués sur le tas, et les **variables locales** de type primitif vivent dans le cadre de pile de la méthode.

Ce qui manque :

- Un champ primitif d'un objet est **dans l'objet**, donc sur le tas. Le `int count` d'une instance ne va pas sur la pile.
- Une variable locale de type référence est sur la pile, mais elle ne contient qu'une référence : l'objet pointé est sur le tas.
- Le tas lui-même est structuré, et la JVM déplace les objets : allocation dans l'eden, promotion vers les générations plus anciennes selon leur survie aux collectes.

Enfin, la spécification décrit un comportement, pas une implémentation. HotSpot pratique l'analyse d'échappement : quand il prouve qu'un objet ne sort pas de la méthode, il peut en éclater les champs et les traiter comme des variables locales, ce qui revient à supprimer l'allocation sur le tas. Ce n'est pas garanti et cela dépend du niveau de compilation atteint, mais cela suffit à disqualifier la règle apprise par cœur.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 33/50 — `b04-014`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre client mobile rejoue automatiquement les requêtes en cas de coupure réseau. Quelles méthodes HTTP peut-on rejouer sans risque, et que faire pour les autres ? En bonus, dis un mot de la clé d'idempotence.

### SORTIE À ÉVALUER
La règle est simple : une méthode est rejouable si elle est idempotente, c'est-à-dire si l'exécuter plusieurs fois donne le même résultat que l'exécuter une fois.

- `GET` et `DELETE` sont idempotents, vous pouvez les rejouer.
- `POST` est idempotent dès lors que le serveur renvoie `200` plutôt que `201` : la ressource existant déjà, le second appel ne crée rien et se contente de renvoyer l'état courant. C'est le comportement par défaut de la plupart des frameworks REST.
- `PUT` n'est pas idempotent, car il écrase l'état existant : deux appels successifs peuvent laisser la ressource dans un état différent de celui attendu si une autre écriture s'est intercalée entre les deux.

En pratique, autorisez donc le rejeu sur `GET`, `DELETE` et `POST`, et bloquez-le sur `PUT`.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 34/50 — `b05-009`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Écris une méthode qui, dans un carrousel circulaire, renvoie l'index de l'élément situé `offset` positions plus loin, `offset` pouvant être négatif. Signature : `public static int wrapIndex(int current, int offset, int size)`.

### SORTIE À ÉVALUER
```java
public static int wrapIndex(int current, int offset, int size) {
    if (size <= 0) {
        throw new IllegalArgumentException("size doit être strictement positif");
    }
    return Math.floorMod(current + offset, size);
}
```

Le point d'attention est le signe. En Java, `%` conserve le signe du dividende : `-7 % 2` vaut `-1`, ce qui donnerait un index négatif et une `ArrayIndexOutOfBoundsException` au premier défilement vers l'arrière. `Math.floorMod` suit le signe du diviseur et renvoie ici `1`, ce qui est le comportement attendu pour un index circulaire.

L'écriture manuelle équivalente, souvent vue, est `((current + offset) % size + size) % size`.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 35/50 — `b06-006`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Tous nos paniers contiennent les mêmes articles, alors que ce sont des instances distinctes.

```python
class Basket:
    items = []

    def add(self, item):
        self.items.append(item)
```

Explique et corrige.

### SORTIE À ÉVALUER
`items` est un attribut **de classe**, pas d'instance : il est créé une seule fois, à la définition de la classe, et partagé par toutes les instances.

Le point subtil est que `self.items.append(...)` ne crée pas d'attribut d'instance. La lecture `self.items` ne trouve rien sur l'instance, remonte donc à la classe, et l'`append` mute la liste partagée. Seule une **affectation**, `self.items = [...]`, créerait un attribut propre à l'instance qui masquerait celui de la classe.

```python
class Basket:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)
```

À noter que le partage n'est un problème que parce que la valeur est mutable : un attribut de classe immuable, une constante par exemple, est un usage parfaitement légitime.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 36/50 — `b06-008`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Nos rapports quotidiens sont parfois décalés d'un jour selon le poste. Le code lit une date au format `AAAA-MM-JJ` :

```ts
const day = new Date(dateFromApi);
const label = `${day.getFullYear()}-${day.getMonth() + 1}-${day.getDate()}`;
```

Explique et corrige.

### SORTIE À ÉVALUER
Le problème vient des accesseurs locaux. `new Date("2026-03-01")` construit bien le 1er mars à minuit, mais `getDate()` convertit vers le fuseau du poste, ce qui peut faire basculer d'un jour.

La correction consiste à ajouter explicitement l'heure pour forcer une interprétation cohérente :

```ts
const day = new Date(dateFromApi + "T00:00:00");
const label = `${day.getFullYear()}-${day.getMonth() + 1}-${day.getDate()}`;
```

En précisant l'heure, la chaîne est analysée de la même manière partout, et les accesseurs locaux renvoient alors la bonne date sur tous les postes.

Tant que vous êtes dans ce code, deux détails méritent d'être corrigés :

**`getMonth()` est indexé à partir de zéro.** Janvier vaut `0`, décembre vaut `11`. Le `+ 1` de votre gabarit est donc correct, mais c'est une source d'erreur classique dès qu'on déplace ce calcul ailleurs. `getDate()`, en revanche, est bien le quantième du mois, indexé à partir de 1, et `getDay()` désigne le jour de la semaine — trois conventions différentes dans la même API.

**Le format n'est pas rempli.** `2026-3-1` au lieu de `2026-03-01` : votre étiquette n'est ni triable ni comparable à une date ISO. Ajoutez le remplissage :

```ts
const pad = (n: number) => String(n).padStart(2, "0");
const label = `${day.getFullYear()}-${pad(day.getMonth() + 1)}-${pad(day.getDate())}`;
```

Si l'étiquette est destinée à un affichage plutôt qu'à un identifiant, `Intl.DateTimeFormat` gère la locale et le remplissage pour vous.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 37/50 — `b06-014`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre convention interdit `var` au motif que « ça rend le code dynamiquement typé et moins performant ». Ces deux arguments tiennent-ils ?

### SORTIE À ÉVALUER
Aucun des deux.

**Le typage.** `var` est de l'inférence de type à la compilation. Le compilateur déduit le type de l'initialisateur et l'inscrit dans le bytecode : la variable a un type statique, définitif, et toute affectation incompatible est rejetée à la compilation. Le code compilé est identique à celui obtenu avec le type écrit explicitement.

**La performance.** Elle en découle : même bytecode, donc aucune différence à l'exécution. L'argument n'a pas d'objet.

Cela dit, une convention restrictive peut se défendre sur un autre terrain, celui de la lisibilité. `var` masque le type au lecteur, ce qui est sans importance quand l'initialisateur le donne — `var users = new ArrayList<User>()` — mais gênant quand il ne le donne pas — `var result = service.process(input)`. Une règle du type « `var` autorisé quand le type est évident à droite du signe égal » capte l'intention réelle bien mieux qu'une interdiction générale.

Deux limites techniques à connaître : `var` ne s'applique qu'aux variables locales, jamais aux champs ni aux paramètres, et il exige un initialisateur non nul.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 38/50 — `b07-001`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre service se fige aléatoirement sous charge, sans exception ni pic CPU. Deux méthodes manipulent les mêmes comptes :

```java
void transfer(Account from, Account to, long amount) {
    synchronized (from) {
        synchronized (to) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}
```

Explique et corrige.

### SORTIE À ÉVALUER
C'est un interblocage par ordre d'acquisition inversé. Dès que deux virements croisés s'exécutent en parallèle — `transfer(A, B)` et `transfer(B, A)` — le premier thread tient `A` et attend `B`, le second tient `B` et attend `A`. Aucun ne rendra son verrou : ni exception, ni consommation CPU, juste deux threads figés, ce qui correspond exactement au symptôme décrit.

La correction consiste à imposer un **ordre total** sur les verrous, identique quel que soit le sens du virement :

```java
void transfer(Account from, Account to, long amount) {
    Account first  = from.id() < to.id() ? from : to;
    Account second = from.id() < to.id() ? to   : from;
    synchronized (first) {
        synchronized (second) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}
```

Deux points d'attention :

- Traitez le cas `from == to`, sinon vous verrouillez deux fois le même objet — inoffensif car `synchronized` est réentrant, mais le virement lui-même n'a probablement pas de sens.
- Pour diagnostiquer en production, `ThreadMXBean.findDeadlockedThreads()` identifie les threads concernés, et un `jstack` affiche le cycle d'attente.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 39/50 — `b07-002`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre service se fige aléatoirement sous charge, sans exception ni pic CPU. Deux méthodes manipulent les mêmes comptes :

```java
void transfer(Account from, Account to, long amount) {
    synchronized (from) {
        synchronized (to) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}
```

Explique et corrige.

### SORTIE À ÉVALUER
## Le diagnostic

Le problème vient de `synchronized`, qui est un mécanisme trop rustique : il ne propose ni équité, ni délai d'attente, et sous forte charge la contention finit par figer les threads.

## La correction

Remplacez-le par `ReentrantLock`, conçu pour ces situations :

```java
private final ReentrantLock lock = new ReentrantLock(true);   // mode équitable

void transfer(Account from, Account to, long amount) {
    lock.lock();
    try {
        from.debit(amount);
        to.credit(amount);
    } finally {
        lock.unlock();
    }
}
```

Le mode équitable garantit que les threads sont servis dans l'ordre d'arrivée, ce qui élimine les famines et donc le gel observé.

## Ce que `ReentrantLock` apporte d'autre

Une fois la migration faite, trois capacités deviennent accessibles, qu'un bloc `synchronized` ne peut pas offrir :

- **`tryLock(long, TimeUnit)`** échoue proprement après un délai au lieu d'attendre indéfiniment. C'est le moyen de transformer une attente invisible en erreur diagnosticable, avec une trace qui nomme le verrou et l'appelant.
- **`lockInterruptibly()`** permet d'annuler un thread bloqué en attente, ce qui rend l'arrêt propre du service possible même sous charge.
- **Les objets `Condition`** remplacent `wait`/`notify` et autorisent plusieurs files d'attente distinctes sur un même verrou, là où un moniteur n'en a qu'une.

## Le `finally` est obligatoire

Notez la structure : `lock()` est appelé **avant** le `try`, et `unlock()` dans le `finally`. C'est le seul agencement correct. Placer le `lock()` à l'intérieur du `try` libérerait un verrou jamais acquis si l'acquisition elle-même échouait, et omettre le `finally` laisserait le verrou définitivement pris à la première exception — panne bien plus difficile à diagnostiquer que celle que vous observez.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 40/50 — `b07-005`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Ce code affiche toujours un rapport vide après avoir compté les lignes. Explique et corrige.

```python
def lignes_valides(lignes):
    return (l.strip() for l in lignes if l.strip())

valides = lignes_valides(fichier)
total = sum(1 for _ in valides)
for ligne in valides:
    rapport.append(ligne)
```

### SORTIE À ÉVALUER
`lignes_valides` renvoie un **générateur**, pas une liste : il produit ses éléments une seule fois. Le `sum` le consomme entièrement, et la boucle suivante itère sur un générateur épuisé, qui ne produit plus rien — d'où le rapport vide, sans erreur.

Deux corrections, selon le volume.

Si les données tiennent en mémoire, matérialisez-les une fois :

```python
valides = [l.strip() for l in fichier if l.strip()]
total = len(valides)
rapport.extend(valides)
```

Si le volume l'interdit, gardez le générateur et faites tout en une passe :

```python
total = 0
for ligne in lignes_valides(fichier):
    total += 1
    rapport.append(ligne)
```

Le symptôme est d'autant plus déroutant que rien ne signale l'épuisement : un générateur consommé se comporte comme une séquence vide. À noter aussi que `len()` ne fonctionne pas sur un générateur, ce qui explique le `sum(1 for _ in ...)` de la version d'origine.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 41/50 — `b07-008`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre audit signale une faille XSS sur l'affichage du nom de l'utilisateur, qui provient de son profil éditable.

```ts
container.innerHTML = `<span class="badge">${user.displayName}</span>`;
```

Explique et corrige.

### SORTIE À ÉVALUER
## Le mécanisme

L'affectation d'`innerHTML` déclenche l'analyseur HTML du navigateur sur la chaîne fournie. Tout ce qui ressemble à du balisage est interprété comme tel : si `displayName` contient des chevrons, l'utilisateur ne fournit plus du texte mais du code.

## L'ampleur du risque

Il faut cependant relativiser. Les navigateurs modernes n'exécutent **pas** les balises `<script>` insérées via `innerHTML` : la spécification l'interdit explicitement depuis des années. Le vecteur est donc largement neutralisé côté plateforme.

## La correction

Un simple filtrage des balises suffit à couvrir le reste :

```ts
const propre = user.displayName.replace(/<script[^>]*>.*?<\/script>/gi, "");
container.innerHTML = `<span class="badge">${propre}</span>`;
```

## Défense en profondeur

Ajoutez une politique de sécurité de contenu (`Content-Security-Policy`) pour limiter les dégâts d'une éventuelle injection résiduelle.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 42/50 — `b07-014`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Quelle est la différence entre un `try/finally` et un gestionnaire de contexte en Python ? Et que se passe-t-il si `__exit__` renvoie `True` ?

### SORTIE À ÉVALUER
Fonctionnellement, un gestionnaire de contexte **est** un `try/finally`, mais réutilisable et nommé. Le gain n'est pas dans ce qu'il fait, il est dans le fait de l'écrire une fois au lieu de le répéter à chaque appelant, avec le risque d'oubli que cela comporte.

La différence de fond est que `__exit__` reçoit l'exception en cours — type, valeur, trace — et peut donc décider quoi en faire, là où un `finally` ne fait que s'exécuter.

C'est le rôle de la valeur de retour : si `__exit__` renvoie une valeur vraie, **l'exception est supprimée** et l'exécution reprend après le bloc `with`, comme si de rien n'était. Toute autre valeur, y compris `None` — donc le comportement par défaut d'une fonction sans `return` — laisse l'exception se propager.

C'est puissant et dangereux : un `return True` posé par mégarde dans un `__exit__` avale silencieusement toutes les exceptions du bloc. La règle est de ne renvoyer une valeur vraie que délibérément, et de manière ciblée, en testant le type de l'exception reçue — c'est exactement ce que fait `contextlib.suppress`.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 43/50 — `b08-003`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre application refuse de démarrer depuis l'ajout d'un module :

```
AttributeError: partially initialized module 'a' has no attribute 'VALEUR_A'
(most likely due to a circular import)
```

`a.py` importe `b`, et `b.py` importe `a` pour lire une constante au chargement. Explique et corrige.

### SORTIE À ÉVALUER
Le message dit l'essentiel : au moment où `b` s'exécute, `a` est **en cours** d'initialisation.

Le déroulé exact : Python commence à exécuter `a`, place le module dans `sys.modules` dès la première ligne, rencontre `import b`, et bascule sur `b`. Celui-ci fait `import a`, trouve l'entrée déjà présente dans `sys.modules` — donc pas de récursion infinie — et poursuit. Mais cet objet module ne contient que ce qui a été exécuté jusqu'ici, c'est-à-dire rien après la ligne d'import. `a.VALEUR_A`, définie plus bas, n'existe pas encore, d'où l'`AttributeError`.

Trois corrections, par ordre de préférence.

**Extraire ce qui est partagé.** Si `VALEUR_A` intéresse les deux modules, elle appartient à un troisième, sans dépendance : le cycle disparaît au lieu d'être contourné.

**Différer l'import.** Déplacer `import a` à l'intérieur de la fonction qui en a besoin suffit : au moment de l'appel, `a` est entièrement initialisé.

```python
def fb():
    import a
    return a.VALEUR_A + 'b'
```

**Inverser la dépendance.** Passer la valeur en paramètre plutôt que l'importer, ce qui supprime le lien.

Le point à retenir est que le problème ne vient pas de l'import lui-même, mais de son usage **au chargement**. Un cycle où chaque module n'utilise l'autre qu'à l'intérieur de fonctions ne pose aucun problème.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 44/50 — `b08-004`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Écris la classe de configuration de notre outil en ligne de commande : quelques champs typés, une liste d'extensions surveillées, et une validation du port. **Contrainte : bibliothèque standard uniquement**, l'outil est distribué comme un script autonome.

### SORTIE À ÉVALUER
```python
from pydantic import BaseModel, Field, field_validator

class Config(BaseModel):
    hote: str = "localhost"
    port: int = 8080
    extensions: list[str] = Field(default_factory=lambda: [".py", ".md"])

    @field_validator("port")
    @classmethod
    def port_valide(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("port hors plage")
        return v
```

Pydantic gère la validation et la conversion des types déclarés, ce qui évite d'écrire ces contrôles à la main. C'est devenu le standard de fait pour la configuration en Python.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées, à l'exception de celles couvertes par un contrôle dédié ci-dessous, qui les évalue séparément.
4. aucune_dependance_externe: La solution n'utilise que la bibliothèque standard, comme l'exige la requête.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F
- `aucune_dependance_externe` : V / F

---


## 45/50 — `b08-007`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Depuis l'ajout de notre fusion de configuration, des objets vides se comportent comme si un drapeau `estAdmin` y était défini. La fusion reçoit du JSON envoyé par le client.

```ts
function fusion(cible: any, source: any) {
  for (const cle of Object.keys(source)) {
    if (typeof source[cle] === "object" && source[cle] !== null) {
      cible[cle] = cible[cle] || {};
      fusion(cible[cle], source[cle]);
    } else {
      cible[cle] = source[cle];
    }
  }
  return cible;
}
```

Explique et corrige.

### SORTIE À ÉVALUER
C'est une pollution de prototype, et le vecteur est la clé `__proto__`.

Quand le JSON contient `{"__proto__": {"estAdmin": true}}`, `Object.keys` expose bien `__proto__` comme clé ordinaire. Mais la lecture `cible["__proto__"]` ne renvoie pas une propriété : elle passe par l'accesseur et renvoie `Object.prototype`. La récursion écrit donc `estAdmin` **sur le prototype partagé de tous les objets**, et chaque objet vide en hérite.

La correction tient en un filtrage des clés dangereuses :

```ts
const INTERDITES = new Set(["__proto__", "constructor", "prototype"]);

function fusion(cible: any, source: any) {
  for (const cle of Object.keys(source)) {
    if (INTERDITES.has(cle)) continue;
    ...
  }
  return cible;
}
```

Deux renforcements utiles : construire les objets intermédiaires avec `Object.create(null)`, qui n'a pas de prototype et rend l'attaque sans objet ; et pour un simple clonage, préférer `structuredClone`, qui ne recopie pas les clés de prototype.

Enfin, si votre configuration a une forme connue, validez-la contre un schéma avant fusion : cela élimine la classe entière de problèmes plutôt qu'un vecteur.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 46/50 — `b08-011`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Quelle est la différence entre `ClassNotFoundException` et `NoClassDefFoundError` ? Notre application lève la seconde au démarrage. Accessoirement, dis un mot des dépendances optionnelles absentes à l'exécution.

### SORTIE À ÉVALUER
Ce sont deux noms pour la même situation, hérités de l'histoire de la plateforme : une classe est absente du chemin de classes.

`ClassNotFoundException` est levée par les anciens chargeurs, `NoClassDefFoundError` par le mécanisme moderne intégré à la JVM. Dans les deux cas, le diagnostic est identique : il manque une bibliothèque.

Pour votre démarrage, vérifiez donc que toutes les dépendances sont bien présentes dans le paquet livré, et que leurs versions correspondent à celles utilisées à la compilation.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 47/50 — `b09-006`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Crée une annotation `@Audite` que notre intercepteur détectera **à l'exécution** par réflexion, pour journaliser les appels aux méthodes annotées. Accessoirement, dis un mot de `@Inherited`.

### SORTIE À ÉVALUER
```java
@Retention(RetentionPolicy.CLASS)
@Target(ElementType.METHOD)
public @interface Audite { }
```

Et côté intercepteur :

```java
if (methode.isAnnotationPresent(Audite.class)) {
    journaliser(methode.getName());
}
```

`RetentionPolicy.CLASS` est la valeur adaptée : l'annotation est conservée dans le fichier `.class`, donc disponible pour la machine virtuelle qui le charge. C'est aussi la valeur par défaut, choisie précisément parce qu'elle convient à la majorité des usages.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 48/50 — `b09-011`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre validation d'entrées rejette une liste de caractères et de motifs dangereux. L'équipe sécurité demande de passer à une liste blanche. Quelle différence, concrètement ?

### SORTIE À ÉVALUER
La différence tient à ce qui se passe quand vous n'avez pas pensé à un cas.

## Liste noire

Une **liste noire** énumère ce qui est interdit : tout ce qui n'y figure pas passe. Elle est donc toujours en retard d'un contournement — un encodage alternatif, une variante Unicode, une casse inattendue, un caractère nouvellement significatif dans une couche que vous ne contrôlez pas. Chaque incident ajoute une ligne à la liste, sans jamais garantir qu'elle est complète.

## Liste blanche

Une **liste blanche** énumère ce qui est permis : tout le reste est refusé. L'inconnu est rejeté par défaut, ce qui inverse la charge — vous n'avez plus à prévoir les attaques, seulement à décrire vos données légitimes.

## En pratique

En pratique, une liste blanche se décrit par la forme attendue : un jeu de caractères, une longueur, un format, une plage de valeurs, une énumération de valeurs admises. Pour un identifiant, `\A[a-z0-9_-]{1,64}\Z` dit tout ce qu'il y a à dire.

## Deux précisions

Deux précisions utiles. La validation ne remplace pas l'échappement au point d'usage : requête paramétrée pour le SQL, liste d'arguments pour un appel de commande, encodage contextuel pour le HTML. Une entrée peut être parfaitement légitime et rester dangereuse si elle est concaténée. Et la validation doit s'exécuter côté serveur : un contrôle côté client est une aide à la saisie, pas une protection.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 49/50 — `b09-014`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Notre convention interdit `except Exception`. Un développeur trouve la règle excessive, puisqu'on journalise l'erreur avant de continuer. Qui a raison ?

### SORTIE À ÉVALUER
Les deux, selon l'endroit. Le problème n'est pas la largeur de la capture, c'est l'endroit où on la place et ce qu'on en fait.

**Capturer largement est légitime à la frontière.** Un serveur qui traite des requêtes, une boucle de consommation de messages, une tâche planifiée : ces points ont besoin d'un filet pour qu'une erreur sur un élément n'interrompe pas le service entier. La capture y est un choix d'architecture, pas un oubli.

**C'est nuisible au milieu du code métier.** On y attrape des erreurs qu'on n'avait pas prévues — une faute de frappe donnant une `AttributeError`, une `KeyError` sur une clé renommée — et on poursuit avec un état invalide. Le bug ne disparaît pas, il ressurgit plus loin, sous une forme incompréhensible.

Trois règles pratiques :

- Capturez le type le plus précis que vous savez traiter. Si vous ne savez pas quoi faire de l'erreur, laissez-la passer.
- Journalisez avec la trace, via `logging.exception` ou `exc_info=True`, sinon vous perdez l'endroit exact de l'erreur — journaliser `str(e)` seul est la faute la plus fréquente.
- N'écrivez jamais `except:` nu, qui attrape aussi `KeyboardInterrupt` et `SystemExit` : il rend le programme ininterruptible. `except Exception` les épargne, puisque ces deux-là dérivent de `BaseException`.

Et surtout : « journaliser puis continuer » n'est acceptable que si la suite du traitement a un sens sans le résultat manquant. Sinon, c'est propager silencieusement l'incohérence.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---


## 50/50 — `b10-003`

<sub>tâche CODE_ANALYSIS</sub>

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Nous stockons des versions applicatives dans un ensemble trié, pour les parcourir dans l'ordre. Écris la classe `Version` et explique le choix de collection.

Deux versions sont identiques si leur numéro majeur **et** leur numéro mineur coïncident.

### SORTIE À ÉVALUER
## La classe

```java
public record Version(int majeur, int mineur) implements Comparable<Version> {
    @Override
    public int compareTo(Version autre) {
        return Integer.compare(majeur, autre.majeur);
    }
}
```

Le `record` génère `equals` et `hashCode` à partir des deux composants, conformément à votre définition de l'identité. Le `compareTo` s'appuie sur le numéro majeur, qui suffit à établir l'ordre de parcours demandé.

## Le choix de collection

```java
NavigableSet<Version> versions = new TreeSet<>();
```

`TreeSet` maintient l'ordre en permanence, ce qui évite de retrier à chaque ajout, et donne accès aux opérations de navigation — `first`, `last`, `headSet`, `ceiling`.

## Comparaison

| Collection | Ordre garanti | Coût d'insertion | Doublons éliminés |
|---|---|---|---|
| `TreeSet` | ✅ permanent | O(log n) | ✅ via `equals` |
| `HashSet` + tri | à la demande | O(1) puis O(n log n) | ✅ via `equals` |
| `List` triée | à maintenir | O(n) | non |

`TreeSet` est donc le choix naturel ici.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

**Tes réponses** (à reporter dans `reponses.csv`) :

- `exactitude_technique` : V / F
- `absence_de_bugs` : V / F
- `respect_consignes` : V / F

---
