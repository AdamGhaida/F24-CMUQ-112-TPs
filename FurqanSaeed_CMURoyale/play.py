# Furqan Saeed
# faseed@andrew.cmu.edu

from cmu_graphics import *
import math
import string
import random
import home
import time

##################
# Card Mechanics #
##################

def placeCard(app, x, y, side):
    # Placing Selected Card onto Arena
    if (app.playerCardSelected != None and side == "player") or \
        (app.enemyCardSelected != None and side == "enemy"):
        x, y = getCardPlacementLocation(side, x, y)
        if side == "player":
            if app.playerElixir - app.playerCardSelected.cost > 0:
                app.playerElixir -= app.playerCardSelected.cost
                app.playerCards.extend(initCard(str(app.playerCardSelected),
                                                x,y,"player"))
                for i in app.playerCards:
                    i.towerCollisions(app)

                index = app.playerCardSelectedIndex
                temp = app.playerDeck[index]
                app.playerDeck[index] = app.playerDeck[4]
                app.playerDeck[4] = temp
                app.playerDeck.append(app.playerDeck.pop(4))
                app.playerCardSelected = None
        else:
            if app.enemyElixir - app.enemyCardSelected.cost > 0:
                app.enemyElixir -= app.enemyCardSelected.cost
                app.enemyCards.extend(initCard(str(app.enemyCardSelected),
                                               x,y,"enemy"))
                for i in app.enemyCards:
                    i.towerCollisions(app)
                app.enemyDeck.append(app.enemyDeck.pop\
                                     (app.enemyCardSelectedIndex))
                app.enemyCardSelected = None


# Gets a random Deck and returns it
def randomizer(app):
    shuffled = getAllCards()
    random.shuffle(shuffled)
    for i in range(len(shuffled)):
        shuffled[i] = initCard(shuffled[i])[0]
    return shuffled

def getAllCards():
    return ['miniPekka', 'bomber', 'knight', 'skeletons', 'wizard',
            'fireSpirit'] # Add Tesla or Elixir Collecter maybe

class playingCard:
    def __init__(self):
        self.alive = True
        self.state = "Spawned"
        self.hitbox = 12.5
        self.spawningCD = 0

    def onStep(self, app):
        if self.state == "Spawned":
            self.state = "Idle"
        elif self.state == "Idle":
            if self.spawningCD > app.stepsPerSecond*0.5:
                self.state = "Active"
            else:
                self.spawningCD += 1
        else:
            self.checkCollisions(app)
            if self.mode == "Battling":
                if self.target.alive == False:
                    self.target = None
                    self.mode = "Moving"
                    self.range = self.originalRange
                else:
                    self.fight(app)
                    if self.target.health <= 0:
                        self.target.alive = False
                        self.target = None
                        self.mode = "Moving"
                        self.range = self.originalRange
            if self.mode == "Moving":
                self.riverDetection(app)
                closest = self.closestTarget(app, self.side)
                if str(closest) == "kingTower":
                    if self.range <= 2:
                        self.range = 3
                self.move(app, closest, self.side)
                self.towerCollisions(app)
                
                if self.cooldown % (app.stepsPerSecond * self.hitSpeed) != 0:
                    self.cooldown += 1

    def towerCollisions(self, app):
        
        # If card is spawned inside tower somehow then move it outside
        target = None
        target2 = None
        for tower in app.enemyTowers:
            if tower.alive:
                dist = distance(self.x, self.y, tower.x, tower.y)
                if dist < tower.hitbox:
                    target = tower
                    break
                elif dist < tower.hitbox + self.hitbox:
                    target2 = tower
                    dist2 = dist
                    break
                    
        if target == None:
            for tower in app.playerTowers:
                if tower.alive:
                    dist = distance(self.x, self.y, tower.x, tower.y)
                    if dist < tower.hitbox:
                        target = tower
                        break
                elif dist < tower.hitbox + self.hitbox:
                    target2 = tower
                    dist2 = dist
                    break
        if target != None:
            r = (self.hitbox+target.hitbox)
            self.y = target.y + (r * (self.y-target.y))/dist
            self.x = target.x + (r * (self.x-target.x))/dist

        # This is to move the cards to the edge of the tower as they move
        if target2 != None:
            r = (self.hitbox+target2.hitbox)
            self.y = target2.y + (r * (self.y-target2.y))/dist2
            self.x = target2.x + (r * (self.x-target2.x))/dist2
            
            if self.x < target2.x and self.y < target2.y:
                self.x -= 1
                self.y -= 1
            elif self.x < target2.x and self.y > target2.y:
                self.x -= 1
                self.y += 1
            elif self.x > target2.x and self.y < target2.y:
                self.x += 1
                self.y -= 1
            else:
                self.x += 1
                self.y -= 1


    def riverDetection(self, app):
        if self.target != None:
            t = self.target
            if (self.y < 375 and t.y > 375) or (self.y > 375 and t.y < 375) \
            or (self.y < 425 and t.y > 425) or (self.y > 425 and t.y < 425):
                mp = ((self.x+t.x)/2, (self.y+t.y)/2) # Midpoint of two cards
                if mp[0] < 377 and mp[0] > 238:
                    self.x -= 2
                    t.x -= 2
                elif mp[0] < 238:
                    self.x += 2
                    t.x += 2
                elif mp[0] > 377 and mp[0] < 516:
                    self.x += 2
                    t.x += 2
                elif mp[0] > 516:
                    self.x -= 2
                    t.x -= 2

        x = self.x
        y = self.y
        if 280 < x < 475 and 400 < y < 425:
            self.y = 427
            if x < 377:
                self.x -= 2
            else:
                self.x += 2
        elif 280 < x < 475 and 375 < y < 400:
            self.y = 373
            if x < 377:
                self.x -= 2
            else:
                self.x += 2
        elif 276 < x < 280 and 375 < y < 425:
            self.x = 274
        elif 475 < x < 450 and 375 < y < 425:
            self.x = 452
        elif 149 < x < 198 and 400 < y < 425:
            self.y = 427
            self.x += 2
        elif 149 < x < 198 and 375 < y < 400:
            self.y = 373
            self.x += 2
        elif 198 < x < 202 and 375 < y < 425:
            self.x = 204
        elif 556 < x < 605 and 400 < y < 425:
            self.y = 427
            self.x -= 2
        elif 556 < x < 605 and 375 < y < 400:
            self.y = 373
            self.x -= 2
        elif 556 < x < 605 and 375 < y < 425:
            self.x = 552



    #Moves card to the given Target
    def move(self, app, closestTarget, side):

        if self.movementType == "Ground":    
            point = self.getPointGround(closestTarget, side)
            check = self.inEnemyRangeCheck(app, side)
        else:
            point = self.getPointAir(closestTarget, side, app)
            check = self.inEnemyRangeCheck(app, side)

        if check:
            self.target = closestTarget
            self.mode = "Battling"
            if str(self.target) == "kingTower" and self.range <= 2:
                self.range += 2
        else:
            self.moveCard(point)

    
    def fight(self, app):
        if self.cooldown % (app.stepsPerSecond * self.hitSpeed) == 0:
            self.attack()
        self.cooldown += 1
    
    
    def closestTarget(self, app, side):
        if side == "player":
            closestTower = self.closestTower(app.enemyTowers)
            closestCard = self.closestCard(app.enemyCards)
        else:
            closestTower = self.closestTower(app.playerTowers)
            closestCard = self.closestCard(app.playerCards)
        
        distT = distance(self.x, self.y, closestTower.x, closestTower.y)
        distC = distance(self.x, self.y, closestCard.x, closestCard.y)
        
        if distT < distC:
            closest = closestTower
        else:
            closest = closestCard
        
        return closest
        
    def closestTower(self, towers):
        lowDist = 1000
        closest = None
        radius = self.sight * 25
        for i in towers:
            if i.alive:
                dist = distance(self.x, self.y, i.x, i.y)
                if dist <= radius and dist <= lowDist:
                    lowDist = dist
                    closest = i
        if closest == None:
            return templateCard()
        
        return closest
    
    def closestCard(self, cards):
        lowDist = 1000
        closest = None
        radius = self.sight * 25
        for i in cards:
            dist = distance(self.x, self.y, i.x, i.y)
            if dist <= radius and dist <= lowDist:
                lowDist = dist
                closest = i
        if closest == None:
            return templateCard()
        
        return closest

    def moveCard(self, point):
        # Move Card to the closest Point
        angle = 360 - angleTo(self.x, self.y, point[0], point[1])
        angle = math.radians(angle)
        dx = -self.movementSpeed * math.sin(angle)
        dy = -self.movementSpeed * math.cos(angle)
        self.x += dx
        self.y += dy
    

    def checkCollisions(self, app):
        # An observation, cards only collide with same side (most of the time)
        if self.side == "enemy":
            for i in app.enemyCards:
                if i != self:
                    dist = distance(self.x, self.y, i.x, i.y)
                    if dist < i.hitbox + self.hitbox and self.y < i.y:
                        self.moveCollision(i)
        else:
            for i in app.playerCards:
                if i != self:
                    dist = distance(self.x, self.y, i.x, i.y)
                    if dist < i.hitbox + self.hitbox and self.y > i.y:
                        self.moveCollision(i)
        
        # Edge of Map Collisions
        if self.x < 149:
            self.x = 149+self.hitbox
        elif self.x > 605:
            self.x = 605-self.hitbox
        if self.y > 780:
            self.y = 780-self.hitbox
        elif self.y < 20:
            self.y = 20+self.hitbox

        # River Collisions

    # If a collision is detected, move accordingly
    def moveCollision(self, collider):
        if self.side == "enemy":
            dy = -1
        else:
            dy = 1
        
        # Check to see if on bridge or not
        if self.hitbox < collider.hitbox:
            if not (425 >= self.y >= 375):
                if self.x < 377:
                    if self.x < 200:
                        dx = 1
                    else:
                        dx = -1
                else:
                    if self.x > 554:
                        dx = -1
                    else:
                        dx = 1
            else:
                if self.x < 377:
                    if self.x < 238:
                        dx = 1
                    else:
                        dx = -1
                else:
                    if self.x < 516:
                        dx = 1
                    else:
                        dx = -1
        else:
            dx = 1
        self.x += dx
        self.y += dy

    def inEnemyRangeCheck(self, app, side):
        cardRange = self.range * 25        
        closest = self.closestTarget(app, side)
        lowDist = distance(self.x, self.y, closest.x, closest.y)
        if lowDist <= cardRange:
            return True 
        else:
            return False
    
    def getPointAir(self, closestTarget, side, app):
        if closestTarget.x == 1000: # Checks if no target is seen by card
            if side == "player":
                point = self.closestTower(app.enemyTowers)
            else:
                point = self.closestTower(app.playerTowers)
        else:
            point = (closestTarget.x, closestTarget.y)
        return point

    # If no enemies in range then find the point for the card to move towards
    def getPointGround(self, closestTarget, side):
        if closestTarget.x == 1000:
            if side == "player":
                point = self.closestPointPlayer()
            else:
                point = self.closestPointEnemy()
        else:
            point = (closestTarget.x, closestTarget.y)
        return point

    # Point refers to location on map, no specific card
    def closestPointPlayer(self):
        if self.y > 425:
            if self.x < 377:
                point = (237.5, 425)
            else:
                point = (517.5, 425)
        elif self.y > 375:
            if self.x < 377:
                point = (237.5, 375)
            else:
                point = (517.5, 375)
        elif self.y > 131:
            if self.x < 377:
                point = (237.5, 131)
            else:
                point = (517.5, 131)
        else:
            point = (377, 71)
        return point
    
    def closestPointEnemy(self):
        if self.y < 375:
            if self.x < 375:
                point = (237.5, 378)
            else:
                point = (517.5, 378)
        elif self.y < 425:
            if self.x < 377:
                point = (237.5, 428)
            else:
                point = (517.5, 428)
        elif self.y < 679:
            if self.x < 377:
                point = (237.5, 682)
            else:
                point = (517.5, 681)
        else:
            point = (377, 729)
        return point
    
    def getEnemiesInRange(self, x, y, side, radius):
        enemies = []
        if side == "player":
            allEnemies = app.enemyCards + app.enemyTowers
        else:
            allEnemies = app.playerCards + app.playerTowers
        
        for i in allEnemies:
            if distance(x, y, i.x, i.y) <= radius*25:
                enemies.append(i)
        
        return enemies


    def drawHealthBar(self):
        if self.health == self.maxHealth:
            return
        if self.health > 0:
            drawRect(self.x-13.5, self.y-self.hitbox-4,
                     27*(self.health/self.maxHealth), 5, fill=self.colour,
                     border=None, align='left')
        drawRect(self.x, self.y-self.hitbox-4, 27, 5, fill='black',
                 border=self.colour, align='center', borderWidth=0.05,
                 opacity=40)
    
    def drawSpawning(self, app):
        if self.spawningCD != 0 and self.spawningCD < app.stepsPerSecond*0.5:
            drawArc(self.x+self.hitbox+10, self.y+self.hitbox+10, 8, 8, 0,
                360*(self.spawningCD/(app.stepsPerSecond*0.5)),
                fill=None, border="grey", borderWidth=3)



# Card 1
class miniPekka(playingCard):
    card = "Assets/miniPekka/miniPekkaCard.png"
    playerW = ["Assets/miniPekka/pw0.png"]
    enemyW = ["Assets/miniPekka/ew0.png"]
    enemyA = ["Assets/miniPekka/ea0.png"]
    playerA = ["Assets/miniPekka/pa0.png"]



    def __init__(self, x=0, y=0, side=None):
        super().__init__()
        self.health = 1500
        self.maxHealth = self.health
        self.dmg = 680
        self.hitSpeed = 1.6
        self.movementSpeed = 2    # "Fast"
        
        self.range = 2
        self.originalRange = self.range
        self.hitbox = 8

        self.targets = "Ground"
        self.attackType = "Melee"
        self.cost = 4
        self.movementType = "Ground"
        self.mode = "Moving"
        self.side = side
        self.target = None
        self.sight = 6
        self.cooldown = 0
        self.movingPlayerIndex = 0
        self.movingEnemyIndex = 0
        if self.side == "player":
            self.colour = "blue"
        else:
            self.colour = "red"

        if side == "enemy":
            self.angle = 180
        else:
            self.angle = 0
        
        self.x = x
        self.y = y

    def draw(self):
        if self.state == "Idle":
            self.drawSpawning(app)
        if self.mode == "Moving":
            if self.side == 'player':
                drawImage(miniPekka.playerW[0], self.x, self.y, align='center',
                          width=35, height=35)
            else:
                drawImage(miniPekka.enemyW[0], self.x, self.y, align='center',
                          width=35, height=35)
        else:
            if self.side == 'player':
                drawImage(miniPekka.playerA[0], self.x, self.y, align='center',
                          width=35, height=35)
            else:
                drawImage(miniPekka.enemyA[0], self.x, self.y, align='center',
                          width=35, height=35)
        self.drawHealthBar()
    
    def attack(self):
        self.target.health -= self.dmg

    def __repr__(self):
        return "miniPekka"
    
    def drawCard(self, x, y, h=None, w=None):
        if h and w != None:
            drawImage(miniPekka.card, x, y, height=h, width=w)
        else:
            drawImage(miniPekka.card, x, y)

# Card 2
class knight(playingCard):
    card = "Assets/knight/knightCard.png"
    playerW = ["Assets/knight/pw0.png"]
    enemyW = ["Assets/knight/ew0.png"]
    enemyA = ["Assets/knight/ea0.png"]
    playerA = ["Assets/knight/pa0.png"]

    def __init__(self, x=0, y=0, side=None):
        super().__init__()
        self.health = 2000
        self.maxHealth = self.health
        self.dmg = 202
        self.hitSpeed = 1.2
        self.movementSpeed = 1    # "Medium"
        self.range = 2
        self.originalRange = self.range
        self.hitbox = 10
        self.targets = "Ground"
        self.atttackType = "Melee"
        self.cost = 3
        self.movementType = "Ground"
        self.mode = "Moving"
        self.side = side
        self.target = None
        self.sight = 6
        self.cooldown = 0
        if self.side == "player":
            self.colour = "blue"
        else:
            self.colour = "red"

        if side == "enemy":
            self.angle = 180
        else:
            self.angle = 0

        self.x = x
        self.y = y
    
    def draw(self):
        if self.state == "Idle":
            self.drawSpawning(app)
        if self.mode == "Moving":
            if self.side == 'player':
                drawImage(knight.playerW[0], self.x, self.y, align='center',
                          width=35, height=35)
            else:
                drawImage(knight.enemyW[0], self.x, self.y, align='center',
                          width=35, height=35)
        else:
            if self.side == 'player':
                drawImage(knight.playerA[0], self.x, self.y, align='center',
                          width=35, height=35)
            else:
                drawImage(knight.enemyA[0], self.x, self.y, align='center',
                          width=35, height=35)
        self.drawHealthBar()
    
    def attack(self):
        self.target.health -= self.dmg

    def __repr__(self):
        return "knight"
    
    def drawCard(self, x, y, h=None, w=None):
        if h and w != None:
            drawImage(knight.card, x, y, height=h, width=w)
        else:
            drawImage(knight.card, x, y)
        

# Card 3
class skeleton(playingCard):
    card = "Assets/skeleton/skeletonCard.png"
    playerW = ["Assets/skeleton/pw0.png"]
    enemyW = ["Assets/skeleton/ew0.png"]
    enemyA = ["Assets/skeleton/ea0.png"]
    playerA = ["Assets/skeleton/pa0.png"]

    def __init__(self, x=0, y=0, side=None):
        super().__init__()
        self.health = 81
        self.maxHealth = self.health
        self.dmg = 81
        self.hitSpeed = 1
        self.movementSpeed = 2   # "Fast"
        self.range = 2
        self.originalRange = self.range
        self.hitbox = 5
        self.targets = "Ground"
        self.atttackType = "Melee"
        self.cost = 1
        self.movementType = "Ground"
        self.side = side
        self.target = None
        self.sight = 6.5
        self.cooldown = 0
        self.mode = "Moving"
        if self.side == "player":
            self.colour = "blue"
        else:
            self.colour = "red"

        if side == "enemy":
            self.angle = 180
        else:
            self.angle = 0

        self.x = x
        self.y = y

    def draw(self):
        if self.state == "Idle":
            self.drawSpawning(app)
        if self.mode == "Moving":
            if self.side == 'player':
                drawImage(skeleton.playerW[0], self.x, self.y, align='center',
                          width=25, height=25)
            else:
                drawImage(skeleton.enemyW[0], self.x, self.y, align='center',
                          width=25, height=25)
        else:
            if self.side == 'player':
                drawImage(skeleton.playerA[0], self.x, self.y, align='center',
                          width=25, height=25)
            else:
                drawImage(skeleton.enemyA[0], self.x, self.y, align='center',
                          width=25, height=25)
        self.drawHealthBar()

    def attack(self):
        self.target.health -= self.dmg

    def __repr__(self):
        return "skeletons"
    
    def drawCard(self, x, y, h=None, w=None):
        if h and w != None:
            drawImage(skeleton.card, x, y, height=h, width=w)
        else:
            drawImage(skeleton.card, x, y)

# Card 4
class bomber(playingCard):
    card = "Assets/bomber/bomberCard.png"
    playerW = ["Assets/bomber/pw0.png"]
    enemyW = ["Assets/bomber/ew0.png"]
    enemyA = ["Assets/bomber/ea0.png"]
    playerA = ["Assets/bomber/pa0.png"]

    def __init__(self, x=0, y=0, side=None):
        super().__init__()
        self.health = 400
        self.maxHealth = self.health
        self.dmg = 225
        self.hitSpeed = 1.8
        self.movementSpeed = 1    # "Medium"
        self.range = 4.5
        self.originalRange = self.range
        self.hitbox = 6
        self.targets = "Ground"
        self.atttackType = "Ranged"
        self.cost = 2
        self.movementType = "Ground"
        self.mode = "Moving"
        self.sight = 6.5
        self.cooldown = 0
        self.side = side
        self.target = None
        self.splashRadius = 1
        if self.side == "player":
            self.colour = "blue"
        else:
            self.colour = "red"

        if side == "enemy":
            self.angle = 180
        else:
            self.angle = 0

        self.x = x
        self.y = y
    
    def draw(self):
        if self.state == "Idle":
            self.drawSpawning(app)
        if self.mode == "Moving":
            if self.side == 'player':
                drawImage(bomber.playerW[0], self.x, self.y, align='center',
                          width=30, height=30)
            else:
                drawImage(bomber.enemyW[0], self.x, self.y, align='center',
                          width=30, height=30)
        else:
            if self.side == 'player':
                drawImage(bomber.playerA[0], self.x, self.y, align='center',
                          width=30, height=30)
            else:
                drawImage(bomber.enemyA[0], self.x, self.y, align='center',
                          width=30, height=30)
        self.drawHealthBar()

    def attack(self):
        app.projectiles.append(bomb(self.x, self.y, self.target,
                                         self.dmg, self.splashRadius,
                                         self.side, str(self)))

    def __repr__(self):
        return "bomber"
    
    def drawCard(self, x, y, h=None, w=None):
        if h and w != None:
            drawImage(bomber.card, x, y, height=h, width=w)
        else:
            drawImage(bomber.card, x, y)


# Card 5
class wizard(playingCard):
    card = "Assets/wizard/wizardCard.png"
    playerW = ["Assets/wizard/pw0.png"]
    enemyW = ["Assets/wizard/ew0.png"]
    enemyA = ["Assets/wizard/ea0.png"]
    playerA = ["Assets/wizard/pa0.png"]

    def __init__(self, x=0, y=0, side=None):
        super().__init__()
        self.health = 754
        self.maxHealth = self.health
        self.dmg = 281
        self.hitSpeed = 1.4
        self.movementSpeed = 1    # "Medium"
        self.range = 5.5
        self.originalRange = self.range
        self.hitbox = 10
        self.targets = "All"
        self.atttackType = "Ranged"
        self.cost = 5
        self.movementType = "Ground"
        self.mode = "Moving"
        self.sight = 6.5
        self.cooldown = 0
        self.side = side
        self.target = None
        self.splashRadius = 1
        if self.side == "player":
            self.colour = "blue"
        else:
            self.colour = "red"

        if side == "enemy":
            self.angle = 180
        else:
            self.angle = 0
        
        self.x = x
        self.y = y

    def draw(self):
        if self.state == "Idle":
            self.drawSpawning(app)
        if self.mode == "Moving":
            if self.side == 'player':
                drawImage(wizard.playerW[0], self.x, self.y, align='center',
                          width=35, height=35)
            else:
                drawImage(wizard.enemyW[0], self.x, self.y, align='center',
                          width=35, height=35)
        else:
            if self.side == 'player':
                drawImage(wizard.playerA[0], self.x, self.y, align='center',
                          width=35, height=35)
            else:
                drawImage(wizard.enemyA[0], self.x, self.y, align='center',
                          width=35, height=35)
        self.drawHealthBar()
    
    def attack(self):
        app.projectiles.append(fireball(self.x, self.y, self.target,
                                        self.dmg, self.splashRadius,
                                        self.side, str(self)))

    def __repr__(self):
        return "wizard"
    
    def drawCard(self, x, y, h=None, w=None):
        if h and w != None:
            drawImage(wizard.card, x, y, height=h, width=w)
        else:
            drawImage(wizard.card, x, y)

# Card 6
class fireSpirit(playingCard):
    card = "Assets/fireSpirit/fireSpiritCard.png"
    playerW = ["Assets/fireSpirit/pw0.png"]
    enemyW = ["Assets/fireSpirit/ew0.png"]


    def __init__(self, x=0, y=0, side=None):
        super().__init__()
        self.health = 240
        self.maxHealth = self.health
        self.dmg = 207
        self.hitSpeed = 1000
        self.movementSpeed = 2.7   # "Very Fast"
        self.range = 3
        self.originalRange = self.range
        self.hitbox = 5.5
        self.targets = "All"
        self.atttackType = "Ranged"
        self.cost = 1
        self.movementType = "Ground"
        self.mode = "Moving"
        self.sight = 6
        self.cooldown = 0
        self.side = side
        self.target = None
        self.splashRadius = 1.5
        self.movePlayerI = 0
        self.moveEnemyI = 0
        self.attackPlayerI = 0
        self.attackEnemyI = 0
        if self.side == "player":
            self.colour = "blue"
        else:
            self.colour = "red"
        
        if side == "enemy":
            self.angle = 180
        else:
            self.angle = 0
        
        self.x = x
        self.y = y
    
    def draw(self):
        if self.state == "Idle":
            self.drawSpawning(app)
        if self.mode == "Moving":
            if self.side == 'player':
                drawImage(fireSpirit.playerW[0], self.x, self.y, align='center',
                          width=30, height=30)
            else:
                drawImage(fireSpirit.enemyW[0], self.x, self.y, align='center',
                          width=30, height=30)
        self.drawHealthBar()
    
    def attack(self):
        app.projectiles.append(fireball(self.x, self.y, self.target,
                                        self.dmg, self.splashRadius,
                                        self.side, str(self)))
        self.alive = False
        self.health = 0

    def __repr__(self):
        return "fireSpirit"
    
    def drawCard(self, x, y, h=None, w=None):
        if h and w != None:
            drawImage(fireSpirit.card, x, y, height=h, width=w)
        else:
            drawImage(fireSpirit.card, x, y)

# Blank Card with template for all Properties

class templateCard(playingCard):
    def __init__(self, x=0, y=0, side=None):
        super().__init__()
        self.health = 0
        self.maxHealth = self.health
        self.dmg = 0
        self.hitSpeed = "Instant, A number"
        self.movementSpeed = "A number"
        self.range = 0
        self.targets = "All, Ground"
        self.atttackType = "Ranged, Melee"
        self.cost = 0
        self.movementType = "Ground, Air"
        self.x = 1000
        self.y = 1000
        self.side = side




def initCard(s, x=0, y=0, side=None):
    if s == "miniPekka":
        return [miniPekka(x, y, side)]
    elif s == "bomber":
        return [bomber(x, y, side)]
    elif s == "knight":
        return [knight(x, y, side)]
    elif s == "skeletons":
        return [skeleton(x+20, y, side),
                skeleton(x-20, y, side),
                skeleton(x, y+20, side)]
    elif s == "wizard":
        return [wizard(x, y, side)]
    elif s == "fireSpirit":
        return [fireSpirit(x, y, side)]
    elif s == "skeleton":
        return [skeleton(x, y, side)]




###############
# Projectiles #
###############

class projectile:

    def __init__(self, x, y, target, dmg, side, spawner):
        self.exists = True
        self.x = x
        self.y = y
        self.target = target
        self.dmg = dmg
        self.side = side
        self.spawner = spawner

    def onStep(self, app):
        if self.target.health > 0:
            self.moveProjectile((self.target.x, self.target.y))
        else:
            self.exists = False
        if distance(self.x, self.y, self.target.x, self.target.y) <= \
            self.target.hitbox + 5:
            self.exists = False
            self.detonate()

    def moveProjectile(self, point):
        # Move Card to the closest Point
        angle = 360 - angleTo(self.x, self.y, point[0], point[1])
        angle = math.radians(angle)
        dx = -self.movementSpeed * math.sin(angle)
        dy = -self.movementSpeed * math.cos(angle)
        self.x += dx
        self.y += dy

    def getEnemiesInRange(self, x, y, side, radius):
        enemies = []
        if side == "player":
            allEnemies = app.enemyCards + app.enemyTowers
        else:
            allEnemies = app.playerCards + app.playerTowers
        
        for i in allEnemies:
            if distance(x, y, i.x, i.y) <= radius*25:
                enemies.append(i)
        
        return enemies

    
    

class arrow(projectile):
    arrowe = "Assets/arrowe.png"
    arrowp = "Assets/arrowp.png"
    cannonball = "Assets/cannonball.png"

    def __init__(self, x, y, target, dmg, side, spawner):
        super().__init__(x, y, target, dmg, side, spawner)
        self.movementSpeed = 15

    def draw(self):
        if self.side == "player":
            if self.spawner == "princessTower":
                drawImage(arrow.arrowp, self.x, self.y, width=20, height=20,
                          align='center')
            else:
                drawImage(arrow.cannonball, self.x, self.y, width=20,
                          height=20, align='center')
        elif self.side == "enemy":
            if self.spawner == "princessTower":
                drawImage(arrow.arrowe, self.x, self.y, width=20, height=20,
                          align='center')
            else:
                drawImage(arrow.cannonball, self.x, self.y, width=20,
                          height=20, align='center')

    def detonate(self):
        self.target.health -= self.dmg
    
class bomb(projectile):

    def __init__(self, x, y, target, dmg, splashRadius, side, spawner):
        super().__init__(x, y, target, dmg, side, spawner)
        self.movementSpeed = 15
        self.splashRadius = splashRadius

    def draw(self):
        drawImage("Assets/bomb.png", self.x, self.y, width=20, height=20,
                  align='center')
    
    def detonate(self):
        for i in self.getEnemiesInRange(self.target.x, self.target.y, \
                                        self.side, self.splashRadius):
            i.health -= self.dmg
            if i.health <= 0:
                i.alive = False

class fireball(projectile):

    def __init__(self, x, y, target, dmg, splashRadius, side, spawner):
        super().__init__(x, y, target, dmg, side, spawner)
        self.movementSpeed = 15
        self.splashRadius = splashRadius

    def draw(self):
        drawImage("Assets/fireball.png", self.x, self.y, width=20, height=20,
                  align='center')

    def detonate(self):
        for i in self.getEnemiesInRange(self.target.x, self.target.y, \
                                        self.side, self.splashRadius):
            i.health -= self.dmg
            if i.health <= 0:
                i.alive = False



##########
# Towers #
##########

class towers:
    
    def __init__(self):
        self.alive = True
    
    def onStep(self, app):
        if self.state == "Idle":
            if self.health < self.maxHP:
                self.activate()
        if self.alive:
            if self.mode == "Battling":
                self.fight(app)
                if self.target.health <= 0:
                    self.target.alive = False
                    self.target = None
                    self.mode = "Idle"
            elif self.mode == "Idle":
                target = self.getTarget(app)
                if self.targetInRange(target) and self.state == "Active":
                    self.mode = "Battling"
                    self.target = target
    
    def fight(self, app):
        if self.cooldown % (app.stepsPerSecond * self.hitSpeed) == 0:
            app.projectiles.append(arrow(self.x, self.y, self.target,
                                         self.dmg, self.side, str(self)))
            self.attack()
        self.cooldown += 1

    def getTarget(self, app):
        possibleTargets = [] # If cards are attacking tower, they take priority
        if self.side == "player":
            for card in app.enemyCards:
                if card.target == self:
                    possibleTargets.append(card)
        else:
            for card in app.playerCards:
                if card.target == self:
                    possibleTargets.append(card)
        if possibleTargets == []:
            if self.side == "player":
                closestCard = self.closestCard(app.enemyCards)
            else:
                closestCard = self.closestCard(app.playerCards)
        else:
            closestCard = self.closestCard(possibleTargets)
        return closestCard
        
    def closestCard(self, cards):
        lowDist = 1000
        closest = None
        radius = self.range * 25
        for i in cards:
            dist = distance(self.x, self.y, i.x, i.y)
            if dist <= radius and dist <= lowDist:
                lowDist = dist
                closest = i
        if closest == None:
            return templateCard()
        return closest
    
    def targetInRange(self, target):
        dist = distance(self.x, self.y, target.x, target.y)
        if dist <= self.range*25:
            return True
        else:
            return False
    
    def drawHealthBar(self):
        if self.health == self.maxHP:
            return
        if self.health > 0:
            drawRect(self.x-(self.hitbox/2), self.y-self.hitbox-4,
                     self.hitbox*(self.health/self.maxHP), 5, fill=self.colour,
                     border=None, align='left')
        drawRect(self.x, self.y-self.hitbox-4, self.hitbox, 5, fill='black',
                 border=self.colour, align='center', borderWidth=0.05,
                 opacity=40)


class princessTower(towers):
    player = "Assets/pPT.png"
    enemy = "Assets/ePT.png"


    def __init__(self, x, y, side):
        super().__init__()
        self.health = 3052
        self.maxHP = self.health
        self.dmg = 109
        self.hitSpeed = 1.1
        self.range = 8
        self.targets = "All"
        self.atttackType = "Ranged"
        self.x = x
        self.y = y
        self.mode = "Idle"
        self.target = None
        self.side = side
        self.state = "Active"
        self.cooldown = 0
        self.hitbox = 37.5
        if self.side == "player":
            self.colour = "blue"
        else:
            self.colour = "red"

    def draw(self):
        if self.alive:

            if self.side == "player":
                drawImage(princessTower.player, self.x, self.y, 
                          align="center", width=128, height=128)
            else:
                drawImage(princessTower.enemy, self.x, self.y, 
                          align="center", width=128, height=128)
            self.drawHealthBar()
    
    def attack(self):
        pass

    def __repr__(self):
        return "princessTower"


class kingTower(towers):
    enemy = ["Assets/eKTIdle.png",
             "Assets/eKTActive.png"]
    player = ["Assets/pKTIdle.png",
              "Assets/pKTActive.png"]

    def __init__(self, x, y, side):
        super().__init__()
        self.health = 4824
        self.maxHP = self.health
        self.dmg = 109
        self.hitSpeed = 1.25
        self.range = 7.5
        self.targets = "All"
        self.atttackType = "Ranged"
        self.x = x
        self.y = y
        self.state = "Idle" # Can also be "Active" (The tower is hidden) 
        self.mode = "Idle" # The tower has no target
        self.side = side
        self.cooldown = 0
        self.hitbox = 50
        if self.side == "player":
            self.colour = "blue"
        else:
            self.colour = "red"

    def draw(self):
        if self.alive:
            if self.state == "Idle":
                if self.side == "player":
                    drawImage(kingTower.player[0], self.x, self.y, 
                              align="center", width=128, height=128)
                else:
                    drawImage(kingTower.enemy[0], self.x, self.y, 
                              align="center", width=128, height=128)
            else:
                if self.side == "player":
                    drawImage(kingTower.player[1], self.x, self.y, 
                              align="center", width=128, height=128)
                else:
                    drawImage(kingTower.enemy[1], self.x, self.y, 
                              align="center", width=128, height=128)
            self.drawHealthBar()

    def attack(self):
        pass

    def activate(self):
        self.state = "Active"


    def __repr__(self):
        return "kingTower"


##############################
# Elixir and Other Mechanics #
##############################

def elixirOnStep(app):
    if not app.suddenDeath:
        if app.playerElixir > 10:
            app.playerElixir = 10
        else:
            if app.minutes >= 1:
                app.playerElixir += 1/(app.stepsPerSecond*2.8)
            else:
                app.playerElixir += 1/(app.stepsPerSecond*1.4)

        if app.playerElixir > 10:
            app.enemyElixir = 10
        else:
            if app.minutes >= 1:
                app.enemyElixir += 1/(app.stepsPerSecond*2.8)
            else:
                app.enemyElixir += 1/(app.stepsPerSecond*1.4)
    else:
        if app.playerElixir > 10:
            app.playerElixir = 10
        else:
            if app.minutes >= 1:
                app.playerElixir += 1/(app.stepsPerSecond*1.4)
            else:
                app.playerElixir += 1/(app.stepsPerSecond*0.7)

        if app.playerElixir > 10:
            app.enemyElixir = 10
        else:
            if app.minutes >= 1:
                app.enemyElixir += 1/(app.stepsPerSecond*1.4)
            else:
                app.enemyElixir += 1/(app.stepsPerSecond*0.7)


def timerOnStep(app):
    app.gameTimer += 1
    if not app.suddenDeath:
        if app.gameTimer % app.stepsPerSecond == 0:
            if app.minutes == 0 and app.seconds == 0:
                if winnerCheck(app):
                    app.suddenDeath = False
                else:
                    app.suddenDeath = True
                    app.battleMusic[app.battleMusicPlaying].pause()
                    app.suddenDeathMusic.play(loop=True, restart=True)
                    app.minutes = 2
                    app.seconds = 30
            elif app.seconds-1 == -1:
                app.minutes -= 1
                app.seconds = 59
                app.timer = f"{app.minutes}:{app.seconds}"
            elif app.seconds-1 < 10:
                app.seconds -= 1
                app.timer = f"{app.minutes}:0{app.seconds}"
            else:
                app.seconds -=1 
                app.timer = f"{app.minutes}:{app.seconds}"
            
            if app.minutes == 0 and app.seconds > 56:
                app.x2Elixir = True
            elif app.minutes == 0 and app.seconds == 56:
                app.x2Elixir = False

    else:
        if app.gameTimer % app.stepsPerSecond == 0:
            if app.minutes == 0 and app.seconds == 0:
                winnerCheck(app)
            elif app.seconds-1 == -1:
                app.minutes -= 1
                app.seconds = 59
                app.timer = f"{app.minutes}:{app.seconds}"
            elif app.seconds-1 < 10:
                app.seconds -= 1
                app.timer = f"{app.minutes}:0{app.seconds}"
            else:
                app.seconds -=1 
                app.timer = f"{app.minutes}:{app.seconds}"
            
            if app.minutes == 0 and app.seconds > 56:
                app.x3Elixir = True
            elif app.minutes == 0 and app.seconds == 56:
                app.x3Elixir = False

def checkClick(app, x, y):
    if not app.gameOver:
        #Check if click on arena
        if (149 <= x <= 605) and (20 <= y <= 780):
            # Makes sure not to spawn card if click in tower
            if not checkClickInTower(x, y):
                placeCard(app, x, y, "player")
                app.highlightTile = (False, app.highlightTile[1],
                                    app.highlightTile[2])
        
        if 648 <= x <= 795:
            if 24 <= y <= 204:
                app.playerCardSelected = app.playerDeck[0]
                app.playerCardSelectedIndex = 0
            elif 214 <= y <= 394:
                app.playerCardSelected = app.playerDeck[1]
                app.playerCardSelectedIndex = 1
            elif 404 <= y <= 584:
                app.playerCardSelected = app.playerDeck[2]
                app.playerCardSelectedIndex = 2
            elif 594 <= y <= 774:
                app.playerCardSelected = app.playerDeck[3]
                app.playerCardSelectedIndex = 3
    else:
        if 446 <= x <= 574 and 679 <= y <= 729:
            app.gameOver = False
            app.ai = None
            app.HomePage = True
            app.battleArena = False
            app.suddenDeath = False
            app.ultimateDeath = False
            app.lobbyMusicPlaying = random.randint(0, len(app.lobbyMusic)-1)
            app.lobbyMusic[app.lobbyMusicPlaying].play(loop=True)

def checkClickInTower(x, y):
    if ((200 <= x <= 276) and (603 <= y <= 679)) or \
        ((200 <= x <= 276) and (122 <= y <= 197)) or \
        ((478 <= x <= 554) and (603 <= y <= 679)) or \
        ((478 <= x <= 554) and (122 <= y <= 197)) or \
        ((327 <= x <= 428) and (21 <= y <= 121)) or \
        ((327 <= x <= 428) and (679 <= y <= 780)):
        return True
    else:
        return False

def getCardPlacementLocation(side, x, y):
    if side == "player":
        x0, y0 = 149, 425
        x1, y1 = 605, 780
    else:
        x0, y0 = 149, 20
        x1, y1 = 605, 375
    if x0 <= x <= x1:
        if y0 <= y <= y1:
            x = ((x-x0)//25)*25+x0+12.5
            y = ((y-y0)//25)*25+y0+12.5
        else:
            if side == "player":
                y = 437.5
            else:
                y = 362.5
            x = ((x-x0)//25)*25+x0+12.5

    return x, y

def winnerCheck(app):
    # The count of towers aliver per player
    pCount = 0
    eCount = 0
    for i in range(3):
        if app.playerTowers[i].alive:
            pCount += 1
        if app.enemyTowers[i].alive:
            eCount += 1
    if pCount > eCount:
        app.winner = "player"
        app.gameOver = True
        if not app.suddenDeath:
            app.battleMusic[app.battleMusicPlaying].pause()
        else:
            app.suddenDeathMusic.pause()
        return True
    elif pCount < eCount:
        app.winner = "enemy"
        app.gameOver = True
        if not app.suddenDeath:
            app.battleMusic[app.battleMusicPlaying].pause()
        else:
            app.suddenDeathMusic.pause()
        return True
    else:
        if app.ultimateDeath:
            if app.utDeathP == 1 and app.utDeathE == 1:
                app.winner = "draw"
                app.utDeathP = 0
                app.utDeathE = 0

        return False
    

def ultimateDeathOnStep(app):
    for i in range(3):
        if app.playerTowers[i].alive:
            app.playerTowers[i].health -= 1
            if app.playerTowers[i].health <= 0:
                app.playerTowers[i].alive = False
                app.ultimateDeath = False
                app.utDeathP += 1
        if app.enemyTowers[i].alive:
            app.enemyTowers[i].health -= 1
            if app.enemyTowers[i].health <= 0:
                app.enemyTowers[i].alive = False
                app.ultimateDeath = False
                app.utDeathE += 1
    winnerCheck(app)

    app.utDeathP = 0
    app.utDeathE = 0

def highlightTile(app, x, y):
    x0, y0 = 149, 425
    x1, y1 = 605, 780
    if x0 <= x <= x1 and y0 <= y <= y1 and not checkClickInTower(x, y):
        x = ((x-x0)//25)*25+x0+12.5
        y = ((y-y0)//25)*25+y0+12.5
        app.highlightTile = (True, x, y)
    else:
        app.highlightTile = (False, x, y)



# All stats and cards gained from https://statsroyale.com 
# (with slight modifications)
# https://github.com/smlbiobot/cr-assets-png/tree/master (All sprites)
# https://youtube.com/playlist?list=PLlpyBoP2Q5ysDKNHzhhqioz2EOS0Rk3O6&si=HBfEfoCYcVRNfmrE (All the music)
# Fireball Picture https://www.nicepng.com/ourpic/u2q8y3r5e6y3w7y3_fireball-best-clip-art-fireball/