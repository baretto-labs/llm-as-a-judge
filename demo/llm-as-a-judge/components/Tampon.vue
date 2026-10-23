<!--
  A rubber stamp, for verdicts: <Tampon>PASS</Tampon>, <Tampon couleur="vert">PASS</Tampon>.
  The ink texture comes from an SVG turbulence mask, so the stamp looks pressed, not printed.
-->
<script setup lang="ts">
withDefaults(defineProps<{ couleur?: 'rouge' | 'vert' | 'encre', angle?: number, taille?: string }>(), {
  couleur: 'rouge',
  angle: -8,
  taille: '1.6rem',
})
</script>

<template>
  <span class="tampon" :class="couleur" :style="{ transform: `rotate(${angle}deg)` }">
    <svg width="0" height="0" class="absolute">
      <filter id="tampon-encre">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" />
        <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.3 1.45" />
        <feComposite in="SourceGraphic" operator="in" />
      </filter>
    </svg>
    <span class="cadre" :style="{ fontSize: taille }"><slot /></span>
  </span>
</template>

<style scoped>
.tampon {
  display: inline-block;
  filter: url(#tampon-encre);
  mix-blend-mode: multiply;
}

.cadre {
  display: inline-block;
  padding: 0.25em 0.7em;
  border: 0.18em solid currentColor;
  outline: 0.07em solid currentColor;
  outline-offset: 0.18em;
  border-radius: 0.2em;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  line-height: 1;
}

.rouge { color: var(--rouge); }
.vert  { color: var(--vert); }
.encre { color: var(--encre); }
</style>
