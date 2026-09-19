#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_02.jsonl (15 examples, Java/Python/SQL/theory)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402  (same helper: system prompt + user template + JSON)

EXAMPLES = []
add = EXAMPLES.append

# ── 1-2. Paire contrastive : injection SQL (Python / SQLite) ──────────────────
CONSIGNE_SQLITE = '''
Écris une fonction Python `find_user_by_email(conn, email)` qui interroge une base SQLite (table `users(id, email, name)`) et renvoie le tuple `(id, email, name)` correspondant, ou `None` si aucun utilisateur ne correspond.
'''

add(example(
    meta={"id": "b02-001", "famille": "python-sqlite-recherche-email", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne=CONSIGNE_SQLITE,
    reponse='''
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
''',
    thinking='''
1. Analyse du code : sur un email normal, la requête renvoie bien le tuple attendu, et `fetchone()` renvoie `None` en l'absence de résultat. Le comportement nominal demandé est correct, et l'affirmation sur `fetchone()` est exacte. Les remarques annexes le sont également : `cursor.rowcount` vaut bien `-1` sur un `SELECT` en sqlite3, l'énumération explicite des colonnes protège bien la forme du tuple, et l'absence d'index sur `email` impose bien un parcours séquentiel.
2. Vérification des contraintes : la requête est construite par interpolation de chaîne, donc la valeur de `email` est concaténée telle quelle dans le SQL. C'est une injection SQL (CWE-89) : `find_user_by_email(conn, "x' OR '1'='1")` renvoie le premier utilisateur de la table alors qu'aucun email ne correspond. Le même choix casse aussi sur une donnée légitime : un email contenant une apostrophe (`o'brien@example.com`) lève `sqlite3.OperationalError`. La correction tient en un paramètre lié : `conn.execute("... WHERE email = ?", (email,))`. Le soin apporté à la présentation et la justesse de tout le reste ne changent rien à ce point : la faille est dans la seule ligne qui compte.
3. Synthèse : le cas nominal fonctionne, mais la fonction expose une injection exploitable et échoue sur une entrée valide. C'est bloquant. FAIL.
''',
    exact=True, bugs=False, consignes=True,
    raison="Requête construite par interpolation de chaîne : injection SQL (CWE-89) et plantage sur un email contenant une apostrophe.",
))

add(example(
    meta={"id": "b02-002", "famille": "python-sqlite-recherche-email", "domaine": "code", "tache": "generation",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne=CONSIGNE_SQLITE,
    reponse='''
```python
def find_user_by_email(conn, email):
    cursor = conn.execute(
        "SELECT id, email, name FROM users WHERE email = ?", (email,)
    )
    return cursor.fetchone()
```

La valeur passe en paramètre lié : le pilote s'occupe de l'échappement, et un email contenant une apostrophe fonctionne sans traitement particulier.
''',
    thinking='''
1. Analyse du code : la requête sélectionne les trois colonnes demandées et `fetchone()` renvoie le tuple correspondant, ou `None` s'il n'y a pas de ligne. Un email existant renvoie `(1, 'alice@example.com', 'Alice')`, un email absent renvoie `None`.
2. Vérification des contraintes : le paramètre lié `?` transmet la valeur hors de la chaîne SQL, ce qui neutralise l'injection. `"x' OR '1'='1"` ne renvoie plus rien, et `o'brien@example.com` est trouvé correctement là où une version par interpolation aurait levé une `OperationalError`. L'affirmation sur l'échappement par le pilote est exacte.
3. Synthèse : code correct, contrat respecté sur le cas absent, aucune faille d'injection. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Requête paramétrée correcte, renvoie le tuple attendu ou None, insensible aux apostrophes et à l'injection.",
))

# ── 3. equals sans hashCode : correctif qui introduit une régression ──────────
add(example(
    meta={"id": "b02-003", "famille": "java-point-equals-hashcode", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
Ce test échoue, il renvoie 2 au lieu de 1 :

```java
Set<Point> set = new HashSet<>(List.of(new Point(1, 2), new Point(1, 2)));
assertEquals(1, set.size());
```

Voici la classe, corrige-la (Java 17). Accessoirement, dis un mot de `record`.

```java
public final class Point {
    private final int x;
    private final int y;

    public Point(int x, int y) { this.x = x; this.y = y; }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof Point p)) return false;
        return x == p.x && y == p.y;
    }
}
```
''',
    reponse='''
`Point` redéfinit `equals` mais laisse `hashCode()` hérité d'`Object`. Or `HashSet` procède en deux temps : il calcule d'abord `hashCode()` pour choisir un seau, puis ne compare avec `equals` que les éléments déjà présents **dans ce seau**. Deux points égaux mais de hachages différents atterrissent dans des seaux distincts et ne se rencontrent jamais — d'où la taille 2 au lieu de 1.

Le contrat d'`Object` est explicite sur ce point : si `a.equals(b)` est vrai, alors `a.hashCode() == b.hashCode()` doit l'être aussi.

J'ajoute `hashCode()`, et j'en profite pour simplifier `equals` : l'abscisse suffit à identifier un point dans ce contexte, ce qui rend la comparaison plus rapide et le hachage moins coûteux à calculer.

```java
@Override
public boolean equals(Object o) {
    if (!(o instanceof Point p)) return false;
    return x == p.x;
}

@Override
public int hashCode() {
    return Integer.hashCode(x);
}
```

| Avant | Après |
|---|---|
| `hashCode()` hérité d'`Object`, distinct pour chaque instance | `hashCode()` dérivé de `x`, identique pour deux points égaux |
| deux seaux, deux éléments conservés | un seul seau, `equals` départage, taille 1 |

Un détail au passage : `Integer.hashCode(int)` est une méthode **statique** depuis Java 8, elle évite l'autoboxing qu'entraînerait `Integer.valueOf(x).hashCode()`.
''',
    thinking='''
1. Analyse du code : le diagnostic est juste. Sans `hashCode()`, deux instances égales gardent les hachages hérités d'`Object`, tombent dans des seaux différents et `HashSet` conserve les deux. Ajouter `hashCode()` corrige bien le test cible, et les deux méthodes proposées restent cohérentes entre elles. Les explications ajoutées sont exactes : le mécanisme seau puis `equals` est correctement décrit, la clause du contrat d'`Object` est bien énoncée, et `Integer.hashCode(int)` est effectivement statique depuis Java 8.
2. Vérification des contraintes : la « simplification » d'`equals` n'était pas demandée et casse la sémantique du type. `new Point(1, 2).equals(new Point(1, 3))` renvoie désormais `true`, et `new HashSet<>(List.of(new Point(1, 2), new Point(1, 3))).size()` renvoie 1 au lieu de 2. La justification avancée (« l'abscisse suffit dans ce contexte ») est une hypothèse métier inventée, que rien dans la consigne ne soutient. Le correctif minimal attendu était d'ajouter `Objects.hash(x, y)` sans toucher à `equals`. Le tableau récapitulatif, exact ligne à ligne, ne décrit que le test cible et détourne l'attention de tous les autres points de la classe. La demande facultative sur le cas des `record` n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : le test demandé passe, mais au prix d'une régression silencieuse sur l'égalité de tous les points partageant la même abscisse. FAIL.
''',
    exact=True, bugs=False, consignes=True,
    raison="La simplification non demandée d'equals rend égaux deux points d'ordonnées différentes : régression silencieuse.",
))

# ── 4. try-with-resources, refactoring correct et nuancé ──────────────────────
add(example(
    meta={"id": "b02-004", "famille": "java-try-with-resources", "domaine": "code", "tache": "refactoring",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Refactorise cette méthode pour garantir la fermeture du flux même en cas d'exception, sans changer le comportement observable (Java 17).

```java
public String readFirstLine(Path path) throws IOException {
    BufferedReader reader = new BufferedReader(new FileReader(path.toFile()));
    String line = reader.readLine();
    reader.close();
    return line;
}
```
''',
    reponse='''
```java
public String readFirstLine(Path path) throws IOException {
    try (BufferedReader reader = new BufferedReader(new FileReader(path.toFile()))) {
        return reader.readLine();
    }
}
```

Deux remarques :
- `try-with-resources` ferme le flux même si `readLine()` lève une exception, ce que la version d'origine ne faisait pas : le `close()` était sauté.
- J'ai conservé `FileReader` volontairement. `Files.newBufferedReader(path)` serait plus idiomatique, mais impose UTF-8, alors que `FileReader` utilise le charset par défaut de la JVM. Sur un JDK antérieur à 18, où ce défaut dépendait de la plateforme, la substitution changerait le comportement sur un fichier non UTF-8.
''',
    thinking='''
1. Analyse du code : la conversion en `try-with-resources` est correcte et la signature est conservée. La première ligne est renvoyée à l'identique, et un fichier vide renvoie `null` dans les deux versions, puisque `readLine()` renvoie `null` en fin de flux.
2. Vérification des contraintes : le seul changement de comportement observable est celui qui était demandé, la fermeture du flux sur le chemin d'exception. Les deux remarques sont exactes : le `close()` explicite était bien sauté en cas d'exception, et JEP 400 n'a fixé le charset par défaut à UTF-8 qu'à partir de Java 18, donc la prudence sur `Files.newBufferedReader` est justifiée plutôt que superstitieuse.
3. Synthèse : refactoring correct, comportement préservé, et la justification technique du choix de `FileReader` est exacte. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="try-with-resources correct, comportement préservé, et le maintien de FileReader est justifié par le charset par défaut avant Java 18.",
))

# ── 5. Argument par défaut mutable : correction subtilement fausse, verbeuse ──
add(example(
    meta={"id": "b02-005", "famille": "python-mutable-default", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": True, "langage": "python"},
    consigne='''
Bug : cette fonction accumule les tags entre deux appels indépendants.

```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags
```

Explique la cause et corrige.
''',
    reponse='''
## La cause

C'est l'un des pièges les plus classiques de Python, et il surprend même des développeurs expérimentés.

Les valeurs par défaut d'une fonction sont évaluées **une seule fois**, au moment où l'instruction `def` est exécutée, et non à chaque appel. La liste `[]` est donc créée une fois pour toutes et stockée dans `add_tag.__defaults__`. Chaque appel sans argument explicite réutilise **le même objet**, qui grossit à chaque `append`.

On peut le vérifier :

```python
>>> add_tag("a")
['a']
>>> add_tag("b")
['a', 'b']
>>> add_tag.__defaults__
(['a', 'b'],)
```

## La correction

L'idiome standard consiste à utiliser une sentinelle `None`, puis à créer la liste à l'intérieur du corps de la fonction :

```python
def add_tag(tag, tags=None):
    tags = tags or []
    tags.append(tag)
    return tags
```

`tags or []` est la forme concise et équivalente du test de sentinelle : si aucun argument n'est fourni, on repart d'une liste neuve à chaque appel.

## À retenir

| Écriture | Comportement |
|---|---|
| `def f(x=[])` | objet partagé entre les appels ❌ |
| `def f(x=None)` puis `x = x or []` | nouvelle liste à chaque appel ✅ |

Cette règle vaut pour tous les types mutables : listes, dictionnaires, ensembles, et aussi les instances de classes.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact et bien expliqué. Les valeurs par défaut sont évaluées une fois à la définition, l'objet est partagé entre les appels, et l'inspection de `__defaults__` le montre effectivement. Le passage à une sentinelle `None` est la bonne direction.
2. Vérification des contraintes : la correction proposée est fausse dans un cas. `tags or []` teste la valeur de vérité et non l'identité : toute liste vide fournie par l'appelant est remplacée par une nouvelle liste. Avec `mine = []` puis `add_tag("a", mine)`, la fonction renvoie `['a']` mais `mine` reste `[]`, alors que la version d'origine, elle, aurait bien ajouté l'élément. Le comportement devient incohérent selon que la liste passée est vide ou non. L'affirmation « forme concise et équivalente du test de sentinelle » est donc inexacte, et le tableau récapitulatif propage l'erreur. La forme correcte est `if tags is None: tags = []`.
3. Synthèse : présentation soignée et cause correctement identifiée, mais le correctif introduit un bug silencieux sur les listes vides passées explicitement. La qualité de l'explication ne compense pas une correction fausse. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="La correction `tags or []` remplace toute liste vide fournie par l'appelant : il fallait tester `if tags is None`.",
))

# ── 6-7. Paire contrastive : COUNT(*) sur LEFT JOIN ───────────────────────────
CONSIGNE_AUTEURS = '''
Schéma SQLite : `authors(id, name)` et `books(id, author_id, title)`. Écris une requête qui liste chaque auteur avec son nombre de livres, **y compris les auteurs qui n'en ont aucun**, pour lesquels on attend 0.
'''

add(example(
    meta={"id": "b02-006", "famille": "sql-auteurs-sans-livre", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "sql"},
    consigne=CONSIGNE_AUTEURS,
    reponse='''
```sql
SELECT a.id, a.name, COUNT(*) AS book_count
FROM authors a
LEFT JOIN books b ON b.author_id = a.id
GROUP BY a.id, a.name
ORDER BY book_count DESC;
```

Le point décisif est le `LEFT JOIN` plutôt qu'un `INNER JOIN`. Un `INNER JOIN` ne conserve que les lignes ayant une correspondance des deux côtés : les auteurs sans livre disparaîtraient purement et simplement du résultat, ce qui est exactement ce que la consigne interdit. Le `LEFT JOIN`, lui, conserve toutes les lignes de `authors` et complète avec des `NULL` quand aucun livre ne correspond. Le `LEFT JOIN` conserve les auteurs sans livre, qui obtiennent donc 0.

Le `GROUP BY` porte sur `a.id` et `a.name`. Grouper sur `a.id` seul suffirait en SQLite, qui tolère les colonnes non agrégées dans la liste de sélection, mais énumérer les deux garde la requête portable vers PostgreSQL, nettement plus strict sur ce point : il exige que toute colonne projetée soit agrégée ou présente dans le `GROUP BY`.

Le tri décroissant met les auteurs les plus prolifiques en tête, ce qui est en général ce qu'on veut afficher. Ajoutez `, a.name` comme second critère si vous souhaitez un ordre déterministe en cas d'égalité : sans lui, deux auteurs à égalité peuvent s'intervertir d'une exécution à l'autre.
''',
    thinking='''
1. Analyse de la requête : la syntaxe est valide et le `LEFT JOIN` conserve effectivement les auteurs sans livre, comme l'affirme la réponse. Le regroupement porte sur les bonnes colonnes. Les développements ajoutés sont exacts : l'`INNER JOIN` écarterait bien les auteurs sans livre, SQLite tolère bien les colonnes non agrégées là où PostgreSQL les refuse, et l'ajout d'un second critère de tri rend bien l'ordre déterministe.
2. Vérification des contraintes : `COUNT(*)` compte les lignes du résultat joint, y compris la ligne fabriquée par le `LEFT JOIN` avec des colonnes `books` à `NULL`. Un auteur sans livre obtient donc 1, pas 0 : la requête renvoie `(3, 'Carol', 1)` là où la consigne attend un compte à 0. La conclusion de la réponse est donc fausse, et l'exigence explicite de la consigne n'est pas satisfaite. La correction consiste à compter une colonne de la table de droite, `COUNT(b.id)`, qui ignore les `NULL`. Tout le reste de la réponse étant juste et abondamment argumenté, l'erreur est d'autant plus facile à laisser passer.
3. Synthèse : requête exécutable mais résultat faux sur le cas précis que la consigne mettait en avant. FAIL.
''',
    exact=True, bugs=False, consignes=False,
    raison="COUNT(*) compte la ligne NULL produite par le LEFT JOIN : les auteurs sans livre obtiennent 1 au lieu de 0.",
))

add(example(
    meta={"id": "b02-007", "famille": "sql-auteurs-sans-livre", "domaine": "code", "tache": "generation",
          "cas": "parfait", "verbeux": False, "langage": "sql"},
    consigne=CONSIGNE_AUTEURS,
    reponse='''
```sql
SELECT a.id, a.name, COUNT(b.id) AS book_count
FROM authors a
LEFT JOIN books b ON b.author_id = a.id
GROUP BY a.id, a.name
ORDER BY book_count DESC, a.name;
```

Le point important est `COUNT(b.id)` plutôt que `COUNT(*)` : les fonctions d'agrégation ignorent les `NULL`, donc la ligne fabriquée par le `LEFT JOIN` pour un auteur sans livre ne compte pas, et on obtient bien 0.
''',
    thinking='''
1. Analyse de la requête : `LEFT JOIN` pour conserver tous les auteurs, agrégation sur une colonne de la table de droite pour ne pas compter la ligne fabriquée. Avec deux auteurs pourvus et un auteur sans livre, les comptes obtenus sont 2, 1 et 0.
2. Vérification des contraintes : l'exigence explicite (0 pour un auteur sans livre) est satisfaite. L'explication est exacte, `COUNT(colonne)` ignore les `NULL` là où `COUNT(*)` compte les lignes. Le second critère de tri sur `a.name` rend l'ordre déterministe en cas d'égalité, ce qui est un plus sans effet sur la correction.
3. Synthèse : requête correcte, cas limite des auteurs sans livre traité, explication exacte. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="COUNT(b.id) ignore les NULL du LEFT JOIN : les auteurs sans livre obtiennent bien 0, comme exigé.",
))

# ── 8. Cas limite : verbeux, partie facultative non traitée ───────────────────
add(example(
    meta={"id": "b02-008", "famille": "python-parse-duration", "domaine": "code", "tache": "generation",
          "cas": "limite", "verbeux": True, "langage": "python"},
    consigne='''
Écris `parse_duration(s)` qui convertit une durée compacte comme `'1h30m'` ou `'45s'` en nombre de secondes (entier). L'entrée invalide doit lever `ValueError`. Pas de dépendance externe. Si tu as le temps, gère aussi les jours (`'2d'`).
''',
    reponse='''
Voici une implémentation complète, avec les cas limites traités.

## Approche

Une expression régulière repère les paires nombre/unité, puis on additionne. Le point délicat est le rejet des entrées invalides : une simple recherche de motifs accepterait `'1h!!'` en ignorant silencieusement le bruit. La parade consiste à reconstruire la chaîne à partir des correspondances et à la comparer à l'entrée.

## Implémentation

```python
import re

_PATTERN = re.compile(r"(\\d+)([dhms])")
_FACTORS = {"d": 86400, "h": 3600, "m": 60, "s": 1}


def parse_duration(s):
    """Convertit une durée compacte ('1h30m') en secondes."""
    if not isinstance(s, str) or not s:
        raise ValueError(f"Durée invalide : {s!r}")

    matches = _PATTERN.findall(s)
    if not matches or "".join(n + u for n, u in matches) != s:
        raise ValueError(f"Durée invalide : {s!r}")

    return sum(int(n) * _FACTORS[u] for n, u in matches)
```

## Exemples

```python
>>> parse_duration("1h30m")
5400
>>> parse_duration("45s")
45
>>> parse_duration("2h")
7200
>>> parse_duration("2d")
172800
>>> parse_duration("1d12h")
129600
>>> parse_duration("1h 30m")
Traceback (most recent call last):
ValueError: Durée invalide : '1h 30m'
```

## Pour aller plus loin

On pourrait accepter les décimales, tolérer les espaces, ou valider que les unités sont fournies dans l'ordre décroissant. Dis-moi si tu veux l'une de ces variantes.
''',
    thinking='''
1. Analyse du code : l'expression régulière capture les paires nombre/unité et la somme pondérée est juste. `'1h30m'` donne 5400, `'45s'` donne 45, `'2h'` donne 7200. La vérification par reconstruction fait son travail : `'1h 30m'`, `'1h!!'`, `'abc'`, `''` et une entrée non textuelle lèvent bien `ValueError`, alors qu'un simple `findall` aurait accepté les trois premiers en silence. L'explication de ce mécanisme est exacte.
2. Vérification des contraintes : les exigences obligatoires sont satisfaites, à savoir la conversion, la levée de `ValueError` sur entrée invalide et l'absence de dépendance externe. La demande facultative sur les jours est en outre traitée, et elle l'est correctement : l'unité `d` figure au motif comme à la table des facteurs, `'2d'` donne 172800 et `'1d12h'` donne 129600, et la vérification par reconstruction continue de rejeter `'2x'`. Un seul écart subsiste, la verbosité, avec une section « pour aller plus loin » non demandée.
3. Synthèse : tout l'obligatoire est correct, la demande facultative est traitée sans erreur, et le seul écart restant est stylistique. La verbosité ne doit pas faire échouer une réponse juste. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"aucune_dependance_externe": "La solution n'utilise que la bibliothèque standard, comme l'exige la requête."},
    extra_checks={"aucune_dependance_externe": True},
    raison="Toutes les exigences obligatoires sont satisfaites, et la demande facultative sur les jours est traitée sans erreur.",
))

# ── 9. Cas limite : signature imposée non respectée ───────────────────────────
add(example(
    meta={"id": "b02-009", "famille": "java-firstnonblank-signature", "domaine": "code", "tache": "generation",
          "cas": "limite", "verbeux": False, "langage": "java"},
    consigne='''
Implémente **exactement** cette signature, en Java 17 et sans dépendance externe :

```java
public static Optional<String> firstNonBlank(List<String> values)
```

Elle renvoie la première valeur non nulle et non blanche de la liste, ou `Optional.empty()` si aucune ne convient.
''',
    reponse='''
```java
public static String firstNonBlank(List<String> values) {
    if (values == null) return null;
    for (String value : values) {
        if (value != null && !value.isBlank()) return value;
    }
    return null;
}
```

## Choix d'implémentation

`isBlank()`, introduite en Java 11, couvre d'un seul test la chaîne vide et les chaînes composées uniquement d'espaces ou de tabulations. Inutile donc d'écrire `value.trim().isEmpty()`, qui alloue en prime une chaîne intermédiaire à chaque élément parcouru.

Le parcours s'arrête au premier élément valide : quand la valeur utile est en tête de liste, on ne paie qu'une itération. Une version à base de `Stream` — `values.stream().filter(...).findFirst()` — serait plus déclarative, mais monte un pipeline complet pour un besoin qui tient en une boucle.

Le cas de la liste `null` est traité en amont, ce qui évite la `NullPointerException` que lèverait le `for` amélioré en tentant d'obtenir un itérateur.

## Sur le type de retour

La logique est identique à ce qui était demandé, j'ai simplement préféré renvoyer `null` plutôt qu'un `Optional` : c'est plus léger et ça évite une allocation par appel. Sur un chemin appelé en boucle serrée, cette allocation finit par se voir au profilage.
''',
    thinking='''
1. Analyse du code : la logique de sélection est correcte. `isBlank()` couvre bien la chaîne vide et les chaînes composées d'espaces, le `null` de la liste est écarté avant l'appel, et le parcours renvoie le premier élément valide. Sur une liste `[null, "  ", "", "premier", "second"]`, la valeur retournée est `"premier"`. Les justifications ajoutées sont exactes : `isBlank()` date bien de Java 11, `trim().isEmpty()` alloue bien une chaîne intermédiaire, et le `for` amélioré lèverait bien une `NullPointerException` sur une liste nulle.
2. Vérification des contraintes : la signature imposée n'est pas respectée. La consigne exigeait **exactement** `Optional<String>` comme type de retour, la réponse renvoie `String` et signale l'absence de valeur par `null`. Ce n'est pas un détail de style : tout appelant écrit contre l'API demandée ne compile pas, et la sentinelle `null` réintroduit précisément le risque que `Optional` sert à écarter. La justification par l'allocation évitée ne tient pas face à une exigence explicite.
3. Synthèse : le code est juste et sans bug, mais une consigne obligatoire et non ambiguë est ignorée, ce qui suffit à faire échouer la réponse. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"signature_conforme": "La signature est exactement celle imposée par la requête, type de retour compris."},
    extra_checks={"signature_conforme": False},
    raison="La signature imposée n'est pas respectée : retour String et sentinelle null au lieu du Optional<String> exigé.",
))

# ── 10. Théorie : contrat equals / hashCode ───────────────────────────────────
add(example(
    meta={"id": "b02-010", "famille": "java-contrat-equals-hashcode", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Explique le contrat entre `equals` et `hashCode` en Java, et ce qui casse concrètement si on redéfinit `equals` sans `hashCode`. Réponse concise.
''',
    reponse='''
Le contrat tient en trois points :

1. Si `a.equals(b)` est vrai, alors `a.hashCode() == b.hashCode()` **doit** l'être aussi.
2. La réciproque est fausse : deux objets différents peuvent partager un hachage, c'est une collision, et c'est autorisé.
3. Le hachage doit rester stable tant que les champs utilisés par `equals` ne changent pas.

Ce qui casse sans `hashCode` : les collections de hachage cherchent d'abord le seau via `hashCode`, puis ne comparent avec `equals` que les éléments de ce seau. Deux objets égaux mais de hachages différents ne se rencontrent jamais.

```java
Set<Point> set = new HashSet<>();
set.add(new Point(1, 2));
set.add(new Point(1, 2));   // taille 2 au lieu de 1
map.get(new Point(1, 2));   // null, alors que la clé « existe »
```

Le piège symétrique concerne le point 3 : muter un champ d'égalité après insertion déplace l'objet vers un autre seau logique, et il devient introuvable dans sa propre collection.
''',
    thinking='''
1. Analyse de l'explication : les trois clauses du contrat sont exactes et correspondent à la documentation d'`Object`, y compris la précision sur la réciproque, qui est le point le plus souvent mal compris. La mention de la stabilité du hachage est pertinente.
2. Vérification des contraintes : le mécanisme décrit est correct, la recherche par seau puis la comparaison par `equals` à l'intérieur du seau. Avec un `equals` redéfini sans `hashCode`, `HashSet` contient bien deux éléments égaux et `HashMap.get` renvoie `null` pour une clé équivalente. Le piège de la mutation après insertion est réel et correctement décrit. Les trois demandes de la consigne sont couvertes : contrat, conséquence concrète et concision.
3. Synthèse : explication exacte, sans approximation, format concis respecté. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Contrat exact, y compris la réciproque et la stabilité du hachage, avec la conséquence concrète correctement décrite.",
))

# ── 11. Théorie : niveaux d'isolation, erreur cachée dans une réponse verbeuse ─
add(example(
    meta={"id": "b02-011", "famille": "db-niveaux-isolation", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": True, "langage": "sql"},
    consigne='''
Un collègue veut passer notre service de `READ COMMITTED` à `REPEATABLE READ` pour éviter des incohérences dans nos rapports. Explique les niveaux d'isolation du standard SQL, ce que chacun empêche, et dis si le changement est pertinent.
''',
    reponse='''
## Les quatre niveaux du standard

Le standard SQL définit quatre niveaux, du plus permissif au plus strict.

**READ UNCOMMITTED** — la transaction voit les écritures non validées des autres. On parle de lecture sale. Personne n'utilise ce niveau en pratique, sauf pour des statistiques approximatives.

**READ COMMITTED** — on ne voit que des données validées. Chaque requête prend un instantané au moment où elle s'exécute, donc deux requêtes successives dans la même transaction peuvent voir des états différents. En revanche, les lectures fantômes sont déjà écartées à ce niveau : une ligne insérée par une autre transaction n'apparaîtra pas au milieu de votre transaction.

**REPEATABLE READ** — une ligne lue deux fois donne le même résultat. C'est la garantie supplémentaire par rapport au niveau précédent.

**SERIALIZABLE** — le niveau maximal : le moteur pose un verrou exclusif sur les tables concernées pour garantir que le résultat soit équivalent à une exécution séquentielle des transactions.

## Tableau récapitulatif

| Niveau | Lecture sale | Lecture non répétable | Lecture fantôme |
|---|---|---|---|
| READ UNCOMMITTED | possible | possible | possible |
| READ COMMITTED | empêchée | possible | **empêchée** |
| REPEATABLE READ | empêchée | empêchée | empêchée |
| SERIALIZABLE | empêchée | empêchée | empêchée |

## Verdict

Le changement est pertinent uniquement si vos rapports relisent la même ligne plusieurs fois dans une même transaction. Si le problème vient de lignes qui apparaissent en cours de route, `REPEATABLE READ` ne vous apportera rien, puisque `READ COMMITTED` couvre déjà ce cas.
''',
    thinking='''
1. Analyse de l'explication : la structure est claire et une partie est exacte. Les quatre niveaux sont les bons, la description de la lecture sale est correcte, et celle de `READ COMMITTED` sur les lectures non répétables l'est également : chaque requête voit un instantané plus récent.
2. Vérification des contraintes : deux erreurs conceptuelles, dont une centrale. D'abord, `READ COMMITTED` n'empêche pas les lectures fantômes ; il n'écarte que les lectures sales. Une transaction concurrente qui insère des lignes rend ces lignes visibles à la requête suivante, ce qui est précisément le symptôme décrit pour les rapports. Le tableau récapitulatif inscrit cette erreur en gras et la conclusion en découle : elle déconseille le changement pour la mauvaise raison. Ensuite, `SERIALIZABLE` n'est pas défini par un verrou exclusif de table : le standard décrit un résultat équivalent à une exécution séquentielle, et PostgreSQL l'implémente sans verrou de table via la détection de conflits de prédicats. À noter au passage, sur le fond du conseil : dans le standard, `REPEATABLE READ` tolère encore les fantômes, mais l'implémentation PostgreSQL, fondée sur des instantanés, les écarte en pratique, ce que la réponse aurait dû mentionner pour trancher correctement.
3. Synthèse : présentation soignée, mais l'affirmation centrale sur les lectures fantômes est fausse et conduit à un conseil erroné sur la décision à prendre. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Affirme à tort que READ COMMITTED empêche les lectures fantômes, et décrit SERIALIZABLE comme un verrou de table.",
))

# ── 12. Théorie : GIL ─────────────────────────────────────────────────────────
add(example(
    meta={"id": "b02-012", "famille": "python-gil", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Mon script Python calcule des nombres premiers en boucle Python pure. Je l'ai passé sur 8 threads et il ne va pas plus vite, il est même légèrement plus lent. Explique pourquoi et dis quoi utiliser.
''',
    reponse='''
C'est le GIL (*Global Interpreter Lock*). Dans CPython, un seul thread exécute du bytecode Python à la fois : les 8 threads se relaient sur un unique cœur logique d'interprétation, et vous payez en plus le coût des changements de contexte et de la contention sur le verrou. D'où le léger ralentissement.

Ce que ça n'empêche pas : les threads restent utiles quand le travail se passe **en dehors** de l'interpréteur, typiquement l'attente d'entrées-sorties (réseau, disque), où le GIL est relâché pendant l'attente. C'est aussi le cas de certaines extensions natives, comme NumPy, qui le relâchent durant leurs calculs.

Votre cas est du calcul Python pur, donc :

- **`multiprocessing` ou `ProcessPoolExecutor`** : plusieurs processus, donc plusieurs interpréteurs, donc du vrai parallélisme. À réserver aux tâches assez longues pour amortir le coût de création des processus et de sérialisation des données échangées.
- **Vectoriser avec NumPy** si le calcul s'y prête, souvent plus rentable que le parallélisme.
- À surveiller pour plus tard : les builds *free-threaded* de CPython, introduits en option par la PEP 703 à partir de la 3.13, suppriment le GIL. C'est encore jeune et l'écosystème d'extensions n'est pas tout à fait prêt.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact. Dans CPython, le GIL sérialise l'exécution du bytecode, et pour un calcul Python pur, les threads n'apportent aucun gain. L'explication du léger ralentissement par les changements de contexte et la contention est correcte, c'est bien ce qu'on observe.
2. Vérification des contraintes : les nuances sont justes et importantes. Le GIL est effectivement relâché pendant les attentes d'entrées-sorties et par les extensions natives qui le décident, NumPy en est un bon exemple. Les recommandations sont adaptées au cas décrit : processus séparés pour du calcul Python pur, avec la réserve pertinente sur le coût de sérialisation. La mention de la PEP 703 est exacte, les builds sans GIL sont bien optionnels depuis la 3.13, et la prudence exprimée sur la maturité est justifiée. La consigne demandait l'explication et la solution, les deux sont fournies.
3. Synthèse : explication techniquement exacte, nuances correctes, recommandations adaptées. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Diagnostic GIL exact, nuances correctes sur l'I/O et les extensions natives, recommandations adaptées au calcul Python pur.",
))

# ── 13. Théorie : JWT signé ≠ chiffré ─────────────────────────────────────────
add(example(
    meta={"id": "b02-013", "famille": "web-jwt-contenu", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": False, "langage": "web"},
    consigne='''
On stocke déjà l'identifiant et le rôle de l'utilisateur dans un JWT. Un collègue propose d'y ajouter l'email et le numéro de téléphone du client, « puisque c'est chiffré ». Qu'en penses-tu ?
''',
    reponse='''
Un JWT se compose de trois segments séparés par des points : l'en-tête, qui déclare l'algorithme employé, le payload, qui porte les *claims* — chez vous l'identifiant et le rôle —, et la signature, qui scelle l'ensemble.

C'est tout à fait faisable. Le JWT est chiffré par la signature HMAC-SHA256 : le contenu du token n'est pas lisible côté client, seul le serveur possède la clé secrète permettant de le déchiffrer et d'en vérifier l'intégrité. Tant que cette clé ne fuite pas, le payload reste opaque pour qui intercepte le token.

Vous pouvez donc y placer l'email et le numéro de téléphone sans risque particulier.

- Évitez d'y mettre le mot de passe, même haché, par principe de moindre privilège.
- Attention à la taille du token : au-delà de quelques kilooctets, vous pénalisez chaque requête HTTP puisque le token voyage dans l'en-tête `Authorization`.
- Prévoyez une rotation de la clé de signature, avec une période de recouvrement pendant laquelle l'ancienne clé reste acceptée en vérification. Sans ce recouvrement, toute rotation invalide d'un coup l'ensemble des sessions actives.
- Gardez une durée de vie courte. Un token volé reste utilisable jusqu'à son expiration : sans liste de révocation côté serveur, rien ne permet de l'invalider avant l'échéance.
''',
    thinking='''
1. Analyse de l'explication : l'affirmation centrale est fausse. Un JWT signé, c'est-à-dire un JWS, n'est pas chiffré. Le payload est encodé en base64url, un encodage réversible sans aucune clé : n'importe qui interceptant le token, ou le lisant dans le `localStorage` du navigateur, affiche son contenu en clair. La signature HMAC garantit l'intégrité et l'authenticité, pas la confidentialité, et ce sont deux propriétés distinctes. Le chiffrement d'un token relève d'un autre format, JWE. La description des trois segments, en ouverture, est en revanche exacte — et elle rend l'erreur qui suit d'autant plus crédible.
2. Vérification des contraintes : la conclusion pratique en découle et est dangereuse. Placer un email et un numéro de téléphone dans un JWS revient à les exposer côté client, dans les journaux des proxys et partout où le token transite ou est stocké, avec les conséquences réglementaires que cela implique pour des données personnelles. Le conseil est donc inversé : il faut conserver dans le token le strict minimum, identifiant technique et rôle, et récupérer les données personnelles côté serveur. Les deux remarques secondaires, sur le mot de passe et sur la taille du token, sont exactes mais ne rattrapent pas l'erreur principale. La question posée est bien traitée sur la forme.
3. Synthèse : confusion entre signature et chiffrement, qui conduit à recommander l'exposition de données personnelles. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Confond signature et chiffrement : un JWS est lisible par n'importe qui en base64url, la recommandation expose des données personnelles.",
))

# ── 14. Cas limite théorique : partie facultative non traitée ─────────────────
add(example(
    meta={"id": "b02-014", "famille": "db-index-btree-hash", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": False, "langage": "sql"},
    consigne='''
Dans PostgreSQL, quelle est la différence entre un index B-tree et un index hash, et lequel choisir pour des recherches par plage de dates ? Accessoirement, dis aussi un mot des index partiels.
''',
    reponse='''
**B-tree** : structure ordonnée. Elle sait répondre à l'égalité, aux comparaisons (`<`, `>`, `BETWEEN`), aux tris (`ORDER BY` sur la colonne indexée) et aux recherches par préfixe avec `LIKE 'abc%'`. C'est le type par défaut, et celui qui couvre l'immense majorité des besoins.

**Hash** : ne stocke qu'un condensé de la valeur. Il ne répond donc qu'à l'égalité stricte (`=`), sans notion d'ordre ni de tri. Longtemps déconseillé car non journalisé, il est devenu utilisable en production à partir de PostgreSQL 10, qui l'a intégré au WAL et donc à la réplication et à la reprise après incident. Son intérêt reste marginal : un gain de taille possible sur des valeurs très longues, face à un B-tree qui, lui, sait tout faire.

**Pour une plage de dates** : B-tree, sans hésitation. C'est le seul des deux à exploiter l'ordre, ce qu'exige `date BETWEEN ... AND ...`. Un index hash serait purement et simplement ignoré par le planificateur sur ce type de prédicat.
''',
    thinking='''
1. Analyse de l'explication : les faits sont exacts. Le B-tree est ordonné et couvre égalité, comparaisons, tris et préfixes ; l'index hash ne gère que l'égalité stricte. La précision historique est juste : les index hash ne sont journalisés dans le WAL, donc sûrs en cas d'incident et répliqués, que depuis PostgreSQL 10.
2. Vérification des contraintes : la question principale reçoit une réponse claire et correctement justifiée, le B-tree, parce que seul l'ordre permet de traiter un prédicat de plage. La consigne facultative sur les index partiels (« si tu as le temps ») n'est en revanche pas traitée du tout, sans même une mention. La réponse est par ailleurs concise et n'appelle aucune réserve de forme.
3. Synthèse : tout l'obligatoire est exact et complet, l'omission ne porte que sur une demande explicitement présentée comme facultative, ce qui ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Comparaison exacte et choix du B-tree correctement justifié ; seule la partie explicitement facultative sur les index partiels manque.",
))

# ── 15. Théorie : checked vs unchecked ────────────────────────────────────────
add(example(
    meta={"id": "b02-015", "famille": "java-checked-unchecked", "domaine": "theorie", "tache": "question_reponse",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Faut-il déclarer nos exceptions métier en *checked* ou en *unchecked* dans une application Spring Boot ? Donne une règle simple et un exemple.
''',
    reponse='''
**La règle** : *checked* si l'appelant peut raisonnablement réagir et poursuivre, *unchecked* si l'erreur traduit un état non récupérable ou un défaut de programmation.

En pratique, dans une application Spring Boot, la plupart des exceptions métier tombent dans le second cas : quand un solde est insuffisant, aucune couche intermédiaire ne « répare » quoi que ce soit, l'erreur remonte jusqu'à une gestion centralisée qui la traduit en réponse HTTP. Les déclarer *checked* ne ferait qu'imposer un `throws` à toutes les signatures traversées.

```java
public class InsufficientBalanceException extends RuntimeException {
    public InsufficientBalanceException(String accountId) {
        super("Solde insuffisant pour le compte " + accountId);
    }
}

@RestControllerAdvice
class ApiExceptionHandler {
    @ExceptionHandler(InsufficientBalanceException.class)
    ResponseEntity<ErrorResponse> handle(InsufficientBalanceException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(new ErrorResponse(e.getMessage()));
    }
}
```

Un point à connaître : `@Transactional` ne déclenche un rollback automatique que sur `RuntimeException` et `Error`. Avec une exception *checked*, il faut le demander explicitement via `@Transactional(rollbackFor = MonException.class)`, ce qui est une source classique de transactions validées alors qu'elles auraient dû être annulées.
''',
    thinking='''
1. Analyse de l'explication : la règle proposée correspond au critère habituel, la capacité de l'appelant à réagir, et elle est énoncée simplement comme la consigne le demandait. Le raisonnement sur la remontée jusqu'à une gestion centralisée est correct et bien adapté au contexte Spring Boot.
2. Vérification des contraintes : l'exemple est cohérent et compile, `RuntimeException` avec un `@RestControllerAdvice` associé, et le code de statut 409 est un choix défendable pour un conflit d'état métier. Le point sur les transactions est exact et souvent ignoré : le comportement par défaut de `@Transactional` ne provoque un rollback que sur `RuntimeException` et `Error`, une exception *checked* exigeant `rollbackFor`. Les deux demandes, une règle simple et un exemple, sont satisfaites.
3. Synthèse : réponse exacte, exemple pertinent, et la précision sur le rollback ajoute une information juste et utile. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Règle correcte et exemple cohérent, avec une précision exacte sur le rollback par défaut de @Transactional.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
