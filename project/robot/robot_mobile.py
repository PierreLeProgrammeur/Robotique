import math

class RobotMobile:
    def __init__(self, x=0.0, y=0.0, theta=0.0, moteur=None):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)
        self.moteur = moteur

    def position(self):
        return self.x, self.y

    def afficher(self):
        print(self.x, self.y, self.theta)

    def commander(self, **kwargs):
        if self.moteur is not None:
            self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        if self.moteur is not None:
            self.moteur.mettre_a_jour(self, dt)
