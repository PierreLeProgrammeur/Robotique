import math
import random
from typing import List, TYPE_CHECKING

import numpy as np
import pygame

from config import CFG
from utils import angle_diff, vec_from_angle, angle_from_vec, clamp_angle
from project.agents.agent import Agent
from environment.environnement import SOIL_WBC, SOIL_VIRUS

if TYPE_CHECKING:
    from environment.environnement import Environnement


class Virus(Agent):
    """
    Agent pathogène.
    Comportement : marche aléatoire biaisée.
    Perception   : fuite si sol blanc (WBC) détecté dans le cône de vision.
    Peinture sol : SOIL_VIRUS (sombre).
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
        self._turn_timer = 0.0
        self._next_turn  = random.uniform(0.3, 1.2)

    # ── Décision ───────────────────────────────────────────────────────────

    def decide(self, env: "Environnement", agents: List[Agent], dt: float):
        self._flee_or_wander(env, dt)
        self._repel_from_walls(dt)
        self.theta = clamp_angle(self.theta)

    def _flee_or_wander(self, env: "Environnement", dt: float):
        """Fuit le sol blanc ; sinon effectue une marche aléatoire biaisée."""
        white_target = env.has_enemy_color_in_cone(
            self.pos, self.theta, self.vision_half_angle,
            self.vision_radius, enemy_state=SOIL_WBC
        )
        if white_target is not None:
            flee_dir = self.pos - white_target
            desired  = math.atan2(flee_dir[1], flee_dir[0])
            delta    = angle_diff(self.theta, desired)
            max_turn = CFG.VIRUS_TURN_SPEED * dt
            self.theta += max(-max_turn, min(max_turn, delta))
        else:
            self._turn_timer += dt
            if self._turn_timer >= self._next_turn:
                self._turn_timer = 0.0
                self._next_turn  = random.uniform(0.3, 1.2)
                if random.random() < CFG.VIRUS_RANDOM_BIAS:
                    self.theta += random.gauss(0, 0.8)

    def _repel_from_walls(self, dt: float):
        """Pousse doucement le virus loin des bords avant le rebond physique."""
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
            desired  = angle_from_vec(force)
            delta    = angle_diff(self.theta, desired)
            max_turn = CFG.VIRUS_TURN_SPEED * dt
            self.theta += max(-max_turn, min(max_turn, delta))

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
