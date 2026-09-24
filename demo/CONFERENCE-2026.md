---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
style: |
  section {
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 1.35rem;
    color: #1a1a1a;
    padding: 70px;
  }
  h1 { font-size: 2.2rem; font-weight: 600; }
  h2 { font-size: 1.7rem; font-weight: 600; margin-bottom: 0.8em; }
  ul { line-height: 1.8; }
  strong { font-weight: 600; }
  .ref { font-size: 0.85rem; color: #666; }
  section.title { justify-content: center; }
---

<!--
Support de la conférence de novembre 2026.

ÉTAT : introduction seule (4 diapositives). Les parties 1 à 4 restent à écrire.
Le contenu de référence — chiffres, réserves, formulations à ne pas employer —
est dans judge-finetune/REX_TRAME.md, qui fait foi. Ce fichier-ci en est la mise
en scène, pas la source.

ATTENTION : demo/SLIDES.md est un AUTRE deck, celui du talk précédent sur le
benchmark RAG. Il note la qualité sur 10, avec le juge gradué abandonné le
2026-09-13. Ne pas y reprendre de chiffres.

RENDU (marp-cli via docker, voir demo/SUPPORT.md) :
  docker run --rm -v "$(pwd)/demo:/home/marp/app" marpteam/marp-cli \
    CONFERENCE-2026.md --html --output CONFERENCE-2026.html

Les blocs en commentaire HTML sous chaque diapositive sont les notes orateur :
Marp les exporte en notes, elles ne s'affichent pas à l'écran.
-->

<!-- _class: title -->

# Évaluer un système LLM sans se mentir

## LLM-as-a-Judge : construire son juge, et mesurer ce qu'il vaut

Mehdi El Ketroussi
Novembre 2026

<!--
Reprendre ici le titre et le sous-titre exacts de l'abstract retenu
(REX_TRAME.md, section « Abstract — retenu, verbatim, ne pas retoucher »).
Ce qui est écrit ci-dessus n'est qu'un gabarit.
-->

---

## Nos tests ne voient pas les erreurs qui comptent

- Un test unitaire vérifie une valeur de retour, **pas un raisonnement**

- BLEU / ROUGE comparent des mots, pas du sens :
  une réponse **juste** formulée autrement est pénalisée,
  une réponse **fausse** bien formulée passe

- Il n'y a pas d'oracle : la même question admet dix bonnes réponses

<!--
À dire, pas à écrire : la conséquence pratique, c'est qu'on livre en se fiant à
l'impression qu'on a en relisant trois sorties à la main.
-->

---

## Trois fois, ça a tenu jusqu'en production

- **Air Canada, 2024** — le chatbot invente une politique de remboursement.
  Le tribunal juge l'entreprise responsable de ce que son chatbot affirme.
  <span class="ref">Moffatt v. Air Canada, 2024 BCCRT 149</span>

- **Mata v. Avianca, 2023** — un avocat dépose **six décisions de justice
  inventées** par ChatGPT, avec des citations d'apparence normale.
  5 000 $ de sanction.
  <span class="ref">S.D.N.Y., 22-cv-1461 (PKC), juge P. Kevin Castel, 22 juin 2023</span>

- **Deloitte Australie, 2025** — rapport à 440 000 AUD remis à un ministère,
  références fabriquées dont une citation attribuée à un juge fédéral.
  ~97 000 AUD remboursés.
  <span class="ref">Targeted Compliance Framework Assurance Review, DEWR</span>

<!--
À dire : dans les trois cas, personne n'a rien vu — non par négligence, mais
parce que le faux avait exactement la forme du vrai. Un avocat ne relit pas une
citation bien formatée. C'est le problème que le reste du talk essaie de résoudre.

État de vérification (2026-09-24) :
- Mata v. Avianca : VÉRIFIÉ sur le texte de l'opinion. Caption, docket, juge,
  date, montant, et la mauvaise foi constatée en ces termes : « acts of conscious
  avoidance and false and misleading statements to the Court ». Le compte est
  SIX décisions inventées (Varghese, Shaboon, Petersen, Martinez, Estate of
  Durden, Miller) — pas neuf. Les trois autres noms qui circulent (Zicherman,
  Ehrlich, In re Air Crash Disaster) sont de VRAIES décisions, citées à
  l'intérieur des fausses.
- Air Canada : citation du jugement à confirmer sur la décision elle-même
  (montant exact des dommages, date).
- Deloitte : concordant sur AP, Fortune et CFO Dive ; la source primaire — le
  rapport révisé et sa mention d'usage d'Azure OpenAI — est sur le site du DEWR
  et n'a pas pu être ouverte le 2026-09-24 (timeout). À confirmer avant l'oral.

Écartés faute de source opposable : NYC MyCity (presse seule) et Chevy Chatbot
(captures d'écran sur les réseaux).
-->

---

## Pourquoi j'ai voulu mesurer

**OllamAssist**, mon propre assistant de code

- J'avais deux stratégies de RAG et **aucun moyen de les départager**

- Le seul juge disponible, c'était moi, sur quelques exemples choisis

- Ma crainte : *[à compléter — ta formulation]*

<!--
La troisième puce est à écrire par Mehdi : c'est la crainte initiale, elle ne
figure nulle part dans les notes du projet. C'est la puce qui fait basculer le
talk du général au vécu.

Transition vers la Partie 1 : « Avant d'écrire une ligne de juge, il y a quatre
questions à se poser — et la première, c'est ce qu'il ne faut surtout pas lui
donner à évaluer. »
-->
