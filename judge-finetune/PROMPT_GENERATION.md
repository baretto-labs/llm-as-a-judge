# Prompts de génération pour modèles tiers

Deux prompts, selon ce que tu délègues. Le **A** est recommandé : il fait produire par un autre modèle la
matière à juger, et laisse l'étiquetage à un annotateur unique. Le **B** délègue tout, avec relecture obligatoire.

Dans les deux cas, la sortie passe par `make validate`, qui rejette tout écart de format, tout désalignement
entre les critères déclarés et les contrôles rendus, et toute incohérence du verdict.

---

## Prompt A — produire seulement la matière à juger (recommandé)

À donner à un modèle de code local, idéalement **celui que le juge évaluera en production**, pour que les
erreurs soient authentiques plutôt que simulées.

```
Tu es un assistant de code. On te donne une consigne de développement.

Réponds comme tu le ferais normalement, sans te censurer et sans chercher à être exemplaire :
produis ta réponse naturelle, avec le code et les explications que tu jugerais utiles.

Ne signale pas les défauts éventuels de ta propre réponse et n'ajoute aucun avertissement :
un relecteur s'en chargera ensuite.

CONSIGNE :
<insérer ici la consigne>
```

| Variante | Réglage | Ce qu'on récupère |
|---|---|---|
| Nominale | température 0,2 | souvent correcte → cas `parfait` |
| Dégradée | température 0,9, ou un modèle plus petit | erreurs authentiques → cas `defaillant` |
| Bavarde | ajouter « Développe en détail, structure ta réponse avec des titres » | cas verbeux, à défaut caché ou corrects |

**Pour les exemples RAG**, la matière ne se génère pas : elle se récupère. Lancer les stratégies du dépôt
sur `QuestionCorpus` et conserver les contextes réellement retournés, bruit et troncatures compris.

---

## Prompt B — produire des exemples complets

À n'utiliser que si tu acceptes une relecture systématique. Colle ce bloc tel quel.

````
Tu produis des exemples d'entraînement pour un juge IA ultra-rigoureux.

## Format de sortie

Une ligne JSON par exemple, rien d'autre : pas de texte avant ou après, pas de bloc markdown.
Chaque ligne a exactement deux clés, "meta" et "messages".

## Les trois tâches

Chaque exemple porte un marqueur de tâche, qui détermine la POSTURE du juge :

- CODE_ANALYSIS — monde ouvert. Le juge mobilise ses connaissances techniques pour
  détecter un défaut que la sortie ne mentionne pas.
- RAG_CONTEXT_RELEVANCE — le juge évalue si les extraits récupérés suffisent à répondre
  à la requête, sans se prononcer sur la réponse elle-même.
- RAG_FAITHFULNESS — monde fermé strict. Le juge ne juge QUE d'après le contexte fourni.
  Toute affirmation non étayée par un extrait est rejetée, MÊME SI ELLE EST VRAIE.
  C'est la règle la plus importante de cette tâche.

## Contrôles atomiques imposés par tâche

CODE_ANALYSIS
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

RAG_CONTEXT_RELEVANCE
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

RAG_FAITHFULNESS
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

## Contrôles supplémentaires — obligatoires quand la requête l'appelle

Les trois contrôles ci-dessus sont un socle, pas une liste figée. Dès que la requête porte une
contrainte explicite et vérifiable, AJOUTE un quatrième contrôle nommé d'après cette contrainte :

  signature_conforme, format_impose, dependance_autorisee, perimetre_respecte,
  contrainte_disponibilite, aucune_dependance_externe, validation_entree, ...

Deux règles :
- environ un exemple sur cinq doit porter un contrôle supplémentaire ;
- ce contrôle doit valoir true dans certains exemples et false dans d'autres. S'il n'était
  false que lorsqu'il apparaît, le juge apprendrait « quatrième contrôle donc échec ».

## meta

| Champ | Valeurs autorisées |
|---|---|
| id | "bNN-001" à "bNN-015", NN = numéro de lot |
| famille | slug du scénario, ex. "java-stream-tomap-doublons" |
| task | "CODE_ANALYSIS", "RAG_CONTEXT_RELEVANCE", "RAG_FAITHFULNESS" |
| domaine | "code", "theorie", "rag" |
| tache | "generation", "refactoring", "debogage", "explication", "question_reponse", "retrieval", "synthese" |
| cas | "parfait", "defaillant", "limite" |
| verbeux | true ou false |
| langage | "java", "python", "typescript", "sql", "go", "web", ... |

## Gabarits — à recopier caractère pour caractère

message system :

Tu es un juge IA ultra-rigoureux. TÂCHE: {TASK}. Analyse la situation pas à pas dans <thinking> avant de rendre ton verdict JSON.

message user :

### CONTEXTE / RAG
[les extraits récupérés, ou pour CODE_ANALYSIS la ligne exacte :
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)]

### ENTREE / REQUÊTE
[la demande adressée à l'assistant]

### SORTIE À ÉVALUER
[le code, la réponse ou les extraits à juger]

### CRITÈRES DE VALIDATION
1. nom_du_controle: description factuelle observable
2. nom_du_controle: description factuelle observable
3. nom_du_controle: description factuelle observable

message assistant :

<thinking>
1. Énumération : symboles, méthodes et signatures en jeu. Pour les tâches RAG, cite TEXTUELLEMENT les extraits pertinents.
2. Vérification point par point : confronte chaque contrôle à un fait concret (entrée → sortie, exception nommée, extrait cité).
3. Synthèse : justification en une ou deux phrases, terminée par PASS. ou FAIL.
</thinking>
{
  "checks": {
    "exactitude_technique": true,
    "absence_de_bugs": false,
    "respect_consignes": true
  },
  "verdict": "FAIL",
  "reason": "une phrase nommant le motif décisif du verdict"
}

## Règles invariantes

1. verdict = "PASS" si et seulement si TOUS les contrôles valent true. Sinon "FAIL". Aucune exception.
2. Les clés de "checks" sont exactement les noms déclarés dans CRITÈRES DE VALIDATION, dans le même ordre.
3. Clés JSON exactement checks, verdict, reason, dans cet ordre : les contrôles sont posés
   AVANT la décision qu'ils justifient. Rien après l'accolade fermante.
4. L'étape 3 du <thinking> se termine par le même verdict que le JSON.
5. cas "parfait" → PASS. cas "defaillant" → FAIL. cas "limite" → selon la gravité.

Obligatoire contre facultatif, c'est ce qui tranche les cas limites :
- une consigne formulée comme préférence (« si possible », « si tu as le temps ») non suivie
  ne met PAS le contrôle à false ; on le mentionne dans le <thinking> ;
- une sortie verbeuse mais correcte n'est JAMAIS pénalisée pour sa seule longueur ;
- une exigence explicite et vérifiable non respectée (signature imposée, version, dépendance
  interdite, format ou longueur imposés, périmètre exclu) met le contrôle à false.

## Règle d'honnêteté — la plus importante

N'invente JAMAIS un résultat d'exécution, un chiffre, une mesure ou un message d'erreur.
Si tu veux citer un comportement précis, écris À VÉRIFIER: <affirmation>. Le relecteur
l'exécutera et remplacera le marqueur par la valeur réelle, ou retirera l'affirmation.

Pour RAG_FAITHFULNESS, n'invente pas non plus le contexte : il doit provenir d'une
récupération réelle, fournie avec la demande.

## Composition d'un lot de 15

- répartition des tâches conforme à la cible globale : environ 11 CODE_ANALYSIS,
  2 RAG_CONTEXT_RELEVANCE, 2 RAG_FAITHFULNESS
- 6 "parfait", 6 "defaillant", 3 "limite"
- au moins 2 exemples verbeux à défaut caché, au moins 1 verbeux et correct en contrôle
- verdicts globalement équilibrés, autour de 8 PASS pour 7 FAIL
- varier langages et types de défauts : sécurité, concurrence, correction, mauvais usage
  d'API, performance, erreurs conceptuelles

Deux exemples peuvent partager la même requête avec des sorties de qualité opposée :
donne-leur alors la MÊME famille.

## Familles déjà utilisées — ne pas les reprendre

<coller ici les sections « Familles consommées » de data/PLAN_CORPUS.md>

## Avant de répondre, vérifie

1. 15 lignes JSON valides, aucune autre sortie.
2. Message system identique au gabarit, marqueur de tâche compris.
3. Les quatre en-têtes du message user présents, dans l'ordre, orthographe exacte.
4. checks aligné sur les critères déclarés, mêmes noms, même ordre.
5. verdict cohérent avec les checks, et cas cohérent avec le verdict.
6. Quotas de composition respectés.
````

---

## Après réception

```bash
make validate                              # doit afficher 0 error(s)
make stats                                 # dérive par tâche, cas, verbosité
grep -c "À VÉRIFIER" data/seed/batch_NN.jsonl
```

Tant qu'il reste un `À VÉRIFIER`, le lot n'est pas intégrable : chaque marqueur doit être exécuté et
remplacé par la valeur mesurée, ou supprimé. Voir la méthode par sondes dans `generators/README.md`.
