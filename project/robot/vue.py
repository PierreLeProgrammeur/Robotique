import math
import pygame


class VueTerminal:
    def dessiner_robot(self, robot):
        print("robot")
        print(f"Robot -> x={robot.x:.2f}, y={robot.y:.2f}, orientation={robot.theta:.2f}")

    def dessiner_obstacle_cercle(self, x, y, r):
        print(f"Obstacle cercle: centre=({x:.2f},{y:.2f}) r={r:.2f}")

    def dessiner_robot(self, robot):
        print(f"Robot -> x={robot.x:.2f}, y={robot.y:.2f}, orientation={robot.theta:.2f}")

    def dessiner_environnement(self, env):
        self.dessiner_robot(env.robot)
        for obs in env.obstacles:
            obs.dessiner(self)

class VuePygame:
    def __init__(self, largeur=800, hauteur=800, scale=50):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Simulation Robot Mobile")
        self.largeur = largeur
        self.hauteur = hauteur
        self.scale = scale
        self.clock = pygame.time.Clock()

    def convertir_coordonnees(self, x, y):
        px = int(self.largeur / 2 + (x * self.scale))
        py = int(self.hauteur / 2 - (y * self.scale))
        return px, py

    def dessiner_obstacle_cercle(self, x, y, r_m):
        ox, oy = self.convertir_coordonnees(x, y)
        r_px = int(r_m * self.scale)
        pygame.draw.circle(self.screen, (0, 0, 0), (ox, oy), r_px, 0)
        pygame.draw.circle(self.screen, (0, 0, 0), (ox, oy), r_px, 2)

    def dessiner_robot(self, robot):
        x, y = self.convertir_coordonnees(robot.x, robot.y)
        r_px = int(getattr(robot, "rayon", 0.2) * self.scale)

        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), r_px, 0)
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), r_px, 2)

        x_dir = x + int(r_px * math.cos(robot.theta))
        y_dir = y - int(r_px * math.sin(robot.theta))
        pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x_dir, y_dir), 3)

    def dessiner_environnement(self, env):
        self.screen.fill((255, 0, 0))

        for obs in env.obstacles:
            obs.dessiner(self)

        self.dessiner_robot(env.robot)

        pygame.display.flip()

    def tick(self, fps=60):
        self.clock.tick(fps)