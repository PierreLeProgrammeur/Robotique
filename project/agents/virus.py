import math
import random
from typing import List, TYPE_CHECKING

import numpy as np
import pygame

from config import CFG
from utils import vec_from_angle, angle_from_vec, clamp_angle
from agents.agent import Agent
from environment.environnement import SOIL_VIRUS, SOIL_EMPTY

if TYPE_CHECKING:
    from environment.environnement import Environnement


class Virus(Agent):
    """
    Agent pathogène.
    Objectif  : contaminer (peindre en noir) un maximum de sol.
    Priorités :
      1. Cases rouges (SOIL_EMPTY) visibles dans le cône → les couvrir
      2. Rien en vue → cap maintenu (ligne droite)
    """

    def __init__(self, x: float, y: float):
        super().__init__(
            x=x, y=y,
            theta=random.uniform(-math.pi, math.pi),
            speed=CFG.VIRUS_SPEED,
            color=CFG.COLOR_VIRUS,
            vision_radius=CFG.VISION_RADIUS,
            vision_angle=CFG.VISION_ANGLE,
            radius=CFG.AGENT_RADIUS,
        )

    # ── Décision ───────────────────────────────────────────────────────────

    def decide(self, env: "Environnement", agents: List[Agent], dt: float):
        self._seek_to_contaminate(env, dt)
        self._repel_from_walls(dt)
        self.theta = clamp_angle(self.theta)

    def _seek_to_contaminate(self, env: "Environnement", dt: float):
        """Se dirige vers les cases rouges (SOIL_EMPTY) pour les contaminer."""
        target = env.has_enemy_color_in_cone(
            self.pos, self.theta, self.vision_half_angle,
            self.vision_radius, enemy_state=SOIL_EMPTY
        )
        if target is not None:
            self.steer_toward(target, CFG.VIRUS_TURN_SPEED, dt)

    def _repel_from_walls(self, dt: float):
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
        if np.linalg.norm(force) > 0.05:
            self.steer_toward(
                self.pos + vec_from_angle(angle_from_vec(force)) * 10,
                CFG.VIRUS_TURN_SPEED, dt
            )

    # ── Sol & rendu ────────────────────────────────────────────────────────

    def paint_soil(self, env: "Environnement"):
        env.paint(self.pos[0], self.pos[1], SOIL_VIRUS)

    def render(self, screen: pygame.Surface):
        if not self.alive:
            return
        ix, iy = int(self.pos[0]), int(self.pos[1])
        pygame.draw.circle(screen, self.color, (ix, iy), int(self.radius))
        for i in range(8):
            angle = self.theta + (2 * math.pi * i / 8)
            tip   = self.pos + vec_from_angle(angle) * (self.radius + 5)
            pygame.draw.line(screen, (70, 30, 30),
                             (ix, iy), (int(tip[0]), int(tip[1])), 1)
        pygame.draw.circle(screen, (50, 20, 20), (ix, iy), int(self.radius), 2)