#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_01.jsonl (5 hand-written examples)."""
import json
import sys
from pathlib import Path

# ── Schéma unifié (réorientation du 2026-09-13) ───────────────────────────────
# Verdict binaire strict, contrôles booléens atomiques nommés, marqueur de tâche
# dans le message system pour séparer les postures (monde ouvert / monde fermé).

TASKS = ("CODE_ANALYSIS", "RAG_CONTEXT_RELEVANCE", "RAG_FAITHFULNESS")

SYSTEM_TEMPLATE = (
    "Tu es un juge IA ultra-rigoureux. TÂCHE: {task}. "
    "Analyse la situation pas à pas dans <thinking> avant de rendre ton verdict JSON."
)

USER_TEMPLATE = (
    "### CONTEXTE / RAG\n{contexte}\n\n"
    "### ENTREE / REQUÊTE\n{requete}\n\n"
    "### SORTIE À ÉVALUER\n{reponse}\n\n"
    "### CRITÈRES DE VALIDATION\n{criteres}"
)

# Posture monde ouvert : aucun contexte fourni, le juge mobilise ses connaissances.
NO_CONTEXT = "(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)"

# Contrôles atomiques par tâche. Chaque description énonce un fait observable.
CRITERIA = {
    "CODE_ANALYSIS": {
        "exactitude_technique": "Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.",
        "absence_de_bugs": "Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.",
        "respect_consignes": "Toutes les consignes obligatoires de la requête sont respectées.",
    },
    "RAG_CONTEXT_RELEVANCE": {
        "contexte_pertinent": "Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.",
        "contexte_suffisant": "Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.",
        "bruit_maitrise": "Le contexte ne noie pas l'information utile sous des extraits hors sujet.",
    },
    "RAG_FAITHFULNESS": {
        "affirmations_etayees": "Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.",
        "absence_invention": "La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.",
        "citations_exactes": "Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.",
    },
}


def example(meta, thinking, *, task=None, contexte=None, requete=None, reponse=None,
            criteres=None, checks=None, reason=None,
            consigne=None, exact=None, bugs=None, consignes=None, raison=None):
    """Assemble un exemple au schéma unifié.

    Deux façons d'appeler :
      - explicite : task=..., contexte=..., requete=..., reponse=..., checks={nom: bool, ...}
      - abrégée (CODE_ANALYSIS) : consigne=..., reponse=..., exact=..., bugs=..., consignes=...

    Le verdict n'est jamais fourni : il vaut PASS si et seulement si tous les contrôles sont vrais.
    """
    task = task or meta.get("task") or "CODE_ANALYSIS"
    if task not in TASKS:
        raise ValueError(f"tâche inconnue : {task}")

    if checks is None:
        checks = {
            "exactitude_technique": exact,
            "absence_de_bugs": bugs,
            "respect_consignes": consignes,
        }
    if any(v is None for v in checks.values()):
        raise ValueError(f"contrôle non renseigné dans {meta.get('id')}: {checks}")

    criteres = criteres or CRITERIA[task]
    if list(criteres) != list(checks):
        raise ValueError(f"critères et contrôles désalignés dans {meta.get('id')}")

    verdict = "PASS" if all(checks.values()) else "FAIL"
    judgment = {"verdict": verdict, "checks": checks, "reason": (reason or raison).strip()}

    criteres_bloc = "\n".join(
        f"{i}. {nom}: {desc}" for i, (nom, desc) in enumerate(criteres.items(), 1)
    )
    user = USER_TEMPLATE.format(
        contexte=(contexte or NO_CONTEXT).strip(),
        requete=(requete or consigne).strip(),
        reponse=reponse.strip(),
        criteres=criteres_bloc,
    )
    assistant = f"<thinking>\n{thinking.strip()}\n</thinking>\n" + json.dumps(judgment, ensure_ascii=False, indent=2)

    meta = dict(meta)
    meta.setdefault("task", task)
    return {
        "meta": meta,
        "messages": [
            {"role": "system", "content": SYSTEM_TEMPLATE.format(task=task)},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ],
    }


EXAMPLES = []

# ── 1. Code / refactoring / parfait (PASS) ────────────────────────────────────
EXAMPLES.append(example(
    meta={"id": "b01-001", "famille": "java-stream-tomap-doublons", "domaine": "code", "tache": "refactoring",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Refactorise cette méthode Java 17 avec l'API Stream, sans changer son comportement observable. Garde la signature.

```java
public Map<String, Customer> indexActiveByEmail(List<Customer> customers) {
    Map<String, Customer> index = new HashMap<>();
    for (Customer c : customers) {
        if (c.isActive()) {
            index.put(c.email().toLowerCase(Locale.ROOT), c);
        }
    }
    return index;
}
```
''',
    reponse='''
```java
public Map<String, Customer> indexActiveByEmail(List<Customer> customers) {
    return customers.stream()
            .filter(Customer::isActive)
            .collect(Collectors.toMap(
                    c -> c.email().toLowerCase(Locale.ROOT),
                    Function.identity(),
                    (previous, next) -> next,   // doublon : le dernier gagne, comme put()
                    HashMap::new));
}
```

Points d'attention :
- La fonction de fusion `(previous, next) -> next` reproduit la sémantique de `Map.put` : sans elle, `Collectors.toMap` lèverait une `IllegalStateException` dès que deux clients actifs partagent le même email normalisé.
- `HashMap::new` garantit le même type de map mutable qu'avant (la surcharge à deux arguments ne garantit ni le type ni la mutabilité de la map).
- Imports à ajouter : `java.util.function.Function` et `java.util.stream.Collectors`.
''',
    thinking='''
1. Analyse du code : la méthode d'origine filtre les clients actifs et les indexe par email normalisé (`toLowerCase(Locale.ROOT)`) dans une `HashMap` ; en cas de doublon, `put` écrase l'entrée précédente (le dernier gagne). La version Stream applique le même filtre (`filter(Customer::isActive)`), la même clé et `Function.identity()` comme valeur. La syntaxe est valide en Java 17 et la signature est conservée.
2. Vérification des contraintes : le piège classique de ce refactoring est `Collectors.toMap` à deux arguments, qui lève `IllegalStateException` sur clé dupliquée (par exemple `A@x.com` et `a@x.com`). Ici, la fonction de fusion `(previous, next) -> next` restitue exactement la sémantique « dernier gagnant » de `put`, et `HashMap::new` fixe le type de map retourné, qui n'est pas garanti sans fournisseur. Le flux est séquentiel : l'ordre de traitement et le point de levée d'une éventuelle `NullPointerException` (email null d'un client actif) sont identiques à ceux de la boucle. Les affirmations de l'explication sont exactes et les imports nécessaires sont signalés.
3. Synthèse : refactoring correct, comportement observable préservé y compris sur les doublons, consignes respectées (API Stream, signature inchangée, aucun changement de comportement). PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Refactoring Stream équivalent : la fonction de fusion et HashMap::new préservent la sémantique de put sur les doublons.",
))

# ── 2. Code / débogage / défaillant (FAIL, faille de sécurité) ────────────────
EXAMPLES.append(example(
    meta={"id": "b01-002", "famille": "flask-download-sous-dossiers", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Ma route Flask renvoie 404 dès que le fichier demandé est dans un sous-dossier (ex. `/download/reports/2024/q1.pdf`), alors que le fichier existe bien dans `UPLOAD_DIR`. Corrige le bug.

```python
from flask import Flask, send_from_directory

app = Flask(__name__)
UPLOAD_DIR = "/srv/app/uploads"

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_DIR, filename)
```
''',
    reponse='''
Le problème vient du convertisseur par défaut `<filename>`, qui n'accepte pas les `/`. Il faut utiliser `<path:filename>`. J'en profite pour construire le chemin explicitement avec `send_file`, ce qui est plus lisible :

```python
import os
from flask import Flask, send_file

app = Flask(__name__)
UPLOAD_DIR = "/srv/app/uploads"

@app.route("/download/<path:filename>")
def download(filename):
    file_path = os.path.join(UPLOAD_DIR, filename)
    return send_file(file_path)
```

Désormais, `/download/reports/2024/q1.pdf` fonctionne.
''',
    thinking='''
1. Analyse du code : le diagnostic est juste. Le convertisseur par défaut `string` de Werkzeug refuse le caractère `/`, et `<path:filename>` corrige bien le 404 sur `reports/2024/q1.pdf`. En revanche, la réponse remplace aussi `send_from_directory` par `send_file(os.path.join(UPLOAD_DIR, filename))`, un changement qui n'était pas nécessaire au correctif.
2. Vérification des contraintes : ce remplacement introduit une régression de sécurité. `send_from_directory` passe par `safe_join` et refuse tout chemin qui sort de `UPLOAD_DIR`, alors que `os.path.join` ne fait aucune vérification. Avec le convertisseur `path`, une requête contenant des segments `..` produit par exemple `filename = "../../../etc/passwd"`, et le serveur renvoie n'importe quel fichier lisible par le processus : c'est une traversée de répertoire (CWE-22). Il y a aussi une régression secondaire : un fichier inexistant lève désormais `FileNotFoundError` (erreur 500) au lieu d'un 404 propre. Le correctif minimal attendu consistait à changer uniquement le convertisseur en conservant `send_from_directory`.
3. Synthèse : le bug signalé est corrigé et le code s'exécute, mais le correctif ouvre une faille de lecture de fichiers arbitraires, ce qui est bloquant. FAIL.
''',
    exact=True, bugs=False, consignes=True,
    raison="Le correctif remplace send_from_directory par send_file + os.path.join et introduit une traversée de répertoire (CWE-22).",
))

# ── 3. Code / génération / cas limite (PASS : verbeux + typage optionnel absent) ─
EXAMPLES.append(example(
    meta={"id": "b01-003", "famille": "python-merge-intervals", "domaine": "code", "tache": "generation",
          "cas": "limite", "verbeux": True, "langage": "python"},
    consigne='''
Écris une fonction Python `merge_intervals(intervals)` qui fusionne des intervalles fermés `[start, end]` qui se chevauchent ou se touchent (ex. `[1, 3]` et `[3, 5]` donnent `[1, 5]`). L'entrée n'est pas forcément triée et ne doit pas être modifiée. Si possible, ajoute des annotations de type.
''',
    reponse='''
Excellente question ! La fusion d'intervalles est un problème classique d'algorithmique, très fréquent en entretien technique et utile dans de nombreux contextes réels (planification de réunions, réservation de ressources, calcul de plages horaires, etc.). Voici une solution complète et détaillée.

## Approche

L'idée générale est la suivante :
1. On trie d'abord les intervalles selon leur borne de début, ce qui permet de ne comparer chaque intervalle qu'avec le dernier intervalle fusionné.
2. On parcourt ensuite les intervalles triés un par un.
3. Si l'intervalle courant commence avant ou exactement à la fin du dernier intervalle fusionné, on étend ce dernier.
4. Sinon, on ajoute l'intervalle courant comme nouvel intervalle fusionné.

## Implémentation

```python
def merge_intervals(intervals):
    """Fusionne des intervalles fermés qui se chevauchent ou se touchent."""
    if not intervals:
        return []

    # sorted() renvoie une nouvelle liste : l'entrée n'est pas réordonnée
    ordered = sorted(intervals, key=lambda iv: iv[0])

    # Copie du premier intervalle pour ne jamais muter les listes d'origine
    merged = [list(ordered[0])]

    for start, end in ordered[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])

    return merged
```

## Exemple d'utilisation

```python
>>> merge_intervals([[8, 10], [1, 3], [2, 6], [15, 18], [6, 7]])
[[1, 7], [8, 10], [15, 18]]
```

## Complexité

- Temps : O(n log n), dominé par le tri.
- Espace : O(n) pour la liste triée et le résultat.

## Pour aller plus loin

On pourrait aussi gérer des intervalles semi-ouverts, vérifier que `start <= end` pour chaque intervalle ou utiliser des tuples immuables. N'hésite pas si tu veux que je développe l'une de ces variantes !
''',
    thinking='''
1. Analyse du code : l'algorithme trie par borne de début avec `sorted` (nouvelle liste, l'entrée n'est pas réordonnée), puis fusionne séquentiellement. La condition `start <= last[1]` couvre le chevauchement et le cas « se touchent » exigé (`[1, 3]` + `[3, 5]` → `[1, 5]`), et `max(last[1], end)` gère les intervalles inclus (`[1, 10]` + `[2, 3]` → `[1, 10]`). La liste vide est traitée. En déroulant l'exemple fourni, `[[8, 10], [1, 3], [2, 6], [15, 18], [6, 7]]` donne bien `[[1, 7], [8, 10], [15, 18]]`. La complexité annoncée, O(n log n), est exacte.
2. Vérification des contraintes : la non-mutation de l'entrée est respectée. Le premier intervalle est copié via `list(...)` et chaque élément ajouté ensuite est une nouvelle liste, donc `last[1] = ...` ne modifie jamais une liste d'origine. L'entrée non triée est gérée. Il y a deux écarts mineurs : (a) aucune annotation de type, mais la consigne les présentait comme optionnelles (« si possible ») ; (b) la réponse est verbeuse (préambule flatteur, section « Pour aller plus loin » non demandée). Aucun de ces écarts n'affecte la correction du code ni une exigence obligatoire.
3. Synthèse : cas limite. Toutes les exigences obligatoires (fusion des intervalles adjacents, entrée non triée, non-mutation) sont satisfaites et le code est correct ; les défauts relèvent du style et d'une consigne facultative. La verbosité ne doit pas faire échouer une réponse correcte. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Code correct et exigences obligatoires respectées ; l'absence d'annotations (consigne optionnelle) et la verbosité sont des écarts mineurs non bloquants.",
))

# ── 4. Théorie / parfait (PASS) ───────────────────────────────────────────────
EXAMPLES.append(example(
    meta={"id": "b01-004", "famille": "java-completablefuture-compose", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Quelle est la différence entre `thenApply` et `thenCompose` sur un `CompletableFuture` en Java ? Donne un exemple où utiliser `thenApply` à la place de `thenCompose` pose problème. Réponse concise.
''',
    reponse='''
- `thenApply(Function<? super T, ? extends U>)` applique une fonction qui renvoie directement une valeur `U` : on obtient un `CompletableFuture<U>`. C'est l'équivalent de `map`.
- `thenCompose(Function<? super T, ? extends CompletionStage<U>>)` enchaîne une opération elle-même asynchrone : la fonction renvoie un `CompletionStage<U>` et le résultat est « aplati » en `CompletableFuture<U>`. C'est l'équivalent de `flatMap`.

Exemple problématique :

```java
CompletableFuture<User> findUser(long id) { ... }
CompletableFuture<List<Order>> findOrders(User user) { ... }

// thenApply : type imbriqué, difficile à exploiter
CompletableFuture<CompletableFuture<List<Order>>> nested =
        findUser(42).thenApply(this::findOrders);

// thenCompose : on obtient directement le résultat final
CompletableFuture<List<Order>> orders =
        findUser(42).thenCompose(this::findOrders);
```

Avec `thenApply`, `nested.join()` renvoie le future interne et non la liste : il faut un second `join()`, et si `findOrders` échoue de façon asynchrone, le future externe, lui, ne passe pas en erreur.
''',
    thinking='''
1. Analyse de l'explication : les signatures citées sont exactes. `thenApply` prend une `Function<? super T, ? extends U>` et renvoie `CompletableFuture<U>` ; `thenCompose` prend une fonction qui renvoie un `CompletionStage<U>` et aplatit le résultat. L'analogie `map` / `flatMap` est correcte et pertinente sur le plan pédagogique.
2. Vérification des contraintes : l'exemple est valide (`findUser(42)` avec un paramètre `long` compile par élargissement) et illustre le vrai problème : `thenApply(this::findOrders)` produit `CompletableFuture<CompletableFuture<List<Order>>>`. L'affirmation finale est exacte et nuancée. Si le future interne échoue, le future externe se termine normalement avec ce future comme valeur, donc l'échec n'est pas propagé. La précision « de façon asynchrone » est juste, car une exception levée directement par `findOrders` ferait, elle, échouer le future externe. Les trois demandes sont couvertes : la différence, l'exemple problématique et la concision.
3. Synthèse : explication techniquement exacte, sans erreur conceptuelle, et format concis respecté. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Explication exacte (map vs flatMap) avec un exemple pertinent de future imbriqué et de propagation d'erreur.",
))

# ── 5. Théorie / défaillant, verbeux avec erreur cachée (FAIL) ────────────────
EXAMPLES.append(example(
    meta={"id": "b01-005", "famille": "java-volatile-compteur", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": True, "langage": "java"},
    consigne='''
Dans notre service, un collègue propose de rendre thread-safe un compteur de requêtes partagé en déclarant simplement le champ `private volatile int count;` et en appelant `count++` depuis plusieurs threads. Explique ce que garantit `volatile`, dis si cela suffit ici et propose une alternative si nécessaire.
''',
    reponse='''
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
''',
    thinking='''
1. Analyse de l'explication : la réponse est longue et bien structurée, et une grande partie est exacte. `volatile` garantit la visibilité des écritures entre threads (relation happens-before) et rend correct le double-checked locking depuis Java 5 (JSR-133). `AtomicInteger` (CAS) et `LongAdder` (cellules réparties sous contention) sont correctement décrits.
2. Vérification des contraintes : l'affirmation centrale est fausse. `count++` n'est pas atomique, même sur un champ `volatile` : c'est une séquence lecture → incrément → écriture (`getfield`, `iadd`, `putfield` en bytecode), et aucune « barrière mémoire commune » n'existe dans la JVM. Deux threads peuvent lire la même valeur et écrire le même résultat, ce qui fait perdre des incréments (race condition read-modify-write). `volatile` garantit la visibilité, pas l'atomicité des opérations composées. Le tableau récapitulatif propage l'erreur (« atomicité ✅ ») et la conclusion valide une implémentation boguée. Les alternatives citées sont les bonnes, mais elles sont présentées comme optionnelles alors qu'elles sont nécessaires. Sur la forme, toutes les parties de la consigne sont traitées.
3. Synthèse : sous une présentation soignée et majoritairement exacte se cache une erreur conceptuelle qui conduirait à mettre en production un compteur non thread-safe. La longueur et la qualité de la mise en forme ne compensent pas cette erreur. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Affirme à tort que count++ est atomique sur un champ volatile : la solution validée perd des incréments sous concurrence.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
