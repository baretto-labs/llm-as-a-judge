<!--
  Section divider: the talk as an exam paper in three exercises.
  Done exercises are ticked in green, the current one is circled, the next ones are faded.
  Usage: <Exercices :courant="2" />
-->
<script setup lang="ts">
defineProps<{ courant: number }>()

const exercices = ['Le principe', 'Mon juge', 'Mon RAG']
</script>

<template>
  <ol class="exercices">
    <li
      v-for="(titre, i) in exercices"
      :key="titre"
      :class="{ fait: i + 1 < courant, courant: i + 1 === courant, avenir: i + 1 > courant }"
    >
      <svg viewBox="0 0 40 32" class="coche" aria-hidden="true">
        <path v-if="i + 1 < courant" d="M4 18 L15 27 L36 4" />
      </svg>
      <span :class="{ entoure: i + 1 === courant }">
        <span class="numero">Exercice {{ i + 1 }}</span> · {{ titre }}
      </span>
    </li>
  </ol>
</template>

<style scoped>
.exercices {
  list-style: none;
  padding: 0;
  margin: 0 auto;
  display: inline-flex;
  flex-direction: column;
  gap: 1.6rem;
  text-align: left;
}

li {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--encre);
}

.numero {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.1rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--encre-douce);
  vertical-align: middle;
}

.avenir { opacity: 0.35; }
.fait { opacity: 0.6; }

.coche {
  width: 2.4rem;
  height: 2rem;
  flex: none;
}

.coche path {
  fill: none;
  stroke: var(--vert);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
