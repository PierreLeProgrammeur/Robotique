import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    # Fenêtre — rempli dynamiquement à l'init
    SCREEN_WIDTH: int  = 0
    SCREEN_HEIGHT: int = 0

    # Grille de sol
    GRID_CELL_SIZE: int = 8

    # Agents — général
    AGENT_RADIUS: float = 7.0
    VISION_RADIUS: float = 90.0
    VISION_ANGLE: float = math.pi

    # Virus
    VIRUS_SPEED: float = 55.0
    VIRUS_TURN_SPEED: float = 2.5
    VIRUS_RANDOM_BIAS: float = 0.6
    VIRUS_SPAWN_INTERVAL: float = 1.8
    VIRUS_SPAWN_BATCH: int = 2
    VIRUS_MAX: int = 120

    # Globules blancs
    N_WBC: int = 14
    WBC_SPEED: float = 75.0
    WBC_TURN_SPEED: float = 3.5

    # Forces Boids
    BOID_SEPARATION_RADIUS: float = 30.0
    BOID_W_SEPARATION: float = 1.8
    BOID_W_ALIGNMENT: float = 0.9
    BOID_W_COHESION: float = 0.7
    BOID_W_HUNT: float = 1.4
    BOID_W_AVOID_WALL: float = 2.0
    WALL_REPULSION_DIST: float = 40.0

    # Palette
    COLOR_BG: Tuple         = (210, 60, 60)
    COLOR_VIRUS: Tuple      = (10, 10, 10)
    COLOR_WBC: Tuple        = (245, 245, 245)
    COLOR_SOIL_VIRUS: Tuple = (96, 96, 96)
    COLOR_SOIL_WBC: Tuple   = (240, 240, 240)
    COLOR_UI_TEXT: Tuple    = (255, 255, 255)

    # Simulation
    FPS: int = 60
    COLLISION_KILL_DIST: float = 14.0

    # ── Accélération ──────────────────────────────────────────────────────
    SPEED_STEPS: tuple = (1.0, 1.5, 2.0)
    SPEED_STEP_IDX: int = 0

    # ── Règles de fin ─────────────────────────────────────────────────────
    # Les virus gagnent s'ils atteignent ce % du sol. 0.0 = désactivé.
    VIRUS_WIN_COVERAGE_PCT: float = 40.0

    # Les globules blancs gagnent si les virus n'ont pas gagné après ce délai
    # (en secondes). 0.0 = désactivé.
    WBC_WIN_TIME: float = 120.0


CFG = Config()