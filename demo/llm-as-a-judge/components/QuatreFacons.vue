<!--
  The four ways to use an LLM as a judge, redrawn after the DataCamp figure
  (datacamp.com/fr/tutorial/llm-as-a-judge-rag) in the "copie corrigée" style.
  One card per click; once a card is in, its verdict lands like a stamp.
  Click 5 circles the fourth card: binary checks are what my judge does.
-->
<template>
  <svg viewBox="0 0 900 455" class="quatre-facons w-full" role="img"
       aria-label="Quatre façons de juger : score direct, comparaison par paires, avec référence, classification binaire">
    <defs>
      <marker id="qf-arrow" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10z" fill="currentColor" />
      </marker>
    </defs>

    <!-- 1 · direct scoring -->
    <g v-click class="carte-qf" transform="translate(10 10)">
      <rect width="430" height="200" rx="10" class="fond" />
      <path d="M0 10 a10 10 0 0 1 10 -10 h410 a10 10 0 0 1 10 10 v26 h-430z" class="bandeau jaune" />
      <text x="14" y="25" class="nom">1 · Score direct</text>
      <text x="416" y="26" class="question">« c'est bien ? »</text>
      <rect x="20" y="62" width="125" height="48" rx="6" />
      <text x="82" y="91" class="boite">Réponse</text>
      <line x1="145" y1="86" x2="181" y2="86" marker-end="url(#qf-arrow)" />
      <rect x="185" y="64" width="80" height="44" rx="6" class="juge" />
      <text x="225" y="91" class="juge-txt">Juge</text>
      <line x1="265" y1="86" x2="301" y2="86" marker-end="url(#qf-arrow)" />
      <g class="sortie">
        <circle cx="340" cy="86" r="30" class="note" />
        <text x="340" y="93" class="verdict rouge">4/5</text>
      </g>
      <text x="20" y="158" class="pied"><tspan class="cle">quand</tspan> suivre la qualité dans le temps</text>
      <text x="20" y="180" class="pied"><tspan class="cle attention">attention</tspan> la note dérive, tout finit à 3 ou 4</text>
    </g>

    <!-- 2 · pairwise comparison -->
    <g v-click class="carte-qf" transform="translate(460 10)">
      <rect width="430" height="200" rx="10" class="fond" />
      <path d="M0 10 a10 10 0 0 1 10 -10 h410 a10 10 0 0 1 10 10 v26 h-430z" class="bandeau vert" />
      <text x="14" y="25" class="nom">2 · Comparaison par paires</text>
      <text x="416" y="26" class="question">« lequel est mieux ? »</text>
      <rect x="20" y="50" width="125" height="34" rx="6" />
      <text x="82" y="72" class="boite">Réponse A</text>
      <rect x="20" y="92" width="125" height="34" rx="6" />
      <text x="82" y="114" class="boite">Réponse B</text>
      <path d="M145 67 h14 v42 h-14 M159 88 h22" fill="none" marker-end="url(#qf-arrow)" />
      <rect x="185" y="66" width="80" height="44" rx="6" class="juge" />
      <text x="225" y="93" class="juge-txt">Juge</text>
      <line x1="265" y1="88" x2="291" y2="88" marker-end="url(#qf-arrow)" />
      <g class="sortie">
        <rect x="295" y="68" width="118" height="40" rx="6" class="verdict-cadre" />
        <text x="354" y="94" class="verdict">B gagne ✓</text>
      </g>
      <text x="20" y="158" class="pied"><tspan class="cle">quand</tspan> A/B de prompts ou de modèles</text>
      <text x="20" y="180" class="pied"><tspan class="cle attention">attention</tspan> deux fois plus d'appels, biais de position</text>
    </g>

    <!-- 3 · reference-based -->
    <g v-click class="carte-qf" transform="translate(10 222)">
      <rect width="430" height="200" rx="10" class="fond" />
      <path d="M0 10 a10 10 0 0 1 10 -10 h410 a10 10 0 0 1 10 10 v26 h-430z" class="bandeau bleu" />
      <text x="14" y="25" class="nom">3 · Avec référence</text>
      <text x="416" y="26" class="question">« proche du corrigé ? »</text>
      <rect x="20" y="50" width="125" height="34" rx="6" />
      <text x="82" y="72" class="boite">Corrigé type</text>
      <rect x="20" y="92" width="125" height="34" rx="6" />
      <text x="82" y="114" class="boite">Réponse</text>
      <path d="M145 67 h14 v42 h-14 M159 88 h22" fill="none" marker-end="url(#qf-arrow)" />
      <rect x="185" y="66" width="80" height="44" rx="6" class="juge" />
      <text x="225" y="93" class="juge-txt">Juge</text>
      <line x1="265" y1="88" x2="301" y2="88" marker-end="url(#qf-arrow)" />
      <g class="sortie">
        <rect x="305" y="64" width="100" height="48" rx="6" class="verdict-cadre" />
        <text x="355" y="81" class="petit">accord</text>
        <text x="355" y="103" class="verdict">82 %</text>
      </g>
      <text x="20" y="158" class="pied"><tspan class="cle">quand</tspan> Q&amp;R factuelles, vérité terrain connue</text>
      <text x="20" y="180" class="pied"><tspan class="cle attention">attention</tspan> punit une bonne réponse dite autrement</text>
    </g>

    <!-- 4 · binary classification -->
    <g v-click class="carte-qf" transform="translate(460 222)">
      <rect width="430" height="200" rx="10" class="fond" />
      <path d="M0 10 a10 10 0 0 1 10 -10 h410 a10 10 0 0 1 10 10 v26 h-430z" class="bandeau rose" />
      <text x="14" y="25" class="nom">4 · Classification</text>
      <text x="416" y="26" class="question">« oui ou non ? »</text>
      <rect x="20" y="62" width="125" height="48" rx="6" />
      <text x="82" y="82" class="boite">Réponse</text>
      <text x="82" y="100" class="petit">+ un critère</text>
      <line x1="145" y1="86" x2="181" y2="86" marker-end="url(#qf-arrow)" />
      <rect x="185" y="64" width="80" height="44" rx="6" class="juge" />
      <text x="225" y="91" class="juge-txt">Juge</text>
      <line x1="265" y1="78" x2="301" y2="62" marker-end="url(#qf-arrow)" />
      <line x1="265" y1="94" x2="301" y2="110" marker-end="url(#qf-arrow)" />
      <g class="sortie">
        <rect x="305" y="44" width="96" height="34" rx="4" class="tampon-qf vert" transform="rotate(-4 353 61)" />
        <text x="353" y="67" class="verdict vert" transform="rotate(-4 353 61)">PASS</text>
        <rect x="305" y="94" width="96" height="34" rx="4" class="tampon-qf rouge" transform="rotate(3 353 111)" />
        <text x="353" y="117" class="verdict rouge" transform="rotate(3 353 111)">FAIL</text>
      </g>
      <text x="20" y="158" class="pied"><tspan class="cle">quand</tspan> prod, conformité, « fidèle au contexte ? »</text>
      <text x="20" y="180" class="pied"><tspan class="cle attention">attention</tspan> perd la nuance des cas limites</text>
    </g>

    <!-- 5 · the one my judge uses -->
    <g v-click class="mien">
      <path d="M452 236 C 470 222, 880 220, 895 240 C 905 300, 902 400, 890 428 C 860 440, 480 440, 458 428 C 446 380, 446 280, 452 236z"
            class="entoure" />
      <text x="880" y="450" class="annotation-qf">↑ mon juge : trois checks oui / non</text>
    </g>
  </svg>
</template>

<style scoped>
.quatre-facons {
  max-height: 390px;
  color: var(--encre);
}

/* Cards slide up as they appear; the verdict lands a beat later */
.carte-qf,
.mien {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.carte-qf.slidev-vclick-hidden {
  translate: 0 12px;
}
.carte-qf:not(.slidev-vclick-hidden) .sortie {
  transform-box: fill-box;
  transform-origin: center;
  animation: tampon-qf 0.45s 0.35s cubic-bezier(0.3, 1.6, 0.5, 1) both;
}
@keyframes tampon-qf {
  from { opacity: 0; transform: scale(1.8) rotate(-12deg); }
  to   { opacity: 1; transform: scale(1) rotate(0); }
}
.mien:not(.slidev-vclick-hidden) .entoure {
  stroke-dasharray: 1600;
  animation: trait-qf 0.8s ease-out both;
}
@keyframes trait-qf {
  from { stroke-dashoffset: 1600; }
  to   { stroke-dashoffset: 0; }
}

rect {
  fill: var(--papier-carte);
  stroke: currentColor;
  stroke-width: 1.3;
  stroke-opacity: 0.55;
}
rect.fond {
  stroke-width: 2;
  stroke-opacity: 0.85;
  filter: drop-shadow(0 3px 6px rgba(28, 37, 65, 0.12));
}
.bandeau { stroke: none; }
.bandeau.jaune { fill: rgba(255, 226, 60, 0.35); }
.bandeau.vert  { fill: rgba(47, 125, 79, 0.16); }
.bandeau.bleu  { fill: rgba(120, 150, 205, 0.22); }
.bandeau.rose  { fill: rgba(214, 40, 57, 0.13); }

rect.juge { fill: var(--encre); stroke: none; }
rect.verdict-cadre { stroke-width: 2; stroke-opacity: 0.9; }
rect.tampon-qf { fill: none; stroke-width: 2.5; stroke-opacity: 1; }
rect.tampon-qf.vert  { stroke: var(--vert); }
rect.tampon-qf.rouge { stroke: var(--rouge); }
circle.note {
  fill: var(--papier-carte);
  stroke: var(--rouge);
  stroke-width: 2.5;
}

line, path {
  stroke: currentColor;
  stroke-width: 1.5;
}
.entoure {
  fill: none;
  stroke: var(--rouge);
  stroke-width: 3;
  stroke-linecap: round;
}

text { fill: currentColor; text-anchor: middle; }
.nom { text-anchor: start; font-size: 17px; font-weight: 800; }
.question {
  text-anchor: end;
  font-family: 'Caveat', cursive;
  font-size: 19px;
  fill: var(--encre-douce);
}
.boite { font-size: 14px; font-weight: 600; }
.petit { font-size: 12px; fill: var(--encre-douce); }
.juge-txt { font-size: 15px; font-weight: 700; fill: var(--papier); }
.verdict { font-size: 18px; font-weight: 800; letter-spacing: 0.04em; }
.verdict.rouge { fill: var(--rouge); }
.verdict.vert  { fill: var(--vert); }
.pied { text-anchor: start; font-size: 13.5px; }
.cle {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  fill: var(--encre-douce);
}
.cle.attention { fill: var(--rouge); }
.annotation-qf {
  text-anchor: end;
  font-family: 'Caveat', cursive;
  font-size: 22px;
  fill: var(--rouge);
}
</style>
