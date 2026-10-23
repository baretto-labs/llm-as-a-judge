<!-- Coupé le 2026-10-21 : diapos 12–13 (biais RAG, littérature). Recollable tel quel dans slides.md. -->
---
transition: fade-out
---
# Quelques biais de la pipeline RAG

Ce que la littérature décrit.

<div class="fiches">
<div v-click class="fiche">
  <span class="etiquette">01 · composants</span>
  <strong>Les biais s'additionnent</strong>
  <p>Le LLM, les embeddings et le corpus ont chacun les leurs.</p>
  <span class="annotation">trois correcteurs, trois manies</span>
</div>
<div v-click class="fiche">
  <span class="etiquette">02 · position</span>
  <strong>Le milieu est moins lu</strong>
  <p>La preuve au milieu d'un long contexte pèse moins. Courbe en U.</p>
  <span class="annotation">la copie du milieu de la pile</span>
</div>
<div v-click class="fiche">
  <span class="etiquette">03 · autorité</span>
  <strong>Il croit la source, pas les faits</strong>
  <p>Le modèle fait trop confiance à l'invite ou à une source.</p>
  <span class="annotation">« c'est le prof qui l'a dit »</span>
</div>
<div v-click class="fiche">
  <span class="etiquette">04 · injection</span>
  <strong>Des passages vrais, mais orientés</strong>
  <p>Glissés dans la base, ils évincent les autres points de vue.</p>
  <span class="annotation">le corrigé truqué</span>
</div>
</div>

<!--
Une fiche par clic. Ce que la littérature décrit ; mes propres mesures viennent après.

Texte d'origine (EN), si la question vient :
- Component Bias Conflict: mismatches between the individual biases of the LLM, the embedding
  model, and the external corpus (often following a linear scaling relationship).
- Position Bias: in multimodal or long-context RAG, models show a U-shaped accuracy and
  attention curve where evidence placement heavily sways the outcome.
- Authority Bias: LLMs tend to over-trust user prompts or specific sources over factual or
  counter-stereotypical evidence.
- Bias Injection Attacks: adversarial "knowledge poisoning" where factually true but
  semantically slanted passages are slipped into vector databases to crowd out opposing views.
-->

---
transition: fade-out
---
# Et quelques parades

Ce que la littérature propose.

<div class="fiches trois">
<div v-click class="fiche">
  <span class="etiquette">01 · embeddings</span>
  <strong>Régler les embeddings</strong>
  <p>Un réglage léger (PEFT), ou un biais inverse, pour calmer les conflits.</p>
  <span class="annotation">rééduquer le correcteur</span>
</div>
<div v-click class="fiche">
  <span class="etiquette">02 · récupération</span>
  <strong>Récupérer équilibré</strong>
  <p>Des filtres attentifs aux biais, une base à plusieurs points de vue.</p>
  <span class="annotation">plusieurs manuels, pas un</span>
</div>
<div v-click class="fiche">
  <span class="etiquette">03 · ordre</span>
  <strong>Remettre de l'ordre</strong>
  <p>Mélanger ou structurer les extraits, contre le biais de position.</p>
  <span class="annotation">mélanger la pile</span>
</div>
</div>

<!--
Une fiche par clic. La 3 annonce une parade que j'applique : le mélange des extraits.

Texte d'origine (EN), si la question vient :
- Embedder Control & Fine-Tuning: applying light parameter-efficient fine-tuning (such as PEFT)
  or reverse-biasing the embedding model to neutralize component conflicts.
- Fairness-Sensitive Retrieval: using bias-aware retrieval filters and multi-perspective
  knowledge bases to ensure balanced representation of protected groups.
- Evidence Reordering: shuffling or structuring retrieved chunks to counteract position bias
  in the decoder context window.

Des approches sont déjà connues pour limiter les biais des pipelines RAG, bon comme je n'ai qu'un temps limité, je passe rapidement dessus, pour retourner sur la construction du juge.
Mais on se rend vite compte qu'on n'est plus dans un monde déterministe quand on travaille avec les llms, et qu'il est nécessaire d'y penser quand on construit son juge d'évaluation
-->

