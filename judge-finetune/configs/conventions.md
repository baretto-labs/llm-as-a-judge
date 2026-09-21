CONVENTIONS DE NOTATION

1. Verdict. verdict = "PASS" si et seulement si tous les contrôles de checks valent true. Aucune exception.

2. Consignes obligatoires contre préférences.
   - Consigne formulée comme préférence (« si possible », « si tu as le temps ») non suivie : contrôle à
     true, écart mentionné dans le <thinking>.
   - Sortie verbeuse mais correcte : jamais pénalisée pour sa seule longueur.
   - Exigence explicite et vérifiable non respectée (signature, version, dépendance interdite, format,
     périmètre) : contrôle à false.

3. Contrôle dédié. Toutes les consignes obligatoires de la requête sont respectées, à l'exception de
   celles couvertes par un contrôle dédié, qui les évalue séparément.

4. Portée de citations_exactes (RAG_FAITHFULNESS). citations_exactes ne sanctionne que la déformation de
   matériau réellement puisé dans le contexte. Lorsqu'une sortie invente de bout en bout sans rien citer
   ni paraphraser du contexte, il n'existe aucune citation à déformer et le contrôle vaut vrai par
   vacuité — le rejet est alors porté par affirmations_etayees et absence_invention, et le verdict reste
   FAIL puisque PASS exige tous les contrôles.
