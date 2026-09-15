#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_05.jsonl (15 examples).

Chiffres issus des sondes probe05.* et Probe05b.java exécutées le 2026-09-12.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402

EXAMPLES = []
add = EXAMPLES.append

# ── 1. HashMap partagée entre threads ─────────────────────────────────────────
add(example(
    meta={"id": "b05-001", "famille": "java-hashmap-partagee", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Notre cache perd des entrées en production, sans aucune exception dans les journaux. Le code :

```java
private final Map<String, Session> cache = new HashMap<>();

public void register(Session session) {
    cache.put(session.id(), session);
}
```

`register` est appelée depuis le pool de threads du serveur. Explique et corrige.
''',
    reponse='''
`HashMap` n'est pas sûre en présence de plusieurs threads, et c'est exactement le symptôme décrit : des écritures perdues, sans exception.

Ce qui se passe : `put` lit la table, calcule le seau, écrit, et met à jour la taille. Ces étapes ne sont pas atomiques et les écritures d'un thread ne sont pas garanties visibles par les autres. Deux threads qui écrivent dans le même seau au même moment peuvent s'écraser mutuellement, et le compteur de taille lui-même se désynchronise. Sur les versions antérieures à Java 8, un redimensionnement concurrent pouvait même produire une boucle infinie ; depuis, on perd « seulement » des données.

La correction :

```java
private final Map<String, Session> cache = new ConcurrentHashMap<>();
```

`ConcurrentHashMap` verrouille par seau et garantit la visibilité des écritures, pour un coût négligeable en lecture. Deux précisions utiles :

- Si vous enchaînez plusieurs opérations, `put` conditionnel par exemple, utilisez les méthodes atomiques dédiées : `putIfAbsent`, `computeIfAbsent`, `merge`. Remplacer la map ne rend pas atomique un `if (!map.containsKey(k)) map.put(k, v)`.
- `Collections.synchronizedMap` est une alternative, mais elle sérialise tous les accès sur un unique verrou, ce qui est nettement moins performant sous charge.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact et correspond au symptôme, à savoir des pertes silencieuses sans exception. La description du `put` non atomique et du compteur de taille désynchronisé est correcte, et la précision historique sur la boucle infinie lors d'un redimensionnement concurrent avant Java 8 est juste.
2. Vérification des contraintes : mesuré par exécution avec 4 threads écrivant chacun 20 000 clés distinctes. La `HashMap` partagée termine à 47 327, 40 765 puis 40 730 entrées sur trois exécutions, pour 80 000 attendues, tandis que la `ConcurrentHashMap` atteint 80 000 à chaque fois. L'ampleur des pertes correspond bien à ce que décrit la réponse. Les deux précisions finales sont pertinentes et souvent omises : le remplacement de la map ne rend pas atomique une séquence de deux opérations, et `synchronizedMap` sérialise effectivement tous les accès sur un verrou unique.
3. Synthèse : cause exacte, correction adaptée et mesurée, mises en garde justes sur les opérations composées. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Diagnostic exact des écritures perdues, vérifié par mesure (40 730 sur 80 000), et correction adaptée avec les bonnes réserves.",
))

# ── 2. Dépassement d'entier dans une recherche binaire ────────────────────────
add(example(
    meta={"id": "b05-002", "famille": "java-recherche-binaire-depassement", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
Écris une recherche binaire sur une **plage de valeurs** : trouver le plus petit `x` dans `[lo, hi]` tel que `predicate.test(x)` soit vrai. Les bornes peuvent aller jusqu'à `Integer.MAX_VALUE` (on cherche un seuil de débit, pas un index de tableau). Signature imposée : `public static int firstTrue(int lo, int hi, IntPredicate predicate)`.
''',
    reponse='''
```java
public static int firstTrue(int lo, int hi, IntPredicate predicate) {
    while (lo < hi) {
        int mid = (lo + hi) / 2;
        if (predicate.test(mid)) {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    return lo;
}
```

L'invariant est classique : `hi` reste toujours une borne pour laquelle le prédicat est vrai, `lo` progresse tant qu'il est faux. La boucle se termine quand les deux se rejoignent.
''',
    thinking='''
1. Analyse du code : l'invariant décrit est correct et la recherche fonctionne pour des bornes modestes. Mais `(lo + hi) / 2` déborde dès que la somme dépasse `Integer.MAX_VALUE`, ce que la consigne annonce explicitement comme possible.
2. Vérification des contraintes : mesuré par exécution. Avec `lo = 2 000 000 000` et `hi = 2 100 000 000`, `(lo + hi) / 2` vaut `-97 483 648`, alors que la forme correcte `lo + (hi - lo) / 2` donne `2 050 000 000`. Un milieu négatif sort de la plage, le prédicat est évalué sur une valeur absurde et la boucle peut ne jamais converger. À noter que le défaut est invisible sur les cas de test habituels : avec `lo = 0`, `(lo + hi) / 2` et `lo + (hi - lo) / 2` donnent tous deux `1 073 741 823`, la somme ne débordant pas. C'est précisément ce qui rend ce bug durable en production. Les deux corrections classiques sont `lo + (hi - lo) / 2` et `(lo + hi) >>> 1`, la seconde donnant également `2 050 000 000` sur le cas mesuré.
3. Synthèse : la logique de recherche est juste, mais le calcul du milieu déborde précisément dans le domaine de valeurs que la consigne exigeait de couvrir. FAIL.
''',
    exact=True, bugs=False, consignes=False,
    raison="(lo + hi) / 2 déborde sur les bornes hautes exigées par la consigne : mesuré à -97 483 648 au lieu de 2 050 000 000.",
))

# ── 3. Tri en deux passes appuyé sur la stabilité ─────────────────────────────
add(example(
    meta={"id": "b05-003", "famille": "java-tri-stable-deux-passes", "domaine": "code", "tache": "refactoring",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Simplifie ce tri : on veut les employés triés par département, et à département égal par nom.

```java
employees.sort((a, b) -> {
    int byDept = a.dept().compareTo(b.dept());
    if (byDept != 0) return byDept;
    return a.name().compareTo(b.name());
});
```
''',
    reponse='''
Le plus direct est de composer les comparateurs :

```java
employees.sort(Comparator.comparing(Employee::dept).thenComparing(Employee::name));
```

C'est strictement équivalent au comparateur manuel, et l'intention se lit immédiatement.

Une autre écriture consiste à trier en deux passes, du critère le moins significatif au plus significatif :

```java
employees.sort(Comparator.comparing(Employee::name));
employees.sort(Comparator.comparing(Employee::dept));
```

Elle fonctionne parce que `List.sort` est **stable** : le second tri préserve l'ordre relatif établi par le premier. C'est garanti par la spécification, pas un effet de bord de l'implémentation. Je recommande néanmoins la première version : un seul parcours, et l'intention est explicite plutôt que déduite d'une propriété du tri.
''',
    thinking='''
1. Analyse du code : la composition `comparing(...).thenComparing(...)` reproduit exactement la logique du comparateur manuel, y compris l'ordre des critères et le repli sur le nom à département égal. C'est bien la simplification attendue.
2. Vérification des contraintes : l'affirmation sur la stabilité est exacte et vérifiée par exécution. Sur un jeu `[(R&D, Ana), (Ops, Bob), (R&D, Cid), (Ops, Dan)]`, un tri par département donne `[(Ops, Bob), (Ops, Dan), (R&D, Ana), (R&D, Cid)]` : l'ordre relatif d'origine est conservé au sein de chaque département, et le tri en deux passes produit le même résultat que le comparateur composé. La stabilité est bien contractuelle pour `List.sort` et `Arrays.sort` sur des objets, contrairement au tri des tableaux de primitifs, et la recommandation finale en faveur de la version en une passe est un conseil pertinent plutôt qu'une correction nécessaire.
3. Synthèse : simplification équivalente, propriété de stabilité correctement invoquée et vérifiée, recommandation justifiée. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Composition de comparateurs équivalente, et l'argument de stabilité invoqué pour la variante est exact et vérifié.",
))

# ── 4. Encodage : « Python 3 lit toujours en UTF-8 », verbeux ─────────────────
add(example(
    meta={"id": "b05-004", "famille": "python-encodage-defaut", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": True, "langage": "python"},
    consigne='''
Notre script plante chez un client Windows avec `UnicodeDecodeError`, alors qu'il fonctionne sur nos machines. Le code :

```python
with open(path) as f:
    content = f.read()
```

Explique et corrige.
''',
    reponse='''
## Le contexte

Ce genre d'écart entre postes est presque toujours une histoire de fin de ligne ou de séquence d'octets inattendue, et la bonne nouvelle est qu'il se diagnostique vite.

## Ce que fait Python 3

Depuis Python 3, le mode texte lit **toujours en UTF-8**. C'est un choix de conception de la version 3, précisément pour éliminer les divergences entre systèmes qui empoisonnaient Python 2. Préciser `encoding="utf-8"` est donc redondant : vous obtiendrez exactement le même comportement sur toutes les plateformes.

## D'où vient alors l'erreur ?

Du fichier lui-même, pas de la lecture. Le client vous envoie très probablement un fichier encodé en Windows-1252, produit par Excel ou le Bloc-notes, qui contient des octets invalides en UTF-8.

## La correction

```python
with open(path, errors="replace") as f:
    content = f.read()
```

Les octets non décodables sont remplacés par le caractère de remplacement `\\ufffd` au lieu de faire échouer la lecture. Le script devient robuste quel que soit le fichier reçu.

## À retenir

| Plateforme | Encodage utilisé par `open()` en mode texte |
|---|---|
| Linux | UTF-8 |
| macOS | UTF-8 |
| Windows | UTF-8 |
''',
    thinking='''
1. Analyse de l'explication : l'affirmation centrale est fausse, et c'est précisément la cause du bug décrit. En mode texte, `open()` sans paramètre `encoding` n'utilise pas UTF-8 par principe : il utilise l'encodage local, exposé par `locale.getpreferredencoding(False)`. Vérifié par exécution sur cette machine : cette fonction renvoie `UTF-8` et `sys.flags.utf8_mode` vaut `0`, ce qui montre bien que le résultat vient du réglage local et non d'une garantie du langage. Sur un poste Windows configuré en français, ce même appel renvoie typiquement `cp1252`, d'où la divergence constatée entre les machines.
2. Vérification des contraintes : le tableau final généralise l'erreur en affichant UTF-8 pour Windows. La correction proposée est pire que le mal : `errors="replace"` ne corrige pas l'encodage, il masque l'échec en remplaçant les octets non décodables, ce qui produit silencieusement des accents corrompus dans les données traitées. Vérifié : relire un fichier UTF-8 en latin-1 donne `cafÃ© â\\x80\\x94 naÃ¯ve` sans lever la moindre exception, illustrant qu'une lecture qui « passe » n'est pas une lecture correcte. Le correctif attendu est de déclarer explicitement l'encodage du fichier reçu, `open(path, encoding="utf-8")` ou `encoding="cp1252"` selon la source, éventuellement avec détection préalable.
3. Synthèse : la cause réelle est niée, remplacée par une affirmation fausse sur le comportement de `open()`, et la correction proposée masque l'erreur en corrompant les données. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="Affirme à tort que open() lit toujours en UTF-8 : c'est l'encodage local, et errors=\"replace\" masque le défaut en corrompant les accents.",
))

# ── 5. Comparaison de versions par chaînes ────────────────────────────────────
add(example(
    meta={"id": "b05-005", "famille": "python-comparaison-versions", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Notre vérificateur de mise à jour propose parfois de « mettre à jour » vers une version plus ancienne. Le code :

```python
if latest_version > current_version:
    notify_update(latest_version)
```

Les versions sont des chaînes du type `"1.9.0"`. Explique et corrige.
''',
    reponse='''
Le problème vient de la comparaison lexicographique des chaînes, qui compare caractère par caractère.

La correction consiste à normaliser la longueur des composants avec un remplissage de zéros :

```python
def normalize(version: str) -> str:
    return ".".join(part.zfill(3) for part in version.split("."))

if normalize(latest_version) > normalize(current_version):
    notify_update(latest_version)
```

Avec ce remplissage, `"1.9.0"` devient `"001.009.000"` et `"1.10.0"` devient `"001.010.000"` : la comparaison de chaînes redonne alors le bon ordre.
''',
    thinking='''
1. Analyse du code : le diagnostic est exact. La comparaison lexicographique compare `"1"` puis `"."` puis `"1"` contre `"9"`, si bien que `"1.10.0"` est jugé inférieur à `"1.9.0"`. Vérifié par exécution : trier `["1.9.0", "1.10.0", "1.2.0"]` comme des chaînes donne `['1.10.0', '1.2.0', '1.9.0']`, et `"1.10" > "1.9"` renvoie `False`.
2. Vérification des contraintes : le correctif proposé fonctionne sur les exemples donnés, mais il est fragile sur trois points que la réponse passe sous silence. Il suppose que chaque composant tient sur trois chiffres, et casse dès qu'une version atteint 1000. Il suppose que les deux versions ont le même nombre de composants, sinon `"1.9"` et `"1.9.1"` restent mal ordonnés. Et il échoue sur tout suffixe non numérique, `zfill` laissant `"1.0.0-rc1"` intact. La solution robuste est de comparer des tuples d'entiers, vérifiée comme donnant `['1.2.0', '1.9.0', '1.10.0']`, ou d'utiliser `packaging.version.Version`, qui gère aussi les pré-versions.
3. Synthèse : cause correctement identifiée, mais la correction reste une comparaison de chaînes déguisée, avec des limites non signalées qui reproduiront le même symptôme. FAIL.
''',
    exact=True, bugs=False, consignes=True,
    raison="Le remplissage par zéros reste une comparaison lexicographique : il casse au-delà de 999, sur des longueurs inégales et sur les pré-versions.",
))

# ── 6. N+1 ────────────────────────────────────────────────────────────────────
add(example(
    meta={"id": "b05-006", "famille": "sql-requetes-n-plus-1", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "sql"},
    consigne='''
Notre page « liste des auteurs » met plusieurs secondes à s'afficher pour 100 auteurs. Le code :

```python
authors = db.execute("SELECT id, name FROM authors").fetchall()
for author_id, name in authors:
    books = db.execute("SELECT title FROM books WHERE author_id = ?", (author_id,)).fetchall()
    render(name, books)
```

Explique et corrige.
''',
    reponse='''
C'est le problème classique des requêtes N+1 : une requête pour la liste, puis une par élément. Pour 100 auteurs, cela fait 101 allers-retours vers la base, et c'est la latence cumulée qui vous coûte les secondes constatées, pas le travail de la base elle-même.

La correction consiste à tout récupérer en une requête et à regrouper côté application :

```python
rows = db.execute("""
    SELECT a.id, a.name, b.title
    FROM authors a
    LEFT JOIN books b ON b.author_id = a.id
    ORDER BY a.id
""").fetchall()

books_by_author = defaultdict(list)
names = {}
for author_id, name, title in rows:
    names[author_id] = name
    if title is not None:
        books_by_author[author_id].append(title)
```

Le `LEFT JOIN` conserve les auteurs sans livre, dont le `title` vaut alors `NULL`, d'où le test avant l'ajout.

Si vous utilisez un ORM, la même correction porte un nom : chargement anticipé, `selectinload` ou `joinedload` sous SQLAlchemy, `prefetch_related` sous Django. Et pensez à vérifier qu'un index existe sur `books.author_id`, sinon chaque recherche parcourt la table entière.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact et le comptage aussi. Vérifié par exécution avec un compteur de requêtes : la boucle déclenche 101 requêtes pour 100 auteurs, contre 1 pour la version jointe. L'attribution du coût à la latence cumulée des allers-retours plutôt qu'au travail de la base est la bonne analyse pour ce volume.
2. Vérification des contraintes : la requête corrigée est juste, et le `LEFT JOIN` préserve bien les auteurs sans livre, avec le test sur `title is not None` qui évite d'insérer un `NULL` dans la liste. Le regroupement côté application est correct. Les compléments sont exacts et utiles : les noms des mécanismes de chargement anticipé correspondent bien aux ORM cités, et la remarque sur l'index est vérifiée, le plan passant de `SCAN books` à `SEARCH books USING INDEX idx_books_author (author_id=?)` une fois l'index créé.
3. Synthèse : cause exacte et chiffrée, correction équivalente qui traite le cas des auteurs sans livre, compléments justes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Diagnostic N+1 exact et mesuré (101 requêtes contre 1), correction jointe correcte y compris les auteurs sans livre.",
))

# ── 7. Pagination par OFFSET présentée comme stable ───────────────────────────
add(example(
    meta={"id": "b05-007", "famille": "sql-pagination-offset", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "sql"},
    consigne='''
Conçois la pagination de notre flux d'activité, qui reçoit des insertions en continu. L'utilisateur fait défiler page après page. Explique la garantie que ton approche offre sur les éléments vus.
''',
    reponse='''
La pagination par décalage est la plus simple et convient parfaitement ici :

```sql
SELECT id, message, created_at
FROM activity
ORDER BY id
LIMIT 20 OFFSET :page * 20;
```

La garantie est solide : comme le tri porte sur un identifiant croissant et stable, chaque élément occupe une position déterminée dans l'ordre global. L'utilisateur qui fait défiler verra donc chaque élément exactement une fois, sans doublon ni oubli, même si des insertions ont lieu pendant sa navigation.

Côté performance, pensez simplement à indexer la colonne de tri.
''',
    thinking='''
1. Analyse de la proposition : la requête est syntaxiquement correcte et la pagination par décalage fonctionne sur un jeu figé. La remarque sur l'index de tri est juste. Mais la garantie annoncée est fausse dans le cas d'usage décrit, un flux qui reçoit des insertions en continu.
2. Vérification des contraintes : `OFFSET` compte des lignes dans le résultat au moment de la requête, il ne mémorise pas où l'utilisateur en était. Toute insertion qui s'intercale avant la position courante décale l'ensemble. Vérifié par exécution : après lecture d'une première page `[1, 2, 3]`, l'insertion d'une ligne en tête fait renvoyer `[3, 4, 5]` à la page suivante, l'élément 3 est donc affiché deux fois. Symétriquement, une suppression fait sauter un élément. La consigne demandait explicitement d'expliquer la garantie offerte sur les éléments vus, et la réponse en affirme une qui n'existe pas. L'approche adaptée est la pagination par curseur, `WHERE id > :dernier_id ORDER BY id LIMIT 20`, vérifiée comme renvoyant `[4, 5, 6]` dans la même situation, et qui présente en prime un coût constant là où `OFFSET` doit parcourir puis jeter les lignes ignorées.
3. Synthèse : la requête fonctionne, mais la garantie centrale demandée par la consigne est fausse sur un flux en insertion continue, ce qui est exactement le contexte donné. FAIL.
''',
    exact=True, bugs=False, consignes=False,
    raison="La pagination par OFFSET n'est pas stable sous insertions : mesuré, l'élément 3 est renvoyé sur deux pages consécutives.",
))

# ── 8. Cas limite : __slots__, réponse correcte mais verbeuse ─────────────────
add(example(
    meta={"id": "b05-008", "famille": "python-slots-memoire", "domaine": "code", "tache": "refactoring",
          "cas": "limite", "verbeux": True, "langage": "python"},
    consigne='''
On instancie plusieurs millions de ces objets et la mémoire explose. Optimise.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```
''',
    reponse='''
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
''',
    thinking='''
1. Analyse du code : le diagnostic et la correction sont exacts. Le dictionnaire d'instance est bien la source du surcoût, et `__slots__` le remplace par des descripteurs de classe et un emplacement fixe par attribut.
2. Vérification des contraintes : les chiffres annoncés sont conformes à la mesure. Sur cette machine, une instance avec dictionnaire totalise 344 octets en additionnant l'objet et son `__dict__`, contre 48 octets avec `__slots__`, soit bien un facteur sept, et l'extrapolation à cinq millions d'instances est cohérente. Les trois limitations citées sont exactes : l'ajout d'attribut lève effectivement `AttributeError: 'WithSlots' object has no attribute 'z'`, l'absence de `__dict__` gêne les bibliothèques qui l'inspectent, et une sous-classe sans `__slots__` réintroduit le dictionnaire. Les alternatives proposées sont pertinentes. Le seul écart est la longueur : cinq sections pour une optimisation qui tient en trois lignes, avec une section « alternatives » non demandée.
3. Synthèse : l'optimisation demandée est correcte, mesurée et accompagnée de ses vraies limitations ; seule la verbosité dépasse le nécessaire, ce qui ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Optimisation correcte, chiffres conformes à la mesure (344 contre 48 octets) et limitations exactes ; seule la longueur est excessive.",
))

# ── 9. Index circulaire avec modulo négatif ───────────────────────────────────
add(example(
    meta={"id": "b05-009", "famille": "java-modulo-negatif", "domaine": "code", "tache": "generation",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Écris une méthode qui, dans un carrousel circulaire, renvoie l'index de l'élément situé `offset` positions plus loin, `offset` pouvant être négatif. Signature : `public static int wrapIndex(int current, int offset, int size)`.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse du code : la méthode répond exactement à la consigne, y compris pour les décalages négatifs, et la validation de `size` évite une division par zéro. `Math.floorMod` est la primitive correcte pour ce besoin.
2. Vérification des contraintes : l'explication du signe est exacte et vérifiée par exécution. `-7 % 2` vaut bien `-1` en Java, tandis que `Math.floorMod(-7, 2)` vaut `1`. La conséquence annoncée, un index négatif provoquant une exception d'indice hors bornes, est correcte. L'écriture manuelle proposée en complément est bien équivalente pour un `size` positif. À noter que `current + offset` pourrait théoriquement déborder sur des valeurs extrêmes, mais des index de carrousel n'atteignent pas cet ordre de grandeur, et ce silence ne constitue pas un défaut dans ce contexte.
3. Synthèse : solution correcte, explication du piège de signe exacte et vérifiée, validation d'entrée présente. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Math.floorMod traite correctement les décalages négatifs, et l'explication du signe de % est exacte et vérifiée.",
))

# ── 10. Théorie : == et equals sur les chaînes ────────────────────────────────
add(example(
    meta={"id": "b05-010", "famille": "java-identite-chaines", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Pourquoi `==` fonctionne-t-il parfois sur des chaînes en Java, et parfois non ? Explique le mécanisme sous-jacent.
''',
    reponse='''
`==` compare toujours des références. S'il « fonctionne » parfois, c'est parce que deux variables désignent réellement le même objet, pas parce que le contenu serait comparé.

Le mécanisme est le **pool de chaînes**. Les littéraux sont internés par la JVM : deux occurrences du même littéral dans le code désignent la même instance, d'où un `==` vrai. Les concaténations de constantes sont résolues à la compilation et rejoignent ce pool. En revanche, tout ce qui est construit à l'exécution produit une nouvelle instance :

```java
String a = "config", b = "config";
a == b;                                    // true  : même littéral interné
a == new String("config");                 // false : instance distincte
a == new String("config").intern();        // true  : intern() renvoie l'instance du pool
a == "con" + "fig";                        // true  : concaténation résolue à la compilation
a == new StringBuilder("con").append("fig").toString();  // false : construite à l'exécution
```

D'où la règle : comparez toujours avec `equals`, et réservez `==` aux cas où l'identité est précisément ce que vous voulez tester. Le piège est d'autant plus vicieux que les tests passent souvent avec des littéraux, avant d'échouer en production sur des chaînes lues depuis un fichier ou une base.
''',
    thinking='''
1. Analyse de l'explication : le mécanisme est correctement exposé. `==` compare des références, le pool de chaînes explique les cas où la comparaison réussit, et la distinction entre résolution à la compilation et construction à l'exécution est la clé du phénomène.
2. Vérification des contraintes : les cinq résultats annoncés sont vérifiés par exécution et tous conformes. Deux littéraux identiques donnent `true`, la comparaison avec `new String` donne `false`, `intern()` ramène `true`, la concaténation de deux constantes littérales donne `true`, et la construction via `StringBuilder` donne `false`. La remarque finale est pertinente et correspond à un mode de défaillance réel : les tests écrits avec des littéraux passent, alors que des chaînes lues depuis une source externe échouent.
3. Synthèse : mécanisme exact, cinq cas vérifiés, conclusion pratique justifiée. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Explique exactement le pool de chaînes et la résolution à la compilation, avec cinq résultats vérifiés par exécution.",
))

# ── 11. Théorie : CAP mal compris, verbeux ────────────────────────────────────
add(example(
    meta={"id": "b05-011", "famille": "archi-theoreme-cap", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": True, "langage": "architecture"},
    consigne='''
On hésite entre PostgreSQL et une base distribuée pour notre nouveau service. Un architecte invoque le théorème CAP. Explique ce qu'il dit vraiment et ce qu'on peut en tirer pour ce choix.
''',
    reponse='''
## L'énoncé

Le théorème CAP, formulé par Eric Brewer, énonce qu'un système de données ne peut garantir que **deux** des trois propriétés suivantes :

- **C**ohérence : toutes les lectures voient la dernière écriture.
- **D**isponibilité : toute requête reçoit une réponse.
- **P**artitionnement : le système tolère la perte de messages entre nœuds.

## Le triangle des choix

Chaque système se positionne donc sur un côté du triangle, une fois pour toutes :

| Catégorie | Systèmes | Ce qu'on sacrifie |
|---|---|---|
| CA | PostgreSQL, MySQL, Oracle | la tolérance au partitionnement |
| CP | MongoDB, HBase, Redis Cluster | la disponibilité |
| AP | Cassandra, DynamoDB, Riak | la cohérence |

## Ce qu'il faut en tirer

PostgreSQL est un système CA : il vous offre cohérence et disponibilité, au prix de l'impossibilité de tolérer un partitionnement réseau. C'est parfaitement acceptable pour un service dont la base tient sur un serveur, et c'est le choix que je recommanderais tant que vous n'avez pas de contrainte de répartition géographique.

Si vous partez sur du distribué, il faudra en revanche trancher entre cohérence et disponibilité, et ce choix est structurant pour toute l'application.
''',
    thinking='''
1. Analyse de l'explication : la définition des trois propriétés est à peu près correcte, mais la lecture du théorème est celle, très répandue, que ses propres auteurs ont explicitement corrigée. Le théorème ne dit pas qu'on choisit deux propriétés sur trois en permanence. Il énonce que **lorsqu'un partitionnement survient**, il faut choisir entre cohérence et disponibilité. Hors partition, un système peut parfaitement offrir les deux.
2. Vérification des contraintes : la catégorie « CA » du tableau n'a pas de sens pratique. Le partitionnement n'est pas une option d'architecture qu'on retire, c'est un événement réseau qu'on subit : tout système réparti sur plusieurs nœuds doit le tolérer. Classer PostgreSQL en CA revient à décrire une instance unique, où la question du partitionnement ne se pose pas, faute de réseau entre nœuds — ce n'est pas un choix, c'est l'absence de répartition. Le classement de MongoDB et de Redis Cluster dans une case fixe est également faux : leur comportement dépend de la configuration, du niveau d'écriture et de lecture demandé, et se règle par requête. La conclusion, qui recommande PostgreSQL pour un service mono-serveur, est raisonnable, mais elle est étayée par un raisonnement erroné et par une propriété (« CA ») qui n'existe pas.
3. Synthèse : reprise de l'interprétation « deux sur trois » que le théorème ne soutient pas, avec un tableau de classement faux, même si la recommandation finale tombe juste par accident. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Reprend le mythe « deux propriétés sur trois » : CAP n'impose un choix qu'en cas de partition, et la catégorie CA n'a pas de sens pour un système réparti.",
))

# ── 12. Cas limite : versionnage sémantique ───────────────────────────────────
add(example(
    meta={"id": "b05-012", "famille": "outillage-semver", "domaine": "theorie", "tache": "question_reponse",
          "cas": "limite", "verbeux": False, "langage": "outillage"},
    consigne='''
On sort une version de notre bibliothèque qui corrige un bug, mais dont la correction change le comportement observable d'une méthode publique. Majeure, mineure ou correctif ? Si tu as le temps, dis un mot des versions `0.x`.
''',
    reponse='''
Version **majeure**.

Le critère du versionnage sémantique n'est pas l'intention, c'est la compatibilité. Un correctif de bug reste un `PATCH` tant que le contrat public est préservé. Dès lors que le comportement observable d'une API publique change, du code qui fonctionnait peut cesser de fonctionner : c'est une rupture, donc `MAJOR`, même si le changement est une correction et même s'il est souhaitable.

En pratique, deux atténuations valent mieux qu'un débat sur le numéro :

- documenter la rupture dans le journal des modifications, avec la migration à suivre ;
- si la rupture est coûteuse pour vos utilisateurs, livrer le correctif derrière une option, désactivée par défaut en mineure, puis activée dans la majeure suivante.
''',
    thinking='''
1. Analyse de l'explication : la réponse est exacte. La spécification du versionnage sémantique fait bien de la compatibilité ascendante le critère, et non la nature ou l'intention du changement : une correction qui modifie le comportement observable d'une API publique est une rupture et appelle un incrément majeur.
2. Vérification des contraintes : le raisonnement est correctement conduit et les deux atténuations proposées sont des pratiques courantes et pertinentes, en particulier la livraison derrière une option pour étaler la migration. La question principale reçoit une réponse nette dès la première ligne, ce qui convient à la forme de la demande. En revanche, la partie sur les versions `0.x` n'est pas traitée du tout, alors qu'elle est intéressante ici, puisque la spécification y suspend justement ces garanties. La consigne la présentait explicitement comme facultative.
3. Synthèse : la question obligatoire reçoit une réponse exacte et bien argumentée, l'unique omission porte sur une demande explicitement facultative. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Réponse exacte sur le critère de compatibilité ; seule la mention des versions 0.x, explicitement facultative, manque.",
))

# ── 13. Théorie : TCP et UDP ──────────────────────────────────────────────────
add(example(
    meta={"id": "b05-013", "famille": "reseau-tcp-udp", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "reseau"},
    consigne='''
Pour notre flux de télémétrie temps réel, un collègue propose UDP « parce que c'est plus rapide ». Explique la vraie différence et dis si c'est un bon choix.
''',
    reponse='''
« Plus rapide » mérite d'être précisé : à débit utile égal, UDP n'envoie pas les bits plus vite. Ce qu'il supprime, c'est le travail que TCP fait pour vous.

TCP établit une connexion, numérote les segments, retransmet ce qui manque, réordonne à l'arrivée et adapte son débit à la congestion. Vous recevez donc un flux d'octets complet et dans l'ordre. Le coût : la poignée de main initiale, et surtout le blocage en tête de file, un segment perdu retarde la livraison de tout ce qui suit, même déjà reçu.

UDP se contente d'envoyer des datagrammes indépendants. Pas de connexion, pas de retransmission, pas d'ordre garanti, pas de contrôle de congestion. Un datagramme arrive entier ou pas du tout.

Pour de la télémétrie temps réel, c'est effectivement souvent le bon choix, mais pour la bonne raison : une mesure perdue est sans intérêt une fois périmée, et vous préférez la suivante à une retransmission tardive. Trois réserves toutefois :

- L'absence de contrôle de congestion est un problème de voisinage : sous charge, votre flux peut noyer le reste du trafic. Prévoyez une limitation de débit côté émetteur.
- Vous devrez gérer vous-même ce dont vous avez besoin : numéros de séquence pour détecter les pertes, horodatage, éventuellement déduplication.
- Certains réseaux d'entreprise filtrent UDP hors DNS. Vérifiez avant de vous engager, et prévoyez un repli.

Si vous voulez le meilleur des deux, QUIC offre des flux fiables ou non fiables au-dessus d'UDP, avec contrôle de congestion, sans le blocage en tête de file entre flux.
''',
    thinking='''
1. Analyse de l'explication : le recadrage initial est juste et pédagogiquement utile, UDP ne transmet pas les bits plus vite, il retire des mécanismes. La description de TCP est exacte : connexion, numérotation, retransmission, réordonnancement, contrôle de congestion, et le blocage en tête de file est correctement identifié comme le coût principal pour un flux temps réel. La description d'UDP est exacte également, y compris le caractère atomique du datagramme.
2. Vérification des contraintes : la recommandation est correcte et surtout correctement motivée, la péremption des mesures plutôt qu'un gain de vitesse supposé. Les trois réserves sont réelles et rarement toutes mentionnées : l'absence de contrôle de congestion et son effet sur le trafic voisin, la nécessité de réimplémenter détection de perte et horodatage, et le filtrage d'UDP sur certains réseaux. La mention de QUIC est exacte, ce protocole fournit bien des flux fiables ou non fiables au-dessus d'UDP et supprime le blocage en tête de file entre flux distincts. Les deux demandes, la vraie différence et l'avis sur le choix, sont satisfaites.
3. Synthèse : explication exacte, recommandation bien motivée, réserves pertinentes et complètes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Différence TCP/UDP exacte, recommandation motivée par la péremption des mesures et réserves pertinentes sur congestion et filtrage.",
))

# ── 14. Théorie : 401 et 403 inversés ─────────────────────────────────────────
add(example(
    meta={"id": "b05-014", "famille": "web-codes-statut", "domaine": "theorie", "tache": "question_reponse",
          "cas": "defaillant", "verbeux": False, "langage": "web"},
    consigne='''
Quand renvoyer 401 et quand renvoyer 403 dans notre API ? Et quel code pour une ressource qu'un utilisateur authentifié n'a pas le droit de voir, sans lui révéler qu'elle existe ?
''',
    reponse='''
La règle est la suivante :

- **401 Forbidden** : l'utilisateur est authentifié, mais ses droits ne suffisent pas pour l'opération demandée.
- **403 Unauthorized** : l'utilisateur n'est pas authentifié, ou son jeton est expiré. Le client doit alors se reconnecter.

Pour votre troisième cas, renvoyez **403** : puisque l'utilisateur n'a pas les droits, c'est bien un défaut d'authentification pour cette ressource précise, et le client saura qu'il doit renouveler son jeton.
''',
    thinking='''
1. Analyse de l'explication : les deux codes sont inversés, y compris dans leurs libellés. Le code 401 se nomme « Unauthorized » et correspond en réalité à un défaut d'**authentification** : identité absente, invalide ou expirée, et la réponse doit accompagner ce code d'un en-tête `WWW-Authenticate`. Le code 403 se nomme « Forbidden » et correspond à un défaut d'**autorisation** : l'identité est connue, mais les droits ne suffisent pas ; se réauthentifier ne changera rien.
2. Vérification des contraintes : la troisième question, la plus intéressante, reçoit une réponse doublement fausse. Elle est fausse par l'inversion, puisque le cas décrit relève de 403 et non d'un problème d'authentification, et elle passe surtout à côté de ce qui était demandé : ne pas révéler l'existence de la ressource. Or un 403 confirme précisément qu'elle existe, ce qui constitue une fuite d'information exploitable pour énumérer des identifiants. La réponse attendue est **404**, renvoyé délibérément à la place de 403 pour rendre indiscernables la ressource inexistante et la ressource interdite. Le conseil final, inviter le client à renouveler son jeton, enverrait de surcroît l'utilisateur dans une boucle de reconnexion inutile.
3. Synthèse : inversion complète des deux codes et de leurs libellés, et la question sur la non-divulgation reste sans réponse correcte. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="Inverse 401 et 403 jusque dans leurs libellés, et manque le 404 délibéré demandé pour ne pas révéler l'existence de la ressource.",
))

# ── 15. Cas limite : périmètre explicite non respecté ─────────────────────────
add(example(
    meta={"id": "b05-015", "famille": "db-normalisation", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": False, "langage": "sql"},
    consigne='''
Faut-il dénormaliser notre schéma pour accélérer la page d'accueil ? **On reste sur PostgreSQL, ne propose pas de solution NoSQL ni de changement de moteur**, c'est hors périmètre pour cette étude.
''',
    reponse='''
Avant de dénormaliser, mesurez : un plan d'exécution et un index bien choisi règlent la majorité des pages lentes, sans introduire de duplication à maintenir.

Si la mesure confirme que les jointures sont le coût dominant, la dénormalisation devient défendable, avec une règle : dupliquer une donnée, c'est s'engager à la maintenir cohérente. Prévoyez le mécanisme de synchronisation, déclencheur ou recalcul périodique, et acceptez la fenêtre d'incohérence associée.

Cela dit, pour une page d'accueil, je recommanderais plutôt de sortir de PostgreSQL pour ce cas d'usage précis. Un cache Redis en amont, alimenté à l'écriture, vous donnerait des temps de réponse d'un ordre de grandeur inférieur sans toucher au schéma. Une alternative consiste à stocker le document agrégé de la page d'accueil dans MongoDB, ce qui supprime les jointures par construction. Ces deux approches sont plus simples à maintenir qu'un schéma dénormalisé.
''',
    thinking='''
1. Analyse de l'explication : les deux premiers paragraphes sont exacts et bien ordonnés. Mesurer avant de dénormaliser, vérifier le plan d'exécution et les index d'abord, puis assumer le coût de maintien de la cohérence en cas de duplication : c'est le raisonnement attendu, et la mention de la fenêtre d'incohérence est juste.
2. Vérification des contraintes : le dernier paragraphe sort du périmètre explicitement fixé. La consigne interdisait sans ambiguïté de proposer une solution NoSQL ou un changement de moteur, en précisant même que c'était hors périmètre pour l'étude en cours. La réponse recommande pourtant Redis, puis MongoDB, et en fait sa recommandation principale, celle qui commence par « je recommanderais plutôt ». Ce n'est pas une digression marginale : c'est la conclusion du texte, et elle rend le livrable inutilisable tel quel pour l'étude demandée. Le contenu technique de ce paragraphe n'est pas faux en soi, mais la question posée était de trancher sur la dénormalisation dans PostgreSQL.
3. Synthèse : le raisonnement sur la dénormalisation est correct, mais la recommandation finale viole une contrainte de périmètre explicite et non ambiguë. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"perimetre_respecte": "La réponse reste dans le périmètre technique fixé par la requête, sans proposer d'outil exclu."},
    extra_checks={"perimetre_respecte": False},
    raison="La recommandation principale propose Redis puis MongoDB, alors que la consigne excluait explicitement NoSQL et tout changement de moteur.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
