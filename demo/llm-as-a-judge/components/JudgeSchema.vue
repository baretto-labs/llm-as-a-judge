<!--
  The judge pipeline, drawn after demo/SCHEMA-ETATS.md (state 11), revealed in four clicks:
  0 the judge alone · 1 CI + L0 filter · 2 retrieval + seeded shuffle · 3 the bench loop
  · 4 the corpus and the four conventions.
  The corpus legend says "un relecteur" on purpose: never "κ 0,880" (see SCHEMA-ETATS.md header).
-->
<template>
  <svg viewBox="0 0 900 450" class="judge-schema w-full" role="img"
       aria-label="Le pipeline du juge : CI, filtre L0, récupération, mélange, juge, verdict, banc, corpus">
    <defs>
      <marker id="js-arrow" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10z" fill="currentColor" />
      </marker>
    </defs>

    <!-- 0 · the judge and its output -->
    <g>
      <rect x="360" y="195" width="200" height="110" rx="10" class="accent" />
      <text x="460" y="238" class="title">LE JUGE</text>
      <text x="460" y="264" class="sub">question · contexte</text>
      <text x="460" y="284" class="sub">réponse</text>
      <line x1="560" y1="250" x2="616" y2="250" marker-end="url(#js-arrow)" />
      <rect x="620" y="210" width="250" height="80" rx="10" />
      <text x="745" y="243" class="title">checks · verdict</text>
      <text x="745" y="268" class="sub">PASS ⟺ tous les checks vrais</text>
    </g>

    <!-- 1 · CI and the deterministic filter -->
    <g v-click>
      <rect x="30" y="225" width="80" height="50" rx="10" />
      <text x="70" y="256" class="title">CI</text>
      <line x1="110" y1="250" x2="146" y2="250" marker-end="url(#js-arrow)" />
      <rect x="150" y="215" width="160" height="70" rx="10" />
      <text x="230" y="245" class="title">FILTRE L0</text>
      <text x="230" y="268" class="sub">déterministe</text>
      <line x1="310" y1="250" x2="356" y2="250" marker-end="url(#js-arrow)" />
      <line x1="230" y1="285" x2="230" y2="321" marker-end="url(#js-arrow)" />
      <text x="230" y="342" class="sub">écartée</text>
    </g>

    <!-- 2 · retrieval, then the seeded shuffle -->
    <g v-click>
      <rect x="120" y="115" width="190" height="55" rx="10" />
      <text x="215" y="140" class="title">RÉCUPÉRATION</text>
      <text x="215" y="160" class="sub">Lucene / Neo4j</text>
      <line x1="310" y1="142" x2="356" y2="142" marker-end="url(#js-arrow)" />
      <rect x="360" y="115" width="200" height="55" rx="10" />
      <text x="460" y="140" class="title">MÉLANGE</text>
      <text x="460" y="160" class="sub">graîné par la question</text>
      <line x1="460" y1="170" x2="460" y2="191" marker-end="url(#js-arrow)" />
    </g>

    <!-- 3 · the bench closes the loop -->
    <g v-click>
      <line x1="745" y1="290" x2="745" y2="356" marker-end="url(#js-arrow)" />
      <rect x="660" y="360" width="170" height="55" rx="10" />
      <text x="745" y="385" class="title">LE BANC</text>
      <text x="745" y="405" class="sub">aligné ? stable ?</text>
      <path d="M660 387 H460 V309" fill="none" marker-end="url(#js-arrow)" />
    </g>

    <!-- 4 · the corpus, and the four conventions around everything -->
    <g v-click>
      <rect x="20" y="85" width="860" height="355" rx="14" class="frame" />
      <text x="450" y="104" class="legend">LES 4 CONVENTIONS</text>
      <rect x="20" y="8" width="200" height="50" rx="10" />
      <text x="120" y="31" class="title">LE CORPUS</text>
      <text x="120" y="50" class="sub">50 relus · un relecteur</text>
      <line x1="120" y1="58" x2="120" y2="83" marker-end="url(#js-arrow)" />
      <text x="232" y="38" class="sub start">tout est mesuré contre lui</text>
    </g>
  </svg>
</template>

<style scoped>
.judge-schema {
  max-height: 370px;
  color: currentColor;
}
.judge-schema rect {
  fill: var(--papier-carte, none);
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-opacity: 0.7;
}
.judge-schema rect.accent {
  stroke: var(--slidev-theme-primary, #5d8392);
  stroke-width: 3;
  stroke-opacity: 1;
}
.judge-schema rect.frame {
  fill: none;
  stroke-dasharray: 6 5;
  stroke-opacity: 0.45;
}
.judge-schema line,
.judge-schema path {
  stroke: currentColor;
  stroke-width: 1.5;
}
.judge-schema text {
  fill: currentColor;
  text-anchor: middle;
}
.judge-schema .title {
  font-size: 17px;
  font-weight: 700;
}
.judge-schema .sub {
  font-size: 13px;
  opacity: 0.75;
}
.judge-schema .legend {
  font-size: 12px;
  letter-spacing: 0.15em;
  opacity: 0.6;
}
.judge-schema .start {
  text-anchor: start;
}
</style>
