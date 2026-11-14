#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_08.jsonl (15 examples, CODE_ANALYSIS).

Chiffres issus des sondes probe08.py, Probe08.java et probe08.js exécutées le 2026-09-13.
Polarités inversées volontairement sur aucune_dependance_externe, signature_conforme et
format_impose, qui n'apparaissaient jusqu'ici qu'avec une seule valeur.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402

EXAMPLES = []
add = EXAMPLES.append

# ── 1-2. Paire contrastive : persistance d'un cache utilisateur ───────────────
CONSIGNE_CACHE = '''
Écris les fonctions qui sauvegardent et rechargent sur disque le cache de préférences d'un utilisateur. Le fichier est stocké dans le répertoire personnel de l'utilisateur, qui peut aussi être synchronisé entre ses postes.
'''

add(example(
    meta={"id": "b08-001", "famille": "python-persistance-cache", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": True, "langage": "python"},
    consigne=CONSIGNE_CACHE,
    reponse='''
## Implémentation

`pickle` est le format naturel ici : il sérialise n'importe quelle structure Python sans conversion, là où JSON obligerait à aplatir les types.

```python
import pickle
from pathlib import Path

def sauver_cache(chemin: Path, preferences: dict) -> None:
    chemin.write_bytes(pickle.dumps(preferences))

def charger_cache(chemin: Path) -> dict:
    if not chemin.exists():
        return {}
    return pickle.loads(chemin.read_bytes())
```

## Sur la sécurité

On lit parfois que `pickle` serait dangereux. C'est vrai dans l'absolu, mais le risque suppose un flux **d'origine inconnue**, typiquement reçu par le réseau. Ici, le fichier est écrit par notre propre application dans le répertoire de l'utilisateur : la source est maîtrisée, et un attaquant capable d'y écrire aurait de toute façon déjà la main sur la machine.

## Avantages

| Format | Types Python préservés | Vitesse | Lisible |
|---|---|---|---|
| `pickle` | ✅ tous | rapide | non |
| JSON | types de base seulement | rapide | oui |

Le choix de `pickle` est donc justifié pour un cache interne.
''',
    thinking='''
1. Analyse du code : les deux fonctions sont correctes sur le plan fonctionnel, le cas du fichier absent est traité, et le tableau comparatif des formats est exact sur les types préservés comme sur la lisibilité.
2. Vérification des contraintes : le raisonnement de sécurité est faux, et la requête donne précisément le contre-exemple. `pickle.loads` ne désérialise pas des données, il **exécute** les instructions de reconstruction contenues dans le flux : une classe dont la méthode `__reduce__` renvoie un appelable voit celui-ci invoqué au chargement. Un flux de 83 octets suffit à déclencher l'exécution d'un appel arbitraire pendant `pickle.loads`, sans exception ni avertissement d'aucune sorte. L'argument « la source est maîtrisée » ne tient pas ici : la requête précise que le répertoire personnel peut être **synchronisé entre postes**, donc le fichier traverse un service tiers et revient depuis une source qui n'est plus la nôtre. Il suffit qu'un seul poste ou le service de synchronisation soit compromis pour transformer un cache en exécution de code. La conclusion « un attaquant capable d'y écrire aurait déjà la main sur la machine » est donc fausse dans le scénario décrit. JSON convient parfaitement à des préférences, et ne peut porter aucun appelable.
3. Synthèse : code fonctionnel, mais choix de format justifié par une analyse de risque erronée qui ignore le vecteur donné dans la requête. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="pickle.loads exécute le contenu du flux, et le fichier transite par une synchronisation tierce : la source n'est pas maîtrisée.",
))

add(example(
    meta={"id": "b08-002", "famille": "python-persistance-cache", "domaine": "code", "tache": "generation",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne=CONSIGNE_CACHE,
    reponse='''
```python
import json
from pathlib import Path

def sauver_cache(chemin: Path, preferences: dict) -> None:
    temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
    temporaire.write_text(json.dumps(preferences, ensure_ascii=False), encoding="utf-8")
    temporaire.replace(chemin)          # remplacement atomique

def charger_cache(chemin: Path) -> dict:
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}                        # cache corrompu : on repart d'un cache vide
```

Trois choix à expliciter :

- **JSON plutôt que `pickle`.** Le fichier vit dans un répertoire susceptible d'être synchronisé entre postes : il peut donc revenir d'une source que nous ne contrôlons plus. Or `pickle.loads` exécute les instructions de reconstruction contenues dans le flux, ce qui ferait d'un cache un vecteur d'exécution de code. JSON ne peut porter aucun appelable.
- **Écriture puis remplacement.** Écrire dans un fichier temporaire avant `replace` évite de laisser un cache tronqué si le processus est interrompu en cours d'écriture.
- **Encodage explicite.** `encoding="utf-8"` des deux côtés, sans quoi la lecture dépendrait du réglage local du poste.
''',
    thinking='''
1. Analyse du code : les deux fonctions remplissent le contrat. Le fichier absent et le fichier corrompu renvoient un cache vide plutôt que de propager une exception, ce qui est le comportement attendu d'un cache.
2. Vérification des contraintes : les trois justifications sont exactes. Le risque `pickle` est réel — un flux forgé exécute un appel arbitraire pendant `pickle.loads`, sans exception —, et l'argument est correctement rattaché au fait, donné dans la requête, que le répertoire peut être synchronisé entre postes. Le remplacement atomique par fichier temporaire puis `Path.replace` est la bonne pratique et protège effectivement d'une écriture interrompue. L'encodage explicite évite la dépendance au réglage local d'`open()`. Aucune affirmation non étayée.
3. Synthèse : implémentation correcte, format choisi pour la bonne raison, et deux précautions pertinentes sur l'atomicité et l'encodage. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="JSON justifié par le vecteur de synchronisation, écriture atomique par fichier temporaire et encodage explicite.",
))

# ── 3. Imports circulaires ────────────────────────────────────────────────────
add(example(
    meta={"id": "b08-003", "famille": "python-imports-circulaires", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Notre application refuse de démarrer depuis l'ajout d'un module :

```
AttributeError: partially initialized module 'a' has no attribute 'VALEUR_A'
(most likely due to a circular import)
```

`a.py` importe `b`, et `b.py` importe `a` pour lire une constante au chargement. Explique et corrige.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse de l'explication : le mécanisme est exact, y compris le détail qui compte — l'inscription dans `sys.modules` avant exécution du corps, qui évite la récursion infinie mais expose un module partiellement initialisé. Le message d'erreur cité est exactement celui que produit l'interpréteur : `AttributeError: partially initialized module 'a' has no attribute 'VALEUR_A' (most likely due to a circular import)`.
2. Vérification des contraintes : les trois corrections sont valides et correctement hiérarchisées, l'extraction d'un module tiers étant la seule qui supprime le cycle plutôt que de l'accommoder. La deuxième fonctionne bien : en déplaçant `import a` à l'intérieur de la fonction, le programme se termine normalement et produit le résultat attendu. La conclusion est exacte et souvent mal comprise : un cycle n'est fautif que si un module a besoin de l'autre pendant son chargement.
3. Synthèse : mécanisme exact, message d'erreur conforme, corrections valides et bien ordonnées. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Mécanisme du module partiellement initialisé exactement décrit, message conforme, et correction par import différé valide.",
))

# ── 4. Dépendance externe interdite ──────────────────────────────────────────
add(example(
    meta={"id": "b08-004", "famille": "python-config-immuable", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Écris la classe de configuration de notre outil en ligne de commande : quelques champs typés, une liste d'extensions surveillées, et une validation du port. **Contrainte : bibliothèque standard uniquement**, l'outil est distribué comme un script autonome.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse du code : le code est correct en soi. La syntaxe de Pydantic v2 est respectée, `field_validator` avec `@classmethod` est la forme attendue, et `default_factory` évite le partage d'une liste entre instances. L'affirmation sur la validation automatique des types est exacte.
2. Vérification des contraintes : la requête impose la bibliothèque standard uniquement, en donnant la raison — un script distribué de façon autonome. Pydantic est une dépendance externe, qui plus est avec une extension compilée : elle ne peut pas être supposée présente sur le poste cible, et l'outil échouerait à l'import. La contrainte est explicite, vérifiable et bloquante. La réponse standard existe : `dataclasses` couvre exactement ce besoin, avec `field(default_factory=list)` pour la liste et une validation dans `__post_init__`. À noter que `dataclasses` protège d'ailleurs mieux que le langage nu sur un point précis : déclarer une liste nue en valeur par défaut lève `ValueError: mutable default <class 'list'> for field articles is not allowed: use default_factory` dès la définition de la classe, là où une fonction ordinaire accepterait silencieusement le même piège.
3. Synthèse : code juste mais dépendance explicitement interdite par la requête, alors que la bibliothèque standard offre l'équivalent. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"aucune_dependance_externe": "La solution n'utilise que la bibliothèque standard, comme l'exige la requête."},
    extra_checks={"aucune_dependance_externe": False},
    raison="Utilise Pydantic alors que la requête impose la bibliothèque standard pour un script autonome ; dataclasses couvre le besoin.",
))

# ── 5. Clé mutable dans une HashMap ───────────────────────────────────────────
add(example(
    meta={"id": "b08-005", "famille": "java-cle-mutable", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Des entrées de notre index disparaissent : `get` renvoie `null` pour des clés que nous venons pourtant d'insérer, et la taille de la map n'a pas bougé. Les clés sont des objets `Cle` avec `equals` et `hashCode` corrects, mais dont le champ est modifié après insertion. Corrige, **en conservant la signature publique de l'index**.
''',
    reponse='''
Le défaut n'est pas dans `equals` ni dans `hashCode`, mais dans la mutation elle-même.

`HashMap` range l'entrée dans un seau déterminé par le hachage **au moment de l'insertion**. Muter ensuite un champ utilisé par `hashCode` change le seau où l'entrée *devrait* se trouver, sans la déplacer. L'entrée devient alors inatteignable : ni l'ancienne valeur de la clé ni la nouvelle ne mènent au bon seau, alors que l'entrée est toujours là et compte dans la taille.

La correction consiste à rendre la clé immuable, sans toucher à la signature de l'index :

```java
public final class Cle {
    private final int valeur;
    public Cle(int valeur) { this.valeur = valeur; }
    public int valeur() { return valeur; }
    public Cle withValeur(int nouvelle) { return new Cle(nouvelle); }
    @Override public boolean equals(Object o) { return o instanceof Cle c && c.valeur == valeur; }
    @Override public int hashCode() { return Integer.hashCode(valeur); }
}
```

Un `record Cle(int valeur)` conviendrait tout aussi bien et génère les deux méthodes.

Là où le code mutait la clé, il faut désormais retirer l'entrée, construire la nouvelle clé, puis réinsérer :

```java
index.remove(ancienne);
index.put(ancienne.withValeur(nouvelle), valeur);
```

La règle générale : une clé de table de hachage doit être immuable, ou du moins ses champs d'égalité doivent l'être.
''',
    thinking='''
1. Analyse de l'explication : le mécanisme est exact. Le seau est déterminé au moment de l'insertion, et muter un champ d'égalité désynchronise l'emplacement réel de l'entrée et celui que la recherche calcule.
2. Vérification des contraintes : la conséquence annoncée est réelle, et plus forte que ce à quoi on s'attend spontanément. Après mutation de la clé de 1 vers 2, `get(new Cle(2))` renvoie `null` — la recherche vise le bon seau mais l'entrée n'y est pas — et `get(new Cle(1))` renvoie `null` également, car l'entrée présente dans l'ancien seau ne satisfait plus `equals`. Pendant ce temps, `containsValue("valeur")` reste `true` et la taille vaut toujours 1 : l'entrée existe et reste inatteignable, exactement le symptôme décrit dans la requête. La correction par immuabilité est la bonne, la mention du `record` est pertinente, et le couple retrait puis réinsertion est la manipulation correcte. La signature publique de l'index est bien conservée, comme exigé.
3. Synthèse : cause exacte, symptôme intégralement reproduit par la mesure, correction adaptée et contrainte de signature respectée. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"signature_conforme": "La signature publique visée par la requête est conservée."},
    extra_checks={"signature_conforme": True},
    raison="Explique exactement la désynchronisation du seau, symptôme intégralement reproduit, correction par immuabilité à signature inchangée.",
))

# ── 6. serialVersionUID ───────────────────────────────────────────────────────
add(example(
    meta={"id": "b08-006", "famille": "java-serialversionuid", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
Nos événements sont sérialisés en Java et écrits dans une file persistante que des services relisent après redéploiement. Rédige la classe d'événement et explique comment gérer son évolution.
''',
    reponse='''
```java
public class OrderEvent implements Serializable {
    private final String orderId;
    private final long amountCents;

    public OrderEvent(String orderId, long amountCents) {
        this.orderId = orderId;
        this.amountCents = amountCents;
    }
    // accesseurs omis
}
```

Inutile de déclarer un `serialVersionUID` : la JVM en calcule un automatiquement à partir de la classe, et ce mécanisme est stable — c'est justement pour cela qu'il est fourni par défaut. Ajouter le champ à la main relève de l'habitude, pas de la nécessité.

Pour faire évoluer la classe, ajoutez simplement les nouveaux champs : les anciens messages seront relus avec les valeurs par défaut pour les champs absents.
''',
    thinking='''
1. Analyse du code : la classe est correcte et l'affirmation sur les champs absents est exacte dans son principe — lors d'une évolution compatible, les champs ajoutés reçoivent bien leur valeur par défaut. Mais la prémisse qui la précède est fausse, et elle invalide tout le raisonnement.
2. Vérification des contraintes : l'identifiant calculé par la JVM n'est pas stable, il est **dérivé de la structure de la classe** — nom, modificateurs, interfaces, champs, signatures des méthodes. Toute évolution le change, et la relecture d'un message ancien échoue alors par `InvalidClassException` pour incompatibilité d'identifiant, avant même d'atteindre la logique des champs par défaut. Une classe sans déclaration explicite se voit attribuer un identifiant tel que `-2063441251666474985`, valeur dépendant de sa structure, là où une classe déclarant `serialVersionUID = 1L` expose bien `1`. Le contexte de la requête rend le défaut bloquant : une file persistante relue après redéploiement garantit la coexistence d'anciens messages et d'une nouvelle version de la classe. La correction est de déclarer `private static final long serialVersionUID = 1L;` et de ne l'incrémenter que lors d'une rupture assumée. À noter qu'un format de sérialisation neutre serait de toute façon préférable pour une file persistante, la sérialisation Java couplant le format au code.
3. Synthèse : affirmation fausse sur la stabilité de l'identifiant, qui conduit à une classe incapable de survivre à l'évolution que la requête décrit explicitement. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="L'identifiant calculé dérive de la structure de la classe : toute évolution casse la relecture par InvalidClassException.",
))

# ── 7. Pollution de prototype ─────────────────────────────────────────────────
add(example(
    meta={"id": "b08-007", "famille": "js-pollution-prototype", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "typescript"},
    consigne='''
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
''',
    reponse='''
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
''',
    thinking='''
1. Analyse de l'explication : le mécanisme est exact, y compris le point subtil — `JSON.parse` crée bien `__proto__` comme propriété propre énumérable, donc visible par `Object.keys`, tandis que la lecture sur l'objet cible passe par l'accesseur et renvoie le prototype.
2. Vérification des contraintes : la chaîne complète tient. Après une fusion naïve de `{"__proto__": {"estAdmin": true}}`, `({}).estAdmin` vaut `true` et un objet neuf hérite de la propriété. Avec le filtrage des clés, la même charge laisse `({}).estAdmin` à `undefined`. L'affirmation sur `structuredClone` est exacte elle aussi : le même JSON cloné ainsi ne pollue pas. La recommandation finale sur la validation par schéma est pertinente, et correctement présentée comme supprimant la classe de problèmes plutôt qu'un vecteur.
3. Synthèse : diagnostic exact, correction efficace, renforcements complémentaires justes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Pollution de prototype exactement diagnostiquée, avec une correction efficace et des renforcements pertinents.",
))

# ── 8. NaN et indexOf, réponse verbeuse ───────────────────────────────────────
add(example(
    meta={"id": "b08-008", "famille": "js-egalite-nan", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": True, "langage": "typescript"},
    consigne='''
Notre contrôle « la mesure est-elle déjà enregistrée ? » laisse passer des doublons quand la valeur est `NaN`.

```ts
if (mesures.indexOf(valeur) === -1) {
  mesures.push(valeur);
}
```

Explique et corrige.
''',
    reponse='''
## Pourquoi `NaN` échappe au contrôle

`NaN` est la seule valeur de JavaScript qui n'est égale à rien, pas même à elle-même. La spécification IEEE 754 le prévoit ainsi : toute comparaison impliquant `NaN` est fausse, y compris `NaN === NaN`.

## Ce que fait `indexOf`

`Array.prototype.indexOf` parcourt le tableau en comparant avec l'égalité stricte. Comme aucune comparaison ne peut réussir face à `NaN`, la méthode renvoie systématiquement `-1`, et votre contrôle conclut à chaque fois que la valeur est absente.

## La correction

Il suffit de tester le cas à part :

```ts
const dejaPresent = Number.isNaN(valeur)
  ? mesures.some(Number.isNaN)
  : mesures.indexOf(valeur) !== -1;

if (!dejaPresent) {
  mesures.push(valeur);
}
```

## À retenir

| Méthode | Trouve `NaN` |
|---|---|
| `indexOf` | non |
| `includes` | non |
| `lastIndexOf` | non |

Aucune méthode de recherche de tableau ne sait traiter `NaN` : le test explicite est incontournable.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact et bien expliqué. `NaN === NaN` vaut bien `false`, et `indexOf`, qui s'appuie sur l'égalité stricte, renvoie effectivement `-1` sur un tableau contenant `NaN`. La correction proposée fonctionne.
2. Vérification des contraintes : le tableau récapitulatif est faux sur la ligne qui compte, et cette erreur transforme une réponse correcte en conseil trompeur. `Array.prototype.includes` utilise l'algorithme SameValueZero, et non l'égalité stricte : il **trouve** `NaN`. `[NaN].includes(NaN)` renvoie `true` là où `[NaN].indexOf(NaN)` renvoie `-1`. La conclusion « aucune méthode ne sait traiter NaN » est donc fausse, et elle prive le lecteur de la correction la plus simple : remplacer `indexOf(valeur) === -1` par `!mesures.includes(valeur)`, une ligne au lieu de trois. Dans le même registre, `new Set([NaN, NaN]).size` vaut 1, confirmant que SameValueZero est utilisé aussi par les collections.
3. Synthèse : cause correctement identifiée et correctif fonctionnel, mais le récapitulatif énonce une contre-vérité vérifiable qui masque la solution idiomatique. FAIL.
''',
    exact=False, bugs=True, consignes=True,
    raison="Affirme qu'includes ne trouve pas NaN alors que [NaN].includes(NaN) vaut true, ce qui rendait la correction triviale.",
))

# ── 9. Tri d'objets sans comparateur ──────────────────────────────────────────
add(example(
    meta={"id": "b08-009", "famille": "js-tri-objets", "domaine": "code", "tache": "refactoring",
          "cas": "defaillant", "verbeux": False, "langage": "typescript"},
    consigne='''
Simplifie ce tri, qui me paraît verbeux. Accessoirement, dis un mot du tri stable.

```ts
const tries = [...articles].sort((a, b) => a.quantite - b.quantite);
```
''',
    reponse='''
Le comparateur est superflu ici : `sort` sait ordonner les objets d'une même forme en s'appuyant sur leur représentation naturelle.

```ts
const tries = [...articles].sort();
```

Le résultat est identique et l'intention plus lisible. Le comparateur explicite ne se justifie que lorsqu'on trie sur un critère autre que l'ordre naturel, par exemple un tri décroissant.
''',
    thinking='''
1. Analyse du code : l'affirmation est fausse. Sans comparateur, `Array.prototype.sort` convertit chaque élément en chaîne, et tous les objets ordinaires donnent `"[object Object]"`. Toutes les clés de tri sont donc égales entre elles.
2. Vérification des contraintes : la conséquence est immédiate. `[{n:10},{n:9},{n:1}].sort()` renvoie `[{"n":10},{"n":9},{"n":1}]`, c'est-à-dire l'ordre d'origine inchangé, le tri étant stable depuis ES2019. Le résultat n'est donc pas « identique », il est simplement non trié, et le défaut est particulièrement pernicieux : sur un jeu de données déjà à peu près ordonné, la sortie paraît plausible et le bug passe la revue. La requête demandait une simplification à comportement constant ; le comparateur `(a, b) => a.quantite - b.quantite` est déjà la forme idiomatique et n'a rien de verbeux. La seule remarque défendable aurait été de signaler que `[...articles]` protège bien l'appelant, `sort` triant en place. La demande facultative sur le tri stable n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : la simplification proposée supprime purement et simplement le tri, tout en affirmant l'équivalence. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Sans comparateur, sort() compare des chaînes « [object Object] » : l'ordre reste inchangé, le tri disparaît.",
))

# ── 10. Théorie : préchauffage et mesure ──────────────────────────────────────
add(example(
    meta={"id": "b08-010", "famille": "java-mesure-jit", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Un collègue conclut qu'une méthode est deux fois plus lente qu'une autre après les avoir chronométrées une fois chacune avec `System.nanoTime()`. Que penser de cette mesure ?
''',
    reponse='''
Qu'elle ne permet pas de conclure. Un chronométrage unique sur la JVM mesure surtout l'état du moteur, pas le code.

Trois effets se superposent, tous dans le sens d'une première exécution plus lente :

- **Interprétation puis compilation.** Le bytecode démarre interprété ; la compilation à la volée n'intervient qu'après quelques milliers d'exécutions, et l'optimisation dépend des profils observés.
- **Ramasse-miettes.** Une collecte survenue pendant l'une des deux mesures s'y impute intégralement.
- **Caches et allocation.** Premiers accès mémoire, chargement de classes, initialisation paresseuse.

Sur une boucle simple mesurée cinq fois de suite, les durées observées sont 15, 13, 11, 11, 11 ms : la première exécution est environ 1,4 fois plus lente que le régime établi, et la mesure ne se stabilise qu'au bout de trois tours. L'écart est modeste sur un cas aussi simple, mais il suffit à inverser une comparaison entre deux implémentations proches — ce qui est précisément la situation décrite.

Ce qu'il faut faire : préchauffer avant de mesurer, répéter suffisamment, et rapporter une médiane plutôt qu'une valeur isolée. Pour une comparaison qu'on entend publier, JMH est l'outil approprié : il gère le préchauffage, l'isolation des itérations et la prévention de l'élimination de code mort, ce qu'un chronométrage manuel ne fait pas.
''',
    thinking='''
1. Analyse de l'explication : les trois effets cités sont réels et correctement décrits, et le sens de l'erreur — première exécution pénalisée — est le bon. La description du passage de l'interprétation à la compilation à la volée est exacte, tout comme la dépendance de l'optimisation aux profils d'exécution.
2. Vérification des contraintes : les chiffres avancés sont cohérents. Cinq exécutions successives de la même boucle donnent 15, 13, 11, 11, 11 ms, soit un rapport de 1,4 entre la première et la dernière, avec stabilisation au troisième tour. La réponse ne surestime pas l'effet : elle le qualifie explicitement de modeste sur un cas simple, tout en notant qu'il suffit à inverser une comparaison serrée, ce qui est l'argument pertinent au regard de la question posée. Les recommandations finales sont justes, et l'attribution à JMH de la gestion du préchauffage, de l'isolation des itérations et de la prévention de l'élimination de code mort est exacte.
3. Synthèse : diagnostic exact, chiffres cohérents et correctement relativisés, recommandations appropriées. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Effets de préchauffage exactement décrits, chiffres cohérents et honnêtement relativisés, recommandation JMH pertinente.",
))

# ── 11. Théorie : chargement de classes ───────────────────────────────────────
add(example(
    meta={"id": "b08-011", "famille": "java-chargement-classes", "domaine": "theorie", "tache": "question_reponse",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne='''
Quelle est la différence entre `ClassNotFoundException` et `NoClassDefFoundError` ? Notre application lève la seconde au démarrage. Accessoirement, dis un mot des dépendances optionnelles absentes à l'exécution.
''',
    reponse='''
Ce sont deux noms pour la même situation, hérités de l'histoire de la plateforme : une classe est absente du chemin de classes.

`ClassNotFoundException` est levée par les anciens chargeurs, `NoClassDefFoundError` par le mécanisme moderne intégré à la JVM. Dans les deux cas, le diagnostic est identique : il manque une bibliothèque.

Pour votre démarrage, vérifiez donc que toutes les dépendances sont bien présentes dans le paquet livré, et que leurs versions correspondent à celles utilisées à la compilation.
''',
    thinking='''
1. Analyse de l'explication : l'assimilation des deux types est fausse, et la distinction annoncée entre « anciens chargeurs » et « mécanisme moderne » est inventée. Ce ne sont ni deux époques, ni deux implémentations : ce sont deux situations différentes, ce que reflète déjà leur hiérarchie — l'une est une exception vérifiée, l'autre une erreur.
2. Vérification des contraintes : `ClassNotFoundException` est levée lors d'un chargement **explicite**, typiquement `Class.forName` ou `loadClass`, quand le nom demandé est introuvable. `NoClassDefFoundError` signifie que la classe était présente à la compilation mais que la JVM ne parvient pas à en produire la définition à l'exécution. Le cas décisif, absent de la réponse, est celui où la classe est bien présente : si son initialisation statique échoue, la première tentative lève `ExceptionInInitializerError`, et **toute tentative ultérieure lève `NoClassDefFoundError`** sur une classe pourtant bien empaquetée. Or la requête précise que l'erreur survient au démarrage, moment où les initialisations statiques s'exécutent : le conseil donné, vérifier la présence des bibliothèques, envoie chercher au mauvais endroit. La démarche correcte est de remonter aux premières lignes du journal pour trouver l'`ExceptionInInitializerError` d'origine et sa cause. La demande facultative sur les dépendances optionnelles absentes à l'exécution n'est pas traitée, mais la consigne la présentait explicitement comme telle : l'omission n'entre donc pas dans l'évaluation de `respect_consignes`.
3. Synthèse : les deux types sont confondus sur la base d'une explication historique inventée, et le conseil détourne du diagnostic réel dans le contexte donné. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Confond les deux types : NoClassDefFoundError signale souvent un échec d'initialisation statique, pas une classe absente.",
))

# ── 12. Cas limite : transactions distribuées, verbeux ────────────────────────
add(example(
    meta={"id": "b08-012", "famille": "archi-saga", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": True, "langage": "sql"},
    consigne='''
Nous découpons notre monolithe en deux services, commandes et paiements, chacun avec sa base. Comment garder la cohérence d'une opération qui touche les deux ? En bonus, dis un mot de la boîte d'envoi transactionnelle.
''',
    reponse='''
## Ce qui n'est plus disponible

Avec une base unique, la transaction ACID vous donnait l'atomicité gratuitement. Deux bases, deux gestionnaires de transactions : cette garantie disparaît.

La tentation est de la reconstituer par une validation en deux phases. C'est possible, mais rarement souhaitable : le coordinateur devient un point de défaillance, les verrous sont tenus pendant tout le protocole, et le débit s'effondre dès qu'un participant est lent. La plupart des équipes qui l'ont adoptée dans un contexte de microservices l'ont ensuite abandonnée.

## Le modèle saga

On remplace une transaction atomique par une **suite de transactions locales**, chacune validée dans sa propre base, et chacune dotée d'une **compensation** qui annule son effet métier.

Sur votre cas : la commande est créée en statut « en attente », le paiement est débité, puis la commande passe en « confirmée ». Si le débit échoue, la compensation annule la commande.

Deux propriétés à accepter :

- **La cohérence devient éventuelle.** Il existe une fenêtre où la commande existe sans paiement. L'interface doit l'assumer, par exemple avec un statut explicite.
- **La compensation n'est pas un retour arrière.** On ne défait pas le passé, on ajoute une opération qui en neutralise l'effet. Un remboursement laisse une trace, contrairement à une annulation de transaction.

| | validation en deux phases | saga |
|---|---|---|
| atomicité | conservée | remplacée par des compensations |
| verrous | tenus pendant tout le protocole | locaux à chaque transaction |
| coordinateur | point de défaillance | aucun |
| cohérence | immédiate | éventuelle |

## Le point difficile

Ce n'est pas la saga elle-même, c'est la **fiabilité de la transition** : votre service doit valider en base et publier un message, et ces deux actions ne sont pas atomiques. Si le processus tombe entre les deux, l'état est incohérent sans que personne ne le sache.

## Et l'idempotence

Chaque étape doit être rejouable sans effet supplémentaire, puisqu'un message peut être livré deux fois. En pratique, une clé d'idempotence par étape, mémorisée côté récepteur.
''',
    thinking='''
1. Analyse de l'explication : le contenu est exact. La perte de l'atomicité multi-bases, les réserves sur la validation en deux phases — coordinateur en point de défaillance, verrous tenus pendant le protocole —, la définition de la saga comme suite de transactions locales compensables, et l'exemple appliqué au découpage décrit sont tous corrects.
2. Vérification des contraintes : les deux propriétés énoncées sont justes et bien choisies, en particulier la distinction entre compensation et retour arrière, qui est le point que les réponses superficielles manquent. L'exigence d'idempotence est correctement motivée par la possibilité d'une double livraison. La section « le point difficile » identifie exactement le problème de la double écriture entre base et courtier de messages — mais s'arrête là, alors que la demande facultative portait précisément sur la boîte d'envoi transactionnelle, qui est la réponse standard à ce problème. L'omission est donc d'autant plus visible que le texte y conduit. La consigne la présentait toutefois comme facultative. La réponse est par ailleurs longue, avec cinq sections là où trois auraient suffi.
3. Synthèse : tout l'obligatoire est exact et pertinent, l'omission porte sur une demande explicitement facultative, et la verbosité seule ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Saga et compensation exactement décrites ; la boîte d'envoi transactionnelle, explicitement facultative, n'est pas traitée.",
))

# ── 13. Cas limite : format respecté, partie facultative omise ────────────────
add(example(
    meta={"id": "b08-013", "famille": "web-http2-http3", "domaine": "theorie", "tache": "question_reponse",
          "cas": "limite", "verbeux": False, "langage": "web"},
    consigne='''
Faut-il activer HTTP/3 sur notre passerelle, déjà en HTTP/2 ? **Réponds en quatre puces maximum.** Sans obligation, dis un mot de la découverte de service via `Alt-Svc`.
''',
    reponse='''
- **Le gain réel porte sur les réseaux instables.** HTTP/2 multiplexe plusieurs flux sur une connexion TCP unique : une perte de paquet bloque tous les flux le temps de la retransmission. HTTP/3, au-dessus de QUIC, isole les flux, donc une perte n'affecte que le flux concerné.
- **Sur réseau fiable, l'écart est marginal.** Si vos clients sont des serveurs en centre de données, le blocage en tête de file TCP ne se produit quasiment pas et vous ne mesurerez rien.
- **Le second gain est l'établissement de connexion.** QUIC fusionne la poignée de main transport et TLS, et permet la reprise en zéro aller-retour — sensible sur mobile, où les connexions se rétablissent souvent.
- **Le coût est opérationnel.** UDP sur le port 443 doit être autorisé de bout en bout, certains pare-feux d'entreprise le bloquent, et votre outillage d'observation doit savoir le lire.
''',
    thinking='''
1. Analyse de l'explication : les quatre points sont exacts. Le blocage en tête de file au niveau TCP affecte bien tous les flux multiplexés d'une connexion HTTP/2, l'isolation des flux par QUIC est correctement présentée comme le gain principal, la fusion des poignées de main transport et TLS ainsi que la reprise en zéro aller-retour sont justes, et la réserve sur UDP filtré par certains pare-feux est réelle.
2. Vérification des contraintes : la contrainte de forme, quatre puces au maximum, est respectée à la lettre — exactement quatre puces, sans introduction ni conclusion qui la contourneraient. La réponse tranche la question posée en distinguant les cas d'usage plutôt qu'en donnant un avis général, ce qui est adapté. En revanche, la demande facultative sur `Alt-Svc` n'est pas traitée, alors qu'elle aurait complété utilement le propos, la bascule vers HTTP/3 reposant précisément sur cet en-tête. La consigne la présentait explicitement comme facultative.
3. Synthèse : le fond est exact, la contrainte de format est respectée, et l'unique omission porte sur une demande explicitement facultative. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"format_impose": "La sortie respecte la limite de longueur chiffrée fixée par la requête."},
    extra_checks={"format_impose": True},
    raison="Quatre points exacts dans la limite imposée ; seule la mention d'Alt-Svc, explicitement facultative, manque.",
))

# ── 14. Théorie : is contre == en Python ──────────────────────────────────────
add(example(
    meta={"id": "b08-014", "famille": "python-is-vs-egal", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Un test compare deux entiers avec `is` et passe en local mais échoue en intégration. Explique.
''',
    reponse='''
`is` compare l'**identité** des objets, `==` compare leur **valeur**. Que le test passe parfois est un accident d'implémentation, pas une garantie.

CPython réutilise les objets des petits entiers, conventionnellement de -5 à 256 : deux variables valant 100 désignent alors le même objet et `is` renvoie vrai. Au-delà, chaque évaluation peut produire un objet distinct, et `is` renvoie faux pour des valeurs pourtant égales. Le compilateur ajoute une couche de surprise : deux littéraux identiques dans une même unité de compilation peuvent être repliés en une seule constante, si bien que le comportement diffère selon que les valeurs viennent de littéraux, d'un calcul ou d'une désérialisation — donc typiquement selon qu'on est en test unitaire ou en intégration.

La règle est simple : `==` pour comparer des valeurs, `is` réservé aux singletons, c'est-à-dire `None`, `True`, `False`, et les sentinelles créées explicitement. `if x is None` est la forme correcte ; `if x == None` fonctionne mais laisse une classe redéfinir `__eq__`.

Le même piège existe sur les chaînes, où l'internement dépend de la forme du littéral et du moment de la construction.
''',
    thinking='''
1. Analyse de l'explication : la distinction identité contre valeur est exacte, et le diagnostic est le bon. La réutilisation des petits entiers par CPython, dans la plage usuellement citée de -5 à 256, est correctement présentée comme un détail d'implémentation et non comme une garantie du langage.
2. Vérification des contraintes : la mention du repliement des constantes est juste et explique précisément l'écart entre environnements décrit dans la requête, selon que les valeurs proviennent de littéraux ou d'un calcul. La règle pratique est correcte, et la réserve sur `x == None` est exacte, une redéfinition de `__eq__` pouvant en changer le résultat, là où `is None` teste l'identité du singleton. Le rapprochement final avec l'internement des chaînes est pertinent et correctement nuancé, puisqu'il dépend effectivement de la forme du littéral et du moment de la construction.
3. Synthèse : distinction exacte, cause de l'intermittence correctement identifiée, règle pratique justifiée. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Distinction identité/valeur exacte, réutilisation des petits entiers et repliement des constantes correctement invoqués.",
))

# ── 15. Cas limite : périmètre explicitement exclu ────────────────────────────
add(example(
    meta={"id": "b08-015", "famille": "perf-memoisation", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": False, "langage": "web"},
    consigne='''
Explique la mémoïsation et quand elle est appropriée dans un service applicatif. **Ne parle pas du cache HTTP ni du CDN**, c'est traité ailleurs dans le document.
''',
    reponse='''
La mémoïsation consiste à conserver le résultat d'un appel pour le renvoyer directement lors d'un appel identique ultérieur. Trois conditions doivent être réunies : la fonction doit être **déterministe**, ses arguments doivent constituer une **clé fiable**, et le coût du calcul doit dépasser celui du stockage et de la recherche.

Elle convient bien à un calcul pur et coûteux — un parsing, une transformation de graphe, une agrégation figée — et mal à tout ce qui dépend d'un état externe, où elle sert des données périmées sans le dire.

Trois pièges classiques : la clé doit inclure **tous** les paramètres qui influencent le résultat, faute de quoi on renvoie la réponse d'un autre appel ; la mémoire doit être bornée, avec une éviction de type LRU et une taille maximale, sans quoi on transforme un cache en fuite ; et l'invalidation doit être prévue dès la conception, car c'est elle qui pose problème, pas la mise en cache.

Cela dit, dans un service applicatif, le levier le plus rentable reste souvent en amont : un `Cache-Control` bien réglé évite la requête plutôt que de la traiter vite, et un CDN absorbe le trafic statique avant même qu'il n'atteigne votre application. Je recommanderais de commencer par là avant d'instrumenter le code.
''',
    thinking='''
1. Analyse de l'explication : le contenu technique est exact. Les trois conditions énoncées — déterminisme, clé fiable, coût de calcul supérieur au coût de gestion — sont les bonnes, la distinction entre calcul pur et dépendance à un état externe est pertinente, et les trois pièges cités sont réels, en particulier l'exhaustivité de la clé et le bornage de la mémoire.
2. Vérification des contraintes : le dernier paragraphe viole une exclusion explicite. La requête interdit sans ambiguïté d'aborder le cache HTTP et le CDN, en précisant que le sujet est traité ailleurs dans le document. La réponse les introduit tous les deux, et en fait sa recommandation finale, celle par laquelle elle conseille de commencer. Ce n'est pas une digression marginale : c'est la conclusion du texte, et elle rend le passage inutilisable tel quel dans le document visé, en plus de faire doublon avec une autre section. Le reste de la réponse traitait pourtant la question posée de façon complète.
3. Synthèse : le fond est exact et répond à la demande, mais le périmètre explicitement exclu est franchi, précisément dans la recommandation finale. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"perimetre_respecte": "La réponse reste dans le périmètre fixé par la requête, sans aborder les sujets explicitement exclus."},
    extra_checks={"perimetre_respecte": False},
    raison="Conclut en recommandant Cache-Control et CDN, que la requête excluait explicitement du périmètre.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
