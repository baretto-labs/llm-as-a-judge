<!--
  Progress as a rubric: one box per slide, ticked in red once graded, the current one circled.
  Hidden on the cover.
-->
<script setup lang="ts">
import { useNav } from '@slidev/client'

const { currentPage, total, currentLayout } = useNav()
</script>

<template>
  <div v-if="currentLayout !== 'cover'" class="bareme">
    <span
      v-for="n in total"
      :key="n"
      class="case"
      :class="{ cochee: n < currentPage, courante: n === currentPage }"
    />
    <span class="numero">{{ String(currentPage).padStart(2, '0') }} / {{ String(total).padStart(2, '0') }}</span>
  </div>
</template>

<style scoped>
.bareme {
  position: absolute;
  right: 1.5rem;
  bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.case {
  width: 0.55rem;
  height: 0.55rem;
  border: 1.5px solid rgba(28, 37, 65, 0.35);
  border-radius: 1px;
  position: relative;
}

.case.cochee::after {
  content: '';
  position: absolute;
  left: 0.12rem;
  top: -0.12rem;
  width: 0.22rem;
  height: 0.45rem;
  border: solid var(--rouge);
  border-width: 0 2px 2px 0;
  transform: rotate(40deg);
}

.case.courante {
  border-color: var(--rouge);
  box-shadow: 0 0 0 2px rgba(214, 40, 57, 0.25);
}

.numero {
  margin-left: 0.6rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: rgba(28, 37, 65, 0.55);
}
</style>
