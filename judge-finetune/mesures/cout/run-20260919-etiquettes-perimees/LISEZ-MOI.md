# Entraînement du 2026-09-19 — conservé, mais invalidé

Cet entraînement a été mené sur le corpus **avant** la correction de huit étiquettes
`respect_consignes`, dont **six dans le jeu `train`**. L'adaptateur produit a donc appris des étiquettes
que nous savons aujourd'hui fausses : il a été écarté dans `adapters/perimes/`, et aucun de ses points de
contrôle ne sera benchmarké.

**Ce qui reste valide et citable :**

- durée dérivée **76 min** pour 400 itérations, soit 11,4 s/itération ;
- pic mémoire **11,32 Go** selon les rapports de mlx-lm ;
- 169 501 jetons vus, adaptateur de 43,8 Mo, LoRA sur 16 couches, 11,5 M paramètres entraînables ;
- **la courbe de validation qui se retourne à l'itération 250** — minimum 1,104, puis 1,207 / 1,201 /
  1,183 — pendant que la perte d'entraînement descend à 0,587.

Ces chiffres décrivent le **coût** et le **comportement d'apprentissage** d'un QLoRA 14B sur 150 exemples,
et ni l'un ni l'autre ne dépend de la justesse des huit étiquettes corrigées. Le surapprentissage observé
tient à la taille du jeu, pas à son contenu.

**Ce qui n'est pas valide :** toute mesure de qualité de jugement issue de cet adaptateur.

Contient aussi `train-14b-duree-methode.json`, la méthode de reconstruction de durée déclarée avant la
mise en veille volontaire de la machine — la durée horloge de 823 min englobait la nuit et était
inexploitable.
