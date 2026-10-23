<!--
  The closing picture: the cover said "Copie à corriger", this is the copy, corrected.
  Four rules to take home, ticked one per click in red pen, then the grader's remark
  (the loop: every shortcut led back to the gold set) and the stamp. Keep the rules in
  sync with the REX acts (slides 12–18).
-->
<template>
  <div class="copie">
    <div class="entete">
      <span>Nom : <b>mon juge</b></span>
      <span>Sujet : votre chatbot passe devant le juge</span>
    </div>

    <ol class="regles">
      <li v-for="(regle, i) in regles" :key="i" v-click class="regle">
        <svg viewBox="0 0 40 32" class="coche" aria-hidden="true">
          <path d="M4 18 L15 27 L36 4" />
        </svg>
        <span class="texte">{{ regle.texte }}</span>
        <span class="marge">{{ regle.marge }}</span>
      </li>
    </ol>

    <div v-click class="appreciation">
      <p class="annotation">Chaque raccourci m’a ramené à l’étalon.</p>
      <div class="tampon-final"><Tampon :angle="-9" taille="1.3rem">Copie corrigée</Tampon></div>
    </div>
  </div>
</template>

<script setup lang="ts">
const regles = [
  { texte: 'Écris tes 50 copies d’abord.', marge: 'personne ne le fera pour toi' },
  { texte: 'Écris ton barème.', marge: 'quatre phrases' },
  { texte: 'Vérifie ce que ton juge lit.', marge: 'pas ce que tu lui envoies' },
  { texte: 'Ne relis que les doutes.', marge: '12 au lieu de 50' },
]
</script>

<style scoped>
.copie {
  position: relative;
  width: 780px;
  margin: 0 auto;
  padding: 1.4rem 2.2rem 1.6rem 5.5rem;
  text-align: left;
  background:
    linear-gradient(90deg, transparent 3.6rem, var(--marge) 3.6rem, var(--marge) calc(3.6rem + 2px), transparent calc(3.6rem + 2px)),
    repeating-linear-gradient(to bottom, transparent 0 31px, var(--ligne-forte) 31px 32px),
    var(--papier-carte);
  box-shadow: 0 10px 28px rgba(28, 37, 65, 0.18);
  rotate: -1deg;
}

.entete {
  display: flex;
  justify-content: space-between;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  color: var(--encre-douce);
  border-bottom: 1px solid rgba(28, 37, 65, 0.2);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.regles {
  list-style: none;
  padding: 0;
  margin: 0;
  counter-reset: regle;
}

.regle {
  position: relative;
  display: flex;
  align-items: baseline;
  gap: 1rem;
  padding: 0.55rem 0;
  counter-increment: regle;
  transition: opacity 0.4s ease, translate 0.4s ease;
}

.regle.slidev-vclick-hidden { translate: 0 10px; }

.regle::before {
  content: counter(regle) '.';
  font-weight: 800;
  font-size: 1.5rem;
  color: var(--encre-douce);
}

.texte {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--encre);
}

.marge {
  margin-left: auto;
  font-family: 'Caveat', cursive;
  font-size: 1.35rem;
  color: var(--rouge);
  rotate: -2deg;
}

/* The red tick sits in the margin and is drawn as the line appears */
.coche {
  position: absolute;
  left: -4.6rem;
  top: 0.45rem;
  width: 2.4rem;
  height: 2rem;
}

.coche path {
  fill: none;
  stroke: var(--rouge);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 60;
  stroke-dashoffset: 60;
}

.regle:not(.slidev-vclick-hidden) .coche path {
  animation: trait-coche 0.5s 0.2s ease-out forwards;
}

@keyframes trait-coche {
  to { stroke-dashoffset: 0; }
}

.appreciation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1.1rem;
  transition: opacity 0.4s ease;
}

.appreciation .annotation {
  font-size: 1.7rem;
  line-height: 1.1;
  white-space: nowrap;
  margin: 0;
}

.appreciation { position: static; }

.tampon-final {
  position: absolute;
  top: -1.6rem;
  right: -1.4rem;
  rotate: 4deg;
  white-space: nowrap;
}

.appreciation:not(.slidev-vclick-hidden) .tampon-final {
  animation: tampon-cc 0.45s 0.3s cubic-bezier(0.3, 1.6, 0.5, 1) both;
}

@keyframes tampon-cc {
  from { opacity: 0; scale: 1.8; }
  to   { opacity: 1; scale: 1; }
}
</style>
