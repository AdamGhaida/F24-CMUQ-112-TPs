# Furqan Saeed
# faseed@andrew.cmu.edu

from cmu_graphics import *
import math
import string
import random
import home
import time
import play



class ai:

    def __init__(self):
        pass

    




# lvl1 and lvl2 seem similar but the small change in wait time can mean lvl 1 
# is more brainless and just spammy whereas lvl 2 seems more calculated
class lvl1(ai):
    def __init__(self, app):
        self.deck = app.enemyDeck
        self.card = app.enemyCards
        self.elixir = app.enemyElixir
        self.side = "enemy"
        self.time = 0

    def onStep(self, app):
        if self.time != 0:
            self.time -= 1
        else:
            self.time = random.randint(1, 4) * app.stepsPerSecond
            app.enemyCardSelectedIndex = random.randint(0, 4)
            app.enemyCardSelected = self.deck[app.enemyCardSelectedIndex]
            randx = random.randint(155, 600)
            randy = random.randint(25, 370)
            while play.checkClickInTower(randx, randy):
                randx = random.randint(155, 600)
                randy = random.randint(25, 370)
            play.placeCard(app, randx, randy, "enemy")



# The aggressive AI (Surprisingly the timing is just perfect for it to place 
# all cards and at perfect time intervals to stack cards)
class lvl2(ai):
    def __init__(self, app):
        self.deck = app.enemyDeck
        self.card = app.enemyCards
        self.elixir = app.enemyElixir
        self.side = "enemy"
        self.time = 0

    def onStep(self, app):
        if self.time != 0:
            self.time -= 1
        else:
            self.time = random.randint(1, 8) * app.stepsPerSecond
            app.enemyCardSelectedIndex = random.randint(0, 4)
            app.enemyCardSelected = self.deck[app.enemyCardSelectedIndex]
            randx = random.randint(155, 600)
            randy = random.randint(25, 370)
            while play.checkClickInTower(randx, randy):
                randx = random.randint(155, 600)
                randy = random.randint(25, 370)
            play.placeCard(app, randx, randy, "enemy")