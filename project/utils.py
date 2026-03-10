import math
import numpy as np


def angle_diff(a: float, b: float) -> float:
    """Différence angulaire signée dans [-π, π]."""
    d = (b - a) % (2 * math.pi)
    return d - 2 * math.pi if d > math.pi else d


def vec_from_angle(theta: float) -> np.ndarray:
    return np.array([math.cos(theta), math.sin(theta)])


def angle_from_vec(v: np.ndarray) -> float:
    return math.atan2(v[1], v[0])


def clamp_angle(theta: float) -> float:
    return (theta + math.pi) % (2 * math.pi) - math.pi


def point_in_cone(origin: np.ndarray, theta: float, half_angle: float,
                  radius: float, point: np.ndarray) -> bool:
    """Teste si `point` est dans le cône de vision centré sur `origin`."""
    diff = point - origin
    dist = np.linalg.norm(diff)
    if dist < 1e-6 or dist > radius:
        return False
    angle_to = math.atan2(diff[1], diff[0])
    return abs(angle_diff(theta, angle_to)) < half_angle
