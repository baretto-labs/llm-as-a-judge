# Sources du talk « RAGots et Hallucinations »

Liste complète. La diapo 19 en affiche l'essentiel. Chaque entrée dit où elle sert dans le talk.

## Le code

- **OllamAssist** : https://github.com/baretto-labs/OllamAssist
- **Le banc et le juge** : https://github.com/baretto-labs/llm-as-a-judge

## Les affaires

- **Moffatt v. Air Canada**, 2024 BCCRT 149. https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html Le chatbot d'Air Canada, 650,88 $ CA (diapos 2, 3 et 18).
- **Mata v. Avianca**, S.D.N.Y., 22-cv-1461, juge P. Kevin Castel, 22 juin 2023. https://storage.courtlistener.com/recap/gov.uscourts.nysd.575368/gov.uscourts.nysd.575368.54.0_1.pdf Six décisions inventées par ChatGPT, 5 000 $ d'amende (diapo 5).

## Le juge

- Hamel Husain, *Using LLM-as-a-Judge For Evaluation*. https://hamel.dev/blog/posts/llm-judge/ (méthode de l'étalon, un expert, verdict PASS/FAIL).
- Lianmin Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS 2023 (Datasets and Benchmarks). https://arxiv.org/abs/2306.05685 (biais de position, de verbosité, d'auto-préférence ; diapo 10).
- Yukyung Lee et al., *CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists*, 2024. https://arxiv.org/abs/2403.18771 (questions oui/non plutôt qu'une échelle ; diapo 13).
- Jacob Cohen, *A Coefficient of Agreement for Nominal Scales*, Educational and Psychological Measurement 20(1):37-46, 1960. Le kappa (réponse en questions).
- Potsawee Manakul, Adian Liusie, Mark J. F. Gales, *SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models*, EMNLP 2023. https://arxiv.org/abs/2303.08896 (relancer le modèle avec un peu de hasard : là où les réponses divergent, il hésite ; diapo 17).

## Le jury

- Pat Verga et al., *Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models*, 2024. https://arxiv.org/abs/2404.18796 (pour : un panel de petits modèles de familles différentes bat un seul gros juge ; diapo 17 et questions).
- Kohli, *Nine Judges, Two Effective Votes*, mai 2026. https://arxiv.org/abs/2605.29800 (contre : 9 juges de 7 familles valent environ 2 votes indépendants, le meilleur juge seul égale ou bat le panel ; questions).
