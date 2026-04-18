# TP Robotique – Jeu de survie avec IA

##  Description

Ce projet est un jeu de survie développé en Python avec **Pygame**.
Un robot mobile évolue dans une arène et affronte des vagues d’ennemis.

Le robot est contrôlé par une **intelligence artificielle autonome** capable de :

* esquiver des projectiles,
* fuir les situations dangereuses,
* récupérer des ressources,
* attaquer des cibles,
* capturer des zones.

---

## 🎯 Objectifs du projet

* Implémenter une architecture orientée objet
* Simuler un robot mobile avec contraintes physiques
* Concevoir une IA décisionnelle réactive
* Gérer un environnement dynamique (ennemis, projectiles, items)

---

## ▶️ Lancer le projet

### Prérequis

* Python 3.13
* pygame

### Installation

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install pygame
```

### Exécution

```bash
python main_pygame_ia.py
```

⚠️ Lancer depuis le dossier `tp_robotique`

---

### Possibilité de jouer manuellement

```bash
python main_pygame.py
```

Commande : ZQSD pour les déplacements, ESPACE pour tirer, 123 pour selectionner une amélioration

## 🏗️ Architecture du projet

Le projet suit une architecture inspirée du **modèle MVC** :

### Model (données et logique)

* `environnement.py` → gestion du jeu
* `robot_mobile.py` → robot
* `ennemi.py`, `boss.py`, `item.py` → entités

### View (affichage)

* `vue_pygame.py` → rendu graphique

### Controller (décision)

* `controleur_ia.py` → intelligence artificielle
* `controleur.py` → base abstraite

---

## 🔄 Boucle du jeu

À chaque frame :

1. Lecture des événements
2. L’IA décide (`lire_commande`)
3. Le robot exécute la commande
4. L’environnement se met à jour
5. L’écran est rafraîchi

---

## 🤖 Intelligence Artificielle

### 🔥 Priorités de décision

1. Esquive des projectiles (priorité maximale)
2. Fuite si trop d’ennemis
3. Récupération d’items
4. Attaque des cibles

---

### ⚡ Esquive prédictive

L’IA :

* détecte les projectiles proches
* prédit leur trajectoire
* calcule une direction d’évitement

👉 Basée sur :

* distance
* temps avant collision
* angle d’arrivée

---

### 🧭 Navigation

L’IA combine :

* **Navigation réactive**

  * esquive
  * fuite

* **Navigation autonome**

  * aller vers un item
  * attaquer
  * capturer une zone

---

## 🧠 Algorithmes utilisés

Le projet s’appuie sur des concepts classiques :

* Champs de potentiel (éviter ennemis / projectiles)
* Subsumption architecture (priorités)
* Steering behaviors (déplacement vers cible)
* Prédiction de collision (Time-To-Collision)

---

## ⚙️ Paramètres importants

### 🔥 Dans `controleur_ia.py`

```python
RAYON_DANGER_PROJ_BASE = 6.0
TEMPS_REACTION_PROJ_BASE = 3.5
SEUIL_ESQUIVE_BASE = 0.10
PREDICTION_STEPS = 12
```

👉 Influence :

* détection des projectiles
* réactivité de l’IA

---

### 🚀 Dans `main_pygame_ia.py`

```python
ControleurIA(
    v_max=3.4,
    omega_max=4.4,
    seuil_fuite=2.0,
    rayon_influence=4.2,
    distance_attraction_item=3.5
)
```

👉 Influence :

* vitesse du robot
* comportement global

---

## 📡 Capteurs (simulation)

Le robot n’utilise pas de capteurs physiques.

👉 Il utilise des **capteurs virtuels** :

* accès direct à l’environnement
* détection des ennemis et projectiles
* calcul de distances

On peut assimiler cela à :

* un radar circulaire logiciel
* enrichi par une prédiction de trajectoire

---

## 🎥 Caméra

La caméra est centrée sur le robot.

👉 Technique utilisée :

```
coord écran = coord monde - position robot + centre écran
```

---

## 🧬 Programmation orientée objet

### Héritage

* `ControleurIA` hérite de `Controleur`
* différentes implémentations de contrôleurs

### Polymorphisme

* méthode `lire_commande()` utilisée de manière uniforme
* comportement différent selon le type de contrôleur

---

## 💡 Points forts

* IA avec hiérarchie de décisions
* esquive prédictive
* architecture claire (MVC)
* simulation réaliste du mouvement
* système de jeu complet

---

## 🚀 Améliorations possibles

* ajouter un champ de vision (simulation capteur réel)
* améliorer le comportement du boss
* ajouter de nouveaux types d’ennemis
* optimiser les collisions
* réaliser un log des amélioration utilisé lors d'une simulation pour voir les performances

---

## 👨‍💻 Auteurs

Projet réalisé dans le cadre d’un TP de robotique.

Axel et Alexandre
