# Expérience d'Enchères Multi-Zones

Projet développé avec le framework oTree.  
Il implémente une expérience d'économie comportementale composée de deux parties distinctes :

1. une enchère de vente
2. une mesure de l'aversion au risque.

## 🛠 Structure de l'Expérience

### Partie 1 : Enchères de Vendeurs

Dans cette partie, les participants agissent en tant que vendeurs répartis dans deux zones géographiques distinctes.  

- Affectation des zones : Les joueurs sont répartis aléatoirement entre la Zone 1 (3 joueurs) et la Zone 2 (2 joueurs) au
sein de groupes de 5.  
- Mécanisme d'achat : Le programme informatique (l'Acheteur) sélectionne la combinaison d'offres qui maximise la valeur
totale créée par rapport au coût d'achat (ratio $W$), sous contrainte budgétaire.
- Traitements : Combinatoire (menus par lots), Unitaire (prix fixe par unité) et Base.
- - Paiement : 9 périodes sur 12 sont tirées au sort (échantillonnage sans remise) pour constituer le gain de cette partie.

### Partie 2 : Bomb Risk Elicitation

Une implémentation visuelle du BRET pour mesurer l'aversion au risque des participants.

- Tâche : Le participant choisit le nombre de boîtes à ouvrir (sur 100) via un curseur interactif.
- - Risque : Une bombe est placée aléatoirement dans l'une des boîtes. Si elle est ouverte, le gain du tour est nul.
- - Design : Interface moderne avec mise à jour dynamique de la grille et retour visuel immédiat.

## 🚀 Installation
- Python 3.9+ installé.
- Clonez le dépôt : `clone https://github.com/votre-compte/votre-depot.git`
- Installez oTree : `pip install otree`
- Lancez le serveur local : `otree devserver`

## 📊 Export des données

L'application inclut une fonction de `custom_export` située dans le `__init__.py` de la partie 1. Elle
génère un fichier CSV au format "long" contenant :
- Les décisions de vente, les coûts et les prix par round.
- Le détail des périodes tirées au sort pour le paiement.
- Le nombre de boîtes ouvertes dans la tâche BRET.
- Les erreurs commises lors des tests de compréhension.
- Les gains obtenus dans chaque partie.
- Les données socio-démographiques des participants.

