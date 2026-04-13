from typing import Optional, Tuple

import numpy as np
import pygame

from configuration.cfg import CFG

# États discrets des cellules de sol — 2 états uniquement
SOIL_EMPTY = 0   # sain / guéri → couleur fond rouge
SOIL_VIRUS = 1   # contaminé    → couleur sombre



class Environnement:
    """
    Grille 2D représentant l'état du sol.
    Chaque cellule : SOIL_EMPTY (sain) ou SOIL_VIRUS (contaminé).
    Permanente : écrasée uniquement quand l'agent adverse passe dessus.
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
        Retourne la position monde de la cellule avec `enemy_state` la plus
        proche visible dans le cône de vision, ou None si aucune.
        Version vectorisée numpy — pas de boucle Python sur les cellules.
        """
        cs = self.cell_size
        r0, c0 = self.world_to_cell(origin[0], origin[1])
        margin = int(radius // cs) + 1
        r_min = max(0, r0 - margin)
        r_max = min(self.rows - 1, r0 + margin)
        c_min = max(0, c0 - margin)
        c_max = min(self.cols - 1, c0 + margin)

        # Indices de toutes les cellules de l'état cible dans la bounding box
        subgrid = self.grid[r_min:r_max + 1, c_min:c_max + 1]
        local_rc = np.argwhere(subgrid == enemy_state)
        if len(local_rc) == 0:
            return None

        # Coordonnées monde de chaque candidat
        rows_g = local_rc[:, 0] + r_min
        cols_g = local_rc[:, 1] + c_min
        pts_x = (cols_g + 0.5) * cs
        pts_y = (rows_g + 0.5) * cs

        # Distance et filtre rayon
        dx = pts_x - origin[0]
        dy = pts_y - origin[1]
        dists = np.hypot(dx, dy)
        in_radius = dists <= radius
        if not np.any(in_radius):
            return None

        # Filtre cône angulaire (vectorisé)
        angles = np.arctan2(dy[in_radius], dx[in_radius])
        a_diff = (angles - theta + np.pi) % (2 * np.pi) - np.pi
        in_cone = np.abs(a_diff) < half_angle
        if not np.any(in_cone):
            return None

        # Cellule la plus proche parmi les valides
        valid_dists = dists[in_radius][in_cone]
        valid_idx = np.where(in_radius)[0][in_cone][np.argmin(valid_dists)]
        return np.array([pts_x[valid_idx], pts_y[valid_idx]])

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