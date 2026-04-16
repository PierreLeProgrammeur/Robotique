# Les méchants virus 
### Simulation multi-agents d'un système immunitaire

> Projet fil rouge - Cours de Robotique  
> Alban Stievenard - Pierre Vittu

---

## Présentation

Ce projet simule la dynamique d'un **système immunitaire** confronté à une invasion virale. Deux populations d'agents autonomes s'affrontent en temps réel dans un environnement partagé : des **virus** qui cherchent à contaminer le sol, et des **globules blancs** qui cherchent à le guérir.

La simulation ne script aucun comportement global. Chaque agent prend ses décisions localement à partir de ce qu'il perçoit dans son champ de vision. Le résultat (contamination ou guérison) **émerge** de ces interactions locales.

---

## Démonstration

<img width="1092" height="615" alt="simulation_robotique" src="https://github.com/user-attachments/assets/9a39ac4e-1272-428b-b7a0-97a96b993b7a" />

> Fond rouge = sol sain <br> Zones sombres = sol contaminé <br> Points noirs = virus <br> Points blancs = globules blancs

---

## Fonctionnalités

### Agents

| Agent | Comportement                                                                                                                                                                                         |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Virus** | Se dirige vers les cases saines pour les contaminer. Priorise les cases saintes à portée sinon continue sa lancée. Spawn continu depuis les bords.                                                   |
| **Globule blanc** | Priorité 1 : chasse le virus visible le plus proche. Priorité 2 : se dirige vers le sol contaminé le plus proche pour le guérir. Priorité 3 : algorithme de Boids pour couvrir le terrain en groupe. |

### Environnement
- Grille 2D modélisant l'état du sol cellule par cellule (`SOIL_EMPTY` / `SOIL_VIRUS`)
- Chaque agent peint la cellule sous lui à chaque frame
- La couleur est "permanente", elle ne s'efface que si l'agent adverse passe dessus
- Rendu différentiel : seules les cellules modifiées sont redessinées

### Algorithme de Boids
Les globules blancs implémentent les trois forces classiques de Craig Reynolds (1987) :
- **Séparation** : éviter les congénères trop proches
- **Alignement** : s'aligner sur la direction moyenne du voisinage
- **Cohésion** : se rapprocher du centre de masse du groupe

Ces forces sont combinées avec une force de **chasse** (vers les virus ou le sol contaminé) et une force de **répulsion des bords**, chacune pondérée par des paramètres configurables.

### Système de perception
Chaque agent dispose d'un **cône de vision** (rayon + demi-angle configurable). La détection du sol adverse utilise un algorithme de parcours de grille qui retourne la cellule adverse **la plus proche** dans le cône et non le centroïde moyen, ce qui garantit un comportement stable même en cas de contamination dense.

### Règles de fin
- Les virus gagnent s'ils atteignent un seuil de couverture du sol configurable (défaut : 40 %)
- Les globules blancs gagnent s'ils tiennent pendant un temps configurable (défaut : 120 s)
- Ces règles sont modifiables dans le fichier config.json
### Logging
À chaque fin de partie (victoire, défaite ou abandon), une ligne est ajoutée dans un fichier de log CSV contenant l'ensemble des paramètres de la simulation et les résultats. Ces données permettent d'étudier l'influence de chaque paramètre sur l'issue de la partie.

### Accélération
La simulation peut être accélérée (×1 / ×1.5 / ×2) via les touches `↑` et `↓`, ce qui facilite les runs de collecte de données. <br> *Peut impacter la simulation et réduire les performances.*

---

## Architecture

```
project/
├── main.py                        
├── config.py                      
├── logger.py
├── utils.py                       
├── logs/
│   ├── runs.csv
├── agents/
│   ├── agent.py                   
│   ├── virus.py                   
│   └── globule_blanc.py           
├── environment/
│   └── environnement.py           
└── core/
    └── simulation.py              
```

### Principes POO appliqués
- **Héritage** : `Virus` et `GlobuleBlanc` héritent de `Agent` (classe abstraite)
- **Polymorphisme** : `decide()`, `paint_soil()` et `render()` sont abstraites et surchargées
- **Encapsulation** : chaque agent gère son propre état interne, la simulation n'accède qu'à l'interface publique
- **Séparation des responsabilités** : `Environnement` ne connaît pas les agents, `Agent` ne connaît pas `Simulation`
- **Imports circulaires évités** : utilisation de `TYPE_CHECKING` pour les annotations

---

## Installation

**Prérequis :** Python 3.10+

```bash
pip install pygame numpy
python project/main.py
```

---

## Contrôles

| Touche | Action                             |
|---|------------------------------------|
| `ESPACE` | Pause / Reprendre                  |
| `↑` / `↓` | Accélérer / Ralentir la simulation |
| `R` | Recommencer                        |
| `ESC` | Quitter                            |

---

## Paramètres configurables

Tous les paramètres par défaut sont regroupés dans `config.py` et modifiables arbitrairement dans config.json :

| Paramètre | Description | Défaut |
|---|---|---|
| `VIRUS_SPEED` | Vitesse des virus | 55 px/s |
| `VIRUS_MAX` | Plafond de virus simultanés | 120 |
| `VIRUS_SPAWN_INTERVAL` | Intervalle entre vagues de spawn | 1.8 s |
| `N_WBC` | Nombre de globules blancs | 14 |
| `WBC_SPEED` | Vitesse des globules blancs | 75 px/s |
| `VISION_RADIUS` | Rayon du cône de vision | 90 px |
| `BOID_W_SEPARATION` | Poids de la force de séparation | 1.8 |
| `BOID_W_ALIGNMENT` | Poids de la force d'alignement | 0.9 |
| `BOID_W_COHESION` | Poids de la force de cohésion | 0.7 |
| `VIRUS_WIN_COVERAGE_PCT` | % sol pour victoire virus | 40 % |
| `WBC_WIN_TIME` | Durée pour victoire globules | 120 s |

---

## Références

- Reynolds, C. W. (1987). *Flocks, herds and schools: A distributed behavioral model.* SIGGRAPH Computer Graphics.
- Pygame documentation : https://www.pygame.org/docs/
