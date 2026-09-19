#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_04.jsonl (15 examples).

Chaque chiffre cité dans les <thinking> vient des sondes probe04.* exécutées le 2026-09-12
(Probe04.java, probe04.py, probe04.ts).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402

EXAMPLES = []
add = EXAMPLES.append

# ── 1. CME intermittente : explication correcte du quirk hasNext() ────────────
add(example(
    meta={"id": "b04-001", "famille": "java-cme-intermittente", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Ce code lève parfois `ConcurrentModificationException`, parfois non, et je n'arrive pas à comprendre la règle. Explique et corrige.

```java
List<String> items = new ArrayList<>(source);
for (String s : items) {
    if (shouldRemove(s)) {
        items.remove(s);
    }
}
```
''',
    reponse='''
Ce n'est pas aléatoire : cela dépend de la **position** de l'élément supprimé.

La boucle `for-each` s'appuie sur un itérateur qui compare un compteur de modifications à celui de la liste. Ce contrôle a lieu dans `next()`, pas dans `hasNext()`. Or `hasNext()` se contente de tester `cursor != size`.

Quand vous supprimez l'avant-dernier élément, la taille descend à la valeur du curseur : `hasNext()` renvoie `false`, la boucle s'arrête **avant** le prochain `next()`, et l'exception n'est jamais levée. Le dernier élément n'est simplement jamais examiné. Dans tous les autres cas, le `next()` suivant détecte la modification et lève `ConcurrentModificationException`.

C'est le pire des deux mondes : une exception dans certains cas, une boucle silencieusement incomplète dans les autres.

La correction :

```java
items.removeIf(this::shouldRemove);
```

Ou, s'il faut plus qu'une suppression, l'itérateur explicite :

```java
for (Iterator<String> it = items.iterator(); it.hasNext(); ) {
    String s = it.next();
    if (shouldRemove(s)) {
        it.remove();
    }
}
```
''',
    thinking='''
1. Analyse de l'explication : le mécanisme décrit correspond au code réel d'`ArrayList.Itr`. Le contrôle `checkForComodification` est bien dans `next()`, et `hasNext()` se limite à `cursor != size`. La conséquence annoncée est donc exacte.
2. Vérification des contraintes : sur une liste de quatre éléments dont on retire le deuxième, `ConcurrentModificationException` est levée. Sur une liste `["a", "b"]` dont on retire `"a"`, c'est-à-dire l'avant-dernier, aucune exception n'est levée et la liste finale vaut `[b]` : la boucle s'est arrêtée sans examiner le dernier élément, exactement comme décrit. Les deux corrections proposées sont valides, `removeIf` donnant `[a, c, d]` sur le cas à quatre éléments. La remarque sur la boucle silencieusement incomplète est le point important, souvent oublié dans les réponses à cette question.
3. Synthèse : explication exacte du mécanisme, cas intermittent correctement expliqué, corrections valides. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Explique exactement le quirk hasNext()/next(), y compris la boucle silencieusement incomplète.",
))

# ── 2. Arrays.asList : affirmation d'immuabilité fausse ───────────────────────
add(example(
    meta={"id": "b04-002", "famille": "java-arrays-aslist", "domaine": "code", "tache": "refactoring",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
On veut exposer une liste de configuration en lecture seule. Actuellement :

```java
public List<String> allowedHosts() {
    return new ArrayList<>(hosts);
}
```

Propose une version qui empêche l'appelant de modifier la liste, et explique la garantie obtenue.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse du code : l'affirmation d'immuabilité est fausse. `Arrays.asList` renvoie une vue de taille fixe, pas une liste immuable : `add` et `remove` lèvent bien `UnsupportedOperationException`, mais `set` est parfaitement autorisé et écrit dans le tableau sous-jacent. `Arrays.asList("a", "b").set(0, "z")` réussit et la liste devient `[z, b]`, là où `List.of("a", "b").set(0, "z")` lève bien `UnsupportedOperationException`. Les trois développements annexes sont pourtant exacts : l'idiome `toArray(new String[0])` est bien le plus rapide, l'exposition de la représentation interne est bien le défaut que signalerait un analyseur sur un `return hosts`, et la copie systématique de `new ArrayList<>` a bien un coût.
2. Vérification des contraintes : la consigne demandait d'empêcher l'appelant de modifier la liste et d'expliquer la garantie obtenue. La garantie annoncée n'existe pas : un appelant peut remplacer n'importe quel élément. Le fait que le tableau soit ici fraîchement créé par `toArray` limite les dégâts au seul appelant, mais la réponse affirme explicitement une protection totale, y compris contre `set`, ce qui est faux et pourrait justifier de supprimer une copie défensive ailleurs. Les solutions correctes sont `List.copyOf(hosts)` ou `Collections.unmodifiableList`, cette dernière restant une vue sur la liste source.
3. Synthèse : le code compile et bloque `add` et `remove`, mais la garantie centrale annoncée est fausse et la consigne d'immuabilité n'est pas satisfaite. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="Arrays.asList est de taille fixe, pas immuable : set() est autorisé, la garantie annoncée n'existe pas.",
))

# ── 3. Réutilisation d'un Stream ──────────────────────────────────────────────
add(example(
    meta={"id": "b04-003", "famille": "java-stream-reutilise", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Ce code lève `IllegalStateException` à la deuxième utilisation, je ne comprends pas pourquoi.

```java
Stream<Order> orders = repository.findAll().stream();
long count = orders.count();
List<Order> recent = orders.filter(Order::isRecent).toList();
```
''',
    reponse='''
Un `Stream` est à usage unique. Il est consommé par sa première opération terminale, ici `count()`, puis marqué comme fermé. Toute réutilisation lève `IllegalStateException: stream has already been operated upon or closed`. Ce n'est pas une collection : il ne stocke rien et ne se rembobine pas.

Deux options selon votre besoin.

Si la source est réutilisable, ouvrez deux flux :

```java
List<Order> all = repository.findAll();
long count = all.size();
List<Order> recent = all.stream().filter(Order::isRecent).toList();
```

Si vous voulez ne parcourir qu'une fois, faites-le en une seule passe :

```java
List<Order> recent = repository.findAll().stream()
        .filter(Order::isRecent)
        .toList();
long count = all.size();   // ou un Collectors.teeing si les deux résultats viennent du même flux
```
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact. Un flux est consommé par sa première opération terminale et ne peut pas être réutilisé. Un second appel à `count()` sur le même flux lève `IllegalStateException` avec le message « stream has already been operated upon or closed », cité correctement dans la réponse.
2. Vérification des contraintes : la première correction est la bonne dans le cas présent, puisque `findAll()` renvoie une collection : `size()` évite même de parcourir quoi que ce soit. La mention de `Collectors.teeing` est pertinente pour le cas où la source ne serait parcourable qu'une fois, comme un flux d'entrée. La distinction rappelée entre flux et collection est juste et répond à l'incompréhension exprimée dans la question.
3. Synthèse : cause exacte, message d'erreur correctement cité, corrections adaptées aux deux situations. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Diagnostic exact du flux à usage unique, message d'exception correctement cité et corrections adaptées.",
))

# ── 4. Monnaie en double ──────────────────────────────────────────────────────
add(example(
    meta={"id": "b04-004", "famille": "java-monnaie-double", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
Écris une méthode Java qui additionne les lignes d'un panier et applique une remise en pourcentage. Les montants sont en euros, le résultat sera affiché sur une facture.
''',
    reponse='''
```java
public static double total(List<Line> lines, double discountPercent) {
    double sum = 0;
    for (Line line : lines) {
        sum += line.unitPrice() * line.quantity();
    }
    double discounted = sum * (1 - discountPercent / 100);
    return Math.round(discounted * 100) / 100.0;
}
```

1. **Somme des lignes.** Chaque ligne contribue pour `unitPrice × quantity`, la boucle accumule dans `sum`.
2. **Application de la remise.** `discountPercent` est exprimé en pourcentage, d'où la division par 100 avant de retrancher de 1 : une remise de 20 % donne un facteur `0.8`.
3. **Arrondi de présentation.** `Math.round(x * 100) / 100.0` est l'idiome habituel pour ramener à deux décimales : on décale de deux rangs, on arrondit à l'entier le plus proche, on redivise.

`Math.round` arrondit au plus proche et départage les cas d'égalité vers le haut, ce qui correspond à la convention commerciale attendue sur une facture. Attention toutefois si vous manipulez des avoirs : le départage se faisant toujours vers le haut, il se fait vers zéro pour les valeurs négatives, ce qui n'est pas forcément la convention de votre comptabilité.

Le pourcentage est pris en `double` plutôt qu'en entier pour accepter les remises fractionnaires, par exemple 2,5 % sur un accord cadre. La méthode est statique parce qu'elle ne dépend d'aucun état de l'instance, ce qui la rend triviale à tester isolément.

L'arrondi final à deux décimales par `Math.round` élimine les imprécisions du calcul en virgule flottante, le montant affiché sur la facture sera donc exact.
''',
    thinking='''
1. Analyse du code : la logique de calcul est correcte, mais le type ne l'est pas pour de la monnaie. `double` est binaire : il ne représente pas exactement les décimales usuelles. Additionner dix fois `0.1` donne `0.9999999999999999`, différent de `1.0`, et `0.1 + 0.2` donne `0.30000000000000004`. Sur un panier de plusieurs lignes, l'erreur s'accumule avant l'arrondi. Les explications ajoutées sont exactes prises isolément, y compris la remarque sur le départage vers le haut de `Math.round` et son effet vers zéro sur les négatifs.
2. Vérification des contraintes : l'affirmation finale est fausse. `Math.round` n'élimine pas l'imprécision, il la masque au dernier moment : le total intermédiaire reste faux, et une valeur qui tombe juste sur un demi-centime peut basculer du mauvais côté selon l'erreur accumulée. C'est aussi une divergence classique avec le calcul de TVA fait ailleurs dans le système, qui produit des factures qui ne s'équilibrent pas au centime. Pour de la monnaie destinée à une facture, il faut `BigDecimal` avec un mode d'arrondi explicite : `new BigDecimal("0.10").multiply(BigDecimal.valueOf(3))` donne `0.30`, et l'arrondi `HALF_UP` de `0.615` à deux décimales donne bien `0.62`. Une alternative acceptable est de compter en centimes avec des entiers longs. Le soin apporté au détail du mode d'arrondi rend la conclusion d'autant plus convaincante, alors qu'elle porte sur le mauvais problème.
3. Synthèse : le calcul paraît juste et l'arrondi rassure, mais le type choisi est inadapté à un montant facturé et l'explication affirme une exactitude qui n'existe pas. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Calcul monétaire en double : l'erreur s'accumule avant l'arrondi, et Math.round ne rend pas le total exact.",
))

# ── 5. Cas limite : refactoring correct mais très verbeux ─────────────────────
add(example(
    meta={"id": "b04-005", "famille": "java-concat-boucle", "domaine": "code", "tache": "refactoring",
          "cas": "limite", "verbeux": True, "langage": "java"},
    consigne='''
Cette méthode est lente sur de gros volumes, optimise-la.

```java
public String buildCsvLine(List<String> values) {
    String line = "";
    for (String value : values) {
        line += value + ";";
    }
    return line;
}
```
''',
    reponse='''
## Le problème

Les `String` sont immuables en Java. Chaque `+=` dans la boucle crée donc un nouvel objet et recopie l'intégralité du contenu déjà accumulé. Le coût total est quadratique : pour *n* valeurs, on copie de l'ordre de *n²/2* caractères. Le compilateur sait optimiser une concaténation isolée, mais il ne peut pas sortir l'allocation d'une boucle.

## La correction

```java
public String buildCsvLine(List<String> values) {
    StringBuilder line = new StringBuilder();
    for (String value : values) {
        line.append(value).append(';');
    }
    return line.toString();
}
```

`StringBuilder` maintient un tampon redimensionné par doublement, ce qui ramène le coût à un amorti linéaire.

## Variante avec l'API Stream

Si le séparateur final vous gêne, `String.join` ou un `Collectors.joining` sont plus expressifs :

```java
return String.join(";", values);
```

Attention, ce n'est pas strictement équivalent : `String.join` ne met pas de séparateur final, alors que votre version en ajoute un après la dernière valeur.

## Mesure

Sur 20 000 concaténations, l'écart est déjà d'un ordre de grandeur en faveur de `StringBuilder`. Sur 100 000, la version d'origine devient inutilisable.

## Autres pistes

Si vous générez beaucoup de lignes, pensez à pré-dimensionner le tampon avec `new StringBuilder(estimation)`, à réutiliser un même `StringBuilder` entre les lignes, ou à écrire directement dans un `Writer` bufferisé plutôt que de construire la chaîne en mémoire.
''',
    thinking='''
1. Analyse du code : le diagnostic et la correction sont exacts. L'immuabilité des `String` rend la concaténation en boucle quadratique, `StringBuilder` la ramène à un coût amorti linéaire par doublement du tampon, et la remarque sur l'optimisation du compilateur, valable pour une concaténation isolée mais pas à travers une boucle, est correcte. Sur 20 000 itérations, l'écart est de l'ordre de 15 ms pour la version `+=` contre moins d'une milliseconde pour `StringBuilder`, ce qui correspond bien à l'ordre de grandeur annoncé.
2. Vérification des contraintes : la version proposée préserve exactement le comportement d'origine, séparateur final compris. La réponse signale d'ailleurs d'elle-même que `String.join` n'est pas équivalent sur ce point précis, ce qui évite un piège réel. Deux écarts mineurs : la réponse est nettement plus longue que ce qu'appelait la demande, avec une variante Stream et une section « autres pistes » non sollicitées. Rien de faux, rien qui masque le correctif.
3. Synthèse : l'optimisation demandée est correcte et sans changement de comportement ; seule la longueur dépasse le nécessaire, ce qui ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Optimisation correcte, comportement préservé y compris le séparateur final ; seule la verbosité est excessive.",
))

# ── 6. Changement d'heure : arithmétique sur datetime aware, verbeux ──────────
add(example(
    meta={"id": "b04-006", "famille": "python-dst-timedelta", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": True, "langage": "python"},
    consigne='''
Nos rappels programmés « dans une heure » tombent au mauvais moment la nuit du changement d'heure. On utilise :

```python
reminder_at = scheduled_at + timedelta(hours=1)
```

avec `scheduled_at` un `datetime` conscient du fuseau `Europe/Paris`. Explique et corrige.
''',
    reponse='''
## Ce qui se passe

Le problème est classique et vient du fait qu'un `datetime` conscient du fuseau porte un décalage, et que ce décalage change deux fois par an.

Rappelons le mécanisme : dans la nuit du dernier dimanche de mars, à 2 h locales, les horloges avancent à 3 h. L'heure locale 2 h 30 n'existe donc pas ce jour-là, et le décalage passe de +01:00 à +02:00.

## Ce que fait votre code

Bonne nouvelle : `zoneinfo` gère ce cas pour vous. Comme `scheduled_at` est conscient du fuseau, l'addition d'un `timedelta` recalcule le décalage à l'arrivée. Partant de 1 h 30 heure de Paris, vous obtenez donc 3 h 30 avec un décalage de +02:00, soit exactement une heure réelle plus tard.

## Alors d'où vient le décalage observé ?

De vos données d'entrée. Si `scheduled_at` a été construit sans fuseau, puis attaché après coup, ou s'il provient d'une base qui stocke du naïf, l'arithmétique s'applique à un instant mal défini.

```python
# à faire à la lecture
scheduled_at = scheduled_at.replace(tzinfo=ZoneInfo("Europe/Paris"))
reminder_at = scheduled_at + timedelta(hours=1)
```

## À retenir

| Type de datetime | `+ timedelta` gère le changement d'heure |
|---|---|
| naïf | non |
| conscient du fuseau | oui ✅ |
''',
    thinking='''
1. Analyse de l'explication : la description du changement d'heure est exacte, avec l'heure locale qui saute de 2 h à 3 h et le décalage qui passe de +01:00 à +02:00. Le reste est faux.
2. Vérification des contraintes : l'affirmation centrale, selon laquelle l'addition d'un `timedelta` sur un `datetime` conscient du fuseau recalculerait le décalage, est démentie par l'exécution. En partant de `2026-03-29 01:30:00+01:00` à Paris, l'ajout d'une heure donne `2026-03-29 02:30:00+01:00` : le décalage reste à +01:00 et le résultat désigne une heure locale qui n'existe pas cette nuit-là. L'arithmétique sur `datetime` est délibérément « naïve sur le mur d'horloge », elle ajoute au champ heure sans consulter la base de fuseaux. La correction proposée, un `replace(tzinfo=...)` sur les données d'entrée, ne change rien à ce comportement et le tableau final inscrit l'erreur. La méthode correcte est de calculer en UTC, `dt.astimezone(timezone.utc) + timedelta(hours=1)`, puis de reconvertir, ou d'appeler `normalize` selon la bibliothèque utilisée.
3. Synthèse : contexte correctement posé, mais le diagnostic est inversé, le bug réel est attribué aux données d'entrée et la correction proposée laisse le défaut intact. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="Affirme à tort que l'addition d'un timedelta recalcule le décalage : 01:30+01:00 + 1h donne 02:30+01:00, heure inexistante.",
))

# ── 7. Copie superficielle présentée comme une isolation ──────────────────────
add(example(
    meta={"id": "b04-007", "famille": "python-copie-superficielle", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Écris une fonction `with_extra_tag(config, tag)` qui renvoie une **nouvelle** configuration avec un tag supplémentaire, sans modifier la configuration reçue. `config` est un dictionnaire dont la clé `tags` contient une liste.
''',
    reponse='''
```python
def with_extra_tag(config, tag):
    new_config = dict(config)
    new_config["tags"].append(tag)
    return new_config
```

`dict(config)` crée un nouveau dictionnaire indépendant de l'original, on peut donc modifier son contenu sans risque pour l'appelant.

La copie profonde recopierait récursivement toute la structure, y compris des objets qui n'ont aucune raison d'être dupliqués : une connexion, un client HTTP, un enregistreur de journaux rangés dans la configuration. C'est coûteux dès que la configuration s'étoffe, et cela casse l'identité des objets partagés, ce qui produit des surprises partout où du code compare avec `is`.

`dict(config)` et `config.copy()` sont strictement équivalents ici, et `{**config}` donne le même résultat avec une syntaxe plus moderne. Le choix relève du style de la base de code, pas du comportement.

La signature gagnerait à être annotée, ce qui documente le contrat de retour aussi bien pour le lecteur que pour l'analyseur :

```python
def with_extra_tag(config: dict[str, Any], tag: str) -> dict[str, Any]:
```

Les génériques natifs `dict[str, Any]` demandent Python 3.9 ou plus récent, sans quoi il faut passer par `typing.Dict`.
''',
    thinking='''
1. Analyse du code : `dict(config)` crée bien un nouveau dictionnaire, mais c'est une copie **superficielle** : les valeurs sont partagées, et la clé `tags` référence la même liste que l'original. L'`append` modifie donc la liste de l'appelant. Les développements annexes sont exacts — `deepcopy` recopie bien récursivement et casse l'identité des objets partagés, les trois formes d'écriture citées sont bien équivalentes, et les génériques natifs demandent bien Python 3.9 — mais aucun ne porte sur le point qui décide du résultat.
2. Vérification des contraintes : avec `original = {"tags": ["a", "b"], "n": 1}`, un `append` sur la copie superficielle laisse `original` à `{"tags": ["a", "b", "c"], "n": 1}` : la mutation a bien traversé la copie, et `dict(original)["tags"] is original["tags"]` renvoie `True`. La consigne exigeait explicitement de ne pas modifier la configuration reçue, ce n'est donc pas respecté, et l'explication affirme le contraire de ce qui se produit. La correction tient en une ligne sans copie profonde : `{**config, "tags": [*config["tags"], tag]}`, qui ne recopie que ce qui est modifié. Ironie du texte : la section qui écarte `deepcopy` frôle le sujet sans jamais voir que c'est précisément le partage des valeurs qui casse la fonction.
3. Synthèse : la fonction renvoie bien un nouveau dictionnaire, mais mute la liste de l'appelant, ce que la consigne interdisait explicitement. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="dict() est une copie superficielle : l'append modifie la liste de l'appelant.",
))

# ── 8. Retour arrière catastrophique corrigé ──────────────────────────────────
add(example(
    meta={"id": "b04-008", "famille": "python-regex-backtracking", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Notre validateur bloque le serveur sur certaines entrées utilisateur. Le motif est `^(\\w+\\s?)+$`, censé valider une suite de mots séparés par des espaces. Explique et corrige.
''',
    reponse='''
C'est un retour arrière catastrophique (*catastrophic backtracking*), et c'est exploitable comme déni de service, d'où le blocage du serveur.

Votre motif contient une quantification imbriquée : `\\w+` à l'intérieur d'un groupe lui-même répété par `+`. Sur une entrée qui ne correspond pas, le moteur doit essayer toutes les façons de découper la chaîne entre les deux quantificateurs, et ce nombre croît exponentiellement avec la longueur.

L'ordre de grandeur se mesure facilement sur le motif équivalent `^(a+)+$` : environ 8 ms pour 18 caractères non conformes, 113 ms pour 22, 454 ms pour 24. Chaque caractère supplémentaire double le temps.

La correction consiste à supprimer l'imbrication en décrivant la même langue sans ambiguïté :

```python
_WORDS = re.compile(r"^\\w+(?: \\w+)*$")
```

Ici, chaque caractère ne peut être consommé que d'une seule manière : plus d'explosion combinatoire. À titre de comparaison, un motif linéaire comme `^a+$` traite 100 000 caractères non conformes en 0,3 ms.

Deux garde-fous complémentaires : validez une longueur maximale d'entrée avant d'appliquer le motif, et si vous avez besoin de motifs fournis par les utilisateurs, utilisez un moteur à garantie linéaire comme le module `regex` avec délai, ou RE2.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact. `^(\\w+\\s?)+$` combine bien une quantification imbriquée, source classique d'explosion combinatoire lors du retour arrière, et la qualification en risque de déni de service est appropriée puisque l'entrée vient des utilisateurs.
2. Vérification des contraintes : les ordres de grandeur cités sont cohérents. Sur `^(a+)+$`, une entrée non conforme demande 0,008 s pour 18 caractères, 0,113 s pour 22 et 0,454 s pour 24, soit bien un doublement par caractère ajouté, et le motif linéaire `^a+$` traite 100 000 caractères en 0,0003 s. La correction proposée est juste : `^\\w+(?: \\w+)*$` rend le découpage déterministe, chaque espace n'appartenant qu'à une seule alternative. À noter que cette réécriture n'accepte plus l'espace optionnel en fin de chaîne que tolérait `\\s?`, un durcissement conforme à l'intention décrite dans la consigne. Les deux garde-fous complémentaires sont pertinents.
3. Synthèse : cause exacte, mesures conformes, correction qui supprime réellement l'imbrication. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Diagnostic exact du retour arrière catastrophique, mesures conformes et réécriture qui supprime l'imbrication.",
))

# ── 9. Perte de `this` en TypeScript ──────────────────────────────────────────
add(example(
    meta={"id": "b04-009", "famille": "ts-liaison-this", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "typescript"},
    consigne='''
Ce code lève `TypeError: Cannot read properties of undefined` au clic, alors que la méthode fonctionne quand je l'appelle normalement. Explique et corrige.

```ts
class Counter {
  private count = 0;
  increment(): void {
    this.count += 1;
  }
}

button.addEventListener("click", counter.increment);
```
''',
    reponse='''
En JavaScript, `this` est déterminé par la manière dont la fonction est **appelée**, pas par l'endroit où elle est définie. En écrivant `counter.increment`, vous passez la fonction seule : le lien avec l'instance est perdu. Au clic, l'écouteur l'appelle sans receveur, `this` vaut `undefined` en mode strict — et le code d'une classe est toujours en mode strict — d'où l'erreur sur `this.count`.

Trois corrections possibles, par ordre de préférence :

```ts
// 1. Fermeture explicite : la plus lisible
button.addEventListener("click", () => counter.increment());

// 2. Champ de classe fléché : `this` est capturé à la construction
class Counter {
  private count = 0;
  increment = (): void => {
    this.count += 1;
  };
}

// 3. Liaison explicite
button.addEventListener("click", counter.increment.bind(counter));
```

La deuxième option a un coût : la fonction est stockée par instance et non sur le prototype, ce qui pèse si vous créez beaucoup d'objets. Elle empêche aussi de la remplacer proprement dans une sous-classe.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact. La valeur de `this` dépend du site d'appel, et détacher la méthode de son receveur la perd. La précision selon laquelle le corps d'une classe est toujours en mode strict est correcte, et c'est bien elle qui explique `undefined` plutôt que l'objet global.
2. Vérification des contraintes : une méthode détachée puis appelée lève `TypeError: Cannot read properties of undefined (reading 'count')`, exactement le message signalé. Le champ fléché détaché fonctionne, tout comme la version liée par `bind` : les trois corrections proposées sont donc valides. La réserve sur le champ fléché est juste, la fonction est bien créée par instance au lieu d'être partagée sur le prototype, avec les conséquences annoncées sur la mémoire et la substitution en sous-classe.
3. Synthèse : cause exacte, message d'erreur reproduit, trois corrections valides et compromis correctement énoncés. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Diagnostic exact de la perte de receveur, message d'erreur reproduit et trois corrections valides.",
))

# ── 10. Théorie : tri par défaut en JavaScript ────────────────────────────────
add(example(
    meta={"id": "b04-010", "famille": "js-tri-par-defaut", "domaine": "theorie", "tache": "question_reponse",
          "cas": "parfait", "verbeux": False, "langage": "typescript"},
    consigne='''
Pourquoi `[10, 9, 1, 20].sort()` renvoie-t-il `[1, 10, 20, 9]` en JavaScript ? Réponse concise.
''',
    reponse='''
Parce que `Array.prototype.sort` **convertit les éléments en chaînes** et les compare selon l'ordre des unités de code UTF-16 quand aucun comparateur n'est fourni. `"10"` passe donc avant `"9"`, puisque `"1"` précède `"9"`.

```js
[10, 9, 1, 20].sort();              // [1, 10, 20, 9]
[10, 9, 1, 20].sort((a, b) => a - b); // [1, 9, 10, 20]
```

Deux précisions utiles :
- `sort` trie **en place** et renvoie la même référence, ce qui surprend quand on croit obtenir une copie.
- Depuis ES2019, le tri est garanti stable, donc l'ordre relatif des éléments jugés égaux est préservé.
''',
    thinking='''
1. Analyse de l'explication : la cause est exacte. Sans comparateur, `sort` convertit chaque élément en chaîne et compare les unités de code UTF-16, ce qui place `"10"` et `"20"` avant `"9"`. `[10, 9, 1, 20].sort()` renvoie bien `[1, 10, 20, 9]` et la version avec comparateur renvoie `[1, 9, 10, 20]`.
2. Vérification des contraintes : les deux précisions sont exactes et pertinentes. Le tri en place se constate directement, le tableau d'origine étant modifié et la valeur de retour étant la même référence. La stabilité garantie depuis ES2019 est correcte. La réponse tient en quelques lignes, comme demandé.
3. Synthèse : cause exacte, exemples conformes, précisions justes et format concis. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Cause exacte (comparaison de chaînes UTF-16), exemples conformes et précisions justes sur le tri en place et la stabilité.",
))

# ── 11. Théorie : précision des entiers JSON, erreur cachée, verbeux ──────────
add(example(
    meta={"id": "b04-011", "famille": "js-json-entiers-64", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": True, "langage": "typescript"},
    consigne='''
Notre API renvoie des identifiants sur 64 bits (`snowflake`). Un collègue s'inquiète de leur passage en JavaScript. Peut-on les manipuler sans risque en JSON ? Explique.
''',
    reponse='''
## Le contexte

Les nombres en JavaScript sont des flottants double précision IEEE 754. Ils disposent de 53 bits de mantisse, ce qui donne un entier sûr maximal de 2⁵³ − 1, soit `9007199254740991`, exposé par `Number.MAX_SAFE_INTEGER`.

## Ce qui se passe réellement

`JSON.parse` est plus robuste que ce qu'on lui prête : l'analyseur lit la représentation décimale complète et reconstruit la valeur exacte tant qu'elle tient dans les limites du format. Pour vos identifiants, la valeur relue est donc identique à l'originale.

La vérification est immédiate :

```js
const parsed = JSON.parse('{"id": 9007199254740993}');
parsed.id === 9007199254740993;   // true
```

Le test renvoie `true`, la valeur a donc bien traversé la sérialisation sans altération.

## Recommandation

Vous pouvez manipuler vos identifiants tels quels. Par prudence, ajoutez simplement un test d'égalité comme ci-dessus dans votre suite de tests d'intégration, il détectera toute régression éventuelle.

| Situation | Sûr ? |
|---|---|
| identifiant < 2⁵³ | oui |
| identifiant 64 bits via `JSON.parse` | oui ✅ |
| calcul arithmétique sur ces identifiants | à éviter |
''',
    thinking='''
1. Analyse de l'explication : le cadrage initial est exact. Les nombres JavaScript sont des flottants double précision, la mantisse de 53 bits fixe `Number.MAX_SAFE_INTEGER` à `9007199254740991`, valeur correctement citée.
2. Vérification des contraintes : la conclusion est fausse, et le raisonnement qui la soutient est un piège. `JSON.parse` produit un `Number`, donc la valeur est arrondie dès l'analyse : `JSON.parse('{"id": 9007199254740993}')` renvoie `9007199254740992`, l'identifiant est bien corrompu. Le test proposé renvoie effectivement `true`, mais pour une raison qui invalide la démonstration : le littéral `9007199254740993` écrit dans le code source subit exactement le même arrondi, on compare donc deux valeurs également fausses. C'est le pire des cas, un contrôle qui passe alors que la donnée est déjà perdue, et la réponse le recommande comme garde-fou en intégration. La solution correcte est de transporter ces identifiants en chaînes de caractères dans le JSON, ou d'utiliser un analyseur qui produit des `BigInt`.
3. Synthèse : bases exactes, mais la conclusion affirme l'inverse du comportement réel et le test proposé donne une fausse assurance. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="JSON.parse arrondit l'identifiant (…993 devient …992) ; le test d'égalité proposé passe car le littéral subit le même arrondi.",
))

# ── 12. Théorie : == vs === ───────────────────────────────────────────────────
add(example(
    meta={"id": "b04-012", "famille": "js-egalite-lache", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": False, "langage": "typescript"},
    consigne='''
Explique la différence entre `==` et `===` en JavaScript, et donne la règle à suivre en pratique. En bonus, dis aussi un mot d'`Object.is`.
''',
    reponse='''
`===` compare type et valeur, sans conversion. `==` applique d'abord un ensemble de règles de conversion, puis compare.

Quelques résultats qui illustrent pourquoi ces règles sont difficiles à retenir :

```js
"" == 0;            // true
"0" == 0;           // true
"" == "0";          // false
null == undefined;  // true
null == 0;          // false
[] == false;        // true
```

Les trois premières lignes montrent que `==` n'est même pas transitif : `""` égale `0`, `"0"` égale `0`, mais `""` n'égale pas `"0"`.

**La règle** : utilisez `===` partout. La seule exception admise est `x == null`, qui teste en une fois `null` et `undefined`, précisément parce que ces deux valeurs sont mutuellement égales avec `==` et avec rien d'autre.
''',
    thinking='''
1. Analyse de l'explication : la distinction est exacte et les six résultats cités sont conformes. `"" == 0` et `"0" == 0` renvoient `true`, `"" == "0"` renvoie `false`, `null == undefined` renvoie `true`, `null == 0` renvoie `false`, et `[] == false` renvoie `true`.
2. Vérification des contraintes : l'observation sur la non-transitivité est correctement construite à partir des trois premiers cas, et c'est l'argument le plus parlant contre `==`. La règle pratique proposée est celle recommandée par les guides de style courants, et l'exception `x == null` est correctement justifiée : `null` et `undefined` ne sont mutuellement égaux qu'entre eux avec `==`. Les deux demandes obligatoires, la différence et la règle pratique, sont satisfaites. En revanche, `Object.is` n'est pas mentionné du tout, alors que la consigne le demandait — mais en le présentant explicitement comme facultatif (« si tu as le temps »).
3. Synthèse : tout l'obligatoire est exact, l'unique omission porte sur une demande explicitement facultative, ce qui ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Distinction exacte et six résultats de coercition exacts ; seule la mention d'Object.is, explicitement facultative, manque.",
))

# ── 13. Théorie Java : pile et tas ────────────────────────────────────────────
add(example(
    meta={"id": "b04-013", "famille": "java-pile-tas", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Un candidat m'a dit en entretien que « les objets vont sur le tas et les primitifs sur la pile ». C'est exact ? Explique ce qui se passe vraiment.
''',
    reponse='''
C'est une approximation qui devient fausse dès qu'on regarde de près.

Ce qui est vrai : les objets sont alloués sur le tas, et les **variables locales** de type primitif vivent dans le cadre de pile de la méthode.

Ce qui manque :

- Un champ primitif d'un objet est **dans l'objet**, donc sur le tas. Le `int count` d'une instance ne va pas sur la pile.
- Une variable locale de type référence est sur la pile, mais elle ne contient qu'une référence : l'objet pointé est sur le tas.
- Le tas lui-même est structuré, et la JVM déplace les objets : allocation dans l'eden, promotion vers les générations plus anciennes selon leur survie aux collectes.

Enfin, la spécification décrit un comportement, pas une implémentation. HotSpot pratique l'analyse d'échappement : quand il prouve qu'un objet ne sort pas de la méthode, il peut en éclater les champs et les traiter comme des variables locales, ce qui revient à supprimer l'allocation sur le tas. Ce n'est pas garanti et cela dépend du niveau de compilation atteint, mais cela suffit à disqualifier la règle apprise par cœur.
''',
    thinking='''
1. Analyse de l'explication : la correction apportée est exacte sur chaque point. Un champ primitif appartient à l'objet et réside donc sur le tas, une variable locale de type référence contient une référence vers un objet du tas, et la structuration du tas en générations avec allocation dans l'eden puis promotion correspond au fonctionnement des collecteurs générationnels de HotSpot.
2. Vérification des contraintes : la distinction finale entre spécification et implémentation est juste et bien amenée. L'analyse d'échappement est correctement décrite : HotSpot peut remplacer une allocation par des variables scalaires lorsqu'il prouve que l'objet ne s'échappe pas, et la réserve exprimée est appropriée, puisque cette optimisation dépend du compilateur JIT atteint et n'est jamais garantie. La réponse traite bien la question posée, à savoir dire si l'affirmation est exacte puis expliquer ce qui se passe réellement.
3. Synthèse : correction exacte de l'approximation, aucun raccourci fautif, nuance appropriée entre spécification et implémentation. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Corrige exactement l'approximation, y compris les champs primitifs sur le tas et la nuance sur l'analyse d'échappement.",
))

# ── 14. Théorie : idempotence REST ────────────────────────────────────────────
add(example(
    meta={"id": "b04-014", "famille": "rest-idempotence", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": False, "langage": "web"},
    consigne='''
Notre client mobile rejoue automatiquement les requêtes en cas de coupure réseau. Quelles méthodes HTTP peut-on rejouer sans risque, et que faire pour les autres ? En bonus, dis un mot de la clé d'idempotence.
''',
    reponse='''
La règle est simple : une méthode est rejouable si elle est idempotente, c'est-à-dire si l'exécuter plusieurs fois donne le même résultat que l'exécuter une fois.

- `GET` et `DELETE` sont idempotents, vous pouvez les rejouer.
- `POST` est idempotent dès lors que le serveur renvoie `200` plutôt que `201` : la ressource existant déjà, le second appel ne crée rien et se contente de renvoyer l'état courant. C'est le comportement par défaut de la plupart des frameworks REST.
- `PUT` n'est pas idempotent, car il écrase l'état existant : deux appels successifs peuvent laisser la ressource dans un état différent de celui attendu si une autre écriture s'est intercalée entre les deux.

En pratique, autorisez donc le rejeu sur `GET`, `DELETE` et `POST`, et bloquez-le sur `PUT`.
''',
    thinking='''
1. Analyse de l'explication : la définition initiale de l'idempotence est correcte, ainsi que le classement de `GET` et `DELETE`. Tout le reste est faux, et de manière symétrique.
2. Vérification des contraintes : selon la RFC 9110, `PUT` **est** idempotent : il remplace intégralement l'état de la ressource par la représentation fournie, donc rejouer la même requête aboutit au même état final. Le contre-exemple invoqué, une écriture concurrente intercalée, ne relève pas de l'idempotence mais de la concurrence, qui se traite par requête conditionnelle avec `If-Match`. À l'inverse, `POST` n'est **pas** idempotent, et le code de statut renvoyé n'y change rien : un code de statut décrit un résultat, il ne modifie pas la sémantique de la méthode. Prétendre que renvoyer `200` rend un `POST` rejouable est faux, et la recommandation finale est exactement inversée : rejouer les `POST` de création produira des doublons en cas de coupure réseau, ce qui est précisément le scénario décrit par la consigne. La bonne réponse consiste à rejouer `GET`, `PUT` et `DELETE`, et à protéger les `POST` par une clé d'idempotence fournie par le client et mémorisée par le serveur. La demande facultative sur la clé d'idempotence n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : les deux classements qui comptent sont inversés, et le conseil produirait des créations en double sur le cas d'usage décrit. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Inverse l'idempotence de PUT et POST : rejouer les POST créerait des doublons, ce que la consigne cherchait justement à éviter.",
))

# ── 15. Cas limite : contrainte de format explicite non respectée ─────────────
add(example(
    meta={"id": "b04-015", "famille": "db-verrous-optimistes", "domaine": "theorie", "tache": "question_reponse",
          "cas": "limite", "verbeux": True, "langage": "sql"},
    consigne='''
Explique la différence entre verrouillage optimiste et pessimiste, et dis lequel choisir pour notre back-office où deux gestionnaires éditent rarement la même fiche. **Contrainte : 5 lignes maximum**, c'est pour une note interne au format court.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse de l'explication : le contenu technique est exact. Le verrou pessimiste posé dès la lecture avec `SELECT ... FOR UPDATE`, la sérialisation des accès et le risque d'interblocage, le contrôle de version en optimiste avec le `UPDATE ... WHERE version = ?` qui affecte zéro ligne en cas de conflit : tout est correct, y compris la requête donnée en exemple. La recommandation finale est cohérente avec le contexte décrit, et l'argument sur les verrous tenus pendant le temps de réflexion humain est le bon.
2. Vérification des contraintes : la consigne impose explicitement 5 lignes maximum, en précisant l'usage, une note interne au format court. La réponse fait plus de vingt lignes, avec trois sections et un bloc de code. Ce n'est pas une préférence de style : c'est une exigence de format chiffrée et vérifiable, et le livrable demandé n'est pas utilisable tel quel. Le sujet se traite pourtant en cinq lignes, la matière essentielle tenant en une définition par mécanisme et une recommandation.
3. Synthèse : le fond est juste et la recommandation pertinente, mais la seule contrainte de forme imposée, chiffrée et non ambiguë, est dépassée d'un facteur quatre. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"format_impose": "La sortie respecte la limite de longueur chiffrée fixée par la requête."},
    extra_checks={"format_impose": False},
    raison="Contenu exact mais la contrainte explicite de 5 lignes maximum est dépassée d'un facteur quatre.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
