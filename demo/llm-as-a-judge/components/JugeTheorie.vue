<!--
  The generic LLM-as-a-judge, as the literature describes it — no project numbers here.
  0 copy → judge → verdict · 1 the rubric · 2 a deterministic filter before the judge
  · 3 an imposed output format · 4 a human-graded reference set to check the judge
  · 5 doubtful copies routed to a human.
  The project's own judge (JudgeSchema.vue) fills these slots later in the talk.
-->
<template>
  <svg viewBox="0 0 900 400" class="juge-theorie w-full" role="img"
       aria-label="Le principe du LLM juge : copie, barème, filtre, juge, verdict, étalon">
    <defs>
      <marker id="jt-arrow" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10z" fill="currentColor" />
      </marker>
    </defs>

    <!-- 0 · the copy, the judge, the verdict -->
    <g>
      <rect x="20" y="160" width="160" height="110" rx="8" />
      <text x="100" y="186" class="title">LA COPIE</text>
      <text x="100" y="212" class="sub">question</text>
      <text x="100" y="232" class="sub">contexte</text>
      <text x="100" y="252" class="sub">réponse</text>
      <line x1="180" y1="215" x2="376" y2="215" marker-end="url(#jt-arrow)" />
      <rect x="380" y="170" width="170" height="90" rx="10" class="juge" />
      <text x="465" y="211" class="title clair">LLM JUGE</text>
      <text x="465" y="235" class="sub clair">lit, ne rédige pas</text>
      <line x1="550" y1="215" x2="626" y2="215" marker-end="url(#jt-arrow)" />
      <g class="sortie">
        <rect x="630" y="180" width="140" height="70" rx="8" class="verdict" />
        <text x="700" y="210" class="title rouge">VERDICT</text>
        <text x="700" y="232" class="sub">+ une raison</text>
      </g>
    </g>

    <!-- 1 · the rubric, written before reading any copy -->
    <g v-click class="piece">
      <rect x="380" y="40" width="170" height="70" rx="8" />
      <text x="465" y="68" class="title">LE BARÈME</text>
      <text x="465" y="91" class="sub">critères écrits avant</text>
      <line x1="465" y1="110" x2="465" y2="166" marker-end="url(#jt-arrow)" />
    </g>

    <!-- 2 · what a rule can decide never reaches the LLM -->
    <g v-click class="piece">
      <rect x="215" y="180" width="130" height="70" rx="8" />
      <text x="280" y="209" class="title">FILTRE</text>
      <text x="280" y="231" class="sub">sans LLM</text>
      <line x1="280" y1="250" x2="280" y2="306" marker-end="url(#jt-arrow)" />
      <text x="280" y="328" class="note">hors-sujet : écartée</text>
      <text x="280" y="348" class="note">avant lecture</text>
    </g>

    <!-- 3 · the answer comes in a shape a program can check -->
    <g v-click class="piece">
      <rect x="630" y="70" width="250" height="56" rx="8" class="code" />
      <text x="755" y="104" class="mono">{ critères, verdict, raison }</text>
      <line x1="700" y1="126" x2="700" y2="176" marker-end="url(#jt-arrow)" />
      <text x="755" y="56" class="note">format imposé, vérifié</text>
    </g>

    <!-- 4 · the judge is graded too, against copies a human graded -->
    <g v-click class="piece">
      <rect x="630" y="310" width="250" height="70" rx="8" />
      <text x="755" y="338" class="title">L'ÉTALON</text>
      <text x="755" y="361" class="sub">copies corrigées à la main</text>
      <line x1="700" y1="306" x2="700" y2="254" marker-end="url(#jt-arrow)" />
      <text x="712" y="286" class="note start">d'accord ?</text>
    </g>

    <!-- 5 · when the judge hesitates, the copy goes to a human -->
    <g v-click class="piece">
      <line x1="770" y1="215" x2="796" y2="215" marker-end="url(#jt-arrow)" />
      <rect x="800" y="180" width="92" height="70" rx="8" class="humain" />
      <text x="846" y="211" class="title">HUMAIN</text>
      <text x="846" y="233" class="sub">relit</text>
      <text x="846" y="168" class="note">doute ?</text>
    </g>
  </svg>
</template>

<style scoped>
.juge-theorie {
  max-height: 380px;
  color: var(--encre);
}

/* Each piece slides into place; the verdict lands like a stamp */
.piece {
  transition: opacity 0.4s ease, translate 0.4s ease;
}
.piece.slidev-vclick-hidden {
  translate: 0 12px;
}
.sortie {
  transform-box: fill-box;
  transform-origin: center;
  animation: tampon-jt 0.45s 0.3s cubic-bezier(0.3, 1.6, 0.5, 1) both;
}
@keyframes tampon-jt {
  from { opacity: 0; transform: scale(1.8) rotate(-10deg); }
  to   { opacity: 1; transform: scale(1) rotate(0); }
}

rect {
  fill: var(--papier-carte);
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-opacity: 0.7;
  filter: drop-shadow(0 3px 6px rgba(28, 37, 65, 0.1));
}
rect.juge { fill: var(--encre); stroke: none; }
rect.verdict { stroke: var(--rouge); stroke-width: 2.5; stroke-opacity: 1; }
rect.humain { stroke-dasharray: 5 4; }
rect.code { fill: var(--ardoise); stroke: var(--ardoise-bord); stroke-width: 3; stroke-opacity: 1; }

line {
  stroke: currentColor;
  stroke-width: 1.5;
}

text { fill: currentColor; text-anchor: middle; }
.title { font-size: 17px; font-weight: 800; letter-spacing: 0.02em; }
.sub { font-size: 13.5px; fill: var(--encre-douce); }
.clair { fill: var(--papier); }
.rouge { fill: var(--rouge); }
.mono { font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #dbd7ca; }
.note {
  font-family: 'Caveat', cursive;
  font-size: 20px;
  fill: var(--rouge);
}
.start { text-anchor: start; }
</style>
