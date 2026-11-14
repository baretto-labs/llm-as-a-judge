# Runs non reproductibles — mélange non graîné (2026-09-23)

Deux scénarios, `hybrid|hybrid-graph` puis `hybrid|hybrid`, mesurés avant correction.

`RagContextJudge.judge()` mélangeait les extraits **sans graine**, et la troncature à 6000
caractères intervient après le mélange : selon le tirage, ce ne sont pas les mêmes extraits qui
survivent. Conséquence — `hintCoverage`, qui est une fonction pure du contexte et des indices,
différait sur **21 questions sur 60** côté Lucene alors que la récupération était identique au bit
près. Les 21 cas sont **tous** sur des contextes longs, aucun sur un contexte court : la signature
du mécanisme.

Ces chiffres sont donc **un tirage, pas une mesure** : Lucene 55,9 % contre Neo4j 23,7 % sur le
premier scénario, 43,3 % contre 22,0 % sur le second, alors que le bras Lucene était configuré à
l'identique dans les deux.

**Ce qu'ils gardent de valable** : 12 verdicts sur 60, par stratégie, basculent à `hintCoverage`
identique — contenu inchangé, ordre seul modifié. C'est une mesure du **biais de position** du
juge, à température 0, et elle reste exploitable.
