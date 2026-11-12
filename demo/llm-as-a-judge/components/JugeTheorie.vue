<!--
  The generic LLM-as-a-judge, as the literature describes it; no project numbers here.
  Built click by click: 1 the copy · 2 the judge · 3 the verdict · 4 the rubric
  · 5 a deterministic filter before the judge · 6 an imposed output format
  · 7 a human-graded reference set to check the judge · 8 doubtful copies routed to a human.
  Main-row boxes share one height (70) so nothing looks more important by size alone.
  Colours follow the grader's code: red only for "wrong", so the neutral notes are in blue ink.
  The project's own judge (JudgeSchema.vue) fills these slots later in the talk.
-->
<template>
  <svg viewBox="0 30 900 360" class="juge-theorie w-full" role="img"
       aria-label="Le principe du LLM juge : copie, barème, filtre, juge, verdict, étalon">
    <defs>
      <marker id="jt-arrow" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10z" fill="currentColor" />
      </marker>
    </defs>

    <!-- 1 · the copy -->
    <g v-click class="piece">
      <rect x="10" y="180" width="190" height="70" rx="8" />
      <text x="105" y="209" class="title">LA COPIE</text>
      <text x="105" y="231" class="sub">question, contexte, réponse</text>
    </g>

    <!-- 2 · the judge reads it -->
    <g v-click class="piece">
      <line x1="200" y1="215" x2="366" y2="215" marker-end="url(#jt-arrow)" />
      <rect x="370" y="180" width="170" height="70" rx="8" class="juge" />
      <text x="455" y="209" class="title clair">LLM JUGE</text>
      <text x="455" y="231" class="sub clair">lit, ne rédige pas</text>
    </g>

    <!-- 3 · the verdict lands like a stamp -->
    <g v-click class="piece">
      <line x1="540" y1="215" x2="586" y2="215" marker-end="url(#jt-arrow)" />
      <g class="tampon">
        <rect x="590" y="180" width="150" height="70" rx="8" class="verdict" />
        <text x="665" y="209" class="title bleu">VERDICT</text>
        <text x="665" y="231" class="sub">+ une raison</text>
      </g>
    </g>

    <!-- 4 · the rubric, written before reading any copy -->
    <g v-click class="piece">
      <rect x="290" y="40" width="250" height="112" rx="8" />
      <text x="415" y="64" class="title">LE BARÈME <tspan class="sub">· écrit avant</tspan></text>
      <rect x="306" y="80" width="11" height="11" class="case" />
      <text x="326" y="90" class="sub start">rien hors contexte, même vrai</text>
      <rect x="306" y="102" width="11" height="11" class="case" />
      <text x="326" y="112" class="sub start">aucune citation déformée</text>
      <rect x="306" y="124" width="11" height="11" class="case" />
      <text x="326" y="134" class="sub start">consigne respectée</text>
      <line x1="455" y1="152" x2="455" y2="176" marker-end="url(#jt-arrow)" />
    </g>

    <!-- 5 · what a rule can decide never reaches the LLM -->
    <g v-click class="piece">
      <rect x="225" y="180" width="120" height="70" rx="8" />
      <text x="285" y="209" class="title">FILTRE</text>
      <text x="285" y="231" class="sub">sans LLM</text>
      <line x1="285" y1="250" x2="285" y2="306" marker-end="url(#jt-arrow)" />
      <text x="285" y="328" class="note">hors-sujet : écartée</text>
      <text x="285" y="348" class="note">avant lecture</text>
    </g>

    <!-- 6 · the answer comes in a shape a program can check -->
    <g v-click class="piece">
      <rect x="540" y="70" width="250" height="56" rx="8" class="code" />
      <text x="665" y="104" class="mono">{ critères, verdict, raison }</text>
      <line x1="665" y1="126" x2="665" y2="176" marker-end="url(#jt-arrow)" />
      <text x="665" y="56" class="note">format imposé, vérifié</text>
    </g>

    <!-- 7 · the judge is graded too, against copies a human graded -->
    <g v-click class="piece">
      <rect x="540" y="310" width="250" height="70" rx="8" />
      <text x="665" y="339" class="title">L'ÉTALON</text>
      <text x="665" y="361" class="sub">copies corrigées à la main</text>
      <line x1="665" y1="306" x2="665" y2="254" marker-end="url(#jt-arrow)" />
      <text x="677" y="286" class="note start">d'accord ?</text>
    </g>

    <!-- 8 · when the judge hesitates, the copy goes to a human -->
    <g v-click class="piece">
      <line x1="740" y1="215" x2="766" y2="215" marker-end="url(#jt-arrow)" />
      <rect x="770" y="180" width="120" height="70" rx="8" class="humain" />
      <text x="830" y="209" class="title">HUMAIN</text>
      <text x="830" y="231" class="sub">relit</text>
      <text x="830" y="168" class="note">doute ?</text>
    </g>
  </svg>
</template>

<style scoped>
.juge-theorie {
  max-height: 460px;
  margin-top: -1rem;
  color: var(--encre);
}

/* Each piece slides into place; the verdict lands like a stamp */
.piece {
  transition: opacity 0.4s ease, translate 0.4s ease;
}
.piece.slidev-vclick-hidden {
  translate: 0 12px;
}
.tampon {
  transform-box: fill-box;
  transform-origin: center;
  transition: transform 0.45s cubic-bezier(0.3, 1.6, 0.5, 1);
}
.slidev-vclick-hidden .tampon {
  transform: scale(1.6) rotate(-8deg);
}

rect {
  fill: var(--papier-carte);
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-opacity: 0.7;
  filter: drop-shadow(0 3px 6px rgba(28, 37, 65, 0.1));
}
rect.juge { fill: var(--encre); stroke: none; }
rect.verdict { stroke: var(--bleu); stroke-width: 2.5; stroke-opacity: 1; }
rect.humain { stroke-dasharray: 5 4; }
rect.case { fill: none; filter: none; stroke-opacity: 0.8; }
rect.code { fill: var(--ardoise); stroke: var(--ardoise-bord); stroke-width: 3; stroke-opacity: 1; }

line {
  stroke: currentColor;
  stroke-width: 1.5;
}

text { fill: currentColor; text-anchor: middle; }
.title { font-size: 17px; font-weight: 800; letter-spacing: 0.02em; }
.sub { font-size: 13.5px; fill: var(--encre-douce); }
.clair { fill: var(--papier); }
.bleu { fill: var(--bleu); }
.mono { font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #dbd7ca; }
.note {
  font-family: 'Caveat', cursive;
  font-size: 20px;
  fill: var(--bleu);
}
.start { text-anchor: start; }
</style>
