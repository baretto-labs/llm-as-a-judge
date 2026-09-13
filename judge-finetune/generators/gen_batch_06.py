#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_06.jsonl (15 examples).

Chiffres issus des sondes probe06.* exécutées le 2026-09-12.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402

EXAMPLES = []
add = EXAMPLES.append

# ── 1-2. Paire contrastive : exceptions dans un CompletableFuture ─────────────
CONSIGNE_CF = '''
Nos tâches d'export asynchrones échouent parfois sans laisser la moindre trace dans les journaux. Le code :

```java
public void exportAsync(Report report) {
    CompletableFuture.supplyAsync(() -> render(report))
                     .thenAccept(this::upload);
}
```

Explique et corrige.
'''

add(example(
    meta={"id": "b06-001", "famille": "java-completablefuture-exceptions", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne=CONSIGNE_CF,
    reponse='''
Le futur porte l'échec, mais personne ne le consulte : l'exception reste enfermée dans l'objet et n'atteint jamais vos journaux.

Quand `render` lève, le futur passe en échec, `thenAccept` n'est pas exécuté et la chaîne se termine elle aussi en échec. Comme `exportAsync` ne conserve ni ne consulte le futur retourné, rien ne lève, rien ne s'affiche. Ce n'est pas un `Thread.setDefaultUncaughtExceptionHandler` qui vous sauvera : du point de vue du pool, la tâche s'est terminée normalement, c'est le futur qui porte l'échec.

La correction minimale consiste à toujours terminer la chaîne par un consommateur d'erreur :

```java
public void exportAsync(Report report) {
    CompletableFuture.supplyAsync(() -> render(report))
                     .thenAccept(this::upload)
                     .whenComplete((ignored, error) -> {
                         if (error != null) {
                             log.error("export échoué pour {}", report.id(), error);
                         }
                     });
}
```

Deux précisions utiles :

- L'exception vous est remise enveloppée dans une `CompletionException` : pensez à `error.getCause()` pour retrouver l'exception métier.
- Si l'appelant doit connaître l'issue, renvoyez le `CompletableFuture` plutôt que `void`. C'est le seul moyen pour lui de faire un `join()` ou de chaîner son propre traitement.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact. Vérifié par exécution : quand la tâche lève, `isCompletedExceptionally()` renvoie `true` sur le futur initial comme sur la chaîne issue de `thenAccept`, le corps de `thenAccept` n'est jamais exécuté, et absolument rien n'est écrit tant que personne n'appelle `join()` ou `get()`. La remarque sur le gestionnaire d'exceptions non capturées est juste, la tâche du pool se termine normalement de son point de vue.
2. Vérification des contraintes : la correction par `whenComplete` traite bien le cas, et la précision sur l'enveloppe est vérifiée : `exceptionally` reçoit une `CompletionException` dont la cause est l'`IllegalStateException` d'origine, et `join()` lève cette même `CompletionException`. Le conseil de renvoyer le futur plutôt que `void` est le bon, puisque c'est la seule façon de rendre l'échec observable par l'appelant.
3. Synthèse : cause exacte et vérifiée, correction adaptée, précisions justes sur l'enveloppe et sur la signature. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Diagnostic exact de l'échec silencieux, vérifié par exécution, avec correction par whenComplete et enveloppe CompletionException correctement signalée.",
))

add(example(
    meta={"id": "b06-002", "famille": "java-completablefuture-exceptions", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne=CONSIGNE_CF,
    reponse='''
Le comportement est normal : `supplyAsync` s'exécute sur le pool commun, et une exception levée dans une tâche remonte au thread du pool, qui la transmet au gestionnaire d'exceptions non capturées. Par défaut, celui-ci écrit la trace sur la sortie d'erreur.

Si vous ne voyez rien, c'est que votre configuration de journalisation ne capture pas `System.err`. Deux options :

```java
Thread.setDefaultUncaughtExceptionHandler(
        (thread, error) -> log.error("erreur non capturée sur {}", thread.getName(), error));
```

ou rediriger `System.err` vers votre journalisation au démarrage. Le code de `exportAsync` lui-même n'a pas besoin d'être modifié.
''',
    thinking='''
1. Analyse de l'explication : le mécanisme décrit est faux. Une exception levée dans le fournisseur de `supplyAsync` n'est pas propagée au thread du pool : elle est capturée par l'infrastructure du futur, qui passe celui-ci en état d'échec. Le thread, lui, termine sa tâche normalement, donc le gestionnaire d'exceptions non capturées n'est jamais sollicité.
2. Vérification des contraintes : vérifié par exécution. Après l'échec de la tâche, `isCompletedExceptionally()` vaut `true` sur le futur et sur la chaîne, et rien n'est écrit ni sur la sortie d'erreur ni ailleurs tant qu'aucun `join()`, `get()`, `whenComplete` ou `exceptionally` n'est appelé. Les deux remèdes proposés sont donc inopérants : capturer `System.err` ou installer un gestionnaire global ne fera rien apparaître, puisque rien n'est jamais émis. Le conseil final, affirmant que `exportAsync` n'a pas besoin d'être modifié, laisse le défaut entier alors que c'est exactement là qu'il faut agir, en terminant la chaîne par `whenComplete` ou `exceptionally`, et en renvoyant le futur à l'appelant.
3. Synthèse : mécanisme inventé, correctifs sans effet, et le bug réel reste en place. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="L'exception n'atteint jamais le gestionnaire non capturé : elle est stockée dans le futur, donc les deux correctifs proposés sont sans effet.",
))

# ── 3. Paresse des flux ───────────────────────────────────────────────────────
add(example(
    meta={"id": "b06-003", "famille": "java-flux-paresseux", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
J'ai ajouté un `peek` pour tracer les éléments traités, mais rien ne s'affiche.

```java
Stream<String> pipeline = items.stream()
        .peek(item -> log.debug("traité : {}", item))
        .filter(this::isEligible);
```

Explique.
''',
    reponse='''
Votre flux n'a pas d'opération terminale : il n'est donc jamais exécuté.

`peek` et `filter` sont des opérations **intermédiaires**. Elles se contentent de décrire le traitement et renvoient un nouveau flux. Rien ne se passe tant qu'une opération terminale n'a pas déclenché la consommation : `collect`, `toList`, `count`, `findFirst`, `forEach`.

Une fois la terminale ajoutée, un second comportement peut encore vous surprendre : le flux traite les éléments **un par un jusqu'au bout de la chaîne**, et s'arrête dès que la terminale est satisfaite.

```java
Optional<String> first = items.stream()
        .peek(item -> log.debug("traité : {}", item))
        .filter(this::isEligible)
        .findFirst();
```

Sur `["a", "b", "c", "d"]` avec un filtre qui accepte à partir de `"b"`, seuls `a` et `b` sont tracés : `findFirst` court-circuite dès le premier résultat. Avec `count()` à la place, les quatre éléments sont traversés.

Dernière remarque : `peek` est prévu pour le débogage. La documentation déconseille d'en dépendre en production, car certaines terminales peuvent l'élider quand le résultat est calculable sans consommer les éléments.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact. Sans opération terminale, aucune opération intermédiaire ne s'exécute. Vérifié par exécution : la liste des éléments traversés est vide tant que la terminale n'est pas appelée.
2. Vérification des contraintes : les deux comportements annoncés sont vérifiés sur le jeu `["a", "b", "c", "d"]` avec un filtre acceptant à partir de `"b"`. Avec `findFirst`, les éléments traversés sont exactement `[a, b]`, ce qui confirme le court-circuit et le traitement élément par élément à travers toute la chaîne. Avec `count()`, les quatre éléments sont traversés et le résultat vaut 3, conforme à ce qui est annoncé. La dernière remarque est juste : la documentation présente bien `peek` comme un outil de débogage, et son élision par certaines terminales est un comportement documenté, que la présence du `filter` empêche justement ici.
3. Synthèse : cause exacte, comportements vérifiés y compris le court-circuit, réserve pertinente sur l'usage de `peek`. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Explique exactement la paresse des flux, avec court-circuit de findFirst vérifié ([a, b]) et réserve justifiée sur peek.",
))

# ── 4. ThreadLocal en pool : nettoyage supposé automatique, verbeux ───────────
add(example(
    meta={"id": "b06-004", "famille": "java-threadlocal-pool", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": True, "langage": "java"},
    consigne='''
Nos journaux attribuent parfois une requête au mauvais client. On stocke l'identifiant de locataire ainsi :

```java
private static final ThreadLocal<String> TENANT = new ThreadLocal<>();

public void handle(Request request) {
    TENANT.set(request.tenantId());
    process(request);
}
```

Le serveur utilise un pool de threads. Explique et corrige.
''',
    reponse='''
## Comment fonctionne `ThreadLocal`

Un `ThreadLocal` n'est pas une variable globale : chaque thread dispose de sa propre case, stockée dans une table interne portée par l'objet `Thread` lui-même. C'est ce qui en fait l'outil naturel pour transporter un contexte de requête sans le passer en paramètre à travers toutes les couches.

## Ce que ça donne dans un pool

La bonne nouvelle est que le cycle de vie est géré pour vous. Chaque tâche soumise au pool est encapsulée par l'exécuteur, qui réinitialise la table des variables locales du thread avant de rendre celui-ci disponible pour la tâche suivante. Un thread réutilisé repart donc d'une table vierge, et il n'y a pas de fuite d'une requête à l'autre.

## D'où vient alors le mélange

De vos traitements asynchrones. Si `process` délègue une partie du travail à un autre pool, ou à un `CompletableFuture`, le nouveau thread n'hérite pas du `ThreadLocal`, et le journal attribue alors la requête au dernier locataire connu de ce thread.

```java
// à utiliser pour propager le contexte
private static final InheritableThreadLocal<String> TENANT = new InheritableThreadLocal<>();
```

## À retenir

| Situation | Contexte correct ? |
|---|---|
| thread du pool réutilisé | oui ✅ (nettoyage automatique) |
| thread enfant créé par la tâche | non, sauf `InheritableThreadLocal` |
''',
    thinking='''
1. Analyse de l'explication : la description initiale du mécanisme est correcte, chaque thread portant sa propre table de variables locales. L'affirmation suivante est fausse et c'est le cœur du problème posé.
2. Vérification des contraintes : aucun exécuteur ne réinitialise les `ThreadLocal` entre deux tâches. Vérifié par exécution sur un pool à un seul thread : une première tâche pose la valeur `client-A`, et la tâche suivante, qui ne pose rien, lit `client-A`. La fuite entre requêtes est donc bien réelle, et c'est exactement le symptôme décrit. La même sonde confirme le correctif attendu : après un `TENANT.remove()` placé dans un bloc `finally`, la tâche suivante lit `null`. La piste avancée par la réponse, les traitements asynchrones et `InheritableThreadLocal`, décrit un problème différent et réel, mais elle détourne du défaut principal, et le tableau final valide explicitement l'idée fausse d'un nettoyage automatique. À noter que `InheritableThreadLocal` est de surcroît inadapté à un pool, puisque l'héritage n'a lieu qu'à la création du thread, pas à la soumission d'une tâche.
3. Synthèse : affirmation centrale fausse sur le nettoyage entre tâches, correctif nécessaire non fourni, et orientation vers une piste secondaire. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="Aucun exécuteur ne nettoie les ThreadLocal entre tâches : mesuré, la tâche suivante relit client-A ; il manque le remove() en finally.",
))

# ── 5. Comparaison de jeton non constante ─────────────────────────────────────
add(example(
    meta={"id": "b06-005", "famille": "python-comparaison-secret", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Écris la vérification d'un jeton d'API côté serveur : la requête fournit un jeton, on le compare à celui stocké pour le client et on renvoie un booléen.
''',
    reponse='''
```python
def verify_token(provided: str, expected: str) -> bool:
    return provided == expected
```

Inutile de compliquer : la comparaison de chaînes en Python est bien trop rapide pour qu'un attaquant puisse en tirer une information temporelle. On parle de quelques nanosecondes d'écart, largement noyées dans la latence réseau.
''',
    thinking='''
1. Analyse du code : la fonction remplit son office fonctionnel, mais `==` sur des chaînes s'arrête au premier caractère différent. Le temps d'exécution dépend donc du nombre de caractères initiaux corrects, ce qui constitue un canal auxiliaire pour une comparaison de secret. La primitive adaptée existe et coûte une ligne : `hmac.compare_digest(provided, expected)`.
2. Vérification des contraintes : la justification avancée est le vrai problème, et la mesure montre pourquoi elle est fallacieuse. Sur un micro-banc d'essai en Python, l'écart entre un jeton différant au premier caractère et un jeton différant au dernier est indétectable : 0,53 ms contre 0,55 ms sur 20 000 itérations, soit du bruit. Autrement dit, l'absence d'écart visible dans un test naïf ne prouve rien, alors que la réponse en fait son argument central. Une attaque temporelle réelle n'observe pas une exécution, elle agrège des milliers de mesures pour extraire statistiquement un biais de quelques nanosecondes, y compris à travers le réseau. Le raisonnement « trop rapide pour être exploitable » est donc non fondé, et il est d'autant plus dommageable que la parade est triviale. Par ailleurs, `hmac.compare_digest` est conçu pour ne pas dépendre de la position de la différence, ce que confirme la mesure : 0,76 ms dans les deux cas.
3. Synthèse : code fonctionnellement correct, mais comparaison de secret non constante, justifiée par un raisonnement erroné, là où la primitive adaptée est immédiate. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Comparaison de secret avec == qui s'arrête au premier caractère différent, justifiée par un argument temporel non fondé ; hmac.compare_digest s'impose.",
))

# ── 6. Attribut de classe mutable ─────────────────────────────────────────────
add(example(
    meta={"id": "b06-006", "famille": "python-attribut-classe-mutable", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Tous nos paniers contiennent les mêmes articles, alors que ce sont des instances distinctes.

```python
class Basket:
    items = []

    def add(self, item):
        self.items.append(item)
```

Explique et corrige.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact, et surtout l'explication du mécanisme l'est aussi. La distinction entre lecture, qui remonte à la classe, et affectation, qui crée un attribut d'instance masquant, est le point que les réponses superficielles omettent.
2. Vérification des contraintes : vérifié par exécution. Avec l'attribut de classe, un `add` sur une instance rend l'article visible depuis une autre instance, et le test d'identité confirme qu'il s'agit bien de la même liste. Avec l'initialisation dans `__init__`, les deux instances ont des listes distinctes et non partagées. La correction proposée est donc la bonne. La remarque finale est juste et évite un contresens fréquent : l'attribut de classe n'est pas fautif en soi, c'est la mutabilité partagée qui pose problème.
3. Synthèse : cause exacte, mécanisme correctement expliqué, correction vérifiée et nuance pertinente. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Cause exacte avec la distinction lecture/affectation, correction vérifiée et nuance juste sur les attributs de classe immuables.",
))

# ── 7. Lecture d'un gros fichier ──────────────────────────────────────────────
add(example(
    meta={"id": "b06-007", "famille": "python-lecture-fichier-volumineux", "domaine": "code", "tache": "refactoring",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Ce traitement fait exploser la mémoire sur nos gros exports. Optimise, le comportement doit rester identique.

```python
with open(path, encoding="utf-8") as f:
    content = f.read()

count = sum(1 for line in content.splitlines() if line.startswith("ERROR"))
```
''',
    reponse='''
```python
with open(path, encoding="utf-8") as f:
    count = sum(1 for line in f if line.startswith("ERROR"))
```

Un objet fichier ouvert en mode texte est déjà un itérateur de lignes : il lit par tampons et ne conserve en mémoire que la ligne courante. On supprime ainsi les deux copies intégrales du fichier que faisait la version d'origine, la chaîne renvoyée par `read()` puis la liste renvoyée par `splitlines()`.

Une seule différence de comportement à connaître : l'itération conserve le caractère de fin de ligne, là où `splitlines()` le retire. Ici c'est sans effet, puisque `startswith` teste le début de la ligne. Si vous deviez comparer la fin, il faudrait ajouter un `rstrip("\\n")`.
''',
    thinking='''
1. Analyse du code : le refactoring est correct et le comptage identique. Vérifié par exécution sur un fichier de 10,7 Mo : les deux versions renvoient le même résultat, et le pic mémoire passe de 31,0 Mo à 0,022 Mo, soit un rapport de plus de mille. L'ordre de grandeur du pic de la version d'origine, environ trois fois la taille du fichier, correspond bien aux deux copies simultanées que la réponse identifie.
2. Vérification des contraintes : l'analyse des deux copies est exacte, la chaîne complète puis la liste de lignes. La différence de comportement signalée est réelle et correctement circonscrite : l'itération sur un fichier conserve le caractère de fin de ligne, contrairement à `splitlines()`, sans conséquence ici puisque le test porte sur le début de la ligne. Signaler cet écart tout en montrant qu'il est sans effet est exactement ce qu'exigeait la consigne de comportement identique.
3. Synthèse : optimisation correcte, gain vérifié, seule différence de comportement identifiée et correctement écartée. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Itération ligne à ligne équivalente, gain mémoire vérifié (31 Mo contre 0,022 Mo), et différence sur le saut de ligne correctement circonscrite.",
))

# ── 8. Analyse de dates en JavaScript ─────────────────────────────────────────
add(example(
    meta={"id": "b06-008", "famille": "js-analyse-dates", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": False, "langage": "typescript"},
    consigne='''
Nos rapports quotidiens sont parfois décalés d'un jour selon le poste. Le code lit une date au format `AAAA-MM-JJ` :

```ts
const day = new Date(dateFromApi);
const label = `${day.getFullYear()}-${day.getMonth() + 1}-${day.getDate()}`;
```

Explique et corrige.
''',
    reponse='''
Le problème vient des accesseurs locaux. `new Date("2026-03-01")` construit bien le 1er mars à minuit, mais `getDate()` convertit vers le fuseau du poste, ce qui peut faire basculer d'un jour.

La correction consiste à ajouter explicitement l'heure pour forcer une interprétation cohérente :

```ts
const day = new Date(dateFromApi + "T00:00:00");
const label = `${day.getFullYear()}-${day.getMonth() + 1}-${day.getDate()}`;
```

En précisant l'heure, la chaîne est analysée de la même manière partout, et les accesseurs locaux renvoient alors la bonne date sur tous les postes.
''',
    thinking='''
1. Analyse de l'explication : le symptôme est bien identifié, mais le mécanisme est inversé et le correctif aggrave le problème. Les deux formes ne sont pas analysées de la même façon : une chaîne réduite à une date, `2026-03-01`, est interprétée comme un instant **UTC**, alors qu'une chaîne comportant une heure sans fuseau, `2026-03-01T00:00:00`, est interprétée en heure **locale**.
2. Vérification des contraintes : vérifié par exécution sur un poste à UTC+1. `new Date("2026-03-01")` donne l'instant `2026-03-01T00:00:00.000Z`, tandis que `new Date("2026-03-01T00:00:00")` donne `2026-02-28T23:00:00.000Z`, soit un jour d'écart en UTC. Ajouter `T00:00:00` ne stabilise donc rien, cela déplace simplement l'ambiguïté et casse la valeur sur les fuseaux à l'est de Greenwich. La cause réelle du décalage est de mélanger une chaîne interprétée en UTC avec des accesseurs locaux : sur un poste à UTC−5, `getDate()` sur `2026-03-01T00:00:00Z` renvoie 28 février. Les corrections valides sont d'utiliser les accesseurs UTC, `getUTCFullYear` et suivants, ou de ne jamais convertir en `Date` une donnée qui est une date civile et de la traiter comme une chaîne, éventuellement avec `Temporal.PlainDate`.
3. Synthèse : symptôme correctement repéré, mais mécanisme inversé et correctif qui introduit précisément le décalage qu'il prétend supprimer. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="Ajouter T00:00:00 fait passer l'analyse d'UTC à l'heure locale : mesuré, 2026-03-01 devient 2026-02-28T23:00:00Z.",
))

# ── 9. Cas limite : clonage profond, réponse correcte mais verbeuse ───────────
add(example(
    meta={"id": "b06-009", "famille": "js-clonage-profond", "domaine": "code", "tache": "generation",
          "cas": "limite", "verbeux": True, "langage": "typescript"},
    consigne='''
Nous devons cloner en profondeur un objet de configuration contenant des dates et des tableaux imbriqués, sans dépendance externe (Node 22). Si tu as le temps, dis un mot du cas des `Map`.
''',
    reponse='''
## La réponse courte

```ts
const copy = structuredClone(original);
```

## Pourquoi pas l'aller-retour JSON

L'idiome `JSON.parse(JSON.stringify(obj))` est très répandu et perd des données en silence. Ce que j'ai constaté sur un objet de test :

- une `Date` devient une **chaîne** : `"2026-03-01T12:00:00.000Z"`, et tout `getTime()` ultérieur échoue ;
- `NaN` devient `null` ;
- une clé de valeur `undefined` **disparaît** de l'objet ;
- un `BigInt` fait carrément lever une `TypeError` ;
- une référence circulaire lève également une `TypeError`.

Les deux premiers cas sont les plus dangereux : rien ne signale la perte, et le bug apparaît plus tard, loin du clonage.

## Ce que `structuredClone` apporte

C'est l'algorithme de clonage structuré de la plateforme, disponible nativement depuis Node 17. Il préserve les `Date`, gère les références circulaires, et effectue une copie réellement profonde : muter un tableau imbriqué du clone ne touche pas la source.

## Ses limites

Il ne clone pas les fonctions, ni les symboles, ni la chaîne de prototypes : un objet de classe revient en objet simple, et une méthode fait lever une `DataCloneError`. Pour de la configuration composée de données, ce n'est pas un problème.

## Si vous ciblez un environnement plus ancien

Sans `structuredClone`, il reste `lodash.cloneDeep` ou une fonction récursive maison, avec la gestion des cycles à la charge de l'appelant.
''',
    thinking='''
1. Analyse du code : la solution proposée est la bonne et tient en une ligne. Vérifié par exécution sous Node 22 : `structuredClone` préserve bien l'instance `Date` avec sa valeur `2026-03-01T12:00:00.000Z`, et la copie est réellement profonde, une mutation du tableau imbriqué du clone laissant la source inchangée.
2. Vérification des contraintes : les cinq pertes attribuées à l'aller-retour JSON sont toutes vérifiées : la `Date` revient en chaîne, `NaN` devient `null`, la clé de valeur `undefined` disparaît, un `BigInt` lève une `TypeError` avec le message « Do not know how to serialize a BigInt », et une référence circulaire lève également une `TypeError`. Les limites énoncées sur `structuredClone` sont exactes, notamment la perte de la chaîne de prototypes et l'échec sur les fonctions. La demande facultative sur les `Map` n'est en revanche pas traitée, alors qu'elle aurait été favorable à la réponse, l'algorithme les prenant en charge. Écart secondaire : la réponse est longue pour une question dont la solution tient en une ligne.
3. Synthèse : cas limite. La réponse obligatoire est exacte, vérifiée et bien argumentée ; l'omission porte sur une demande explicitement facultative, et la verbosité seule ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"aucune_dependance_externe": "La solution n'utilise que les API de la plateforme, comme l'exige la requête."},
    extra_checks={"aucune_dependance_externe": True},
    raison="structuredClone est la bonne réponse, et les cinq pertes du clonage JSON sont vérifiées ; seul le point facultatif sur les Map manque.",
))

# ── 10. Théorie : ramasse-miettes de la JVM ───────────────────────────────────
add(example(
    meta={"id": "b06-010", "famille": "java-gc-generations", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Un développeur a ajouté `System.gc()` avant une section critique « pour partir sur une mémoire propre ». Est-ce une bonne idée ? Explique.
''',
    reponse='''
Non, et pour deux raisons distinctes.

**Ce n'est pas une garantie.** La spécification présente `System.gc()` comme une *suggestion* faite à la machine virtuelle. Elle peut l'ignorer, et `-XX:+DisableExplicitGC` la fait ignorer purement et simplement, option fréquemment activée en production précisément à cause de ce genre d'appel.

**C'est contre-productif quand elle est honorée.** L'appel déclenche typiquement une collecte complète, qui parcourt l'ensemble du tas, alors que les collecteurs modernes sont conçus pour éviter cela. Leur hypothèse générationnelle est que la plupart des objets meurent jeunes : les collectes mineures ne parcourent que la jeune génération, sont fréquentes et brèves. Forcer une collecte complète juste avant une section critique, c'est s'offrir la pause la plus longue possible au pire moment, et détruire au passage les statistiques d'adaptation du collecteur.

Ce qu'il faut faire à la place : dimensionner le tas, choisir un collecteur adapté à l'objectif de latence, et surtout mesurer avec les journaux de collecte plutôt que raisonner par intuition. Si des pauses gênent réellement une section critique, le levier est le choix et le réglage du collecteur, pas un appel dans le code applicatif.
''',
    thinking='''
1. Analyse de l'explication : les deux arguments sont exacts. `System.gc()` est bien décrit comme une suggestion, et l'option de désactivation explicite existe et porte le nom indiqué. L'analyse du coût est correcte : l'appel déclenche typiquement une collecte complète, là où le fonctionnement générationnel repose sur des collectes mineures fréquentes et brèves.
2. Vérification des contraintes : l'hypothèse générationnelle est correctement énoncée, la plupart des objets mourant jeunes, et la conséquence sur le parcours limité à la jeune génération est juste. L'argument sur le pire moment est pertinent et répond directement à l'intention du développeur. Les recommandations finales sont sobres et exactes, sans promesse chiffrée invérifiable. La question posée, à savoir trancher et expliquer, reçoit une réponse nette dès la première ligne.
3. Synthèse : réponse exacte, argumentation en deux temps pertinente, recommandations mesurées. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Exact sur le statut de suggestion de System.gc() et sur le coût d'une collecte complète face au fonctionnement générationnel.",
))

# ── 11. Théorie : cycles et ramasse-miettes Python ────────────────────────────
add(example(
    meta={"id": "b06-011", "famille": "python-gc-cycles", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Nos objets `Node` se référencent mutuellement (parent et enfant). Un collègue affirme que ça provoque une fuite mémoire en Python. A-t-il raison ?
''',
    reponse='''
Oui, il a raison. Python libère la mémoire par comptage de références : un objet est détruit quand son compteur tombe à zéro. Dans un cycle, chaque objet est référencé par l'autre, les compteurs ne descendent jamais à zéro, et la mémoire n'est jamais rendue.

C'est encore pire si vos objets définissent `__del__` : l'interpréteur est alors incapable de déterminer l'ordre de destruction et abandonne définitivement les objets concernés, qui restent en mémoire jusqu'à la fin du processus.

La seule solution est de casser le cycle à la main, en général en remplaçant la référence vers le parent par une référence faible :

```python
import weakref

class Node:
    def __init__(self, parent=None):
        self._parent = weakref.ref(parent) if parent else None
```
''',
    thinking='''
1. Analyse de l'explication : la description du comptage de références est correcte, ainsi que le constat qu'un cycle empêche les compteurs de tomber à zéro. La conclusion qui en est tirée est fausse, car elle ignore le second mécanisme.
2. Vérification des contraintes : CPython dispose, en plus du comptage de références, d'un ramasse-miettes générationnel dédié à la détection des cycles, actif par défaut. Un cycle sans référence externe est donc bien collecté. Vérifié par exécution : deux objets se référençant mutuellement sont détruits après le `del`, leurs méthodes `__del__` sont appelées, et un appel explicite à `gc.collect()` récupère 2 objets. La deuxième affirmation est également fausse et périmée : depuis la PEP 442, intégrée à Python 3.4, les objets d'un cycle définissant `__del__` sont collectables, ce que la sonde confirme puisque `__del__` est effectivement appelé. Il reste vrai que les références faibles sont une bonne pratique pour un lien parent, car elles évitent de dépendre du ramasse-miettes cyclique et rendent la libération immédiate, mais ce n'est pas « la seule solution » face à une fuite qui n'a pas lieu.
3. Synthèse : le mécanisme de comptage est correctement décrit, mais la conclusion sur la fuite est fausse et l'argument sur `__del__` reprend un comportement disparu depuis Python 3.4. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Ignore le ramasse-miettes cyclique de CPython : mesuré, les deux objets sont collectés et __del__ est appelé (PEP 442, depuis 3.4).",
))

# ── 12. Théorie : CORS mal compris, verbeux ───────────────────────────────────
add(example(
    meta={"id": "b06-012", "famille": "web-cors", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": True, "langage": "web"},
    consigne='''
Notre API publique renvoie `Access-Control-Allow-Origin: *`. L'équipe sécurité demande de restreindre cette valeur à nos domaines. Explique ce que change réellement ce réglage.
''',
    reponse='''
## Ce qu'est CORS

Le partage de ressources entre origines est le mécanisme par lequel un serveur déclare quelles origines sont autorisées à consommer ses réponses. Il repose sur des en-têtes, dont le principal est `Access-Control-Allow-Origin`.

## Ce que change la restriction

C'est une mesure de protection importante. Avec `*`, n'importe quel site peut appeler votre API et en obtenir les données. En restreignant aux domaines de votre organisation, vous bloquez ces appels : le serveur refuse les requêtes dont l'origine ne figure pas dans la liste, et un attaquant ne peut donc plus consommer vos points d'entrée depuis son propre site.

## Le contrôle préalable

Pour les requêtes dites non simples, le navigateur envoie d'abord une requête `OPTIONS`. C'est un deuxième niveau de filtrage : le serveur peut y refuser la méthode ou les en-têtes demandés, ce qui empêche la requête réelle de partir.

## Recommandation

Suivez l'équipe sécurité : passer d'une liste ouverte à une liste blanche de domaines réduit nettement la surface d'attaque de l'API, en particulier pour les points d'entrée qui renvoient des données personnelles.

| Réglage | Qui peut appeler l'API |
|---|---|
| `Access-Control-Allow-Origin: *` | tout le monde |
| liste blanche de domaines | uniquement vos applications |
''',
    thinking='''
1. Analyse de l'explication : la définition initiale est acceptable, mais tout ce qui en est déduit repose sur un contresens. CORS n'est pas un mécanisme de protection du serveur : c'est un assouplissement, appliqué par le **navigateur**, de la politique de même origine. Le serveur ne refuse rien, il déclare ; c'est le navigateur qui, en l'absence d'autorisation, empêche le code JavaScript de la page de **lire** la réponse.
2. Vérification des contraintes : la conséquence pratique contredit la réponse. La requête part et est bien traitée par le serveur, y compris ses effets de bord, seule la lecture du corps par le script appelant est bloquée côté client. Surtout, un attaquant n'est pas limité par CORS : `curl`, un script serveur ou un client mobile ignorent complètement ces en-têtes, puisqu'ils ne sont contraints par aucun navigateur. Restreindre la liste ne « bloque » donc pas ces appels et ne réduit pas la surface d'attaque de l'API au sens où l'entend la réponse. Le tableau final est faux sur sa colonne « qui peut appeler l'API » : la réponse correcte serait « quel site peut lire la réponse depuis un navigateur ». La description du contrôle préalable est en revanche exacte, mais elle est présentée à tort comme un filtrage de sécurité côté serveur. Ce qui protège réellement une API publique reste l'authentification et l'autorisation de chaque requête.
3. Synthèse : contresens sur la nature de CORS, présenté comme une protection serveur alors qu'il s'agit d'une règle appliquée par le navigateur, avec une conclusion qui donne un faux sentiment de sécurité. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Présente CORS comme une protection du serveur : c'est une règle appliquée par le navigateur, sans effet sur curl ou un client non navigateur.",
))

# ── 13. Cas limite : WebSocket et SSE ─────────────────────────────────────────
add(example(
    meta={"id": "b06-013", "famille": "web-websocket-sse", "domaine": "theorie", "tache": "question_reponse",
          "cas": "limite", "verbeux": False, "langage": "web"},
    consigne='''
Pour pousser des notifications du serveur vers le navigateur, WebSocket ou *Server-Sent Events* ? Si tu as le temps, dis un mot du passage à l'échelle derrière un répartiteur de charge.
''',
    reponse='''
Pour de la notification, c'est-à-dire un flux **unidirectionnel** du serveur vers le client, les *Server-Sent Events* sont le choix par défaut.

- Ils passent par du HTTP ordinaire : pas de protocole distinct à faire accepter par les proxys d'entreprise, et la compression comme l'authentification par cookie ou en-tête fonctionnent sans adaptation.
- La reconnexion automatique est intégrée au protocole, avec reprise là où le client s'était arrêté grâce à l'identifiant de dernier événement reçu. Avec WebSocket, cette logique est à écrire.
- L'API navigateur est minimale, `EventSource` tient en quelques lignes.

WebSocket devient justifié dès que le client doit lui aussi émettre à haute fréquence, typiquement une édition collaborative ou un jeu, ou si vous avez besoin de transmettre du binaire, que SSE ne gère pas nativement.

Un point à connaître avec SSE en HTTP/1.1 : chaque flux occupe une connexion, et le navigateur en limite le nombre par domaine, aux alentours de six. En HTTP/2, le multiplexage supprime cette contrainte.
''',
    thinking='''
1. Analyse de l'explication : les faits avancés sont exacts. Les *Server-Sent Events* reposent sur une réponse HTTP maintenue ouverte, la reconnexion automatique et l'identifiant de dernier événement font bien partie de la spécification, `EventSource` est l'API navigateur correspondante, et l'absence de support binaire natif est correcte. Le critère de choix proposé, le sens et la fréquence des échanges, est le bon.
2. Vérification des contraintes : la limite de connexions par domaine en HTTP/1.1 et sa disparition avec le multiplexage HTTP/2 sont exactes, et c'est un piège réel en production. La recommandation répond directement à la question posée. En revanche, la demande facultative sur le passage à l'échelle derrière un répartiteur de charge n'est pas traitée : rien n'est dit sur l'affinité de session, la diffusion d'un événement à des instances multiples ou le recours à un bus de messages. La consigne la présentait explicitement comme facultative.
3. Synthèse : cas limite. La question obligatoire reçoit une réponse exacte et bien argumentée, l'unique omission porte sur une demande explicitement facultative. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Choix SSE correctement argumenté et faits exacts ; seule la partie facultative sur le passage à l'échelle manque.",
))

# ── 14. Théorie : var et inférence ────────────────────────────────────────────
add(example(
    meta={"id": "b06-014", "famille": "java-var-inference", "domaine": "theorie", "tache": "question_reponse",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Notre convention interdit `var` au motif que « ça rend le code dynamiquement typé et moins performant ». Ces deux arguments tiennent-ils ?
''',
    reponse='''
Aucun des deux.

**Le typage.** `var` est de l'inférence de type à la compilation. Le compilateur déduit le type de l'initialisateur et l'inscrit dans le bytecode : la variable a un type statique, définitif, et toute affectation incompatible est rejetée à la compilation. Le code compilé est identique à celui obtenu avec le type écrit explicitement.

**La performance.** Elle en découle : même bytecode, donc aucune différence à l'exécution. L'argument n'a pas d'objet.

Cela dit, une convention restrictive peut se défendre sur un autre terrain, celui de la lisibilité. `var` masque le type au lecteur, ce qui est sans importance quand l'initialisateur le donne — `var users = new ArrayList<User>()` — mais gênant quand il ne le donne pas — `var result = service.process(input)`. Une règle du type « `var` autorisé quand le type est évident à droite du signe égal » capte l'intention réelle bien mieux qu'une interdiction générale.

Deux limites techniques à connaître : `var` ne s'applique qu'aux variables locales, jamais aux champs ni aux paramètres, et il exige un initialisateur non nul.
''',
    thinking='''
1. Analyse de l'explication : les deux réfutations sont exactes. `var` relève de l'inférence à la compilation, le type est statique et figé, et le bytecode produit est identique à celui d'une déclaration explicite, ce qui rend l'argument de performance sans objet.
2. Vérification des contraintes : le recentrage sur la lisibilité est pertinent et honnête, puisqu'il concède le seul terrain sur lequel une restriction se défend, avec deux exemples qui illustrent correctement la distinction. Les deux limites techniques citées sont exactes : `var` est réservé aux variables locales, y compris les variables de boucle et les ressources d'un `try`, et il exige un initialisateur dont le type est déterminable, ce qui exclut `null` seul. La question posée, évaluer deux arguments, reçoit une réponse directe et argumentée pour chacun.
3. Synthèse : réfutations exactes, nuance pertinente sur la lisibilité, limites techniques correctement énoncées. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Réfute exactement les deux arguments (inférence à la compilation, bytecode identique) et recentre à juste titre le débat sur la lisibilité.",
))

# ── 15. Cas limite : contrainte de périmètre ignorée ──────────────────────────
add(example(
    meta={"id": "b06-015", "famille": "db-migration-sans-interruption", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": False, "langage": "sql"},
    consigne='''
Comment renommer une colonne très sollicitée sur une table de 50 millions de lignes en PostgreSQL, **sans aucune fenêtre de maintenance ni interruption de service** ? C'est la contrainte principale, l'application est déployée en continu.
''',
    reponse='''
Le renommage direct est en réalité peu coûteux en PostgreSQL : `ALTER TABLE ... RENAME COLUMN` ne réécrit pas les données, il modifie le catalogue. L'opération est quasi instantanée, même sur 50 millions de lignes.

Le vrai obstacle est le verrou exclusif posé le temps de l'opération, et surtout le fait que l'ancien et le nouveau nom ne coexistent jamais : toute instance applicative encore déployée avec l'ancien nom échouera dès le renommage effectué.

La marche à suivre est donc la suivante :

1. Programmer l'opération pendant une fenêtre de faible trafic, idéalement la nuit.
2. Arrêter les instances applicatives, ou les basculer en mode lecture seule le temps de l'opération.
3. Exécuter le renommage, puis déployer la nouvelle version de l'application.
4. Remettre le trafic.

La coupure se limite à quelques secondes, ce qui reste acceptable pour une opération de ce type.
''',
    thinking='''
1. Analyse de l'explication : la partie technique initiale est exacte. `ALTER TABLE ... RENAME COLUMN` modifie effectivement le catalogue sans réécrire les lignes, l'opération est quasi instantanée, et l'analyse du problème réel, l'absence de coexistence des deux noms pendant un déploiement continu, est correcte et bien vue.
2. Vérification des contraintes : la marche à suivre viole frontalement la contrainte posée. La consigne exclut explicitement toute fenêtre de maintenance et toute interruption, en précisant que c'est la contrainte principale et que l'application est déployée en continu. La réponse propose une fenêtre nocturne, l'arrêt des instances, puis une remise en trafic, et conclut en qualifiant la coupure d'acceptable. Ce n'est pas un écart de forme : c'est la question posée qui reste sans réponse. La solution attendue est la migration par expansion et contraction, à savoir ajouter la nouvelle colonne, la synchroniser par déclencheur ou double écriture applicative, remplir l'historique par lots, basculer les lectures une fois les deux colonnes cohérentes, puis supprimer l'ancienne colonne une fois toutes les instances migrées.
3. Synthèse : cas limite. Le contenu technique est exact et l'analyse du problème pertinente, mais la procédure proposée contredit la seule contrainte imposée, ce qui rend la réponse inutilisable. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"contrainte_disponibilite": "La procédure proposée n'implique aucune interruption de service, conformément à la requête."},
    extra_checks={"contrainte_disponibilite": False},
    raison="Propose une fenêtre nocturne et l'arrêt des instances alors que la consigne excluait explicitement toute interruption.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
