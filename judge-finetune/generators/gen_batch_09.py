#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_09.jsonl (15 examples, CODE_ANALYSIS).

Chiffres issus des sondes probe09.py, Probe09.java et probe09.js exécutées le 2026-09-13.
Polarités visées dans ce lot : validation_entree=false, dependance_autorisee=true,
signature_publique_inchangee=false, perimetre_respecte=true.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402

EXAMPLES = []
add = EXAMPLES.append

# ── 1-2. Paire contrastive : appel de commande externe ────────────────────────
CONSIGNE_CONVERT = '''
Écris la fonction qui convertit un document téléversé par l'utilisateur en PDF, en appelant l'outil en ligne de commande `convertisseur`. Le nom du fichier vient du formulaire. **Valide le nom reçu avant de l'utiliser.**
'''

add(example(
    meta={"id": "b09-001", "famille": "python-appel-commande", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": True, "langage": "python"},
    consigne=CONSIGNE_CONVERT,
    reponse='''
## Implémentation

```python
import subprocess

def convertir_en_pdf(nom_fichier: str) -> int:
    commande = f"convertisseur --input uploads/{nom_fichier} --output pdf/{nom_fichier}.pdf"
    resultat = subprocess.run(commande, shell=True, capture_output=True, text=True)
    return resultat.returncode
```

## Sur la validation demandée

Elle est implicite ici, et c'est même plus robuste ainsi. Le nom provient d'un champ de formulaire, donc d'une chaîne unique sans séparateur de chemin : le navigateur ne transmet jamais l'arborescence locale. Ajouter une expression régulière reviendrait à dupliquer une garantie déjà fournie par le protocole, avec le risque de rejeter des noms légitimes contenant des accents ou des espaces.

## Pourquoi `shell=True`

Le mode shell permet d'écrire la commande telle qu'on la taperait, ce qui la rend lisible et facile à recopier depuis un terminal pour déboguer. Sans lui, il faudrait découper les arguments à la main, ce qui est plus verbeux et source d'erreurs sur les chemins comportant des espaces.
''',
    thinking='''
1. Analyse du code : la fonction appelle bien l'outil et renvoie son code de retour, mais elle interpole une valeur d'origine utilisateur dans une chaîne exécutée par un interpréteur de commandes. C'est une injection de commande, la variante la plus directe qui soit.
2. Vérification des contraintes : avec un nom valant `rapport.txt; echo INJECTE`, la forme `shell=True` produit **deux lignes** de sortie, la seconde provenant de la commande injectée, tandis que la forme par liste d'arguments en produit **une seule**, le point-virgule étant traité comme un caractère ordinaire du nom de fichier. Les deux justifications avancées sont fausses : le navigateur n'est en rien une garantie, un client HTTP quelconque envoyant ce qu'il veut dans le corps de la requête ; et l'argument sur les espaces est retourné, puisque c'est précisément la forme par liste qui les traite correctement, sans découpage. La requête exigeait explicitement une validation du nom reçu, elle n'est pas faite, et l'absence de validation est même revendiquée. La correction consiste à passer une liste d'arguments et à valider le nom contre une liste blanche de caractères, sans oublier de refuser les séparateurs de chemin.
3. Synthèse : injection de commande directe, contrainte de validation explicitement écartée, et deux justifications techniquement fausses. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    extra_criteres={"validation_entree": "La sortie valide les entrées d'origine utilisateur comme la requête l'exige."},
    extra_checks={"validation_entree": False},
    raison="Interpolation d'une valeur utilisateur dans shell=True : la commande injectée s'exécute, et la validation exigée est écartée.",
))

add(example(
    meta={"id": "b09-002", "famille": "python-appel-commande", "domaine": "code", "tache": "generation",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne=CONSIGNE_CONVERT,
    reponse='''
```python
import re
import subprocess
from pathlib import Path

NOM_AUTORISE = re.compile(r"\\A[\\w .()-]{1,120}\\Z")
UPLOADS = Path("uploads").resolve()

def convertir_en_pdf(nom_fichier: str) -> int:
    if not NOM_AUTORISE.fullmatch(nom_fichier):
        raise ValueError(f"nom de fichier refusé : {nom_fichier!r}")

    source = (UPLOADS / nom_fichier).resolve()
    if source.parent != UPLOADS:
        raise ValueError("chemin hors du répertoire de téléversement")

    resultat = subprocess.run(
        ["convertisseur", "--input", str(source), "--output", f"pdf/{nom_fichier}.pdf"],
        capture_output=True, text=True,
    )
    return resultat.returncode
```

Trois points :

- **Liste d'arguments plutôt que `shell=True`.** Chaque élément est transmis tel quel au programme, sans interprétation : un point-virgule ou un `&&` dans le nom reste un caractère du nom.
- **Liste blanche.** On énumère ce qui est permis plutôt que ce qui est interdit. Une liste noire oublie toujours un caractère.
- **Vérification du chemin résolu.** La liste blanche exclut déjà `/`, mais comparer le parent après `resolve()` protège aussi des liens symboliques.
''',
    thinking='''
1. Analyse du code : la fonction remplit le contrat et la validation exigée est présente, en deux couches indépendantes.
2. Vérification des contraintes : le choix de la liste d'arguments est correct — avec un nom contenant `; echo INJECTE`, la forme par liste produit une seule ligne de sortie et le point-virgule reste un caractère ordinaire, là où `shell=True` en produit deux. L'argumentaire sur la liste blanche est juste, et la vérification du parent après `resolve()` ajoute bien une protection contre les liens symboliques que la seule expression régulière ne couvrirait pas. Le motif `\\A...\\Z` avec `fullmatch` est correctement ancré, et la borne de longueur évite un nom démesuré.
3. Synthèse : appel de commande sûr, validation explicite en liste blanche conforme à la requête, et défense supplémentaire sur le chemin résolu. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"validation_entree": "La sortie valide les entrées d'origine utilisateur comme la requête l'exige."},
    extra_checks={"validation_entree": True},
    raison="Liste d'arguments au lieu du shell, validation en liste blanche et contrôle du chemin résolu, conformément à la requête.",
))

# ── 3. Appartenance : liste contre ensemble ───────────────────────────────────
add(example(
    meta={"id": "b09-003", "famille": "python-appartenance-ensemble", "domaine": "code", "tache": "refactoring",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Ce filtrage devient très lent quand la liste de référence grossit. Optimise-le, **sans ajouter de dépendance**.

```python
def filtrer_autorises(demandes, identifiants_autorises):
    return [d for d in demandes if d.identifiant in identifiants_autorises]
```
''',
    reponse='''
`identifiants_autorises` est une liste : l'opérateur `in` la parcourt élément par élément. Le filtrage est donc en O(n × m), et c'est ce produit qui explose quand la référence grossit.

Un ensemble suffit, avec une recherche en temps constant amorti :

```python
def filtrer_autorises(demandes, identifiants_autorises):
    autorises = set(identifiants_autorises)
    return [d for d in demandes if d.identifiant in autorises]
```

La conversion coûte un parcours unique, immédiatement amorti dès qu'il y a plus de quelques demandes.

Deux précisions. La construction de l'ensemble doit rester **hors de la boucle** : la placer à l'intérieur reproduirait le coût qu'on cherche à supprimer. Et les identifiants doivent être hachables, ce qui est le cas de chaînes ou d'entiers ; si l'appelant transmet déjà un ensemble, `set()` sur un ensemble reste peu coûteux et le code demeure correct.

Si la liste de référence est stable entre les appels, construisez l'ensemble une fois chez l'appelant plutôt qu'à chaque appel.
''',
    thinking='''
1. Analyse du code : le diagnostic est exact. L'appartenance à une liste est linéaire, celle à un ensemble est en temps constant amorti, et le coût global passe de O(n × m) à O(n + m).
2. Vérification des contraintes : l'ordre de grandeur est net sur 500 recherches. Pour une référence de 2 000 éléments, le parcours de liste prend 1,97 ms contre 0,015 ms pour l'ensemble, soit 127 fois plus ; à 10 000 éléments, 10,00 ms contre 0,018 ms, soit 554 fois ; à 50 000 éléments, 45,06 ms contre 0,020 ms, soit 2 287 fois. Le temps de l'ensemble reste stable pendant que celui de la liste croît linéairement, ce qui confirme l'analyse. Les deux précisions sont pertinentes : sortir la construction de la boucle est bien la faute classique, et la contrainte de hachabilité est réelle. Aucune dépendance n'est ajoutée, conformément à la requête, et le comportement observable est identique, les mêmes éléments étant retenus dans le même ordre.
3. Synthèse : cause exacte, correction équivalente et chiffrée, précisions justes sur les pièges de mise en œuvre. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"dependance_autorisee": "La solution n'utilise aucune bibliothèque au-delà de ce que la requête autorise."},
    extra_checks={"dependance_autorisee": True},
    raison="Passage à un ensemble correct et chiffré (2287× à n=50 000), sans dépendance ajoutée et à comportement identique.",
))

# ── 4. Décalage d'indice sur une tranche ──────────────────────────────────────
add(example(
    meta={"id": "b09-004", "famille": "python-bornes-tranche", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Notre export perd systématiquement la dernière ligne du fichier. Explique et corrige.

```python
lignes = fichier.read().splitlines()
for i in range(len(lignes) - 1):
    exporter(lignes[i])
```
''',
    reponse='''
Le problème vient de l'indexation : en Python, les indices commencent à zéro, donc le dernier élément est à `len(lignes) - 1`. Comme `range` s'arrête avant sa borne, il faut lui donner la longueur augmentée de un pour atteindre ce dernier indice.

```python
for i in range(len(lignes) + 1):
    exporter(lignes[i])
```

Ainsi la boucle couvre tous les indices, du premier au dernier inclus.
''',
    thinking='''
1. Analyse du code : le diagnostic de départ est correct — `range(len(lignes) - 1)` s'arrête un cran trop tôt et omet le dernier élément —, mais la correction proposée surcorrige de deux crans et casse le programme.
2. Vérification des contraintes : `range(n + 1)` produit les indices de 0 à n inclus, donc un indice de plus que la liste n'a d'éléments. L'accès `lignes[len(lignes)]` lève `IndexError: list index out of range`. L'export ne perdrait plus la dernière ligne, il s'interromprait par une exception à la toute fin, sur chaque fichier. La correction juste est `range(len(lignes))`, ou plus simplement l'itération directe `for ligne in lignes: exporter(ligne)`, qui supprime la question des bornes. À noter la dissymétrie qui rend ce genre d'erreur discret : une **tranche** hors bornes comme `lignes[10:20]` renvoie une liste vide sans lever, alors qu'un **accès indexé** hors bornes lève.
3. Synthèse : cause correctement identifiée mais correction fausse, qui remplace une perte silencieuse par une exception systématique. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="range(len + 1) accède à l'indice len et lève IndexError : la correction attendue était range(len) ou l'itération directe.",
))

# ── 5. Valeur nulle dans une map ──────────────────────────────────────────────
add(example(
    meta={"id": "b09-005", "famille": "java-map-valeur-null", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Notre cache de préférences renvoie parfois `null` là où nous attendions la valeur par défaut, alors que nous utilisons `getOrDefault`. Explique.

```java
Map<String, String> prefs = new HashMap<>();
prefs.put("theme", null);                 // l'utilisateur a explicitement effacé son choix
String theme = prefs.getOrDefault("theme", "clair");
```
''',
    reponse='''
`getOrDefault` teste la **présence de la clé**, pas la nullité de la valeur. Ici la clé existe, sa valeur associée est `null`, donc la méthode renvoie cette valeur telle quelle : la valeur par défaut n'est jamais utilisée.

C'est une distinction que `HashMap` matérialise explicitement, puisqu'elle accepte les valeurs nulles :

```java
prefs.get("theme");          // null
prefs.containsKey("theme");  // true
```

Trois façons de corriger, selon l'intention.

Si une valeur nulle doit être traitée comme une absence, testez-la :

```java
String theme = Objects.requireNonNullElse(prefs.get("theme"), "clair");
```

Si l'effacement doit être distingué de l'absence, conservez-le mais rendez-le explicite, par exemple avec une chaîne vide ou une valeur sentinelle plutôt que `null`.

Enfin, le plus robuste reste de ne jamais stocker `null` : retirez la clé à l'effacement. Le cas se règle alors de lui-même, et `getOrDefault` retrouve le comportement attendu.

À noter que `Optional.ofNullable(prefs.get("theme"))` ne vous aidera pas à faire la différence : clé absente et clé présente à `null` donnent le même `Optional` vide.
''',
    thinking='''
1. Analyse de l'explication : le mécanisme est exact. `getOrDefault` ne substitue la valeur par défaut que si la clé est absente, et `HashMap` autorise bien les valeurs nulles, ce qui rend le cas atteignable.
2. Vérification des contraintes : le comportement se reproduit exactement. Avec une clé présente associée à `null`, `get` renvoie `null`, `containsKey` renvoie `true`, et `getOrDefault` avec une valeur par défaut renvoie bien `null` et non le défaut. La dernière remarque est exacte elle aussi : `Optional.ofNullable(map.get(cle))` est vide dans les deux cas, donc indistinguable d'une clé absente, ce qui est précisément le piège que l'on croit éviter en passant par `Optional`. Les trois corrections sont valides et correctement hiérarchisées selon l'intention métier, la dernière — ne jamais stocker `null` — étant la seule qui supprime l'ambiguïté à la source.
3. Synthèse : cause exacte, comportement intégralement reproduit, corrections pertinentes et mise en garde juste sur `Optional`. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Distingue exactement présence de clé et nullité de valeur, y compris le piège d'Optional.",
))

# ── 6. Rétention d'annotation ─────────────────────────────────────────────────
add(example(
    meta={"id": "b09-006", "famille": "java-retention-annotation", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
Crée une annotation `@Audite` que notre intercepteur détectera **à l'exécution** par réflexion, pour journaliser les appels aux méthodes annotées.

Accessoirement, dis un mot de `@Inherited`.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse du code : l'annotation est syntaxiquement correcte et `RetentionPolicy.CLASS` est bien la valeur par défaut, comme l'affirme la réponse. Mais l'inférence tirée de cette conservation est fausse.
2. Vérification des contraintes : `CLASS` signifie que l'annotation figure dans le fichier `.class` mais **n'est pas chargée** en mémoire par la machine virtuelle, donc elle est invisible par réflexion. Sur deux méthodes annotées, l'une en rétention `RUNTIME` et l'autre en `CLASS`, la réflexion voit **1** annotation pour la première et **0** pour la seconde. L'intercepteur proposé ne journaliserait donc jamais rien, en silence, ce qui contredit frontalement l'exigence de la requête, à savoir une détection à l'exécution. La correction tient en un mot : `@Retention(RetentionPolicy.RUNTIME)`. L'argument sur la valeur par défaut est exact mais hors sujet, la valeur par défaut étant justement inadaptée à cet usage. La demande facultative sur `@Inherited` n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : un fait exact sur la rétention par défaut sert à justifier un choix qui rend le dispositif inopérant, alors que la requête exigeait explicitement une détection à l'exécution. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="RetentionPolicy.CLASS rend l'annotation invisible par réflexion : 0 annotation vue contre 1 en RUNTIME.",
))

# ── 7. Fermetures dans une boucle ─────────────────────────────────────────────
add(example(
    meta={"id": "b09-007", "famille": "js-fermeture-boucle", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "typescript"},
    consigne='''
Tous nos boutons déclenchent la même action, celle du dernier onglet.

```ts
for (var i = 0; i < onglets.length; i++) {
  boutons[i].addEventListener("click", () => ouvrir(onglets[i]));
}
```

Explique et corrige.
''',
    reponse='''
`var` a une portée de **fonction**, pas de bloc : la boucle ne crée qu'une seule variable `i`, partagée par toutes les fermetures. Au moment du clic, la boucle est terminée depuis longtemps et `i` vaut `onglets.length` — d'où le comportement identique de tous les boutons, et même un `onglets[i]` indéfini.

La correction tient en un mot-clé :

```ts
for (let i = 0; i < onglets.length; i++) {
  boutons[i].addEventListener("click", () => ouvrir(onglets[i]));
}
```

`let` a une portée de bloc, et la spécification prévoit une **liaison par itération** pour les boucles `for` : chaque tour capture sa propre copie de `i`.

Deux variantes équivalentes : itérer sur les valeurs plutôt que sur les indices, avec `onglets.forEach((onglet, index) => ...)`, ce qui supprime la question ; ou, en code ancien contraint à `var`, envelopper dans une fonction immédiatement invoquée pour créer une portée par tour.
''',
    thinking='''
1. Analyse de l'explication : le mécanisme est exact. `var` étant à portée de fonction, une seule liaison est partagée par toutes les fermetures, tandis que `let` bénéficie d'une liaison par itération dans une boucle `for`, ce qui est bien ce que prévoit la spécification.
2. Vérification des contraintes : trois fermetures créées dans une boucle renvoient `[3, 3, 3]` avec `var`, et `[0, 1, 2]` avec `let`. La variante par fonction immédiatement invoquée donne également `[0, 1, 2]`, ce qui en fait bien un repli valide quand `let` n'est pas disponible. La conséquence annoncée pour la valeur finale, `i` égal à la longueur du tableau et donc un accès indéfini, découle directement de la mesure. La variante `forEach` est correcte et supprime effectivement le problème en liant la valeur au paramètre.
3. Synthèse : cause exacte, correction minimale correcte, variantes valides et correctement présentées. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Portée de var contre liaison par itération de let exactement expliquée, avec [3,3,3] contre [0,1,2].",
))

# ── 8. Égalité de dates, réponse verbeuse ─────────────────────────────────────
add(example(
    meta={"id": "b09-008", "famille": "js-egalite-dates", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": True, "langage": "typescript"},
    consigne='''
Notre déduplication de créneaux laisse passer des doublons : deux créneaux à la même date sont comptés deux fois.

```ts
const uniques = [...new Set(creneaux.map((c) => c.debut))];   // c.debut est un Date
```

Explique et corrige.

En bonus, dis un mot du coût mémoire de la déduplication.
''',
    reponse='''
## Le mécanisme

`Set` déduplique en comparant ses éléments avec l'algorithme SameValueZero, très proche de l'égalité stricte. Or `Date` est un objet : deux instances distinctes ne sont jamais strictement égales, même si elles représentent le même instant.

## La démonstration

```js
const a = new Date("2026-03-01T00:00:00Z");
const b = new Date("2026-03-01T00:00:00Z");
a === b;   // false
```

## La correction

Il suffit de comparer les objets par leur contenu, ce que `Set` sait faire dès lors qu'on lui fournit des valeurs comparables. Le plus simple est de passer par la représentation JSON :

```ts
const uniques = [...new Set(creneaux.map((c) => JSON.stringify(c.debut)))]
  .map((s) => new Date(JSON.parse(s)));
```

## Pourquoi pas `getTime()`

On lit souvent qu'il faudrait passer par `getTime()`. C'est possible, mais cela impose de reconstruire les dates ensuite, et surtout la valeur numérique perd le fuseau d'origine, ce qui fausserait un affichage local.

## À retenir

| Comparaison | Déduplique deux dates égales |
|---|---|
| `Set` sur des `Date` | non |
| `Set` sur `JSON.stringify` | oui ✅ |
| `Set` sur `getTime()` | oui, mais perte du fuseau |
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact. `Set` s'appuie sur SameValueZero, donc sur l'identité pour les objets, et deux `Date` distinctes représentant le même instant ne sont pas égales. `a === b` vaut `false`, `a == b` également, et `new Set([a, b]).size` vaut **2**. La correction par `JSON.stringify` fonctionne, les deux dates produisant la même chaîne.
2. Vérification des contraintes : le raisonnement écartant `getTime()` est faux, et c'est la seule partie qui compte pour le choix final. Un objet `Date` ne porte **aucun fuseau** : il encapsule un instant, un nombre de millisecondes depuis l'époque, et le fuseau n'intervient qu'à l'affichage, via les méthodes locales ou l'option passée au formateur. Passer par `getTime()` ne perd donc strictement rien, ce que la mesure confirme — `a.getTime() === b.getTime()` et `+a === +b` valent tous deux `true`, exactement comme l'égalité des chaînes JSON. La recommandation retenue est donc justifiée par une propriété inexistante, et elle est de surcroît plus coûteuse et plus fragile qu'un `getTime()`, la sérialisation dépendant du format ISO. Le tableau final inscrit cette contre-vérité. La demande facultative sur le coût mémoire de la déduplication n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : cause correctement identifiée et correction fonctionnelle, mais le choix est motivé par une affirmation fausse sur le fuseau, qui écarte la solution idiomatique. FAIL.
''',
    exact=False, bugs=True, consignes=True,
    raison="Affirme qu'un Date porte un fuseau perdu par getTime() : l'objet encapsule un instant, et getTime() déduplique aussi bien.",
))

# ── 9. Cas limite : signature publique modifiée ───────────────────────────────
add(example(
    meta={"id": "b09-009", "famille": "java-api-publique-figee", "domaine": "code", "tache": "refactoring",
          "cas": "limite", "verbeux": False, "langage": "java"},
    consigne='''
Rends cette méthode de notre bibliothèque tolérante à une liste nulle. **La signature publique est figée**, des applications tierces compilées contre cette version doivent continuer à fonctionner.

```java
public static int total(List<Integer> valeurs) {
    return valeurs.stream().mapToInt(Integer::intValue).sum();
}
```
''',
    reponse='''
```java
public static int total(Optional<List<Integer>> valeurs) {
    return valeurs.orElseGet(List::of).stream().mapToInt(Integer::intValue).sum();
}
```

Envelopper le paramètre dans un `Optional` rend l'absence explicite dans la signature, ce qui est plus propre qu'un test de nullité : l'appelant voit immédiatement que la valeur peut manquer, et le compilateur l'oblige à en tenir compte.
''',
    thinking='''
1. Analyse du code : la logique de repli est correcte, `orElseGet(List::of)` fournissant bien une liste vide dont la somme vaut zéro. La justification avancée est en revanche fausse sur un point vérifiable : le compilateur n'oblige nullement l'appelant à tenir compte de l'absence. `total(null)` compile sans avertissement et lève un `NullPointerException` sur `orElseGet` — le type `Optional` contraint à emballer une valeur, non à traiter le cas vide, et ne protège donc même pas du `null` que la requête demandait précisément d'absorber.
2. Vérification des contraintes : la requête pose une contrainte explicite et motivée — signature publique figée, applications tierces déjà compilées. Or changer le type du paramètre de `List<Integer>` à `Optional<List<Integer>>` casse à la fois la compatibilité **source**, tout appel existant cessant de compiler, et la compatibilité **binaire**, la signature de la méthode faisant partie de sa référence dans le bytecode appelant : les applications tierces échoueraient à l'exécution sur un `NoSuchMethodError`. Le conseil de rendre l'absence explicite est par ailleurs contraire à l'usage recommandé d'`Optional`, prévu pour les valeurs de retour plutôt que pour les paramètres. La correction attendue tient dans le corps de la méthode, sans toucher à la signature : `if (valeurs == null) return 0;`, ou `Objects.requireNonNullElse(valeurs, List.of())`.
3. Synthèse : le comportement demandé est bien obtenu, mais au prix d'une rupture de compatibilité que la requête interdisait explicitement, alors qu'une correction interne suffisait. FAIL.
''',
    exact=False, bugs=True, consignes=True,
    extra_criteres={"signature_publique_inchangee": "La signature publique de la méthode est inchangée, comme l'exige la requête."},
    extra_checks={"signature_publique_inchangee": False},
    raison="Change le type du paramètre alors que la signature publique était figée : rupture de compatibilité source et binaire ; affirme de surcroît à tort que le compilateur oblige l'appelant à traiter l'absence.",
))

# ── 10. Théorie : SameSite et CSRF ────────────────────────────────────────────
add(example(
    meta={"id": "b09-010", "famille": "web-samesite-csrf", "domaine": "theorie", "tache": "question_reponse",
          "cas": "defaillant", "verbeux": False, "langage": "web"},
    consigne='''
Peut-on retirer nos jetons anti-CSRF maintenant que nos cookies de session sont en `SameSite=Lax` ?

Sans obligation, dis un mot de `SameSite=Strict`.
''',
    reponse='''
Oui. `SameSite=Lax` empêche le navigateur d'envoyer le cookie de session lors d'une requête initiée par un autre site, ce qui supprime la condition même de l'attaque CSRF : sans cookie, la requête forgée arrive non authentifiée et échoue.

Les jetons anti-CSRF étaient la parade avant l'arrivée de cet attribut. Les conserver aujourd'hui revient à maintenir deux mécanismes pour le même risque, avec le coût de gestion associé — génération, stockage en session, vérification à chaque requête.

Vous pouvez donc les retirer, en vous assurant simplement que tous vos cookies d'authentification portent bien l'attribut.
''',
    thinking='''
1. Analyse de l'explication : la description de `SameSite=Lax` est incomplète sur le point décisif. En mode `Lax`, le cookie **est** envoyé lors d'une navigation de premier niveau en méthode sûre, typiquement un clic de lien conduisant à une requête `GET`. Il n'est écarté que pour les requêtes intersites non sûres ou en sous-ressource.
2. Vérification des contraintes : la conclusion est donc fausse pour toute application exposant une action à effet de bord accessible en `GET`, cas encore fréquent sur des liens de désinscription, de suppression ou de changement d'état — un lien forgé suffit alors, cookie inclus. Trois limites supplémentaires sont passées sous silence. L'attribut est appliqué par le **navigateur** : un client ancien ou non conforme ne l'implémente pas, et la protection disparaît avec lui. Il raisonne par site enregistrable, donc un sous-domaine compromis reste considéré comme le même site. Et il ne protège pas des requêtes émises depuis une page du site elle-même, par exemple via une injection de contenu. `SameSite=Lax` est une défense en profondeur utile et à conserver, mais la protection primaire reste le jeton anti-CSRF ou le motif de double soumission, complétés par la vérification de l'origine. La demande facultative sur `SameSite=Strict` n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : mécanisme incomplet sur le cas des navigations `GET`, aboutissant à recommander le retrait de la protection primaire. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="SameSite=Lax laisse passer le cookie sur une navigation GET de premier niveau : retirer les jetons anti-CSRF expose les actions accessibles en GET.",
))

# ── 11. Théorie : liste blanche contre liste noire ────────────────────────────
add(example(
    meta={"id": "b09-011", "famille": "securite-liste-blanche", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "securite"},
    consigne='''
Notre validation d'entrées rejette une liste de caractères et de motifs dangereux. L'équipe sécurité demande de passer à une liste blanche. Quelle différence, concrètement ?
''',
    reponse='''
La différence tient à ce qui se passe quand vous n'avez pas pensé à un cas.

Une **liste noire** énumère ce qui est interdit : tout ce qui n'y figure pas passe. Elle est donc toujours en retard d'un contournement — un encodage alternatif, une variante Unicode, une casse inattendue, un caractère nouvellement significatif dans une couche que vous ne contrôlez pas. Chaque incident ajoute une ligne à la liste, sans jamais garantir qu'elle est complète.

Une **liste blanche** énumère ce qui est permis : tout le reste est refusé. L'inconnu est rejeté par défaut, ce qui inverse la charge — vous n'avez plus à prévoir les attaques, seulement à décrire vos données légitimes.

En pratique, une liste blanche se décrit par la forme attendue : un jeu de caractères, une longueur, un format, une plage de valeurs, une énumération de valeurs admises. Pour un identifiant, `\\A[a-z0-9_-]{1,64}\\Z` dit tout ce qu'il y a à dire.

Deux précisions utiles. La validation ne remplace pas l'échappement au point d'usage : requête paramétrée pour le SQL, liste d'arguments pour un appel de commande, encodage contextuel pour le HTML. Une entrée peut être parfaitement légitime et rester dangereuse si elle est concaténée. Et la validation doit s'exécuter côté serveur : un contrôle côté client est une aide à la saisie, pas une protection.
''',
    thinking='''
1. Analyse de l'explication : la distinction est exacte et l'argument central est le bon — c'est le comportement face à l'inconnu qui sépare les deux approches, la liste noire laissant passer par défaut, la liste blanche refusant par défaut. Les contournements cités, encodages alternatifs et variantes Unicode, sont les vecteurs réels.
2. Vérification des contraintes : la description opérationnelle d'une liste blanche par jeu de caractères, longueur, format et plage est correcte, et le motif donné en exemple est bien ancré. Les deux précisions finales sont exactes et importantes : la validation ne dispense pas de l'échappement contextuel au point d'usage, et un contrôle côté client ne constitue pas une protection. La question posée, la différence concrète, reçoit une réponse directe et actionnable.
3. Synthèse : distinction exacte, argumentation correcte sur la charge de la preuve, précisions justes sur les limites de la validation. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Distinction exacte fondée sur le comportement face à l'inconnu, avec les bonnes réserves sur l'échappement contextuel.",
))

# ── 12. Théorie : pool de connexions ──────────────────────────────────────────
add(example(
    meta={"id": "b09-012", "famille": "db-pool-connexions", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": False, "langage": "sql"},
    consigne='''
Sous charge, nos requêtes attendent longtemps l'obtention d'une connexion. Un collègue propose de porter le pool de 20 à 200 connexions. Qu'en penses-tu ?

Sans obligation, dis un mot du nombre de cœurs de la base.
''',
    reponse='''
C'est la bonne réaction. L'attente que vous observez est directement causée par l'épuisement du pool : les threads applicatifs se mettent en file dès que les 20 connexions sont prises.

En passant à 200, vous supprimez la file d'attente et chaque requête obtient immédiatement sa connexion. Le débit augmente d'autant, puisque la base peut alors traiter dix fois plus de requêtes en parallèle.

Réglez simplement le délai d'obtention à une valeur généreuse pour couvrir les pics, et surveillez la mémoire du serveur applicatif, chaque connexion ayant un coût côté client.
''',
    thinking='''
1. Analyse de l'explication : le constat de départ est correct — l'attente vient bien de l'épuisement du pool — mais la conclusion inverse le raisonnement. Un pool ne crée pas de capacité, il en **plafonne** la consommation.
2. Vérification des contraintes : l'affirmation selon laquelle la base traiterait dix fois plus de requêtes en parallèle est fausse. Le parallélisme réel d'un serveur de bases de données est borné par ses cœurs et ses disques ; au-delà, les connexions supplémentaires ne s'exécutent pas de front, elles se disputent les mêmes ressources. Chacune consomme en outre de la mémoire de travail côté serveur et un processus ou un fil d'exécution selon le moteur, si bien qu'au-delà d'un seuil le débit **diminue** au lieu d'augmenter, tout en allongeant les temps de réponse. Déplacer la file d'attente du pool vers le moteur ne la supprime pas, elle devient seulement invisible et plus coûteuse. Le conseil d'allonger le délai d'obtention aggrave le défaut : il transforme un échec rapide et diagnosticable en une latence longue subie par l'utilisateur. La démarche correcte consiste à chercher pourquoi les connexions sont retenues si longtemps — requêtes lentes faute d'index, transactions ouvertes pendant un appel réseau, absence de pagination — puis à dimensionner le pool à partir de la capacité réelle du serveur, généralement quelques dizaines de connexions, pas des centaines. La demande facultative sur le nombre de cœurs de la base n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : constat juste mais conclusion inversée, avec un remède qui déplace la file d'attente et peut dégrader le débit. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Un pool plafonne la consommation, il ne crée pas de capacité : au-delà du parallélisme réel du serveur, le débit diminue.",
))

# ── 13. Cas limite : périmètre respecté, partie facultative omise ─────────────
add(example(
    meta={"id": "b09-013", "famille": "obs-journalisation-donnees", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": True, "langage": "web"},
    consigne='''
Que faut-il éviter de journaliser dans une application qui manipule des données clients, et comment s'en assurer ? **Reste sur la journalisation applicative, ne parle pas du chiffrement de la base ni des sauvegardes.** Si possible, dis un mot de la durée de rétention.
''',
    reponse='''
## Ce qui n'a rien à faire dans un journal

Trois catégories, par ordre de gravité.

**Les secrets d'authentification** — mots de passe même erronés, jetons, clés d'API, cookies de session. Un jeton journalisé reste utilisable, et les journaux sont souvent lisibles par plus de personnes que la base.

**Les données personnelles directement identifiantes** — nom complet, adresse, courriel, numéro de téléphone, données de santé ou bancaires. Le journal devient alors un traitement de données personnelles à part entière, avec les obligations correspondantes.

**Les contenus utilisateur** — corps de requête et de réponse journalisés « pour déboguer », qui embarquent tout le reste sans qu'on y pense.

## Comment s'en assurer

Le contrôle ne peut pas reposer sur la discipline de chacun à l'écriture. Trois dispositifs :

- **Journaliser des identifiants, pas des valeurs.** `client=42` plutôt que `client=Jean Dupont`. L'identifiant suffit au diagnostic et la correspondance reste dans la base, sous contrôle d'accès.
- **Une couche de rédaction centralisée.** Un filtre dans la configuration de journalisation qui masque les champs connus comme sensibles, appliqué à tout ce qui sort, plutôt qu'un effort à chaque appel.
- **Un test automatisé.** Une vérification en intégration qui échoue si un motif sensible — numéro de carte, en-tête `Authorization` — apparaît dans la sortie. C'est le seul dispositif qui résiste à l'ajout d'un nouveau développeur.

## Le piège des exceptions

La trace d'une exception embarque souvent les arguments de la méthode, et les objets journalisés passent par leur `toString`. Une classe qui expose tous ses champs y déverse donc son contenu, y compris ce que vous aviez pris soin de ne pas journaliser explicitement.
''',
    thinking='''
1. Analyse de l'explication : le contenu est exact et bien hiérarchisé. Les trois catégories citées sont les bonnes, l'observation sur l'audience plus large des journaux que de la base est juste, et le rappel qu'un journal contenant des données personnelles constitue lui-même un traitement est correct.
2. Vérification des contraintes : les trois dispositifs proposés sont pertinents et opérationnels, en particulier le test automatisé, qui est effectivement le seul à ne pas dépendre de la vigilance individuelle. Le piège des traces d'exception et de `toString` est réel et rarement mentionné. Le périmètre imposé est scrupuleusement respecté : ni chiffrement de la base ni sauvegardes ne sont abordés, alors que le sujet y conduisait naturellement. En revanche, la demande facultative sur la durée de rétention n'est pas traitée. La réponse est par ailleurs longue, avec un niveau de détail que la question n'exigeait pas.
3. Synthèse : tout l'obligatoire est exact et la contrainte de périmètre est respectée ; l'omission porte sur une demande explicitement facultative et la verbosité seule ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"perimetre_respecte": "La réponse reste dans le périmètre fixé par la requête, sans aborder les sujets explicitement exclus."},
    extra_checks={"perimetre_respecte": True},
    raison="Contenu exact et périmètre imposé scrupuleusement respecté ; seule la durée de rétention, facultative, manque.",
))

# ── 14. Théorie : capture d'exception trop large ──────────────────────────────
add(example(
    meta={"id": "b09-014", "famille": "python-exception-large", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Notre convention interdit `except Exception`. Un développeur trouve la règle excessive, puisqu'on journalise l'erreur avant de continuer. Qui a raison ?
''',
    reponse='''
Les deux, selon l'endroit. Le problème n'est pas la largeur de la capture, c'est l'endroit où on la place et ce qu'on en fait.

**Capturer largement est légitime à la frontière.** Un serveur qui traite des requêtes, une boucle de consommation de messages, une tâche planifiée : ces points ont besoin d'un filet pour qu'une erreur sur un élément n'interrompe pas le service entier. La capture y est un choix d'architecture, pas un oubli.

**C'est nuisible au milieu du code métier.** On y attrape des erreurs qu'on n'avait pas prévues — une faute de frappe donnant une `AttributeError`, une `KeyError` sur une clé renommée — et on poursuit avec un état invalide. Le bug ne disparaît pas, il ressurgit plus loin, sous une forme incompréhensible.

Trois règles pratiques :

- Capturez le type le plus précis que vous savez traiter. Si vous ne savez pas quoi faire de l'erreur, laissez-la passer.
- Journalisez avec la trace, via `logging.exception` ou `exc_info=True`, sinon vous perdez l'endroit exact de l'erreur — journaliser `str(e)` seul est la faute la plus fréquente.
- N'écrivez jamais `except:` nu, qui attrape aussi `KeyboardInterrupt` et `SystemExit` : il rend le programme ininterruptible. `except Exception` les épargne, puisque ces deux-là dérivent de `BaseException`.

Et surtout : « journaliser puis continuer » n'est acceptable que si la suite du traitement a un sens sans le résultat manquant. Sinon, c'est propager silencieusement l'incohérence.
''',
    thinking='''
1. Analyse de l'explication : la position est exacte et bien construite. La distinction entre capture à la frontière, légitime, et capture au milieu du code métier, nuisible, est le bon critère, et les exemples de points frontière cités correspondent aux cas réels.
2. Vérification des contraintes : les trois règles sont correctes. La hiérarchie des exceptions est exactement rendue : `KeyboardInterrupt` et `SystemExit` dérivent bien de `BaseException` et non d'`Exception`, donc `except Exception` les laisse passer là où un `except:` nu les intercepte. La recommandation de `logging.exception` ou `exc_info=True` est juste, et le diagnostic sur la perte de la trace avec `str(e)` correspond à une faute très répandue. La conclusion sur la poursuite du traitement est le point le plus important et répond directement à l'argument du développeur, sans lui donner ni tort ni raison de façon simpliste.
3. Synthèse : critère de jugement exact, hiérarchie des exceptions correctement citée, recommandations pratiques justes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Distingue exactement capture à la frontière et capture métier, avec une hiérarchie BaseException correctement citée.",
))

# ── 15. Cas limite : format imposé non respecté ───────────────────────────────
add(example(
    meta={"id": "b09-015", "famille": "reseau-dns-ttl", "domaine": "theorie", "tache": "question_reponse",
          "cas": "limite", "verbeux": False, "langage": "web"},
    consigne='''
Nous basculons une base vers une nouvelle adresse en changeant l'enregistrement DNS. Quelles précautions ? **Format imposé : un tableau à deux colonnes, précaution et raison, rien d'autre.**
''',
    reponse='''
Excellente question, et le sujet mérite quelques explications avant le tableau, car la bascule DNS est plus subtile qu'il n'y paraît.

Le point central est que vous ne contrôlez pas le moment où vos clients cesseront d'utiliser l'ancienne adresse. Un enregistrement DNS est mis en cache à chaque étape de la chaîne de résolution — résolveur du système d'exploitation, résolveur du fournisseur d'accès, et parfois l'application elle-même. La durée de vie que vous publiez n'est qu'une indication, que certains résolveurs allongent d'autorité.

Cela signifie que l'ancienne adresse doit rester opérationnelle bien après la bascule, et que vous devez prévoir une période de double écriture ou de lecture depuis les deux emplacements.

Voici les précautions :

| Précaution | Raison |
|---|---|
| Abaisser la durée de vie plusieurs jours avant | Les caches doivent avoir expiré l'ancienne valeur longue avant la bascule |
| Maintenir l'ancienne adresse active | Des résolveurs conserveront l'ancienne réponse au-delà de la durée annoncée |
| Vérifier le cache de la JVM | Sa politique de mise en cache des résolutions peut être perpétuelle selon la configuration |
| Surveiller le trafic résiduel | C'est le seul signal fiable indiquant que plus personne n'utilise l'ancienne adresse |

En espérant que cela vous aide dans votre migration.
''',
    thinking='''
1. Analyse de l'explication : le contenu technique est exact. La mise en cache à plusieurs niveaux de la chaîne de résolution est correctement décrite, le fait que la durée de vie publiée ne soit pas toujours honorée est réel, la précaution sur le cache de résolution de la JVM est pertinente, et surveiller le trafic résiduel est effectivement le seul signal fiable de fin de bascule. Les quatre lignes du tableau sont justes et bien appariées.
2. Vérification des contraintes : la requête impose un format sans ambiguïté — un tableau à deux colonnes, précaution et raison, **rien d'autre**. La réponse fait précéder le tableau de quatre paragraphes d'explication et le fait suivre d'une formule de politesse. Le tableau lui-même est conforme, mais l'exigence portait sur la totalité de la sortie, et le livrable n'est pas utilisable tel quel. Le contenu des paragraphes préliminaires est d'ailleurs largement redondant avec les raisons figurant dans le tableau, ce qui montre que la contrainte était tenable.
3. Synthèse : le fond est exact et les précautions sont les bonnes, mais la seule contrainte de forme imposée, explicite et vérifiable, n'est pas respectée. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"format_impose": "La sortie respecte exactement le format imposé par la requête, sans contenu supplémentaire."},
    extra_checks={"format_impose": False},
    raison="Le tableau demandé est exact, mais il est noyé dans quatre paragraphes et une conclusion, alors que la requête excluait tout autre contenu.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
