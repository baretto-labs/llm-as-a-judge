# Démo enregistrée : déroulé

Place : juste avant « Premier verdict » (diapo 15). Durée cible à l'écran : 50 à 60 s.
But : montrer le juge au travail sur UNE copie, avant les chiffres sur 60.

## La question choisie

« What does DocumentIndexingPipeline implement? » (STRUCTURAL)

- Vectoriel : la classe ET `implements AutoCloseable`. hintCoverage 1,00. Juge : PASS, 3 cases vertes.
- Graphe : la classe, mais pas ce qu'elle implémente. hintCoverage 0,50. Juge : FAIL, une seule
  case rouge (`contexte_suffisant`).
- Source : `benchmarks/plafond/sans-plafond.jsonl` (le banc des chiffres 16,7 % / 60 %).
  Rejoué le 2026-10-27 : mêmes verdicts, mêmes raisons, au mot près.

C'est exactement la phrase de la diapo 15 : « il ramène la classe, pas ce qu'elle implémente ».

## Préparer

1. Ollama lancé, modèle chargé : `ollama run qwen2.5-coder:32b ""` une fois avant (sinon le
   premier jugement paie le chargement).
2. Terminal plein écran, fond clair si possible, police grande (au moins 20 pt), 100 colonnes.
3. Fermer les notifications.

## Enregistrer

```bash
cd ~/Workspaces/Labs/llm-as-a-judge
clear && python3 -I scripts/demo_juge.py
```

Durée brute : environ 1:20 (44 s de jugement vectoriel, 32 s graphe). Une seule prise suffit,
le reste se fait au montage.

## Monter

- Accélérer les deux attentes « le juge lit la copie… » (x8 environ), garder le compteur visible :
  on voit que c'est un vrai calcul, sans l'attendre.
- Pause de 2 s sur chaque verdict.
- Zoom (ou encadré) sur les deux lignes clés :
  `✗ AutoCloseable` côté graphe, puis `☒ contexte_suffisant` et `FAIL`.
- Capture de secours : une image fixe de l'écran final (les deux verdicts), à mettre en diapo
  cachée juste après la vidéo.

## Voix (phrases clés, une par moment)

1. Question à l'écran : « Une vraie question de mon banc : qu'est-ce que cette classe implémente ? »
2. Extraits vectoriel : « Le vectoriel ramène la classe, avec `implements AutoCloseable`. »
3. Verdict vectoriel : « Trois cases vertes : PASS. »
4. Extraits graphe : « Le graphe ramène la classe… mais pas ce qu'elle implémente. »
5. Verdict graphe : « Une seule case rouge, et la copie est recalée. » (règle 1 de la diapo 12)
6. Transition : « Une copie, c'est une anecdote. Sur soixante ? » → diapo 15.

✂ Ne pas lire la raison du juge à voix haute : le public la lit.
✂ Ne pas expliquer hintCoverage : le ✓ / ✗ vert et rouge suffit.
