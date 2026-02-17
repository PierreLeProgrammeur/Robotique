from abc import ABC, abstractmethod
import math


class Moteur(ABC):

    @abstractmethod
    def commander(self, *args):
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        pass

class MoteurDifferentiel(Moteur):

    def __init__(self, v=0.0, omega=0.0):
        self.v = v
        self.omega = omega

    def commander(self, v, omega):
        self.v = float(v)
        self.omega = float(omega)

    def mettre_a_jour(self, robot, dt):
        robot.x += self.v * math.cos(robot.theta) * dt
        robot.y += self.v * math.sin(robot.theta) * dt
        robot.theta = (robot.theta + self.omega * dt) % (2 * math.pi)

class MoteurOmnidirectionnel(Moteur):

    def __init__(self, vx=0.0, vy=0.0, omega=0.0):
        self.vx = vx
        self.vy = vy
        self.omega = omega

    def commander(self, vx, vy, omega):
        self.vx = float(vx)
        self.vy = float(vy)
        self.omega = float(omega)

    def mettre_a_jour(self, robot, dt):
        robot.x += (self.vx * math.cos(robot.theta) - self.vy * math.sin(robot.theta)) * dt
        robot.y += (self.vx * math.sin(robot.theta) + self.vy * math.cos(robot.theta)) * dt
        robot.theta = (robot.theta + self.omega * dt) % (2 * math.pi)

