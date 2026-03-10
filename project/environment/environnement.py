from typing import Optional, Tuple

import numpy as np
import pygame

from config import CFG
from utils import point_in_cone

# États discrets des cellules de sol
SOIL_EMPTY = 0
SOIL_VIRUS = 1
SOIL_WBC   = 2


class Environnement:
    """
    Grille 2D représentant l'état du sol.
    Chaque cellule stocke un état discret : SOIL_EMPTY / SOIL_VIRUS / SOIL_WBC.
    La couleur ne s'efface jamais d'elle-même : elle est écrasée uniquement
    quand un agent adverse passe sur la cellule.
    Rendu différentiel : seules les cellules modifiées sont redessinées.
    """

    def __init__(self, screen_w: int, screen_h: int, cell_size: int):
        self.cell_size = cell_size
        self.cols = screen_w // cell_size
        self.rows = screen_h // cell_size
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.grid = np.zeros((self.rows, self.cols), dtype=np.int8)
        self.surface = pygame.Surface((screen_w, screen_h))
        self.surface.fill(CFG.COLOR_BG)

        self._color_table = {
            SOIL_EMPTY: CFG.COLOR_BG,
            SOIL_VIRUS: CFG.COLOR_SOIL_VIRUS,
            SOIL_WBC:   CFG.COLOR_SOIL_WBC,
        }
        self._prev_grid = np.full_like(self.grid, -1)

    # ── Accès ──────────────────────────────────────────────────────────────

    def world_to_cell(self, x: float, y: float) -> Tuple[int, int]:
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        col = max(0, min(self.cols - 1, col))
        row = max(0, min(self.rows - 1, row))
        return row, col

    # ── Peinture ───────────────────────────────────────────────────────────

    def paint(self, x: float, y: float, state: int):
        row, col = self.world_to_cell(x, y)
        self.grid[row, col] = state

    def paint_radius(self, x: float, y: float, state: int, r_cells: int = 1):
        row0, col0 = self.world_to_cell(x, y)
        for dr in range(-r_cells, r_cells + 1):
            for dc in range(-r_cells, r_cells + 1):
                if dr * dr + dc * dc <= r_cells * r_cells:
                    r = max(0, min(self.rows - 1, row0 + dr))
                    c = max(0, min(self.cols - 1, col0 + dc))
                    self.grid[r, c] = state

    def reset(self):
        self.grid[:] = SOIL_EMPTY
        self._prev_grid[:] = -1
        self.surface.fill(CFG.COLOR_BG)

    # ── Perception ─────────────────────────────────────────────────────────

    def has_enemy_color_in_cone(self, origin: np.ndarray, theta: float,
                                 half_angle: float, radius: float,
                                 enemy_state: int) -> Optional[np.ndarray]:
        """
        Retourne le centroïde (position monde) des cellules avec `enemy_state`
        visibles dans le cône de vision, ou None si aucune.
        """
        r0, c0 = self.world_to_cell(origin[0], origin[1])
        margin = int(radius // self.cell_size) + 1
        r_min = max(0, r0 - margin)
        r_max = min(self.rows, r0 + margin + 1)
        c_min = max(0, c0 - margin)
        c_max = min(self.cols, c0 + margin + 1)

        positions = []
        for r in range(r_min, r_max):
            for c in range(c_min, c_max):
                if self.grid[r, c] != enemy_state:
                    continue
                cx = (c + 0.5) * self.cell_size
                cy = (r + 0.5) * self.cell_size
                pt = np.array([cx, cy])
                if point_in_cone(origin, theta, half_angle, radius, pt):
                    positions.append(pt)

        return np.mean(positions, axis=0) if positions else None

    # ── Mise à jour ────────────────────────────────────────────────────────

    def update(self, dt: float):
        pass  # Pas de fade — permanence du sol

    # ── Rendu ──────────────────────────────────────────────────────────────

    def render(self, screen: pygame.Surface):
        changed = np.argwhere(self.grid != self._prev_grid)
        cs = self.cell_size
        for (r, c) in changed:
            color = self._color_table[int(self.grid[r, c])]
            pygame.draw.rect(self.surface, color, (c * cs, r * cs, cs, cs))
        self._prev_grid[:] = self.grid
        screen.blit(self.surface, (0, 0))
