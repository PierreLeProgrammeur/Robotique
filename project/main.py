# project/main.py (TEST pygame + environnement + obstacles)

from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.environnement import Environnement, ObstacleCirculaire

robot = RobotMobile(moteur=MoteurDifferentiel(), x=0.0, y=0.0, theta=0.0)
robot.rayon = 0.2  # optionnel si pas déjà dans RobotMobile

env = Environnement(largeur=10.0, hauteur=10.0)
env.ajouter_robot(robot)

# Obstacles de test
env.ajouter_obstacle(ObstacleCirculaire(2.0, 0.0, 0.5))
env.ajouter_obstacle(ObstacleCirculaire(-1.0, 1.5, 0.4))
env.ajouter_obstacle(ObstacleCirculaire(0.0, -2.0, 0.6))

vue = VuePygame(largeur=800, hauteur=600, scale=60)
controleur = ControleurClavierPygame(v_max=1.5, omega_max=1.5)

fps = 60
dt = 1.0 / fps
running = True

while running:
    # Affichage du monde
    vue.dessiner_environnement(env)

    # Clavier pygame
    commande = controleur.lire_commande()
    if commande.get("quit"):
        running = False
        continue

    # Commande robot + update via environnement (collision + rollback)
    robot.commander(v=commande["v"], omega=commande["omega"])
    env.mettre_a_jour(dt)

    vue.tick(fps)
