import robot
import math
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.moteur import MoteurOmnidirectionnel

from robot.controleur import ControleurTerminal
from robot.vue import VueTerminal


'''
robot = RobotMobile()
robot.afficher()
robot.avancer(1.0)
robot.tourner(45)
robot.avancer(3)
robot.afficher()
print(robot.x)
'''

"""
moteur_diff = MoteurDifferentiel()
robot = RobotMobile(moteur=moteur_diff)
dt = 1.0
robot.afficher()
robot.commander(v=3.0, omega=0.0)
robot.mettre_a_jour(dt)
robot.commander(v=0.0, omega=math.pi/2)
robot.mettre_a_jour(1.0)
robot.commander(v=1.0, omega=0.0)
robot.mettre_a_jour(1.0)
robot.afficher()


moteur_omni = MoteurOmnidirectionnel()
robot = RobotMobile(moteur=moteur_omni)
dt = 1.0
robot.afficher()
robot.commander(vx=3.0, vy=1.0, omega=0.0)
robot.mettre_a_jour(dt)
robot.afficher()
"""

robot = RobotMobile(moteur=MoteurDifferentiel())
controleur = ControleurTerminal()
vue = VueTerminal()

dt = 1.0

running = True
while running:

    vue.dessiner_robot(robot)
    commande = controleur.lire_commande()
    robot.commander(**commande)
    robot.mettre_a_jour(dt)