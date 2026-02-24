from abc import ABC, abstractmethod
import math


class Obstacle(ABC):
    @abstractmethod
    def collision(self, x: float, y: float, rayon_robot: float) -> bool:
        pass

    @abstractmethod
    def dessiner(self, vue) -> None:
        pass


class ObstacleCirculaire(Obstacle):
    def __init__(self, x: float, y: float, rayon: float):
        self.x = float(x)
        self.y = float(y)
        self.rayon = float(rayon)

    def collision(self, x: float, y: float, rayon_robot: float) -> bool:
        dx = x - self.x
        dy = y - self.y
        d2 = dx * dx + dy * dy
        r = self.rayon + rayon_robot
        return d2 <= r * r

    def dessiner(self, vue) -> None:
        vue.dessiner_obstacle_cercle(self.x, self.y, self.rayon)


class Environnement:
    def __init__(self, largeur=10.0, hauteur=10.0):
        self.largeur = float(largeur)
        self.hauteur = float(hauteur)
        self.robot = None
        self.obstacles = []

    def ajouter_robot(self, robot) -> None:
        self.robot = robot

    def ajouter_obstacle(self, obstacle: Obstacle) -> None:
        self.obstacles.append(obstacle)

    def _dans_limites(self, x: float, y: float, r: float) -> bool:
        return (
            (-self.largeur / 2 + r) <= x <= (self.largeur / 2 - r)
            and (-self.hauteur / 2 + r) <= y <= (self.hauteur / 2 - r)
        )

    def collision(self) -> bool:
        r_robot = getattr(self.robot, "rayon", 0.2)
        x, y = self.robot.x, self.robot.y

        if not self._dans_limites(x, y, r_robot):
            return True

        for obs in self.obstacles:
            if obs.collision(x, y, r_robot):
                return True
        return False

    def mettre_a_jour(self, dt: float) -> None:
        # 1) sauvegarde état robot
        x0, y0, t0 = self.robot.x, self.robot.y, self.robot.theta

        # 2) robot calcule son mouvement
        self.robot.mettre_a_jour(dt)

        # 3) test collision
        if self.collision():
            # 4) annule déplacement
            self.robot.x, self.robot.y, self.robot.theta = x0, y0, t0