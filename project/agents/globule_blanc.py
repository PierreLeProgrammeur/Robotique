import math
import random
from typing import List, TYPE_CHECKING

import numpy as np
import pygame

from config import CFG
from utils import angle_from_vec, vec_from_angle
from agents.agent import Agent
from agents.virus import Virus
from environment.environnement import SOIL_VIRUS, SOIL_EMPTY

if TYPE_CHECKING:
    from environment.environnement import Environnement


class GlobuleBlanc(Agent):
    """
    Agent immunitaire.
    Comportement : algorithme de Boids (séparation, alignement, cohésion)
                   + chasse des virus (sol contaminé et agents directs).
    Peinture sol : remet SOIL_EMPTY sous ses pieds (nettoyage).
    """

    def __init__(self, x: float, y: float):
        super().__init__(
            x=x, y=y,
            theta=random.uniform(-math.pi, math.pi),
            speed=CFG.WBC_SPEED,
            color=CFG.COLOR_WBC,
            vision_radius=CFG.VISION_RADIUS,
            vision_angle=CFG.VISION_ANGLE,
            radius=CFG.AGENT_RADIUS,
        )

    # ── Forces Boids ──────────────────────────────────────────────────────

    def _separation(self, neighbors: List["GlobuleBlanc"]) -> np.ndarray:
        force = np.zeros(2)
        for n in neighbors:
            diff = self.pos - n.pos
            dist = np.linalg.norm(diff)
            if 0 < dist < CFG.BOID_SEPARATION_RADIUS:
                force += diff / (dist ** 2 + 1e-6)
        return force

    def _alignment(self, neighbors: List["GlobuleBlanc"]) -> np.ndarray:
        if not neighbors:
            return np.zeros(2)
        return np.mean([n.vel for n in neighbors], axis=0) - self.vel

    def _cohesion(self, neighbors: List["GlobuleBlanc"]) -> np.ndarray:
        if not neighbors:
            return np.zeros(2)
        return np.mean([n.pos for n in neighbors], axis=0) - self.pos

    def _wall_avoidance(self) -> np.ndarray:
        margin = CFG.WALL_REPULSION_DIST
        w, h   = CFG.SCREEN_WIDTH, CFG.SCREEN_HEIGHT
        force  = np.zeros(2)
        if self.pos[0] < margin:
            force[0] += (margin - self.pos[0]) / margin
        if self.pos[0] > w - margin:
            force[0] -= (self.pos[0] - (w - margin)) / margin
        if self.pos[1] < margin:
            force[1] += (margin - self.pos[1]) / margin
        if self.pos[1] > h - margin:
            force[1] -= (self.pos[1] - (h - margin)) / margin
        return force

    def _hunt(self, env: "Environnement", agents: List[Agent]) -> np.ndarray:
        """
        Retourne la force de chasse :
        - priorité 1 : virus visible directement dans le cône
        - priorité 2 : cellule de sol contaminé la plus proche dans le cône
        """
        visible_virus = [
            a for a in agents
            if isinstance(a, Virus) and a.alive and self.sees(a)
        ]
        if visible_virus:
            closest = min(visible_virus,
                          key=lambda v: np.linalg.norm(v.pos - self.pos))
            return closest.pos - self.pos

        dark_target = env.has_enemy_color_in_cone(
            self.pos, self.theta, self.vision_half_angle,
            self.vision_radius, enemy_state=SOIL_VIRUS
        )
        return dark_target - self.pos if dark_target is not None else np.zeros(2)

    # ── Décision ──────────────────────────────────────────────────────────

    def decide(self, env: "Environnement", agents: List[Agent], dt: float):
        wbc_neighbors = [
            a for a in agents
            if isinstance(a, GlobuleBlanc) and a is not self
            and a.alive and self.sees(a)
        ]

        total = (
            CFG.BOID_W_SEPARATION * self._separation(wbc_neighbors) +
            CFG.BOID_W_ALIGNMENT  * self._alignment(wbc_neighbors)  +
            CFG.BOID_W_COHESION   * self._cohesion(wbc_neighbors)   +
            CFG.BOID_W_HUNT       * self._hunt(env, agents)          +
            CFG.BOID_W_AVOID_WALL * self._wall_avoidance()
        )

        if np.linalg.norm(total) > 1e-4:
            desired = angle_from_vec(total)
            self.steer_toward(
                self.pos + vec_from_angle(desired),
                CFG.WBC_TURN_SPEED, dt
            )

    # ── Sol ───────────────────────────────────────────────────────────────

    def paint_soil(self, env: "Environnement"):
        """Nettoie la cellule sous le globule : remet le sol à l'état sain."""
        env.paint(self.pos[0], self.pos[1], SOIL_EMPTY)

    # ── Rendu ─────────────────────────────────────────────────────────────

    def render(self, screen: pygame.Surface):
        if not self.alive:
            return
        ix, iy = int(self.pos[0]), int(self.pos[1])
        pygame.draw.circle(screen, self.color, (ix, iy), int(self.radius))
        pygame.draw.circle(screen, (180, 180, 220), (ix, iy),
                           max(2, int(self.radius * 0.45)))
        pygame.draw.circle(screen, (180, 200, 255), (ix, iy), int(self.radius), 2)
        tip = self.pos + vec_from_angle(self.theta) * (self.radius + 4)
        pygame.draw.line(screen, (200, 200, 255),
                         (ix, iy), (int(tip[0]), int(tip[1])), 2)