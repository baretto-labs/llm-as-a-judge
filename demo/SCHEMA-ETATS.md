---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
style: |
  section { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.3rem; padding: 60px; }
  h2 { font-size: 1.5rem; margin-bottom: 0.4em; }
  pre { font-size: 0.95rem; line-height: 1.35; }
  .n { color: #c0392b; font-weight: 700; }
---

<!--
ÉCHAFAUDAGE — à jeter.

Les onze états cumulés du schéma de construction du juge, en ASCII, pour pouvoir
DÉROULER le talk avant d'avoir dessiné quoi que ce soit.

Chaque état correspond à un marqueur [AJOUT AU SCHÉMA] de CONFERENCE-V2.md.
Le numéro de diapositive en titre est celui du support.

Quand les PNG Excalidraw existeront, on remplace chaque bloc par une image et ce
fichier disparaît.

Rendu : docker run --rm -v "$(pwd)/demo:/home/marp/app" marpteam/marp-cli \
          SCHEMA-ETATS.md --html --output SCHEMA-ETATS.html
-->

## État 1 — diapo 9 · le filtre L0

```
   réponse à juger
         │
         ▼
   ┌──────────────┐
   │  FILTRE L0   │───►  écartée    (parenthèses, JSON, compilation)
   │ déterministe │
   └──────┬───────┘
          ▼
       LE JUGE
```

Première boîte, et elle est **avant** le juge.
Rien de ce qu'elle recale n'atteint le LLM.

---

## État 2 — diapo 10 · ce qui entre

```
   ┌────────┐   les MÊMES questions    ┌──────────────┐
   │   CI   │──────────────────────────►│  FILTRE L0   │──► écartée
   │        │   à chaque modification   │ déterministe │
   └────────┘                           └──────┬───────┘
                                               ▼
                                            LE JUGE

   ✗ pas de branche « production » — l'absence est un choix
```

---

## État 3 — diapo 11 · le contrat de sortie

```
   CI ──► FILTRE L0 ──►  ┌───────────┐
                         │  LE JUGE  │
                         └─────┬─────┘
                               ▼
                    <thinking>  … </thinking>
                    checks      { c1, c2, c3 }
                    verdict     PASS / FAIL

                    PASS  ⟺  tous les checks vrais
```

L'ordre des champs est le contrat : **on raisonne, on constate, on conclut.**

---

## État 4 — diapo 12 · première parade

```
   CI ──► FILTRE L0 ──►  ┌───────────┐  ──► thinking / checks / verdict
                         │  LE JUGE  │
                         └─────▲─────┘
                               │
                    ┌──────────┴──────────┐
                    │  le même défaut,    │
                    │  bavard ET sec      │   ← détecte le biais de longueur
                    └─────────────────────┘
```

---

## État 5 — diapo 13 · la récupération entre en scène

```
   ┌──────────────┐    extraits    ┌─────────────┐
   │ RÉCUPÉRATION │───────────────►│  MÉLANGE    │
   │ Lucene/Neo4j │                │  graîné par │
   └──────────────┘                │ la question │
                                   └──────┬──────┘
                                          ▼
   CI ──► FILTRE L0 ──────────────►  ┌───────────┐ ──► thinking/checks/verdict
                                     │  LE JUGE  │
                                     └───────────┘
```

Graîné par la question : **la mesure se rejoue à l'identique.**

---

## État 6 — diapo 14 · le banc qui mesure le juge

```
   RÉCUPÉRATION ─► MÉLANGE ─┐
                            ▼
   CI ──► FILTRE L0 ──►  ┌───────────┐ ──► thinking/checks/verdict
                         │  LE JUGE  │           │
                         └───────────┘           ▼
                                        ┌──────────────────┐
                                        │     LE BANC      │
                                        ├──────────────────┤
                                        │ décisions justes │
                                        │ erreurs attrapées│
                                        └──────────────────┘
```

**Deux cadrans, jamais un seul.**

---

## État 7 — diapo 17 · le contexte entre DANS le juge

```
   RÉCUPÉRATION ─► MÉLANGE ─────────┐
                                    │  le contexte, pas seulement la réponse
                                    ▼
   CI ──► FILTRE L0 ──►  ┌─────────────────────┐ ──► le contexte est-il pertinent ?
                         │       LE JUGE       │ ──► permet-il de répondre ?
                         │  question           │ ──► la réponse s'y appuie-t-elle ?
                         │  contexte           │
                         │  réponse            │           │
                         └─────────────────────┘           ▼
                                                        LE BANC
```

C'est ce qui sépare un **défaut de récupération** d'un **défaut de génération**.

---

## État 8 — diapo 18 · les conventions, le cadre

```
  ╔══════════════ LES 4 CONVENTIONS ══════════════════════════════╗
  ║                                                               ║
  ║  RÉCUPÉRATION ─► MÉLANGE ─┐                                   ║
  ║                           ▼                                   ║
  ║  CI ─► FILTRE L0 ─►  ┌───────────┐ ─► thinking/checks/verdict ║
  ║                      │  LE JUGE  │          │                 ║
  ║                      └───────────┘          ▼                 ║
  ║                                          LE BANC              ║
  ╚═══════════════════════════════════════════════════════════════╝
```

Ce n'est pas une boîte de plus : **elles s'appliquent à chaque contrôle.**

---

## État 9 — diapo 21 · la boucle

```
  ╔══════════════ LES 4 CONVENTIONS ══════════════════════════════╗
  ║  RÉCUPÉRATION ─► MÉLANGE ─┐                                   ║
  ║                           ▼                                   ║
  ║  CI ─► FILTRE L0 ─►  ┌───────────┐ ─► thinking/checks/verdict ║
  ║                      │  LE JUGE  │          │                 ║
  ║                      └─────▲─────┘          ▼                 ║
  ║                            │             LE BANC              ║
  ║                            └─────────────────┘                ║
  ║                         est-il aligné ? est-il stable ?       ║
  ╚═══════════════════════════════════════════════════════════════╝
```

Le schéma cesse d'être une chaîne. **Il se vérifie.**

---

## État 10 — diapo 23 · le corpus, et les deux cadrans

```
  ┌──────────────┐  c'est lui qui plafonne tout
  │  LE CORPUS   │  50 items relus en aveugle · κ 0,880
  └──────┬───────┘
         │ étalon
         ▼
  ╔══════════════ LES 4 CONVENTIONS ══════════════════════════════╗
  ║  RÉCUPÉRATION ─► MÉLANGE ─┐                                   ║
  ║                           ▼                                   ║
  ║  CI ─► FILTRE L0 ─►  ┌───────────┐ ─► thinking/checks/verdict ║
  ║                      │  LE JUGE  │          │                 ║
  ║                      └─────▲─────┘          ▼                 ║
  ║                            │             LE BANC              ║
  ║                            └─────────────────┘                ║
  ║                     alignement κ 0,48  ·  stabilité 76 %      ║
  ╚═══════════════════════════════════════════════════════════════╝
```

---

## État 11 — avant « Le banc » · le schéma entier

```
  ┌──────────────┐
  │  LE CORPUS   │  200 exemples · 50 relus en aveugle · κ 0,880
  └──────┬───────┘
         │ étalon
         ▼
  ╔══════════════ LES 4 CONVENTIONS ══════════════════════════════╗
  ║                                                               ║
  ║  RÉCUPÉRATION ─► MÉLANGE graîné ─┐                            ║
  ║   Lucene / Neo4j                 ▼                            ║
  ║  CI ─► FILTRE L0 ─►  ┌───────────────────┐                    ║
  ║                      │     LE JUGE       │                    ║
  ║                      │ question          │                    ║
  ║                      │ contexte          │                    ║
  ║                      │ réponse           │                    ║
  ║                      └─────▲──────┬──────┘                    ║
  ║                            │      ▼                           ║
  ║                            │  thinking / checks / verdict     ║
  ║                            │      │                           ║
  ║                            │      ▼                           ║
  ║                            │   LE BANC                        ║
  ║                            └──────┘                           ║
  ║                     alignement κ 0,48  ·  stabilité 76 %      ║
  ╚═══════════════════════════════════════════════════════════════╝
```

**Voilà l'instrument. Maintenant, ce qu'il mesure.**
