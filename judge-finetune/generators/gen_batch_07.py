#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_07.jsonl (15 examples, CODE_ANALYSIS).

Chiffres issus des sondes Probe07.java, probe07.py et probe07.js exécutées le 2026-09-13.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402

EXAMPLES = []
add = EXAMPLES.append

# ── 1-2. Paire contrastive : verrous croisés ──────────────────────────────────
CONSIGNE_DEADLOCK = '''
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
'''

add(example(
    meta={"id": "b07-001", "famille": "java-verrous-croises", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne=CONSIGNE_DEADLOCK,
    reponse='''
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
''',
    thinking='''
1. Analyse du code : le diagnostic est exact. La méthode acquiert les verrous dans l'ordre des arguments, donc deux appels croisés produisent un cycle d'attente. Avec deux threads prenant les verrous en ordre inverse, les deux se retrouvent à l'état `BLOCKED` après deux secondes, et `ThreadMXBean.findDeadlockedThreads()` en signale 2. L'absence d'exception et de consommation CPU correspond bien au symptôme rapporté.
2. Vérification des contraintes : la correction proposée est la bonne. Un ordre total fondé sur l'identifiant garantit que tous les threads acquièrent les verrous dans la même séquence, ce qui casse la condition d'attente circulaire. La remarque sur `from == to` est pertinente, et la réentrance de `synchronized` est correctement invoquée : le double verrouillage du même moniteur ne bloque pas. L'outil de diagnostic cité existe et fait bien ce qui est annoncé.
3. Synthèse : cause exacte, correction qui supprime réellement la condition d'interblocage, conseils de diagnostic justes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Interblocage par ordre d'acquisition correctement diagnostiqué et corrigé par un ordre total sur les verrous.",
))

add(example(
    meta={"id": "b07-002", "famille": "java-verrous-croises", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": False, "langage": "java"},
    consigne=CONSIGNE_DEADLOCK,
    reponse='''
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
''',
    thinking='''
1. Analyse du code : le diagnostic est faux. Le gel décrit n'est pas de la contention ni de la famine, mais un interblocage par ordre d'acquisition inversé : deux threads prenant deux verrous en ordre opposé restent à l'état `BLOCKED`, et `findDeadlockedThreads()` en signale 2. Un verrou équitable ne change rien à un cycle d'attente : il ordonne les prétendants à un même verrou, il ne supprime pas la dépendance croisée entre deux verrous distincts. Tout le développement sur les capacités de `ReentrantLock` est en revanche exact — `tryLock` avec délai, `lockInterruptibly`, les objets `Condition` —, de même que l'insistance sur l'agencement `lock()` hors du `try` et `unlock()` dans le `finally`, qui est bien la seule forme correcte.
2. Vérification des contraintes : le code proposé, lui, ne présente effectivement plus d'interblocage — mais pour une raison que la réponse n'identifie pas et qui introduit une régression majeure. En remplaçant les verrous par instance par un **unique verrou partagé**, il sérialise tous les virements du service, y compris ceux portant sur des comptes sans rapport. Le débit s'effondre exactement sous la charge qui motivait la question. Le mode équitable aggrave encore le coût, chaque transmission passant par la file d'attente. La correction attendue était un ordre total d'acquisition, qui conserve le parallélisme entre comptes distincts.
3. Synthèse : cause mal identifiée, explication fausse sur le rôle de l'équité, et remède qui échange un interblocage contre un goulot d'étranglement global. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Attribue le gel à la contention : un verrou équitable ne casse pas un cycle d'attente, et le verrou unique proposé sérialise tous les virements.",
))

# ── 3. Initialisation paresseuse : la course qui ne se voit pas en test ───────
add(example(
    meta={"id": "b07-003", "famille": "java-init-paresseuse", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": True, "langage": "java"},
    consigne='''
Ajoute un cache paresseux à ce composant, partagé par toutes les requêtes du serveur.

```java
public class ReferenceHolder {
    private Map<String, String> cache;
    // à compléter : cache() doit construire la map au premier appel
}
```
''',
    reponse='''
## Implémentation

```java
public class ReferenceHolder {
    private Map<String, String> cache;

    public Map<String, String> cache() {
        if (cache == null) {
            cache = loadFromDatabase();
        }
        return cache;
    }
}
```

## Pourquoi c'est sûr ici

L'initialisation paresseuse a mauvaise réputation en contexte multi-thread, mais le risque est largement théorique dans ce cas précis.

J'ai vérifié le comportement avec quatre threads appelant `cache()` simultanément, sur deux cents itérations : **tous obtiennent la même instance**, aucune divergence constatée. L'explication est simple — l'affectation d'une référence est atomique sur la JVM, et la fenêtre entre le test et l'affectation est de quelques nanosecondes, trop courte pour être réellement franchie.

## Quand s'en préoccuper

Si un jour la construction devient coûteuse, ou si le cache doit être invalidé à chaud, il sera temps de passer à `ConcurrentHashMap` ou à un verrou. Tant que l'objet est construit une fois au démarrage effectif du service, ajouter de la synchronisation reviendrait à payer un coût pour un problème qui ne se produit pas.
''',
    thinking='''
1. Analyse du code : le code compile et l'observation rapportée n'est pas fausse. Quatre threads appelant la méthode simultanément, sur deux cents itérations, obtiennent effectivement la même instance dans la quasi-totalité des essais. Le raisonnement construit sur cette observation est en revanche entièrement faux.
2. Vérification des contraintes : l'absence de manifestation ne prouve pas l'absence de course. Le motif test-puis-affectation n'est pas atomique : deux threads peuvent lire `cache == null` avant que l'un des deux n'affecte, et construire alors deux maps, la seconde écrasant la première. Des appelants détiendraient des instances distinctes, et des écritures seraient perdues en silence. Plus grave, l'absence de barrière mémoire ne garantit pas la visibilité de l'affectation aux autres threads, ni même que la map soit vue entièrement construite — c'est le défaut classique de publication non sûre. L'atomicité de l'affectation d'une référence, correctement invoquée, ne couvre que l'écriture elle-même, jamais la séquence test-puis-affectation. Le fait que la fenêtre soit étroite est précisément ce qui rend le défaut dangereux : il traverse les tests et se manifeste en production sous charge. Les corrections sûres sont l'initialisation à la déclaration, un bloc `synchronized`, le double-checked locking avec un champ `volatile`, ou le langage de l'initialisation à la demande via une classe interne.
3. Synthèse : le code est bogué et l'argumentaire s'appuie sur une mesure réelle pour en tirer une conclusion inverse de la bonne, ce qui est plus nuisible qu'une simple erreur. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Conclut d'une absence de divergence sur 200 essais que le test-puis-affectation est sûr : la course et la publication non sûre demeurent.",
))

# ── 4. Types bruts et effacement : refactoring correct ────────────────────────
add(example(
    meta={"id": "b07-004", "famille": "java-types-bruts", "domaine": "code", "tache": "refactoring",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Ce code génère un avertissement « unchecked call » et a provoqué une `ClassCastException` en production, loin de cette méthode. Corrige-le **sans modifier la signature publique**.

```java
public void register(List items) {
    items.add(currentUser());
}
```
''',
    reponse='''
Le type brut `List` désactive tout contrôle du compilateur : `add` accepte n'importe quel objet, et la `ClassCastException` ne surgit qu'au moment où quelqu'un lit la liste en la croyant typée — d'où la distance entre la faute et le symptôme.

La signature publique doit rester `List`, donc on rétablit la vérification à l'intérieur :

```java
public void register(List items) {
    List<User> users = castOrThrow(items);
    users.add(currentUser());
}

private static List<User> castOrThrow(List raw) {
    for (Object item : raw) {
        if (!(item instanceof User)) {
            throw new IllegalArgumentException(
                    "liste hétérogène : " + item.getClass().getName() + " au lieu de User");
        }
    }
    @SuppressWarnings("unchecked")
    List<User> typed = (List<User>) raw;
    return typed;
}
```

L'échec se produit désormais à l'entrée, avec un message qui nomme le type fautif, au lieu d'être différé jusqu'à une lecture lointaine.

Si la signature pouvait évoluer, `List<User>` en paramètre serait évidemment préférable : le contrôle passerait à la compilation et ce code deviendrait inutile. À défaut, une surcharge générique `register(List<User>)` conservée à côté de l'ancienne permettrait de migrer les appelants progressivement.
''',
    thinking='''
1. Analyse du code : le diagnostic est exact. Un type brut accepte `add(42)` sur une `List<String>` sans le moindre avertissement à l'exécution, la liste contient bien `[42]`, et l'exception ne surgit qu'à la lecture typée : `class java.lang.Integer cannot be cast to class java.lang.String`. C'est bien le transtypage inséré par le compilateur au site de lecture qui échoue, ce qui explique la distance entre la faute et le symptôme.
2. Vérification des contraintes : la signature publique est conservée, comme exigé. Le contrôle explicite déplace l'échec au point d'entrée avec un message nommant le type fautif, ce qui répond au vrai problème. L'usage de `@SuppressWarnings("unchecked")` est ici légitime puisqu'il suit une vérification effective, et non un simple masquage d'avertissement. La réserve finale est juste : le paramètre générique serait supérieur, et la surcharge de migration est une voie réaliste, présentée comme telle sans contredire la contrainte.
3. Synthèse : cause exacte, correction qui rétablit la vérification tout en respectant la contrainte de signature, et suppression d'avertissement justifiée par un contrôle réel. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"signature_publique_inchangee": "La signature publique de la méthode est inchangée, comme l'exige la requête."},
    extra_checks={"signature_publique_inchangee": True},
    raison="Diagnostic exact de l'effacement de type, contrôle rétabli au point d'entrée, et signature publique conservée comme exigé.",
))

# ── 5. Générateur épuisé ──────────────────────────────────────────────────────
add(example(
    meta={"id": "b07-005", "famille": "python-generateur-epuise", "domaine": "code", "tache": "debogage",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Ce code affiche toujours un rapport vide après avoir compté les lignes. Explique et corrige.

```python
def lignes_valides(lignes):
    return (l.strip() for l in lignes if l.strip())

valides = lignes_valides(fichier)
total = sum(1 for _ in valides)
for ligne in valides:
    rapport.append(ligne)
```
''',
    reponse='''
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
''',
    thinking='''
1. Analyse du code : le diagnostic est exact. Un générateur construit sur cinq entrées produit 3 éléments au premier parcours, puis `[]` au second, sans lever d'exception. C'est bien la cause du rapport vide.
2. Vérification des contraintes : les deux corrections sont valides et le critère de choix, la tenue en mémoire, est le bon. La version liste est reparcourable et renvoie bien les mêmes 3 éléments, et la version en une passe conserve le caractère paresseux quand le volume l'exige. La remarque finale est exacte : `len()` sur un générateur lève `TypeError: object of type 'generator' has no len()`, ce qui justifie effectivement la forme `sum(1 for _ in ...)` du code d'origine.
3. Synthèse : cause exacte, deux corrections adaptées avec un critère de choix pertinent, remarques justes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Épuisement du générateur correctement diagnostiqué, avec deux corrections adaptées au volume de données.",
))

# ── 6. Décorateur sans functools.wraps ────────────────────────────────────────
add(example(
    meta={"id": "b07-006", "famille": "python-decorateur-wraps", "domaine": "code", "tache": "refactoring",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Écris un décorateur `chrono` qui mesure le temps d'exécution d'une fonction et le journalise. Il sera appliqué à des routes exposées par notre framework web, qui les enregistre par leur nom.
''',
    reponse='''
## Le décorateur

```python
import time
import logging

def chrono(fn):
    def wrapper(*args, **kwargs):
        debut = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            logging.info("%s a pris %.1f ms", fn.__name__, (time.perf_counter() - debut) * 1000)
    return wrapper
```

## Les choix de mise en œuvre

**`perf_counter` et non `time.time`.** C'est une horloge monotone, de plus haute résolution, et surtout insensible aux ajustements de l'horloge système. Avec `time.time()`, une synchronisation NTP survenant pendant la requête peut produire une durée négative — anomalie rare, impossible à reproduire, et qui pollue durablement les tableaux de bord.

**Le `finally` plutôt qu'un simple enchaînement.** La durée est journalisée même lorsque la fonction lève, et c'est précisément le cas qui vous intéresse le plus : une route qui échoue après cinq secondes est une information plus utile qu'une route qui réussit en trente millisecondes.

**Le formatage différé.** Les paramètres sont passés à `logging.info` plutôt qu'interpolés dans une f-chaîne. L'interpolation n'a lieu que si le niveau `INFO` est effectivement actif, ce qui évite de payer le formatage sur chaque appel lorsque la journalisation est réglée plus haut en production.

**L'unité.** Les millisecondes avec une décimale conviennent à des routes web ; pour du code plus fin, basculez en microsecondes plutôt que d'accumuler les zéros.

## Transparence

Le décorateur est totalement transparent pour l'appelant : il se contente d'envelopper la fonction, sans rien changer à sa signature ni à son identité. Le `finally` garantit que la durée est journalisée même en cas d'exception.
''',
    thinking='''
1. Analyse du code : la mesure elle-même est correcte. `time.perf_counter` est le bon choix pour une durée, le `finally` journalise bien même en cas d'exception, et `fn.__name__` référence la fonction d'origine, donc le message de journalisation affiche le bon nom. Les quatre justifications ajoutées sont exactes : l'horloge monotone protège bien d'un recalage NTP, le formatage différé de `logging` évite bien l'interpolation quand le niveau est inactif, et le choix de l'unité est correctement discuté.
2. Vérification des contraintes : l'affirmation de transparence est fausse, et elle est bloquante compte tenu du contexte annoncé. Sans `functools.wraps`, la fonction renvoyée conserve son identité propre : la fonction décorée expose `__name__ = 'wrapper'` et `__doc__ = None`, contre `'calculer_tva_ok'` et sa docstring d'origine lorsque `@functools.wraps(fn)` est appliqué. La réponse consacre une section entière au soin apporté à l'enveloppe sans jamais examiner l'identité de l'objet qu'elle renvoie. Or la requête précise que le framework enregistre les routes **par leur nom** : toutes les routes décorées s'enregistreraient sous `wrapper`, et se masqueraient les unes les autres. Les mêmes attributs perdus cassent la documentation générée et l'introspection. Le correctif tient en une ligne, `@functools.wraps(fn)` au-dessus de `wrapper`.
3. Synthèse : la mesure fonctionne, mais l'oubli de `functools.wraps` casse précisément le mécanisme d'enregistrement décrit dans la requête, sous couvert d'une transparence affirmée à tort. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Sans functools.wraps, la fonction décorée s'appelle 'wrapper' : toutes les routes s'enregistreraient sous le même nom.",
))

# ── 7. Transaction non validée ────────────────────────────────────────────────
add(example(
    meta={"id": "b07-007", "famille": "python-sqlite-transaction", "domaine": "code", "tache": "generation",
          "cas": "defaillant", "verbeux": False, "langage": "python"},
    consigne='''
Écris la fonction qui enregistre une commande en base SQLite. **Contrainte : l'écriture doit être durable dès le retour de la fonction**, le processus pouvant être arrêté juste après.
''',
    reponse='''
## La fonction

```python
def enregistrer_commande(chemin_db, commande):
    conn = sqlite3.connect(chemin_db)
    try:
        conn.execute(
            "INSERT INTO commandes (reference, montant) VALUES (?, ?)",
            (commande.reference, commande.montant),
        )
    finally:
        conn.close()
```

## Les points d'attention

**Les paramètres liés.** Les valeurs passent par des marqueurs `?` et non par interpolation dans la chaîne SQL. Le pilote les transmet hors du texte de la requête : aucune injection n'est possible, et une référence contenant une apostrophe passe sans traitement particulier, là où une concaténation lèverait une `OperationalError`.

**Le `finally`.** La connexion est refermée quoi qu'il arrive, y compris si l'insertion lève. Sans cela, un processus qui traite beaucoup de commandes finirait par épuiser les descripteurs de fichiers, panne qui se manifeste loin de sa cause et sous charge seulement.

**Le type des montants.** Si `montant` est un flottant, envisagez de stocker des centimes en entier : SQLite n'a pas de type décimal, et un montant facturé mérite mieux qu'une approximation binaire.

**L'index.** Si vous recherchez ensuite les commandes par référence, un index sur cette colonne évite un parcours intégral. À l'inverse, n'indexez pas ce que vous ne lisez jamais : chaque index ralentit l'écriture, qui est précisément le chemin critique ici.

La fermeture propre de la connexion écrit les données sur disque.
''',
    thinking='''
1. Analyse du code : la requête paramétrée est correcte et le `finally` ferme effectivement la connexion. Les quatre points d'attention sont exacts : les marqueurs `?` neutralisent bien l'injection et gèrent les apostrophes, la fermeture systématique évite bien l'épuisement des descripteurs, SQLite n'a bien pas de type décimal, et un index accélère la lecture au prix de l'écriture. Mais l'affirmation finale est fausse : fermer une connexion ne valide pas la transaction en cours, elle l'abandonne.
2. Vérification des contraintes : un `INSERT` suivi d'un `close()` sans `commit()` laisse **0 ligne** en base, alors que le même `INSERT` suivi d'un `commit()` en laisse bien 1. Le module `sqlite3` ouvre implicitement une transaction avant une instruction de modification — son `isolation_level` vaut `''` par défaut, et non `None` qui donnerait le mode autocommit — si bien que rien n'est durable sans validation explicite. La contrainte de la requête, la durabilité dès le retour de la fonction, n'est donc pas respectée, et l'échec est silencieux : aucune exception, une commande simplement perdue. La forme robuste est le gestionnaire de contexte `with conn:`, qui valide en sortie et annule en cas d'exception, laissant le solde inchangé après une erreur au milieu de la transaction. Le détail des quatre précautions listées rend l'omission d'autant plus difficile à voir : la réponse soigne l'injection, les descripteurs, le typage et l'indexation, et laisse tomber la seule exigence que la requête avait posée.
3. Synthèse : requête bien écrite mais jamais validée, et l'explication affirme l'inverse du comportement réel, sur la contrainte même que la requête mettait en avant. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    extra_criteres={"durabilite_garantie": "L'écriture est validée en base avant le retour de la fonction, comme l'exige la requête."},
    extra_checks={"durabilite_garantie": False},
    raison="close() sans commit() abandonne la transaction : 0 ligne persistée là où un commit en laisse 1.",
))

# ── 8. XSS par innerHTML, réponse verbeuse ────────────────────────────────────
add(example(
    meta={"id": "b07-008", "famille": "js-xss-innerhtml", "domaine": "code", "tache": "debogage",
          "cas": "defaillant", "verbeux": True, "langage": "typescript"},
    consigne='''
Notre audit signale une faille XSS sur l'affichage du nom de l'utilisateur, qui provient de son profil éditable.

```ts
container.innerHTML = `<span class="badge">${user.displayName}</span>`;
```

Explique et corrige.
''',
    reponse='''
## Le mécanisme

L'affectation d'`innerHTML` déclenche l'analyseur HTML du navigateur sur la chaîne fournie. Tout ce qui ressemble à du balisage est interprété comme tel : si `displayName` contient des chevrons, l'utilisateur ne fournit plus du texte mais du code.

## L'ampleur du risque

Il faut cependant relativiser. Les navigateurs modernes n'exécutent **pas** les balises `<script>` insérées via `innerHTML` : la spécification l'interdit explicitement depuis des années. Le vecteur est donc largement neutralisé côté plateforme.

## La correction

Un simple filtrage des balises suffit à couvrir le reste :

```ts
const propre = user.displayName.replace(/<script[^>]*>.*?<\\/script>/gi, "");
container.innerHTML = `<span class="badge">${propre}</span>`;
```

## Défense en profondeur

Ajoutez une politique de sécurité de contenu (`Content-Security-Policy`) pour limiter les dégâts d'une éventuelle injection résiduelle.
''',
    thinking='''
1. Analyse de l'explication : le mécanisme d'`innerHTML` est correctement décrit, et l'affirmation sur les balises `<script>` est exacte — la spécification prévoit bien qu'un `<script>` inséré par `innerHTML` ne s'exécute pas. C'est le seul point juste du raisonnement, et il sert à justifier une conclusion fausse.
2. Vérification des contraintes : l'immense majorité des charges XSS n'utilise pas `<script>` mais un **gestionnaire d'événement sur une balise ordinaire**. Avec jsdom, affecter `<img src=x onerror="...">` à `innerHTML` crée bien l'élément `img` avec son attribut `onerror` présent dans le DOM ; il suffit que le chargement de l'image échoue, ce qui est le principe même de la charge, pour que le gestionnaire s'exécute dans un vrai navigateur. Le filtre proposé, une expression régulière ciblant `<script>`, ne retire donc rien à cette charge et donne une fausse assurance ; filtrer du HTML par expression régulière est de toute façon un contre-modèle connu. La correction attendue est `container.textContent = user.displayName`, ou la construction du nœud puis l'affectation de son texte : `textContent` crée **zéro** balise et échappe la charge en `&lt;img src=x onerror=...&gt;`. La politique de sécurité de contenu est un complément utile, pas un correctif.
3. Synthèse : présentation soignée s'appuyant sur un fait exact pour minimiser la faille, avec un correctif inopérant contre le vecteur réellement employé. La faille reste ouverte. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Le filtre ne vise que <script> alors que la charge usuelle est un gestionnaire d'événement : innerHTML crée bien l'img et son onerror, textContent l'échappe.",
))

# ── 9. Cas limite : ordre des tâches, réponse correcte mais verbeuse ──────────
add(example(
    meta={"id": "b07-009", "famille": "js-ordre-taches", "domaine": "code", "tache": "generation",
          "cas": "limite", "verbeux": True, "langage": "typescript"},
    consigne='''
Écris une fonction `defer(fn)` qui exécute `fn` après le code synchrone en cours, mais **avant** tout `setTimeout(..., 0)` déjà programmé. Sans bibliothèque externe. Accessoirement, dis un mot du cas Node contre navigateur.
''',
    reponse='''
## La réponse

```ts
export function defer(fn: () => void): void {
  queueMicrotask(fn);
}
```

## Pourquoi ça répond exactement à la demande

Le moteur JavaScript distingue deux files. Les **micro-tâches** — promesses résolues, `queueMicrotask` — sont vidées intégralement dès que la pile d'appels se libère, avant de rendre la main à la boucle d'événements. Les **macro-tâches** — `setTimeout`, `setInterval`, entrées-sorties — sont traitées ensuite, une par tour de boucle.

Votre contrainte, « après le synchrone mais avant un `setTimeout(0)` », décrit donc précisément une micro-tâche.

## Vérification

```js
console.log("1 synchrone");
setTimeout(() => console.log("5 setTimeout 0"), 0);
Promise.resolve().then(() => console.log("3 microtâche"));
queueMicrotask(() => console.log("4 queueMicrotask"));
console.log("2 synchrone");
```

L'ordre observé est bien 1, 2, 3, 4, 5.

## Alternatives et pièges

`Promise.resolve().then(fn)` est strictement équivalent en termes d'ordonnancement. En revanche, méfiez-vous d'une micro-tâche qui en programme une autre : la file est vidée jusqu'à épuisement, donc une récursion de micro-tâches affame la boucle d'événements et gèle l'interface, là où une récursion de `setTimeout` laisse respirer le navigateur.

## Pour aller plus loin

On pourrait ajouter une variante annulable renvoyant un jeton, ou une file de priorité maison si vous avez besoin de plusieurs niveaux d'urgence. Dis-moi si l'un de ces cas t'intéresse.
''',
    thinking='''
1. Analyse du code : `queueMicrotask` répond exactement à la contrainte. La distinction entre file de micro-tâches et file de macro-tâches est correctement exposée, et le classement de `setTimeout` parmi les secondes est juste.
2. Vérification des contraintes : l'ordre annoncé est bien celui que produit Node — la trace obtenue est `1 synchrone`, `2 synchrone`, `3 microtâche .then`, `4 queueMicrotask`, `5 setTimeout 0`. L'équivalence d'ordonnancement avec `Promise.resolve().then` est exacte, et la mise en garde sur la famine par récursion de micro-tâches est réelle et pertinente. Aucune dépendance externe n'est utilisée, conformément à la contrainte. Deux écarts mineurs : la demande facultative sur la différence Node contre navigateur n'est pas traitée — l'occasion manquée d'évoquer `process.nextTick`, prioritaire sur les micro-tâches en Node — et la réponse est longue, avec une section « pour aller plus loin » non sollicitée pour une fonction d'une ligne.
3. Synthèse : la solution obligatoire est exacte, les écarts portent sur une demande explicitement facultative et sur la longueur, ce qui ne justifie pas un échec. PASS.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"aucune_dependance_externe": "La solution n'utilise que les API de la plateforme, comme l'exige la requête."},
    extra_checks={"aucune_dependance_externe": True},
    raison="queueMicrotask répond exactement à la contrainte, avec le bon ordre d'ordonnancement ; seul le point facultatif Node/navigateur manque.",
))

# ── 10. Théorie : effacement de type ──────────────────────────────────────────
add(example(
    meta={"id": "b07-010", "famille": "java-effacement-type", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "java"},
    consigne='''
Pourquoi ne peut-on pas écrire `if (obj instanceof List<String>)` en Java, ni surcharger une méthode sur `List<String>` et `List<Integer>` ? Réponse concise.
''',
    reponse='''
À cause de l'**effacement de type**. Les paramètres génériques n'existent qu'à la compilation : le compilateur les vérifie, insère les transtypages nécessaires, puis les efface. À l'exécution, il ne reste qu'une `List`.

Les deux interdictions en découlent :

- `instanceof List<String>` testerait une information qui n'existe plus. Seul `obj instanceof List<?>` est autorisé, puisqu'il ne porte que sur le type brut.
- Deux surcharges `f(List<String>)` et `f(List<Integer>)` s'effaceraient toutes deux en `f(List)` : même signature après effacement, le compilateur refuse.

```java
new ArrayList<String>().getClass() == new ArrayList<Integer>().getClass();   // true
```

La contrepartie de ce choix, motivé par la compatibilité avec le code antérieur aux génériques, est la **pollution du tas** : en passant par un type brut, on peut insérer un `Integer` dans une `List<String>` sans erreur immédiate. L'exception ne surgit qu'à la lecture, au transtypage inséré par le compilateur — donc loin de la ligne fautive.
''',
    thinking='''
1. Analyse de l'explication : le mécanisme est exact. L'effacement supprime bien les paramètres de type après vérification, `instanceof` ne peut porter que sur le type brut ou un joker non borné, et deux surcharges dont les signatures s'effacent identiquement sont refusées par le compilateur.
2. Vérification des contraintes : l'égalité de classes est réelle, `new ArrayList<String>().getClass() == new ArrayList<Integer>().getClass()` renvoie bien `true`. La description de la pollution du tas est exacte : un `add(42)` via un type brut sur une `List<String>` est accepté, la liste contient `[42]`, et l'échec ne survient qu'à la lecture typée avec `class java.lang.Integer cannot be cast to class java.lang.String`. La justification historique, la compatibilité avec le code antérieur aux génériques, est correcte. La réponse est concise comme demandé.
3. Synthèse : mécanisme exact, conséquences correctement déduites, illustration conforme. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Effacement de type exactement décrit, les deux interdictions correctement déduites et la pollution du tas correctement illustrée.",
))

# ── 11. Cas limite : contrainte de format sur une réponse juste ───────────────
add(example(
    meta={"id": "b07-011", "famille": "java-double-checked-locking", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": False, "langage": "java"},
    consigne='''
Le double-checked locking est-il correct en Java ? **Réponds en trois points maximum**, c'est pour une fiche de revue de code.
''',
    reponse='''
Le double-checked locking est correct en Java **à condition** que le champ soit déclaré `volatile`. Voici pourquoi, et comment le reconnaître en revue.

**1. Le motif.** On teste le champ hors verrou, on ne prend le verrou que s'il est nul, puis on re-teste à l'intérieur — d'où le nom. L'objectif est d'éviter le coût du verrou sur le chemin nominal, une fois l'instance construite.

**2. Ce qui casse sans `volatile`.** L'écriture `instance = new Holder()` n'est pas atomique : allocation, exécution du constructeur, affectation de la référence. Rien n'interdit au compilateur ou au processeur de rendre la référence visible avant la fin du constructeur. Un autre thread voit alors un champ non nul, saute le verrou, et manipule un objet partiellement initialisé.

**3. Ce que `volatile` garantit.** Depuis Java 5 et la refonte du modèle mémoire par la JSR-133, une écriture volatile établit une relation happens-before avec les lectures suivantes : aucune opération du constructeur ne peut être réordonnée après l'affectation, et la visibilité est assurée.

**4. En pratique.** Pour un singleton, l'idiome de l'initialisation à la demande par classe interne est préférable : le chargeur de classes garantit l'unicité et la sûreté, sans `volatile` ni verrou explicite.

**5. En revue.** Cherchez le couple `if (champ == null)` hors verrou et un champ **non** `volatile` : c'est la signature du défaut.
''',
    thinking='''
1. Analyse de l'explication : le contenu technique est exact de bout en bout. La condition posée d'emblée — correct si et seulement si le champ est `volatile` — est la bonne réponse. La décomposition de `new Holder()` en allocation, construction puis affectation est juste, le risque de publication d'une référence vers un objet partiellement construit est réel, et l'attribution de la garantie à la JSR-133 depuis Java 5 est correcte. L'idiome de la classe interne est effectivement l'alternative recommandée, la sûreté venant du chargeur de classes.
2. Vérification des contraintes : la requête impose « trois points maximum », en précisant l'usage, une fiche de revue de code. La réponse en compte cinq. Ce n'est pas une préférence de style mais une exigence chiffrée et vérifiable, et le livrable demandé n'est pas utilisable tel quel. Le sujet tient d'ailleurs en trois points sans rien perdre d'essentiel : le motif, le rôle de `volatile`, et le signe à chercher en revue.
3. Synthèse : le fond est exact et directement utile, mais la seule contrainte de forme imposée est dépassée. FAIL.
''',
    exact=True, bugs=True, consignes=True,
    extra_criteres={"format_impose": "La sortie respecte la limite de longueur chiffrée fixée par la requête."},
    extra_checks={"format_impose": False},
    raison="Contenu exact mais la contrainte explicite de trois points maximum est dépassée, avec cinq points.",
))

# ── 12. Théorie : TLS et journalisation ───────────────────────────────────────
add(example(
    meta={"id": "b07-012", "famille": "web-tls-parametres-url", "domaine": "theorie", "tache": "question_reponse",
          "cas": "defaillant", "verbeux": False, "langage": "web"},
    consigne='''
Un collègue veut passer le jeton de réinitialisation de mot de passe en paramètre d'URL, en arguant que « de toute façon c'est en HTTPS, donc chiffré ». Qu'en penses-tu ?
''',
    reponse='''
Il a raison sur le principe. TLS chiffre l'intégralité de la requête HTTP, en-têtes et ligne de requête comprises : un observateur du réseau ne voit ni le chemin, ni les paramètres, uniquement l'adresse IP de destination et le volume échangé.

Le chiffrement est établi avant qu'un seul octet HTTP ne circule. La poignée de main négocie une suite cryptographique, authentifie le serveur par son certificat, puis dérive les clés de session ; tout ce qui suit, requête et réponse, passe dans ce tunnel. Avec TLS 1.3, la négociation tient en un aller-retour, et les suites vulnérables ont été retirées de la spécification.

Le jeton est donc protégé en transit, et le mettre dans l'URL plutôt que dans le corps ne change rien à sa confidentialité. C'est même plus pratique pour un lien envoyé par courriel, qui ne peut pas porter de corps de requête.

- **`Strict-Transport-Security`.** Sans cet en-tête, un utilisateur qui saisit votre domaine sans préciser le schéma part en clair et se fait rediriger : cette première requête est interceptable. L'en-tête supprime cette fenêtre pour les visites suivantes.
- **Surveillez vos certificats.** Une expiration non anticipée rend le service inaccessible, et les journaux de transparence des certificats permettent de détecter qu'une autorité a émis un certificat pour votre domaine à votre insu.

Le seul point de vigilance concerne la durée de validité : limitez le jeton à quelques minutes et rendez-le à usage unique.
''',
    thinking='''
1. Analyse de l'explication : le premier paragraphe est exact sur le transit. TLS chiffre effectivement la ligne de requête et les en-têtes, et un observateur réseau ne voit ni le chemin ni la chaîne de requête. La description de la poignée de main est exacte elle aussi, tout comme les deux durcissements proposés — `Strict-Transport-Security` supprime bien la fenêtre de la première requête en clair, et les journaux de transparence des certificats servent bien à détecter une émission illégitime. La conclusion qui en est tirée est pourtant fausse, car elle confond confidentialité **en transit** et confidentialité **de bout en bout** : tout ce déploiement technique porte sur le tunnel, et le problème est entièrement à ses deux extrémités.
2. Vérification des contraintes : une URL fuit par de nombreux canaux situés hors du tunnel TLS. Le serveur consigne la ligne de requête complète dans ses journaux d'accès, tout comme les proxys inverses et les répartiteurs de charge, où le jeton se retrouve en clair et souvent conservé longtemps. Le navigateur l'inscrit dans l'historique, et l'envoie dans l'en-tête `Referer` vers toute ressource tierce chargée par la page — ce qui suffit à divulguer un jeton de réinitialisation à un service d'analyse d'audience. Il apparaît aussi dans les journaux des passerelles de messagerie qui pré-visitent les liens. La réponse omet enfin que le nom de domaine reste visible en transit via le SNI et les requêtes DNS, ce qui contredit l'idée d'une opacité totale. Les recommandations finales, jeton court et à usage unique, sont justes mais très insuffisantes ici : ce sont des mesures d'atténuation, pas la réponse au problème posé.
3. Synthèse : raisonnement fondé sur un fait exact mais appliqué au mauvais périmètre, aboutissant à valider la divulgation d'un jeton dans les journaux et l'en-tête `Referer`. FAIL.
''',
    exact=False, bugs=False, consignes=True,
    raison="Confond confidentialité en transit et de bout en bout : l'URL fuit par les journaux d'accès, l'historique et l'en-tête Referer.",
))

# ── 13. Théorie : limitation de débit ─────────────────────────────────────────
add(example(
    meta={"id": "b07-013", "famille": "archi-limitation-debit", "domaine": "theorie", "tache": "explication",
          "cas": "parfait", "verbeux": False, "langage": "web"},
    consigne='''
On veut limiter notre API à 100 requêtes par minute et par client. Un développeur propose de compter les requêtes par minute civile et de remettre le compteur à zéro au changement de minute. Est-ce suffisant ?
''',
    reponse='''
Non, à cause de l'effet de bord aux frontières. Avec une fenêtre fixe, un client peut envoyer 100 requêtes à 10 h 00 min 59 s, puis 100 autres à 10 h 01 min 00 s : 200 requêtes en deux secondes, tout en respectant la limite affichée sur chaque minute civile. Votre protection laisse donc passer un pic du double du débit annoncé, au pire moment.

Deux approches corrigent cela :

- **Fenêtre glissante.** On compte les requêtes des soixante dernières secondes, pas de la minute en cours. Exact, mais il faut conserver les horodatages, ou approximer en pondérant le compteur de la fenêtre précédente.
- **Seau à jetons.** Le client dispose d'un seau réalimenté à débit constant, ici environ 1,67 jeton par seconde, et chaque requête en consomme un. La capacité du seau fixe la rafale tolérée, indépendamment du débit moyen. C'est le mécanisme le plus courant, parce qu'il exprime séparément les deux propriétés qui vous intéressent.

| | ce qu'on stocke | rafale tolérée |
|---|---|---|
| fenêtre fixe | un compteur par minute civile | jusqu'au double de la limite, à cheval sur la frontière |
| fenêtre glissante | les horodatages, ou un compteur pondéré | conforme à la limite |
| seau à jetons | un niveau et une date de dernier remplissage | fixée par la capacité du seau |

Trois points de mise en œuvre : le compteur doit être partagé entre instances, donc dans un stockage commun avec des opérations atomiques ; renvoyez `429` avec un en-tête `Retry-After` pour que les clients bien élevés sachent attendre ; et décidez explicitement du comportement si le stockage partagé tombe, laisser passer ou refuser, car ce choix est un arbitrage entre disponibilité et protection.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact et l'exemple chiffré correctement construit. Avec une fenêtre fixe, deux rafales placées de part et d'autre d'une frontière autorisent bien jusqu'au double de la limite sur un intervalle glissant, ce qui est l'objection décisive à la proposition évaluée.
2. Vérification des contraintes : les deux solutions proposées sont les bonnes et correctement décrites. La fenêtre glissante exacte suppose effectivement de conserver les horodatages, et l'approximation par pondération de la fenêtre précédente est la variante usuelle. Le calcul du seau à jetons est juste : 100 jetons par minute correspondent bien à environ 1,67 par seconde, et la distinction entre capacité, qui fixe la rafale, et débit de remplissage, qui fixe la moyenne, est exacte. Les trois points de mise en œuvre sont pertinents et rarement tous cités, en particulier le comportement à adopter si le stockage partagé devient indisponible. La question posée reçoit une réponse nette dès la première ligne.
3. Synthèse : objection exacte et chiffrée, solutions correctement décrites, considérations de mise en œuvre justes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Identifie exactement l'effet de bord de la fenêtre fixe, avec des solutions correctement décrites et un calcul de débit juste.",
))

# ── 14. Théorie : gestionnaires de contexte ───────────────────────────────────
add(example(
    meta={"id": "b07-014", "famille": "python-gestionnaire-contexte", "domaine": "theorie", "tache": "question_reponse",
          "cas": "parfait", "verbeux": False, "langage": "python"},
    consigne='''
Quelle est la différence entre un `try/finally` et un gestionnaire de contexte en Python ? Et que se passe-t-il si `__exit__` renvoie `True` ?
''',
    reponse='''
Fonctionnellement, un gestionnaire de contexte **est** un `try/finally`, mais réutilisable et nommé. Le gain n'est pas dans ce qu'il fait, il est dans le fait de l'écrire une fois au lieu de le répéter à chaque appelant, avec le risque d'oubli que cela comporte.

La différence de fond est que `__exit__` reçoit l'exception en cours — type, valeur, trace — et peut donc décider quoi en faire, là où un `finally` ne fait que s'exécuter.

C'est le rôle de la valeur de retour : si `__exit__` renvoie une valeur vraie, **l'exception est supprimée** et l'exécution reprend après le bloc `with`, comme si de rien n'était. Toute autre valeur, y compris `None` — donc le comportement par défaut d'une fonction sans `return` — laisse l'exception se propager.

C'est puissant et dangereux : un `return True` posé par mégarde dans un `__exit__` avale silencieusement toutes les exceptions du bloc. La règle est de ne renvoyer une valeur vraie que délibérément, et de manière ciblée, en testant le type de l'exception reçue — c'est exactement ce que fait `contextlib.suppress`.
''',
    thinking='''
1. Analyse de l'explication : la distinction est exacte. Un gestionnaire de contexte encapsule bien un `try/finally` réutilisable, et la vraie différence tient à ce que `__exit__` reçoit le triplet décrivant l'exception en cours, ce qu'un `finally` ne fait pas.
2. Vérification des contraintes : la réponse à la seconde question est correcte et précise. Une valeur de retour vraie supprime effectivement l'exception, l'exécution reprenant après le bloc `with`, et `None`, valeur par défaut, la laisse se propager. La mise en garde est justifiée, un `return True` involontaire avalant toutes les exceptions du bloc, et la référence à `contextlib.suppress` est exacte : c'est bien un gestionnaire de contexte dont l'`__exit__` renvoie vrai pour les seuls types d'exception qui lui ont été fournis. Les deux questions posées sont traitées.
3. Synthèse : distinction exacte, sémantique de la valeur de retour correctement énoncée, mise en garde et référence pertinentes. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Distinction exacte avec try/finally et sémantique de __exit__ correctement énoncée, y compris la suppression d'exception.",
))

# ── 15. Cas limite : partie facultative omise ─────────────────────────────────
add(example(
    meta={"id": "b07-015", "famille": "archi-reprise-erreur", "domaine": "theorie", "tache": "explication",
          "cas": "limite", "verbeux": False, "langage": "web"},
    consigne='''
Notre client réessaie les appels échoués toutes les secondes, jusqu'à cinq fois. Lors de la dernière panne, cela a aggravé la situation. Explique pourquoi et que faire. Si tu as le temps, dis un mot du disjoncteur.
''',
    reponse='''
Parce que des réessais à intervalle fixe **synchronisent** vos clients. Quand le service tombe, tous échouent en même temps, donc réessaient en même temps, une seconde plus tard, puis encore. Le service qui tentait de se rétablir reçoit alors des vagues régulières de charge, exactement au moment où il en a le moins la capacité : c'est ce qu'on appelle une tempête de réessais.

Deux corrections vont ensemble.

**Attente exponentielle.** Doublez le délai à chaque tentative — 1 s, 2 s, 4 s, 8 s — pour laisser au service une fenêtre de rétablissement qui s'élargit au lieu de rester constante.

**Gigue aléatoire.** L'exponentielle seule ne suffit pas : elle espace les vagues sans les désynchroniser, puisque tous les clients doublent en même temps. Tirez le délai au hasard dans l'intervalle, par exemple uniformément entre zéro et le plafond courant. C'est la gigue qui étale réellement la charge.

Deux garde-fous complémentaires : ne réessayez que ce qui est idempotent, sans quoi vous dupliquez des effets de bord ; et plafonnez le délai comme le nombre total de tentatives, faute de quoi un client attend indéfiniment.
''',
    thinking='''
1. Analyse de l'explication : le diagnostic est exact et bien nommé. Des réessais à intervalle fixe synchronisent effectivement les clients, et le service reçoit des vagues périodiques pendant sa fenêtre de rétablissement.
2. Vérification des contraintes : les deux corrections sont correctes et, surtout, correctement articulées. Le point souvent manqué est traité explicitement : l'attente exponentielle seule espace les vagues sans les désynchroniser, c'est la gigue qui étale la charge, et le tirage uniforme entre zéro et le plafond courant est bien la forme recommandée. Les deux garde-fous sont justes, la restriction aux opérations idempotentes comme le plafonnement du délai et du nombre de tentatives. En revanche, la demande facultative sur le disjoncteur n'est pas traitée, alors qu'elle complétait naturellement le propos en évitant d'émettre des appels voués à l'échec. La consigne la présentait explicitement comme facultative.
3. Synthèse : la question obligatoire reçoit une réponse exacte et complète, l'unique omission porte sur une demande explicitement facultative. PASS.
''',
    exact=True, bugs=True, consignes=True,
    raison="Tempête de réessais correctement expliquée, avec l'articulation exacte entre exponentielle et gigue ; seul le disjoncteur, facultatif, manque.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
