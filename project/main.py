import math
from robot.robot_mobile import RobotMobile
from robot.moteur import *

moteur_diff = MoteurDifferentiel()
robot = RobotMobile(moteur=moteur_diff)
dt = 1.0 # pas de temps (s)
robot.afficher()
# On doit nommer les arguments (v = ..., omega = ...) car on utilise **kwargs !
robot.commander(v = 1.0, omega = 0.0) # avance
robot.mettre_a_jour(dt)
robot.afficher()