#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_10.jsonl (15 examples, CODE_ANALYSIS).

Chiffres issus des sondes Probe10.java, probe10.py, probe10_sql.py et probe10.ts
exécutées le 2026-09-13. Polarités visées : durabilite_garantie=true,
contrainte_disponibilite=true (les deux derniers contrôles à polarité unique).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402

EXAMPLES = []
add = EXAMPLES.append

# ── 1. Comparateur qui ne renvoie jamais zéro ─────────────────────────────────
add(example(
    meta={"id": "b10-001", "famille": "java-contrat-comparateur", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Ce tri passe tous nos tests unitaires mais lève `IllegalArgumentException: Comparison method violates its general contract!` en production. Explique et corrige.

```java
candidats.sort((a, b) -> a.score() >= b.score() ? 1 : -1);
```
''',
    reponse='''
Le comparateur ne renvoie jamais zéro : deux éléments de même score sont déclarés à la fois supérieurs l'un à l'autre, selon l'ordre dans lequel on les présente. Il viole donc l'antisymétrie exigée par le contrat de `Comparator`.

Pourquoi vos tests passent quand même : `List.sort` utilise TimSort, qui bascule sur un simple tri par insertion en dessous de 32 éléments. À cette taille, l'incohérence produit un ordre arbitraire mais aucune exception. Au-delà, TimSort fusionne des segments et détecte l'incohérence en cours de route, d'où l'échec en production sur des volumes réels.

La correction consiste à renvoyer les trois valeurs, ce que les fabriques font pour vous :

```java
candidats.sort(Comparator.comparingDouble(Candidat::score));
```

Trois règles pour ce genre de comparateur :

- Renvoyer zéro pour l'égalité, sans quoi le contrat est rompu.
- Ne jamais comparer par soustraction : `a - b` déborde sur les entiers, et perd les écarts inférieurs à l'unité sur les flottants.
- Si un ordre de départage est nécessaire, l'exprimer explicitement avec `thenComparing` plutôt que de le laisser au hasard.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact. Un comparateur qui renvoie toujours une valeur non nulle est non antisymétrique, ce qui viole le contrat documenté de `Comparator`.
2. Vérification des contraintes : l'explication du seuil est le point qui répond vraiment à la question posée. Sur un jeu comportant de nombreux ex æquo, le tri se termine sans exception à 16 et à 32 éléments, puis lève `IllegalArgumentException: Comparison method violates its general contract!` à 100 et à 1 000 éléments. Cela correspond bien au basculement de TimSort vers le tri par insertion sous 32 éléments, et explique pourquoi des tests unitaires de petite taille ne détectent rien. La correction par `Comparator.comparingDouble` trie sans erreur les 1 000 éléments. Les trois règles sont justes, y compris la mise en garde sur la soustraction : `Integer.MAX_VALUE - 1` moins `-10` donne `-2147483640`, de signe inverse au résultat attendu.
3. Synthèse : cause exacte, explication du caractère intermittent juste, correction et règles pertinentes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Violation d'antisymétrie exactement diagnostiquée, avec le seuil TimSort correctement situé (aucune exception à 32, levée à 100).",
))

# ── 2. Comparateur par soustraction ───────────────────────────────────────────
add(example(
    meta={"id": "b10-002", "famille": "java-comparateur-soustraction", "domaine": "code", "tache": "refactoring",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
Simplifie ce comparateur, qui me paraît trop bavard.

```java
Comparator<Compte> parSolde = (a, b) -> {
    if (a.soldeCentimes() < b.soldeCentimes()) return -1;
    if (a.soldeCentimes() > b.soldeCentimes()) return 1;
    return 0;
};
```
''',
    reponse='''
Ces trois lignes se ramènent à une soustraction, qui est l'idiome consacré :

```java
Comparator<Compte> parSolde = (a, b) -> (int) (a.soldeCentimes() - b.soldeCentimes());
```

Le signe du résultat porte exactement la même information que les trois branches, et le contrat de `Comparator` ne demande que ce signe, pas une valeur particulière. C'est plus court et tout aussi correct.
''',
    thinking='''
1. Analyse du code : l'affirmation sur le contrat est exacte — seul le signe compte — mais la simplification proposée est fausse dès que les valeurs sont grandes, parce que la soustraction elle-même déborde avant qu'on en lise le signe.
2. Vérification des contraintes : avec `Integer.MAX_VALUE - 1` comparé à `-10`, la soustraction donne `-2147483640`, donc un signe **négatif** alors que le premier opérande est le plus grand ; `Integer.compare` renvoie bien `1` sur les mêmes valeurs. Ici le champ est un `long` de centimes, et le transtypage en `int` aggrave le défaut : il tronque les bits de poids fort, si bien que deux soldes très différents peuvent produire une différence nulle ou de signe inverse. Un comparateur ainsi faussé viole la transitivité et peut déclencher, sur une liste assez grande, la même `IllegalArgumentException` que celle observée avec un comparateur non antisymétrique. La simplification correcte existe pourtant et est plus courte encore : `Comparator.comparingLong(Compte::soldeCentimes)`.
3. Synthèse : réécriture qui introduit un débordement sur des montants réalistes, alors qu'une fabrique standard donnait le même raccourci sans le défaut. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="La soustraction déborde : MAX_VALUE-1 moins -10 donne -2147483640, de signe inverse, et le cast en int tronque un long.",
))

# ── 3. TreeSet et compareTo incohérent, verbeux ───────────────────────────────
add(example(
    meta={"id": "b10-003", "famille": "java-treeset-compareto", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": True, "langage": "java"},
    consigne='''
Nous stockons des versions applicatives dans un ensemble trié, pour les parcourir dans l'ordre. Écris la classe `Version` et explique le choix de collection.

Deux versions sont identiques si leur numéro majeur **et** leur numéro mineur coïncident.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse du code : la classe compile et le `record` génère bien `equals` et `hashCode` sur les deux composants, conformément à la définition d'identité donnée. Le défaut est dans l'articulation entre `compareTo` et `equals`.
2. Vérification des contraintes : `compareTo` ne compare que le numéro majeur, alors qu'`equals` compare les deux. Or un `TreeSet` détermine l'appartenance par `compareTo`, jamais par `equals` — le tableau de la réponse affirme le contraire, et c'est l'erreur décisive. Avec `Version(1, 0)` et `Version(1, 5)`, `equals` renvoie `false` et `compareTo` renvoie `0`, si bien que le `TreeSet` construit à partir des deux a une taille de **1**, la seconde version étant purement et simplement perdue, tandis qu'un `HashSet` en contient bien **2**. La collection choisie perd donc silencieusement des données, ce qui contredit directement l'exigence de la requête. La correction consiste à rendre l'ordre cohérent avec l'égalité, `Comparator.comparingInt(Version::majeur).thenComparingInt(Version::mineur)`, ce que la documentation de `SortedSet` recommande explicitement.
3. Synthèse : présentation soignée, mais l'ordre naturel est incohérent avec l'égalité et le tableau affirme une propriété fausse, ce qui conduit à une perte de données silencieuse. FAIL.
''',
    exact=False, bugs=False, consignes=False,
    raison="compareTo ne porte que sur le majeur : le TreeSet contient 1 élément au lieu de 2 et perd une version.",
))

# ── 4. __eq__ sans __hash__ ───────────────────────────────────────────────────
add(example(
    meta={"id": "b10-004", "famille": "python-eq-sans-hash", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Depuis que j'ai ajouté `__eq__` à cette classe, je ne peux plus mettre mes objets dans un ensemble : `TypeError: unhashable type`. Explique et corrige.

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, autre):
        return isinstance(autre, Point) and (self.x, self.y) == (autre.x, autre.y)
```
''',
    reponse='''
Définir `__eq__` met automatiquement `__hash__` à `None` dans la classe. Ce n'est pas un oubli du langage, c'est une protection : deux objets égaux doivent avoir le même hachage, et Python ne peut pas deviner quels attributs participent à votre égalité. Plutôt que de conserver le hachage hérité d'`object`, fondé sur l'identité et donc incohérent avec votre `__eq__`, il rend la classe non hachable.

La correction consiste à définir le hachage sur les mêmes attributs que l'égalité :

```python
def __hash__(self):
    return hash((self.x, self.y))
```

Deux remarques.

Le hachage doit rester stable tant que l'objet est dans un ensemble ou sert de clé : muter `x` après insertion rend l'objet introuvable. Si vos points sont mutables, mieux vaut ne pas les rendre hachables du tout.

Si la classe est un simple porteur de données, `@dataclass(frozen=True)` fait tout : égalité par valeur, hachage cohérent, et immuabilité garantie.
''',
    thinking='''
1. Analyse de l'explication : le mécanisme est exact. Sur une classe définissant `__eq__` sans `__hash__`, l'attribut `__hash__` de la classe vaut bien `None`, et l'insertion dans un ensemble lève `TypeError: unhashable type: 'PointNu'`, exactement le message rapporté. La justification donnée est la bonne : conserver le hachage par identité produirait des objets égaux de hachages différents.
2. Vérification des contraintes : la correction fonctionne, un ensemble contenant deux points égaux dotés de ce `__hash__` a bien une taille de 1. La mise en garde sur la mutation est juste et rejoint le même piège que les clés mutables en Java. La suggestion finale est exacte : une `dataclass(frozen=True)` est hachable et compare par valeur, tandis qu'une `dataclass(eq=True)` non gelée voit son `__hash__` mis à `None` et lève le même `TypeError` — même règle, appliquée automatiquement.
3. Synthèse : cause exacte, correction adaptée, réserves pertinentes sur la mutabilité et alternative correcte. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Explique exactement la mise à None de __hash__ par __eq__, avec un message d'erreur conforme et une correction adaptée.",
))

# ── 5. Cas limite : configuration immuable, option non traitée ────────────────
add(example(
    meta={"id": "b10-005", "famille": "python-config-immuable-frozen", "domaine": "code", "tache": "generation",
          "cas": "limite", "verbeux": False, "langage": "python"},
    consigne='''
Écris la configuration de notre service : hôte, port, et liste d'origines autorisées. Elle doit être **immuable après construction** et utilisable comme clé de cache. Accessoirement, dis un mot de la validation du port.
''',
    reponse='''
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    hote: str
    port: int
    origines: tuple[str, ...] = ()
```

Deux points sur les exigences.

**Immuabilité.** `frozen=True` interdit l'affectation d'attribut après construction : toute tentative lève `FrozenInstanceError`.

**Utilisable comme clé.** Une dataclass gelée reçoit un `__hash__` cohérent avec son égalité par valeur, donc deux configurations identiques désignent la même entrée de cache. C'est la raison du `tuple` plutôt que d'une `list` pour les origines : une liste n'est pas hachable et rendrait toute l'instance inutilisable comme clé, alors même que la classe est gelée.
''',
    thinking='''
1. Analyse du code : la classe répond aux deux exigences obligatoires. Une dataclass gelée est hachable, son égalité porte sur les valeurs, et l'affectation d'un attribut lève `FrozenInstanceError: cannot assign to field 'port'`.
2. Vérification des contraintes : le point le plus fin est correctement traité. L'immuabilité déclarée ne suffit pas à rendre l'instance hachable si un champ contient une structure mutable, d'où le choix du `tuple` — l'explication est exacte et c'est précisément le piège de ce genre de classe. Le contraste avec une dataclass non gelée tient de la même règle, son `__hash__` étant mis à `None` dès que l'égalité est générée. En revanche, la demande facultative sur la validation du port n'est pas traitée : rien n'empêche un port hors plage, alors qu'un `__post_init__` s'en serait chargé en trois lignes. La consigne la présentait explicitement comme facultative.
3. Synthèse : les deux exigences obligatoires sont satisfaites et correctement justifiées, l'unique omission porte sur une demande explicitement facultative. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Immuabilité et hachabilité correctes, avec le tuple justement justifié ; seule la validation du port, facultative, manque.",
))

# ── 6. Écriture durable ───────────────────────────────────────────────────────
add(example(
    meta={"id": "b10-006", "famille": "python-ecriture-durable", "domaine": "code", "tache": "generation",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Écris la fonction qui enregistre l'état de reprise de notre traitement par lots. **Contrainte : après le retour de la fonction, l'état doit survivre à une coupure d'alimentation** — le traitement redémarre à partir de ce fichier.
''',
    reponse='''
```python
import json
import os
from pathlib import Path

def enregistrer_etat(chemin: Path, etat: dict) -> None:
    temporaire = chemin.with_name(chemin.name + ".tmp")

    with temporaire.open("w", encoding="utf-8") as f:
        json.dump(etat, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())          # les octets atteignent le disque, pas seulement le cache

    os.replace(temporaire, chemin)    # substitution atomique

    dossier = os.open(chemin.parent, os.O_RDONLY)
    try:
        os.fsync(dossier)             # rend le renommage lui-même durable
    finally:
        os.close(dossier)
```

Trois étapes, chacune nécessaire à la contrainte posée.

- **`fsync` sur le fichier.** Sans lui, `write` ne fait que remplir le cache du système : une coupure perd les données bien que l'appel ait rendu la main.
- **`os.replace`.** Le renommage est atomique sur le même système de fichiers : un lecteur voit soit l'ancien état complet, soit le nouveau, jamais un fichier tronqué.
- **`fsync` sur le répertoire.** Point le plus souvent oublié : le renommage est une modification du répertoire, elle-même sujette au cache. Sans cette synchronisation, le fichier peut être durable alors que l'entrée qui le nomme ne l'est pas.
''',
    thinking='''
1. Analyse du code : la séquence est correcte et complète. Écriture dans un fichier temporaire, vidage du tampon applicatif, synchronisation du descripteur, substitution atomique, puis synchronisation du répertoire.
2. Vérification des contraintes : les trois justifications sont exactes et correspondent au comportement documenté des appels utilisés. `flush` ne vide que le tampon Python, `os.fsync` force l'écriture des données du fichier, et `os.replace` est bien atomique au sein d'un même système de fichiers, ce que la mention explicite. La synchronisation du répertoire est effectivement l'étape la plus souvent omise, et son absence laisserait exactement le défaut décrit. Le contraste avec une écriture non validée est le même que sur une transaction laissée sans validation : l'appelant croit avoir persisté alors que rien n'est durable. La contrainte de la requête, survivre à une coupure après le retour de la fonction, est donc bien satisfaite.
3. Synthèse : séquence de durabilité complète, chaque étape justifiée par un mécanisme réel, contrainte respectée. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"durabilite_garantie": "L'état est effectivement durable au retour de la fonction, comme l'exige la requête."},
    extra_checks={"durabilite_garantie": True},
    raison="Fichier temporaire, fsync du fichier, substitution atomique et fsync du répertoire : la durabilité exigée est réellement obtenue.",
))

# ── 7. Ordre des colonnes d'un index composite ────────────────────────────────
add(example(
    meta={"id": "b10-007", "famille": "sql-index-composite", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": False, "langage": "sql"},
    consigne='''
Notre requête `WHERE tenant_id = ? ORDER BY cree_le` reste lente malgré l'index `(cree_le, tenant_id)`. Faut-il changer quelque chose ?

Si tu veux compléter, dis un mot des index partiels.
''',
    reponse='''
Non, l'index couvre déjà les deux colonnes utilisées par la requête. Un index composite indexe l'ensemble des colonnes qu'il déclare, et le planificateur sait s'en servir quel que soit l'ordre dans lequel la requête les mentionne — cet ordre n'est qu'une convention d'écriture.

La lenteur vient donc d'ailleurs. Regardez plutôt du côté du volume de lignes ramenées, ou de la fraîcheur des statistiques : lancez une analyse de la table pour que le planificateur dispose de distributions à jour.
''',
    thinking='''
1. Analyse de l'explication : l'affirmation centrale est fausse. Dans un index composite, l'ordre des colonnes est structurant, et non conventionnel : les entrées sont triées d'abord sur la première colonne, puis sur la seconde à l'intérieur de chaque valeur de la première.
2. Vérification des contraintes : la conséquence s'observe sur un index `(tenant_id, cree_le)`, c'est-à-dire l'ordre inverse de celui décrit. Avec cet ordre, la requête `WHERE tenant_id = ? ORDER BY cree_le` donne `SEARCH evenements USING INDEX idx_tenant_date (tenant_id=?)` : l'égalité sur la première colonne fixe un préfixe, et les lignes correspondantes sont déjà triées par la seconde, donc aucun tri n'est nécessaire. Avec l'ordre `(cree_le, tenant_id)` décrit dans la requête, le préfixe n'est pas contraint et le moteur doit soit balayer, soit trier : le cas symétrique le confirme, un `ORDER BY cree_le` sans filtre utilisable sur la colonne de tête donne `SCAN evenements`. La correction consiste donc bien à créer l'index dans l'ordre `(tenant_id, cree_le)`. À noter une nuance que la réponse aurait pu invoquer sans se tromper : certains moteurs savent malgré tout exploiter un index dont la colonne de tête n'est pas filtrée, par parcours par saut, ce qui produit alors un `SEARCH ... (ANY(tenant_id) AND cree_le>?)` — mais cela reste un repli, pas l'équivalent d'un préfixe correctement ordonné, et cela ne dispense pas du tri ici. La demande facultative sur les index partiels n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : ordre des colonnes présenté comme indifférent, ce qui est faux et laisse le problème entier, avec un conseil qui détourne du vrai correctif. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="L'ordre des colonnes d'un index composite est structurant : (tenant_id, cree_le) évite le tri là où l'ordre inverse impose un balayage.",
))

# ── 8. LIKE et index, réponse verbeuse ────────────────────────────────────────
add(example(
    meta={"id": "b10-008", "famille": "sql-like-index", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": True, "langage": "sql"},
    consigne='''
Notre recherche par préfixe sur la colonne `type` est lente. Propose une solution et explique ce qu'on peut en attendre.
''',
    reponse='''
## Le diagnostic

Une recherche par préfixe s'écrit naturellement avec `LIKE 'prefixe%'`, et c'est un cas que les moteurs savent traiter efficacement.

## La solution

```sql
CREATE INDEX idx_type ON evenements(type);
```

## Ce qu'il faut en attendre

La règle est bien connue : un motif **ancré à gauche**, c'est-à-dire sans joker en tête, permet au moteur de descendre dans l'arbre jusqu'au préfixe et de ne parcourir que la plage correspondante. À l'inverse, un motif commençant par `%` interdit toute utilisation de l'index.

Autrement dit :

| Motif | Index utilisé |
|---|---|
| `LIKE 'type1%'` | ✅ recherche par plage |
| `LIKE '%type1'` | ❌ balayage complet |

Une fois l'index créé, votre recherche par préfixe passera donc d'un balayage complet à une recherche ciblée, sans autre changement.
''',
    thinking='''
1. Analyse de l'explication : la distinction entre motif ancré à gauche et motif commençant par un joker est réelle, et l'index proposé est le bon point de départ. Mais la conclusion présentée comme une certitude ne se vérifie pas, et la requête demandait précisément ce qu'on peut attendre.
2. Vérification des contraintes : sur la configuration décrite, avec l'index `idx_type` en place, `WHERE type LIKE 'type1%'` produit `SCAN evenements`, exactement comme `LIKE '%type1'`, alors que l'égalité stricte `WHERE type = 'type1'` produit bien `SEARCH evenements USING INDEX idx_type (type=?)`. L'optimisation par plage n'est donc pas automatique : elle dépend de conditions que la réponse passe sous silence, notamment la collation de la colonne et la sensibilité à la casse de l'opérateur, qui doivent être compatibles pour que le moteur puisse transformer le motif en bornes. Annoncer un passage garanti du balayage à la recherche ciblée est donc faux dans le cas présent, et le tableau donne cette garantie sous forme de règle générale. La démarche correcte consiste à vérifier le plan d'exécution après création de l'index, et à envisager selon le moteur un index adapté à la collation, une colonne normalisée indexée, ou un index de recherche textuelle.
3. Synthèse : solution plausible mais promesse de résultat démentie par le plan d'exécution réel, sur le point même que la requête demandait d'évaluer. FAIL.
''',
    exact=False, bugs=True, consignes=True,
    raison="LIKE 'type1%' donne un SCAN malgré l'index : l'optimisation par plage dépend de la collation, elle n'est pas garantie.",
))

# ── 9. any à la place de unknown ──────────────────────────────────────────────
add(example(
    meta={"id": "b10-009", "famille": "ts-any-unknown", "domaine": "code", "tache": "refactoring",
          "cas": "defaillant", "verbeux": False, "langage": "typescript"},
    consigne='''
Ce code ne compile pas : « Object is of type 'unknown' ». Corrige-le.

```ts
function traiter(charge: unknown) {
  return charge.identifiant;
}
```

Si possible, dis un mot des prédicats de type.
''',
    reponse='''
Le type `unknown` bloque tout accès. Le plus simple est de le remplacer par `any`, qui exprime la même idée — une valeur dont on ignore la forme — sans les contraintes :

```ts
function traiter(charge: any) {
  return charge.identifiant;
}
```

Le code compile et le comportement à l'exécution est identique, `unknown` et `any` étant tous deux effacés à la compilation.
''',
    thinking='''
1. Analyse du code : l'affirmation d'équivalence est fausse. `unknown` et `any` ne diffèrent pas par la commodité mais par la garantie : `unknown` exige un rétrécissement avant tout accès, `any` désactive purement et simplement la vérification de types sur la valeur.
2. Vérification des contraintes : sur une valeur typée `any`, l'appel d'une méthode inexistante et l'affectation à un `number` sont tous deux acceptés sans erreur ; sur la même valeur typée `unknown`, les deux sont refusés à la compilation, et seul un rétrécissement — par `typeof`, par `instanceof` ou par une fonction de garde — débloque l'accès. Le correctif proposé ne corrige donc rien : il supprime le message en supprimant la vérification, et l'erreur se déplace à l'exécution sous la forme d'un accès à une propriété indéfinie. L'argument sur l'effacement à la compilation est exact mais hors sujet, puisque l'intérêt d'`unknown` est précisément ce qu'il impose **avant** l'effacement. La correction attendue est de rétrécir explicitement, par exemple en vérifiant que la valeur est un objet portant la propriété attendue, ou en validant la charge contre un schéma avant usage. La demande facultative sur les prédicats de type n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : le message disparaît au prix de la garantie qui le produisait, avec une équivalence affirmée à tort entre `any` et `unknown`. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Remplacer unknown par any supprime la vérification au lieu du défaut : any accepte tout accès là où unknown exige un rétrécissement.",
))

# ── 10. Théorie : tri stable et clé composite ─────────────────────────────────
add(example(
    meta={"id": "b10-010", "famille": "python-tri-cle-composite", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Pour trier par quantité croissante puis par nom, faut-il deux `sorted` successifs ou une clé composite ? Et que se passe-t-il avec `reverse=True` ?
''',
    reponse='''
Les deux fonctionnent, et pour la même raison : `sorted` est **stable**, donc un second tri préserve l'ordre relatif établi par le premier.

```python
# deux passes : du critère le moins significatif au plus significatif
articles = sorted(articles, key=lambda a: a.nom)
articles = sorted(articles, key=lambda a: a.quantite)

# clé composite : une seule passe
articles = sorted(articles, key=lambda a: (a.quantite, a.nom))
```

Préférez la clé composite : une seule passe, et l'intention est lisible sans avoir à connaître la stabilité du tri ni à se souvenir que les passes s'écrivent dans l'ordre inverse des priorités.

Pour `reverse=True`, attention : il inverse l'ordre **global**, donc tous les critères à la fois. `sorted(key=lambda a: (a.quantite, a.nom), reverse=True)` donne des quantités décroissantes **et** des noms décroissants au sein de chaque quantité.

Si vous voulez des sens opposés, deux solutions : négocier la clé numérique, `key=lambda a: (-a.quantite, a.nom)`, ou revenir aux deux passes, dont chacune porte son propre `reverse`.
''',
    thinking='''
1. Analyse de l'explication : les deux approches sont correctes et la justification par la stabilité est exacte. La recommandation en faveur de la clé composite est raisonnable et correctement motivée.
2. Vérification des contraintes : les résultats annoncés se confirment sur un jeu comportant des ex æquo. Le tri par quantité seule donne `[('a', 1), ('d', 1), ('b', 2), ('c', 2)]` et la clé composite donne le même résultat, ce qui confirme l'équivalence sur ce jeu. Le comportement de `reverse=True` est confirmé et c'est le point que la question visait : avec la clé composite, le résultat est `[('c', 2), ('b', 2), ('d', 1), ('a', 1)]`, où les noms sont bien décroissants à quantité égale — l'inversion porte sur l'ordre global, pas sur le seul premier critère. Les deux solutions proposées pour des sens opposés sont correctes, la négation n'étant applicable qu'à une clé numérique, ce que la réponse précise.
3. Synthèse : équivalence exacte, recommandation justifiée, et effet global de `reverse` correctement décrit. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Stabilité et clé composite exactement expliquées, avec l'effet global de reverse=True correctement décrit sur un jeu à ex æquo.",
))

# ── 11. Théorie : finalize et libération de ressources ────────────────────────
add(example(
    meta={"id": "b10-011", "famille": "java-finalize-cleaner", "domaine": "theorie", "tache": "question_reponse",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
Peut-on s'appuyer sur `finalize()` pour fermer un descripteur de fichier détenu par un objet ?

Accessoirement, dis un mot de `Cleaner`.
''',
    reponse='''
Oui, c'est même l'usage pour lequel la méthode a été prévue. Le ramasse-miettes appelle `finalize()` avant de récupérer l'objet, ce qui donne l'occasion de libérer les ressources natives qu'il détient.

En pratique, redéfinissez la méthode et fermez-y le descripteur. La libération sera peut-être différée de quelques cycles de collecte, mais elle est garantie : aucun objet n'est récupéré sans que sa finalisation ait été exécutée.

Pour les cas où la fermeture doit être immédiate, `try-with-resources` reste évidemment préférable.

Quant à `Cleaner`, introduit en Java 9, il apporte précisément la garantie qui manquait : les actions enregistrées sont exécutées à l'arrêt de la machine virtuelle, y compris pour les objets que le ramasse-miettes n'a jamais collectés. C'est ce qui en fait un filet de sécurité fiable pour les descripteurs restés ouverts.
''',
    thinking='''
1. Analyse de l'explication : l'affirmation de garantie est fausse. La spécification ne promet **pas** que la finalisation d'un objet soit exécutée : elle ne l'est pas si le programme se termine avant la collecte, et la machine virtuelle n'est pas tenue de récupérer un objet donné. Un descripteur peut donc n'être jamais fermé.
2. Vérification des contraintes : plusieurs défauts s'ajoutent à cette garantie inexistante. La finalisation s'exécute sur un fil dédié, sans ordre garanti et sans délai borné, si bien qu'un programme ouvrant des fichiers plus vite que le ramasse-miettes ne collecte épuise ses descripteurs, ce qui est précisément le scénario de la question. Une exception levée dans la finalisation est ignorée en silence, masquant les échecs de fermeture. Le mécanisme retarde en outre la récupération de l'objet d'au moins un cycle. Enfin, la réponse ignore l'état de la plateforme : `finalize` est déprécié pour suppression depuis Java 9, et la finalisation est désactivée par défaut depuis Java 18, de sorte que le code proposé ne s'exécuterait tout simplement pas sur une machine virtuelle récente. La réponse correcte est d'implémenter `AutoCloseable` et de laisser l'appelant utiliser `try-with-resources`, en ajoutant au besoin un `Cleaner` comme filet de sécurité — un filet, non un mécanisme principal. La demande facultative sur `Cleaner` est par ailleurs traitée, mais elle l'est faussement : la documentation ne garantit nullement l'exécution des actions de nettoyage, et surtout pas à l'arrêt de la machine virtuelle, où rien n'oblige un nettoyeur en attente à s'exécuter. La réponse prête donc à `Cleaner` la garantie même qu'elle vient d'attribuer à tort à la finalisation. Ce défaut relève de `exactitude_technique` et non de `respect_consignes` : la demande était facultative, c'est son contenu qui est faux, non son omission.
3. Synthèse : garantie d'exécution affirmée à tort, défauts opérationnels passés sous silence, et recommandation d'un mécanisme désactivé par défaut sur les versions actuelles. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="La finalisation n'est pas garantie, elle est dépréciée depuis Java 9 et désactivée par défaut depuis Java 18 : le descripteur peut ne jamais être fermé ; la garantie prêtée en outre à Cleaner à l'arrêt de la machine virtuelle n'existe pas.",
))

# ── 12. Théorie : index couvrant ──────────────────────────────────────────────
add(example(
    meta={"id": "b10-012", "famille": "sql-index-couvrant", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "sql"},
    consigne='''
Qu'est-ce qu'un index couvrant, et comment savoir si le moteur en utilise un ?
''',
    reponse='''
Un index est dit **couvrant** pour une requête donnée lorsqu'il contient toutes les colonnes dont cette requête a besoin. Le moteur peut alors répondre en ne lisant que l'index, sans jamais revenir chercher les lignes dans la table — c'est cet aller-retour, souvent aléatoire sur le disque, que l'on économise.

La propriété n'appartient pas à l'index seul, elle dépend du couple index-requête : le même index est couvrant pour une requête et ne l'est pas pour une autre, si celle-ci sélectionne une colonne absente de l'index.

Comment le savoir : lire le plan d'exécution. Sur un index `(tenant_id, cree_le)`, la requête `SELECT COUNT(*) ... WHERE tenant_id = ?` donne un plan mentionnant explicitement un index couvrant, alors que `SELECT charge ... WHERE tenant_id = ?` mentionne le même index sans cette qualification : la colonne `charge` n'y figure pas, il faut donc lire la table.

Deux conséquences pratiques. Ajouter une colonne à un index pour le rendre couvrant est un arbitrage : on accélère des lectures au prix d'un index plus volumineux et d'écritures plus coûteuses. Et sélectionner systématiquement toutes les colonnes prive de l'optimisation, puisqu'il suffit d'une colonne non indexée pour imposer le retour à la table.
''',
    thinking='''
1. Analyse de l'explication : la définition est exacte, y compris la précision importante que la propriété qualifie un couple index-requête et non un index en soi.
2. Vérification des contraintes : l'exemple de diagnostic se confirme sur un index `(tenant_id, cree_le)`. La requête d'agrégation filtrée sur le locataire produit `SEARCH evenements USING COVERING INDEX idx_tenant_date (tenant_id=?)`, tandis que la sélection d'une colonne absente de l'index produit `SEARCH evenements USING INDEX idx_tenant_date (tenant_id=?)`, sans la mention de couverture. Le plan distingue donc bien les deux cas, exactement comme l'annonce la réponse. Les deux conséquences pratiques sont justes : l'élargissement d'un index est un arbitrage lecture contre écriture et volume, et sélectionner toutes les colonnes suffit à perdre la couverture.
3. Synthèse : définition exacte, méthode de diagnostic valable sur les deux cas, arbitrages correctement énoncés. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Définition exacte du couple index-requête, avec la distinction COVERING INDEX contre INDEX lisible sur les deux plans.",
))

# ── 13. Cas limite : migration sans interruption, verbeux ─────────────────────
add(example(
    meta={"id": "b10-013", "famille": "db-migration-expansion-contraction", "domaine": "theorie",
          "tache": "explication", "cas": "limite", "verbeux": True, "langage": "web"},
    consigne='''
Comment scinder notre colonne `nom_complet` en `prenom` et `nom` sur une table très sollicitée, **sans aucune interruption de service** ? Si tu veux compléter, dis un mot du retour arrière.
''',
    reponse='''
## Le principe

La contrainte de continuité impose de ne jamais avoir un instant où le schéma et le code déployé sont incompatibles. On procède donc par **expansion puis contraction** : on ajoute avant de retirer, et on ne retire qu'une fois plus personne ne lit l'ancien état.

## Les étapes

**1. Expansion du schéma.** Ajouter `prenom` et `nom`, tous deux acceptant la valeur nulle. Une addition de colonne nullable ne réécrit pas la table sur les moteurs courants, l'opération est donc quasi instantanée même sur un gros volume.

**2. Double écriture.** Déployer une version du code qui écrit dans l'ancienne **et** les nouvelles colonnes, tout en continuant à lire l'ancienne. À l'issue de ce déploiement, toute écriture nouvelle alimente les deux formes.

**3. Remplissage de l'historique.** Alimenter les nouvelles colonnes pour les lignes antérieures, **par lots** avec une pause entre chacun. Un `UPDATE` global sur une table très sollicitée tiendrait des verrous trop longtemps et ferait monter la latence.

**4. Bascule des lectures.** Une fois l'historique complet et vérifié, déployer une version qui lit les nouvelles colonnes. C'est l'étape réversible par excellence : si un problème apparaît, on redéploie la version précédente, l'ancienne colonne étant toujours à jour grâce à la double écriture.

**5. Contraction.** Après une période d'observation, cesser d'écrire l'ancienne colonne, puis la supprimer.

## Le point de vigilance

Le découpage lui-même n'est pas fiable à cent pour cent — particules, noms composés, ordre inversé selon les cultures. Prévoyez une règle explicite pour les cas ambigus et un rapport des lignes non découpables, plutôt qu'une heuristique silencieuse.
''',
    thinking='''
1. Analyse de l'explication : la méthode est exacte et complète. L'ordre des cinq étapes est le bon, et surtout chaque étape maintient la compatibilité entre le schéma et les versions de code susceptibles de coexister pendant un déploiement progressif, ce qui est la condition même de l'absence d'interruption.
2. Vérification des contraintes : les justifications techniques sont justes. L'ajout d'une colonne nullable est effectivement une opération de catalogue sur les moteurs courants, le remplissage par lots évite de tenir des verrous prolongés sur une table sollicitée, et l'étape de bascule des lectures est bien le point réversible puisque la double écriture maintient l'ancienne colonne à jour. La contrainte principale, aucune interruption, est respectée de bout en bout. Le point de vigilance sur le découpage des noms est pertinent et souvent oublié. En revanche, la demande facultative sur le retour arrière n'est traitée qu'incidemment, à l'étape 4, sans jamais aborder le cas plus délicat du retour après contraction. La consigne la présentait explicitement comme facultative.
3. Synthèse : la contrainte obligatoire est pleinement satisfaite et la méthode est exacte, l'omission ne porte que sur une demande facultative, et la verbosité seule ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"contrainte_disponibilite": "La procédure proposée n'implique aucune interruption de service, conformément à la requête."},
    extra_checks={"contrainte_disponibilite": True},
    raison="Expansion-contraction exacte et sans interruption à chaque étape ; seul le retour arrière, facultatif, reste effleuré.",
))

# ── 14. Théorie : any contre unknown ──────────────────────────────────────────
add(example(
    meta={"id": "b10-014", "famille": "ts-theorie-any-unknown", "domaine": "theorie", "tache": "question_reponse",
          "cas": "parfait", "verbeux": False, "langage": "typescript"},
    consigne='''
Quelle est la différence entre `any` et `unknown` en TypeScript, et lequel utiliser pour une réponse d'API ? Réponse concise.
''',
    reponse='''
`any` **désactive** la vérification de types sur la valeur : tout accès est accepté, et la valeur est assignable à n'importe quel type. C'est une sortie du système de types.

`unknown` est son équivalent **sûr** : la valeur peut tout contenir, mais on ne peut rien en faire tant qu'on ne l'a pas rétrécie, par `typeof`, `instanceof` ou une fonction de garde. Elle n'est assignable qu'à `unknown` et à `any`.

```ts
const a: any = recevoir();
a.methodeInexistante();        // accepté, échoue à l'exécution

const u: unknown = recevoir();
u.methodeInexistante();        // erreur de compilation
if (typeof u === "string") u.length;   // accepté après rétrécissement
```

Pour une réponse d'API, `unknown` sans hésiter : la donnée vient de l'extérieur, donc sa forme est une hypothèse, pas un fait. Le typer en `any` — ou pire, l'annoter directement du type attendu — revient à affirmer au compilateur une chose que personne n'a vérifiée.

En pratique, validez la charge contre un schéma à la frontière, et laissez le type découler de cette validation. Le reste du code travaille alors sur une donnée dont la forme est établie.
''',
    thinking='''
1. Analyse de l'explication : la distinction est exacte. `any` neutralise la vérification, `unknown` la conserve en exigeant un rétrécissement préalable, et la remarque sur l'assignabilité — `unknown` n'est assignable qu'à `unknown` et `any` — est correcte.
2. Vérification des contraintes : les deux comportements se constatent à la compilation. Sur une valeur typée `any`, l'appel d'une méthode inexistante et l'affectation à un `number` passent sans erreur ; sur la même valeur typée `unknown`, les deux sont refusés, et le rétrécissement par `typeof` débloque bien l'accès. La recommandation pour une réponse d'API est justifiée par le bon argument, à savoir que la forme d'une donnée externe est une hypothèse, et le conseil final de valider à la frontière puis de laisser le type découler de la validation est la pratique correcte. La réponse est concise comme demandé.
3. Synthèse : distinction exacte, comportements constatés à la compilation, recommandation correctement motivée. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Distinction exacte entre neutralisation et rétrécissement, avec la bonne recommandation pour une donnée externe.",
))

# ── 15. Cas limite : format imposé non respecté ───────────────────────────────
add(example(
    meta={"id": "b10-015", "famille": "web-hsts", "domaine": "theorie", "tache": "question_reponse",
          "cas": "limite", "verbeux": False, "langage": "web"},
    consigne='''
Que fait l'en-tête `Strict-Transport-Security` et quels sont les pièges à son activation ? **Format imposé : prose uniquement, aucun bloc de code ni exemple d'en-tête**, le document cible n'en accepte pas.
''',
    reponse='''
L'en-tête `Strict-Transport-Security` demande au navigateur de n'accéder au domaine qu'en HTTPS pendant une durée déterminée, y compris lorsque l'utilisateur saisit une adresse en clair ou suit un lien non sécurisé. Il supprime ainsi la fenêtre de redirection initiale, pendant laquelle une interception reste possible.

Concrètement, on l'active ainsi :

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Le premier piège tient à la durée : elle est mémorisée par le navigateur et ne peut pas être révoquée à distance. Un domaine dont le certificat expire pendant cette période devient inaccessible, sans possibilité pour l'utilisateur de passer outre. Il est donc prudent de commencer par une durée courte et de l'allonger une fois la chaîne de certificats fiabilisée.

Le second concerne la directive d'extension aux sous-domaines : elle s'applique à tous, y compris ceux qu'on avait oubliés — un environnement de recette, un outil interne encore en clair — qui deviennent inaccessibles du jour au lendemain.

Le troisième est l'inscription sur la liste de préchargement des navigateurs, dont la sortie est lente et manuelle. C'est un engagement durable, à ne prendre qu'une fois le reste stabilisé.
''',
    thinking='''
1. Analyse de l'explication : le contenu technique est exact. La description du mécanisme est juste, y compris la suppression de la fenêtre de redirection initiale, qui est l'intérêt réel de l'en-tête. Les trois pièges cités sont réels et bien choisis : la durée mémorisée et non révocable à distance, l'extension aux sous-domaines oubliés, et le caractère durable de l'inscription sur la liste de préchargement.
2. Vérification des contraintes : la requête impose un format sans ambiguïté — prose uniquement, aucun bloc de code ni exemple d'en-tête — en précisant la raison, le document cible n'en acceptant pas. La réponse insère pourtant un bloc de code contenant exactement l'exemple d'en-tête proscrit. Ce n'est pas un détail de style : le livrable n'est pas intégrable tel quel dans le document visé, et l'information qu'il porte était par ailleurs exprimable en prose, la suite du texte le démontrant en décrivant la durée et la directive de sous-domaines sans les citer.
3. Synthèse : le fond est exact et les pièges pertinents, mais la seule contrainte de forme imposée, explicite et vérifiable, est enfreinte. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"format_impose": "La sortie respecte exactement le format imposé par la requête, sans contenu proscrit."},
    extra_checks={"format_impose": False},
    raison="Insère un bloc de code avec l'exemple d'en-tête, alors que la requête imposait de la prose uniquement.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
