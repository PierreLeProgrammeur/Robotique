import math
import random
from abc import ABC, abstractmethod
from typing import List, Tuple, TYPE_CHECKING

import numpy as np
import pygame

from configuration.cfg import CFG
from utils import angle_diff, vec_from_angle, clamp_angle, point_in_cone

if TYPE_CHECKING:
    from environment.environnement import Environnement


class Agent(ABC):
    """
    Classe de base abstraite pour tous les agents de la simulation.
    Gère : position, orientation, vitesse, déplacement physique,
    rebond sur les bords, direction vers une cible, et rendu minimal.
    """

    def __init__(self, x: float, y: float, theta: float,
                 speed: float, color: Tuple,
                 vision_radius: float, vision_angle: float,
                 radius: float):
        self.pos   = np.array([x, y], dtype=np.float64)
        self.theta = theta
        self.speed = speed
        self.color = color
        self.vision_radius     = vision_radius
        self.vision_half_angle = vision_angle / 2
        self.radius = radius
        self.alive  = True
        self.vel    = vec_from_angle(theta) * speed

    # ── Interface abstraite ────────────────────────────────────────────────

    @abstractmethod
    def decide(self, env: "Environnement", agents: List["Agent"], dt: float):
        """Calcule la nouvelle orientation selon les perceptions."""

    @abstractmethod
    def paint_soil(self, env: "Environnement"):
        """Repeint la cellule sous l'agent avec sa couleur."""

    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Dessine l'agent sur la surface pygame."""

    # ── Physique ───────────────────────────────────────────────────────────

    def move(self, dt: float, w: int, h: int):
        """Avance selon l'orientation courante et rebondit sur les bords."""
        self.vel  = vec_from_angle(self.theta) * self.speed
        self.pos += self.vel * dt

        bounced = False
        if self.pos[0] < self.radius:
            self.pos[0] = self.radius
            self.theta  = clamp_angle(math.pi - self.theta)
            bounced = True
        elif self.pos[0] > w - self.radius:
            self.pos[0] = w - self.radius
            self.theta  = clamp_angle(math.pi - self.theta)
            bounced = True

        if self.pos[1] < self.radius:
            self.pos[1] = self.radius
            self.theta  = clamp_angle(-self.theta)
            bounced = True
        elif self.pos[1] > h - self.radius:
            self.pos[1] = h - self.radius
            self.theta  = clamp_angle(-self.theta)
            bounced = True

        if bounced:
            self.theta += random.uniform(-0.3, 0.3)

    def steer_toward(self, target: np.ndarray, turn_speed: float, dt: float):
        """Tourne progressivement l'agent vers une position cible."""
        diff    = target - self.pos
        desired = math.atan2(diff[1], diff[0])
        delta   = angle_diff(self.theta, desired)
        max_turn = turn_speed * dt
        self.theta += max(-max_turn, min(max_turn, delta))
        self.theta  = clamp_angle(self.theta)

    # ── Perception ─────────────────────────────────────────────────────────

    def sees(self, other: "Agent") -> bool:
        """Retourne True si `other` est dans le cône de vision de cet agent."""
        return point_in_cone(
            self.pos, self.theta, self.vision_half_angle,
            self.vision_radius, other.pos
        )
