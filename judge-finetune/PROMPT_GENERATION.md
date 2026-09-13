# Prompts de génération pour modèles tiers

Deux prompts, selon ce que tu délègues. Le **A** est recommandé : il fait produire par un autre modèle
la matière à juger, et laisse l'étiquetage à un annotateur unique. Le **B** délègue tout, avec relecture obligatoire.

Dans les deux cas, la sortie passe par `make validate`, qui rejette tout ce qui ne respecte pas le format
ou la cohérence verdict/critères.

---

## Prompt A — produire seulement les réponses à juger (recommandé)

À donner à un modèle de code local (Qwen2.5-Coder, Llama, Mistral…), idéalement **le modèle que le juge
évaluera en production**, pour que les erreurs soient authentiques plutôt que simulées.

```
Tu es un assistant de code. On te donne une consigne de développement.

Réponds comme tu le ferais normalement, sans te censurer et sans chercher à être exemplaire :
produis ta réponse naturelle, avec le code et les explications que tu jugerais utiles.

Ne signale pas les défauts éventuels de ta propre réponse et n'ajoute aucun avertissement :
un relecteur s'en chargera ensuite.

CONSIGNE :
<insérer ici la consigne>
```

Trois variantes à faire tourner sur la même consigne, pour obtenir des réponses de qualités différentes :

| Variante | Réglage | Ce qu'on récupère |
|---|---|---|
| Nominale | température 0,2 | souvent correcte → cas `parfait` |
| Dégradée | température 0,9, ou un modèle plus petit | erreurs authentiques → cas `defaillant` |
| Bavarde | ajouter « Développe en détail, structure ta réponse avec des titres » | cas verbeux, à bug caché ou corrects |

Ces réponses brutes sont ensuite étiquetées par l'annotateur unique (voir `PROTOCOLE.md` §1).

---

## Prompt B — produire des exemples complets

À n'utiliser que si tu acceptes une relecture systématique. Colle ce bloc tel quel.

````
Tu produis des exemples d'entraînement pour un juge automatique de code (LLM-as-a-Judge).
Chaque exemple montre à ce juge comment évaluer la réponse d'un assistant de code.

## Format de sortie

Une ligne JSON par exemple, rien d'autre : pas de texte avant ou après, pas de bloc markdown.
Chaque ligne a exactement deux clés, "meta" et "messages".

{"meta": {...}, "messages": [{"role":"system",...},{"role":"user",...},{"role":"assistant",...}]}

### meta

| Champ | Valeurs autorisées |
|---|---|
| id | "bNN-001" à "bNN-015", NN = numéro de lot |
| famille | slug du scénario, ex. "java-stream-tomap-doublons" |
| domaine | "code" ou "theorie" |
| tache | "generation", "refactoring", "debogage", "explication", "question_reponse" |
| cas | "parfait", "defaillant", "limite" |
| verbeux | true ou false |
| langage | "java", "python", "typescript", "sql", "go", "web", ... |

### message system — à recopier caractère pour caractère

Tu es un juge d'évaluation de code expert et impartial. Rédige d'abord ton analyse pas à pas dans une balise <thinking> en vérifiant l'exactitude technique, l'absence de bugs et le respect des consignes. Termine obligatoirement par un objet JSON strict contenant les critères booléens et le verdict final.

### message user — gabarit exact, en-têtes inclus

### CONTEXTE ET CONSIGNE
[la demande adressée à l'assistant]

### RÉPONSE DE L'ASSISTANT À ÉVALUER
[le code ou l'explication produit par l'assistant]

### CRITÈRES D'ÉVALUATION
1. Exactitude technique
2. Absence de bugs ou d'erreurs conceptuelles
3. Respect des consignes

### message assistant

Une balise <thinking> avec exactement trois étapes numérotées, puis un objet JSON strict,
sans rien après. Structure :

<thinking>
1. Analyse du code/de l'explication : [ce que fait le code, ce qui est affirmé]
2. Vérification des contraintes : [le défaut ou son absence, avec un cas concret entrée → sortie]
3. Synthèse : [justification en une ou deux phrases, terminée par PASS. ou FAIL.]
</thinking>
{
  "exactitude_technique": true,
  "absence_de_bugs": false,
  "respect_consignes": true,
  "verdict": "FAIL",
  "raison_principale": "une phrase qui nomme le défaut décisif"
}

## Règle de verdict — sans exception

verdict = "PASS" si et seulement si les trois critères booléens sont true. Sinon "FAIL".

Définition des critères :
- exactitude_technique : le code compile et s'exécute, les API existent, et toutes les
  affirmations techniques de la réponse sont vraies.
- absence_de_bugs : aucun bug logique, faille de sécurité, régression ou erreur conceptuelle.
- respect_consignes : toutes les consignes OBLIGATOIRES sont respectées.

Obligatoire contre facultatif — c'est ce qui tranche les cas limites :
- Une consigne formulée comme préférence (« si possible », « idéalement », « si tu as le temps »)
  non suivie ne met PAS respect_consignes à false. On le mentionne dans le <thinking>.
- Une réponse verbeuse mais correcte n'est JAMAIS pénalisée pour sa seule longueur.
- Une exigence explicite et vérifiable non respectée (signature imposée, version de langage,
  dépendance interdite, format ou longueur imposés, périmètre exclu) met respect_consignes à false.

Cohérence obligatoire : cas "parfait" → verdict PASS. cas "defaillant" → verdict FAIL.
cas "limite" → PASS ou FAIL selon la gravité, en appliquant la règle ci-dessus.

## Règle d'honnêteté — la plus importante

N'invente JAMAIS un résultat d'exécution, un chiffre, une mesure de performance ou un message
d'erreur. Le <thinking> ne doit contenir que des affirmations dont tu es certain.

Si tu veux citer un comportement précis (valeur retournée, exception levée, plan d'exécution),
écris-le sous la forme À VÉRIFIER: <affirmation>. Le relecteur l'exécutera et remplacera le
marqueur par la valeur réelle, ou retirera l'affirmation.

Un <thinking> vague n'apprend rien au juge : cite les lignes, les API et les valeurs concernées.

## Composition d'un lot de 15

- 9 exemples "code", 6 exemples "theorie"
- 6 "parfait", 6 "defaillant", 3 "limite"
- au moins 2 exemples verbeux à bug caché (verbeux: true, verdict FAIL)
- au moins 1 exemple verbeux et correct (verbeux: true, verdict PASS), en contrôle
- verdicts globalement équilibrés, autour de 8 PASS pour 7 FAIL
- varier les langages et les types de défauts : sécurité, concurrence, correction,
  mauvais usage d'API, performance, erreurs conceptuelles

Deux exemples peuvent partager la même consigne avec des réponses de qualité opposée :
donne-leur alors la MÊME famille, jamais des familles différentes.

## Familles déjà utilisées — ne pas les reprendre

<coller ici la liste des familles consommées, section « Familles consommées » de data/PLAN_CORPUS.md>

## Avant de répondre, vérifie

1. Une ligne JSON valide par exemple, 15 lignes, aucune autre sortie.
2. Message system identique au gabarit, caractère pour caractère.
3. Les trois en-têtes du message user présents, dans l'ordre, orthographe exacte.
4. Le message assistant commence par <thinking> et se termine par l'accolade fermante du JSON.
5. L'étape 3 du <thinking> se termine par le même verdict que le JSON.
6. Les cinq clés JSON dans l'ordre : exactitude_technique, absence_de_bugs, respect_consignes,
   verdict, raison_principale.
7. verdict cohérent avec les trois booléens, et cas cohérent avec le verdict.
8. Quotas de composition respectés.
````

---

## Après réception

```bash
# 1. format et cohérence — doit afficher 0 error(s)
make validate

# 2. dérive de distribution sur l'ensemble du corpus
make stats

# 3. affirmations à vérifier laissées par le générateur
grep -c "À VÉRIFIER" data/seed/batch_NN.jsonl
```

Tant qu'il reste un `À VÉRIFIER`, le lot n'est pas intégrable : chaque marqueur doit être exécuté et
remplacé par la valeur mesurée, ou supprimé. Voir la méthode par sondes décrite dans `PLAN_CORPUS.md`.
