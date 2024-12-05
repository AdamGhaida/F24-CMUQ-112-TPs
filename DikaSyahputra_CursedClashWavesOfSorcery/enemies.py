from cmu_graphics import *
import random
import math
from moves import *

from PIL import Image as PilImage
import os
import pathlib

def openImage(fileName):
    return PilImage.open(os.path.join(pathlib.Path(__file__).parent, fileName))

############################################################
### ENEMIES ###
############################################################
class Enemy:
    enemyList = []
    # Initializes important variables for an enemy and appends it to enemyList
    def __init__(self, hp, speed):
        # Spawns enemies in a random X and Y coordinate in the game map
        self.hp, self.maxHp, self.speed = hp, hp, speed
        self.x = random.randint(25, 1975)
        self.y = random.randint(25, 1975)
        # Initialize stun, iFrame duration, facing, followingMoves, and if the
        # enemy is blocking or not
        self.stun = 60
        self.iFrameLen = 0
        self.width = 50
        self.height = 50
        self.isBlocking = False
        self.facing = 'right'
        self.followingMove = None
        self.followingMoveDuration = 0
        Enemy.enemyList.append(self)
    
    # Faces the enemies right if dx is positive and left if dx is negative
    def changeFacing(self, dx, dy):
        if dx < 0:
            self.facing, self.facingIndex = 'left', 0
        elif dx > 0:
            self.facing, self.facingIndex = 'right', 1
    
    # Gets the distance of the enemy to the player
    def getDistToPlayer(self, player):
        return ((player.x - self.x)**2 + (player.y - self.y)**2)**0.5
    
    # Gets the angle of the enemy to the player in degrees
    def getAngleToPlayer(self, player):
        return (math.atan2(player.y - self.y, player.x - self.x) *\
                (-180 / math.pi) % 360)
    
    # Moves the enemy to the player if they are farther than 50 px in distance
    def enemyBehavior(self, player):
        angle = math.atan2(player.y - self.y, player.x - self.x)
        # Only allows them to move if they aren't stunned and no followingMoves
        if self.stun == 0 and self.getDistToPlayer(player) > 50:
            # Calculates angular speed
            dx, dy = self.speed * math.cos(angle), self.speed * math.sin(angle)
            self.changeFacing(dx, dy)
            self.x += dx
            self.y += dy
    
    # Removes duration for stun, iFrame duration, and followingMove duration
    def onStep(self, app):
        if self.iFrameLen > 0: self.iFrameLen -= 1
        if self.stun > 0: self.stun -= 1
        if self.followingMoveDuration > 0:
            self.followingMoveDuration -= 1
    
    # Draws the health bar that will appear on top of the enemy
    def drawEnemy(self, app):
        if self.hp > 0:
            drawRect(self.x - app.scrollX - 50, self.y - app.scrollY - 40,
                 (self.hp/self.maxHp)*100, 10,
                 fill=gradient('green', 'chartreuse', start='left'))
        drawImage(CMUImage(openImage(f'images/enemyhpbar.png')),
                  self.x - app.scrollX, self.y - app.scrollY - 35,
                  align='center', height=15)

############################################################
### GRADE 3 ENEMIES ###
############################################################
class GradeThree(Enemy):
    # Initializes important variables for a Grade Tree enemy and appends it to
    # enemyList
    def __init__(self):
        # Initializes the Hp and speed to the superclass
        super().__init__(50, 2)
        self.mouse1CD, self.move1CD = 0, 0
        self.facingIndex = 1
        # Sprite images for the enemy
        self.imgList = [CMUImage(openImage(f'images/enemies/flyhead/left.png')),
                       CMUImage(openImage(f'images/enemies/flyhead/right.png'))]
    
    # Does the cooldown for moves and followingMoves if it exists
    def onStep(self, app):
        super().onStep(app)
        if self.mouse1CD > 0: self.mouse1CD -= 1
        if self.move1CD > 0: self.move1CD -= 1
        # Resets followingMove if the duration is over
        if self.followingMoveDuration == 0:
            self.followingMove = None
            self.speed, self.followingMoveDuration = 2, -1
        # Adds a specific amount of points if killed
        if self.hp <= 0: app.points += 1
    
    # Defines the behavior of the enemy in the game map
    def enemyBehavior(self, player):
        super().enemyBehavior(player)
        # Executes each move based on its cooldown, distance to player, and stun
        if self.mouse1CD == 0 and self.getDistToPlayer(player) <= 80 and\
           self.stun == 0:
            self.executeMouse1()
        if self.move1CD == 0 and self.getDistToPlayer(player) <= 300 and\
           self.stun == 0:
            self.executeMove1()
        # Makes the move follow the enemy if followingMove duration is above 0
        if self.followingMove == 1 and self.followingMoveDuration > 0:
            self.move1.x, self.move1.y = self.x, self.y
    
    # Draws the enemy sprite based on the direction it faces and the hp bar
    def drawEnemy(self, app):
        drawImage(self.imgList[self.facingIndex], self.x - app.scrollX,
                  self.y - app.scrollY, width=60, height=60, align='center')
        super().drawEnemy(app)
    
    # Executes a basic punch attack creating a rectangular EnemyMove
    def executeMouse1(self):
        # Offsets to the left if the enemy is facing left
        if self.facing == 'left':
            self.mouse1 = EnemyMoves(self.x-45, self.y, 'rect', 40,
                                 40, 10, 3, 10, 10, False, -5, 0, 0,
                                     ["images/punch0.png"])
        # Offsets to the right if the enemy is facing right
        elif self.facing == 'right':
            self.mouse1 = EnemyMoves(self.x+45, self.y, 'rect', 40,
                                 40, 10, 3, 10, 10, False, 5, 0, 0,
                                     ["images/punch1.png"])
        self.stun = 15
        self.mouse1CD = 90
    
    # Executes a circular EnemyMove that follows the enemy
    def executeMove1(self):
        # Gets the image of the rotating wings
        imgLst = []
        for i in range(4):
            imgLst.append(CMUImage(openImage("images/enemies/" +\
                          f"flyhead/move1/move1-{i}.png")))
        # Initializes the following moves and makes the circular EnemyMove
        self.followingMove = 1
        self.followingMoveDuration = 120
        self.move1 = EnemyMoves(self.x, self.y, 'oval', 100, 100, 120, 20, 40,
                    20, False, 50, 50, 0, imgLst)
        self.move1CD = 20 * 60
        self.speed = 4

############################################################
### GRADE 2 ENEMIES ###
############################################################
class GradeTwo(Enemy):
    # Initializes important variables for a Grade Two enemy and appends it to
    # enemyList
    def __init__(self):
        # Initializes the Hp and speed to the superclass
        super().__init__(100, 1)
        self.mouse1CD, self.move1CD, self.move2CD = 0, 0, 0
        self.facingIndex = 1
        # Sprite images for the enemy
        self.imgList = [CMUImage(openImage(f'images/enemies/ko-guy/left.png')),
                       CMUImage(openImage(f'images/enemies/ko-guy/right.png'))]
    
    # Does the cooldown for moves
    def onStep(self, app):
        super().onStep(app)
        if self.mouse1CD > 0: self.mouse1CD -= 1
        if self.move1CD > 0: self.move1CD -= 1
        if self.move2CD > 0: self.move2CD -= 1
        # Adds a specific amount of points if killed
        if self.hp <= 0: app.points += 2
    
    # Defines the behavior of the enemy in the game map
    def enemyBehavior(self, player):
        super().enemyBehavior(player)
        # Executes each move based on its cooldown, distance to player, and stun
        if self.move1CD == 0 and self.getDistToPlayer(player) <= 80 and\
           self.stun == 0:
            self.executeMove1()
        if self.move2CD == 0 and self.getDistToPlayer(player) <= 150 and\
           self.stun == 0:
            self.executeMove2()
        if self.mouse1CD == 0 and self.getDistToPlayer(player) <= 80 and\
           self.stun == 0:
            self.executeMouse1()
    
    # Draws the enemy sprite based on the direction it faces and the hp bar
    def drawEnemy(self, app):
        drawImage(self.imgList[self.facingIndex], self.x - app.scrollX,
                  self.y - app.scrollY, width=90, height=90, align='center')
        super().drawEnemy(app)
    
    # Executes a basic punch attack creating a rectangular EnemyMove
    def executeMouse1(self):
        # Offsets to the left if the enemy is facing left
        if self.facing == 'left':
            self.mouse1 = EnemyMoves(self.x-50, self.y, 'rect', 50,
                                 50, 10, 5, 10, 15, False, -5, 0, 0,
                                     ["images/punch0.png"])
        # Offsets to the right if the enemy is facing right
        elif self.facing == 'right':
            self.mouse1 = EnemyMoves(self.x+50, self.y, 'rect', 50,
                                 50, 10, 5, 10, 15, False, 5, 0, 0,
                                     ["images/punch1.png"])
        self.stun = 15
        self.mouse1CD = 75
    
    # Executes a barrage attack creating a rectangular EnemyMove dealing damage
    # over time
    def executeMove1(self):
        # Gets the images of the barrage moves
        images = [[], []]
        for i in range(2):
            images[0].append(CMUImage(openImage("images/enemies/ko-guy/moves" +\
                      f"/0/left{i}.png")))
        for i in range(2):
            images[1].append(CMUImage(openImage("images/enemies/ko-guy/moves" +\
                      f"/0/right{i}.png")))
        # Offsets to the left if the enemy is facing left and gets the left
        # facing move image
        if self.facing == 'left':
            self.move1 = EnemyMoves(self.x-65, self.y, 'rect', 80,
                                 80, 60, 4, 12, 30, False, -2, 0, 0, images[0])
        # Offsets to the right if the enemy is facing right and gets the right
        # facing move image
        elif self.facing == 'right':
            self.move1 = EnemyMoves(self.x+65, self.y, 'rect', 80,
                                 80, 60, 4, 12, 30, False, 2, 0, 0, images[1])
        self.stun = 120
        self.move1CD = 15 * 60
    
    # Executes a quake attack creating a circular EnemyMove dealing damage over
    # time
    def executeMove2(self):
        images = [CMUImage(openImage("images/enemies/ko-guy/moves/1/" +\
                                     f"{i}.png")) for i in range(4)]
        self.move2 = EnemyMoves(self.x, self.y, 'oval', 400, 400, 120, 6, 24,
                                22, True, 7, 7, 30, images)
        self.stun = 180
        self.move2CD = 35 * 60

############################################################
### GRADE 1 ENEMIES ###
############################################################
class GradeOne(Enemy):
    # Initializes important variables for a Grade One enemy and appends it to
    # enemyList
    def __init__(self):
        # Initializes the Hp and speed to the superclass
        super().__init__(150, 3)
        self.mouse1CD, self.move1CD, self.move2CD, self.move3CD = 0, 0, 0, 0
        self.regenDuration, self.facingIndex = 0, 1
        # Sprite images for the enemy and its aura when regenerating
        self.imgList = [CMUImage(openImage('images/enemies/bearer/left.png')),
                       CMUImage(openImage('images/enemies/bearer/right.png'))]
        self.auraImg = [CMUImage(openImage("images/enemies/bearer/moves/2/" +\
                        f"{i}.png")) for i in range(4)]
        # Important aura index and img counter change for aura animations
        self.auraIndex, self.imgCounter = 0, 0
    
    # Draws the enemy sprite based on the direction it faces and the hp bar
    def drawEnemy(self, app):
        drawImage(self.imgList[self.facingIndex], self.x - app.scrollX,
                  self.y - app.scrollY, width=50, height=50, align='center')
        super().drawEnemy(app)
        # Draws the aura on the enemy if it's using a regenerating move
        if self.regenDuration > 0:
            drawImage(self.auraImg[self.auraIndex], self.x - app.scrollX,
                      self.y - app.scrollY, width=50, height=50, align='center',
                      opacity=50)
    
    # Does the cooldown for moves and regenerating duration
    def onStep(self, app):
        super().onStep(app)
        if self.mouse1CD > 0: self.mouse1CD -= 1
        if self.move1CD > 0: self.move1CD -= 1
        if self.move2CD > 0: self.move2CD -= 1
        if self.move3CD > 0: self.move3CD -= 1
        if self.regenDuration > 0:
            self.regenDuration -= 1
            # Changes the frame of the aura GIF every 5 steps
            self.imgCounter += 1
            if self.imgCounter % 5 == 0:
                self.auraIndex = (self.auraIndex + 1) % 4
            # Regenerates one Hp per step
            if self.hp < self.maxHp: self.hp += 1
        # Adds a specific amount of points if killed
        if self.hp <= 0: app.points += 3
    
    # Defines the behavior of the enemy in the game map
    def enemyBehavior(self, player):
        super().enemyBehavior(player)
        # Executes each move based on its cooldown, distance to player, and stun
        if self.move1CD == 0 and self.getDistToPlayer(player) <= 200 and\
           self.stun == 0:
            self.executeMove1(player)
        if self.move2CD == 0 and self.getDistToPlayer(player) <= 100 and\
           self.stun == 0:
            self.executeMove2(player)
        if self.mouse1CD == 0 and self.getDistToPlayer(player) <= 80 and\
           self.stun == 0:
            self.executeMouse1()
        if self.move3CD == 0 and self.stun == 0:
            self.executeMove3()
    
    # Executes a basic punch attack creating a rectangular EnemyMove
    def executeMouse1(self):
        # Offsets to the left if the enemy is facing left
        if self.facing == 'left':
            self.mouse1 = EnemyMoves(self.x-45, self.y, 'rect', 40,
                                 40, 10, 8, 10, 20, False, -5, 0, 0,
                                     ["images/punch0.png"])
        # Offsets to the right if the enemy is facing right
        elif self.facing == 'right':
            self.mouse1 = EnemyMoves(self.x+45, self.y, 'rect', 40,
                                 40, 10, 8, 10, 20, False, 5, 0, 0,
                                     ["images/punch1.png"])
        self.stun = 15
        self.mouse1CD = 60
    
    # Executes a deafening sound move creating a cone EnemyMove with high stun
    def executeMove1(self, player):
        angle = self.getAngleToPlayer(player)
        images = [CMUImage(openImage("images/enemies/bearer/moves/0/" +\
                  f"{i}.png")) for i in range(5)]
        self.move1 = EnemyMoves(self.x, self.y, 'cone', 400, 400, 10, 45, 10,
                                180, True, 0, 0, 60, images, angle-35, 70)
        self.move1CD = 60 * 60
    
    # Executes an orange energy blast move by creating a circular EnemyMove
    def executeMove2(self, player):
        images = [CMUImage(openImage("images/enemies/bearer/moves/1/img.png"))]
        self.move2 = EnemyMoves(self.x, self.y, 'oval', 300, 300, 10, 50, 10,
                                180, True, 0, 0, 60, images)
        self.move2CD = 60 * 60
    
    # Executes a regeneration act when the enemy's hp is under 75 inclusively
    def executeMove3(self):
        if self.hp <= 75:
            self.regenDuration = 40
            self.stun = 60
            self.move3CD = 45 * 60
    
############################################################
### BOSSES ###
############################################################
class Bosses(Enemy):
    # Initializes important variables for bosses and appends it to enemyList
    def __init__(self, hp, speed):
        # Initializes the Hp and speed to the superclass
        super().__init__(hp, speed)
        # Initializes regenerating cooldown and imgCounter for walking animation
        self.regenCD = 20 * 60
        self.imgCounter = 0
    
    # Does the cooldown for moves, phase changing, and regenerating duration
    def onStep(self, app):
        super().onStep(app)
        self.phaseChange()
        if self.mouse1CD > 0: self.mouse1CD -= 1
        if self.move1CD > 0: self.move1CD -= 1
        if self.move2CD > 0: self.move2CD -= 1
        if self.regenCD > 0 and self.hp < self.maxHp: self.regenCD -= 1
        # Regenerates 10 hp every 20 seconds
        if self.regenCD == 0 and self.hp <= self.maxHp - 10:
            self.hp += 10
            self.regenCD = 20 * 60
        # Adds a specific amount of points if killed
        if self.hp <= 0: app.points += 20
    
    # Changes the boss' phase every one third decrease of maxHp
    def phaseChange(self):
        if self.hp <= 333 and self.phase != 3:
            self.phase = 3
            self.move1CD, self.move2CD = 0, 0
        elif 333 < self.hp <= 666 and self.phase != 2:
            self.phase = 2
            self.move1CD, self.move2CD = 0, 0
        elif 666 < self.hp <= 1000 and self.phase != 1:
            self.phase = 1
            self.move1CD, self.move2CD = 0, 0
    
    # Executes move1 based on the phase the enemy is in
    def executeMove1(self, player):
        if self.phase == 1:
            self.phase1Move1(player)
        if self.phase == 2:
            self.phase2Move1(player)
        if self.phase == 3:
            self.phase3Move1(player)
    
    # Executes move2 based on the phase the enemy is in
    def executeMove2(self, player):
        if self.phase == 1:
            self.phase1Move2(player)
        if self.phase == 2:
            self.phase2Move2(player)
        if self.phase == 3:
            self.phase3Move2(player)
    
    # Draws a big health bar that will appear on top of the boss
    def drawEnemy(self, app):
        if self.hp > 0:
            drawRect(self.x - app.scrollX - 150, self.y - app.scrollY - 40,
                 (self.hp/self.maxHp)*300, 10,
                 fill=gradient('green', 'chartreuse', start='left'))
        drawImage(CMUImage(openImage(f'images/enemyhpbar.png')),
                  self.x - app.scrollX, self.y - app.scrollY - 35,
                  align='center', height=25, width=300)

############################################################
### MAHITO ###
############################################################
class Mahito(Bosses):
    # Initializes important variables for Mahito and appends it to enemyList
    def __init__(self):
        # Initializes the Hp and speed to the superclass
        super().__init__(1000, 3)
        # Initializes base phase, move1 distance, and move2 distance
        self.phase, self.mouse1CD, self.move1CD, self.move2CD = 1, 0, 0, 0
        self.move1Dist, self.move2Dist = 600, 375
        # Damage boost timer
        self.damageBoost = 0
        self.domainCasted = False
        # Walking images and sprites for animations
        self.images, self.imgIndex, self.facingIndex = [[], []], 0, 1
        self.images[0] = [CMUImage(openImage("images/enemies/mahito/walk/" +\
                          f"left{i}.png")) for i in range(4)]
        self.images[1] = [CMUImage(openImage("images/enemies/mahito/walk/" +\
                          f"right{i}.png")) for i in range(4)]
    
    # Draws the walking animation of the boss
    def drawEnemy(self, app):
        # Draws an opaque red circle around the boss if a domain is casted
        if self.domainCasted:
            drawCircle(self.x - app.scrollX, self.y - app.scrollY, 150,
                       fill='red', border='black', dashes=True, opacity=35)
        drawImage(self.images[self.facingIndex][self.imgIndex],
                  self.x - app.scrollX, self.y - app.scrollY, align='center')
        super().drawEnemy(app)
        # Draws the aura animation if the boss has a damage boost
        if self.damageBoost > 0:
            drawImage(CMUImage(openImage("images/enemies/mahito/moves/p2m2/" +\
                      "img.png")), self.x - app.scrollX, self.y - app.scrollY,
                      align='center', opacity=50)
    
    # Does the coolodwns for followingMoves, damageBoost duration, and animation
    def onStep(self, app):
        super().onStep(app)
        if self.damageBoost > 0: self.damageBoost -= 1
        if self.followingMoveDuration == 0:
            self.followingMove = None
            self.speed, self.followingMoveDuration = 3, -1
        self.changeMoveDistance()
        self.imgCounter += 1
        if self.imgCounter == 10:
            self.imgIndex = (self.imgIndex + 1) % len(self.images)
            self.imgCounter = 0
    
    # Defines the behavior of the enemy in the game map
    def enemyBehavior(self, player):
        super().enemyBehavior(player)
        # Executes each move based on its cooldown, distance to player, and stun
        if self.move2CD == 0 and self.stun == 0 and\
           self.getDistToPlayer(player) <= self.move2Dist:
            self.executeMove2(player)
        if self.move1CD == 0 and self.stun == 0 and\
           self.getDistToPlayer(player) <= self.move1Dist:
            self.executeMove1(player)
        if self.mouse1CD == 0 and self.getDistToPlayer(player) <= 50 and\
           self.stun == 0:
            self.executeMouse1()
        # Changes the following move coordinates to follow the boss
        if self.followingMove == 1 and self.followingMoveDuration > 0:
            angle = math.atan2(player.y - self.y, player.x - self.x)
            dx, dy = self.speed * math.cos(angle), self.speed * math.sin(angle)
            if self.getDistToPlayer(player) > 150:
                self.x, self.y = self.x + dx, self.y + dy
                self.move1.x, self.move1.y = self.x, self.y
        # If domain is casted, decreases the player's hp if nearby the boss
        if self.domainCasted:
            if self.move1 not in EnemyDomains.enemyDomains:
                self.domainCasted = False
            if self.getDistToPlayer(player) <= 150: player.hp -= 1
    
    # Changes the distance to player required to execute moves for each phase
    def changeMoveDistance(self):
        if self.phase == 1:
            self.move1Dist, self.move2Dist = 600, 375
        if self.phase == 2:
            self.move1Dist, self.move2Dist = 400, float('inf')
        if self.phase == 3:
            self.move1Dist, self.move2Dist = float('inf'), float('inf')
    
    # Executes a basic punch attack creating a rectangular EnemyMove
    def executeMouse1(self):
        dmg = 14 if self.damageBoost > 0 else 11
        # Offsets to the left if the enemy is facing left
        if self.facing == 'left':
            self.mouse1 = EnemyMoves(self.x-50, self.y, 'rect', 50,
                                 50, 10, dmg, 10, 20, False, -5, 0, 0,
                                     ["images/punch0.png"])
        # Offsets to the right if the enemy is facing right
        elif self.facing == 'right':
            self.mouse1 = EnemyMoves(self.x+50, self.y, 'rect', 50,
                                 50, 10, dmg, 10, 20, False, 5, 0, 0,
                                     ["images/punch1.png"])
        self.stun = 15
        self.mouse1CD = 90
    
    # Randomly spawn normal enemies around the boss
    def phase1Move1(self, player):
        num = random.randint(1, 3)
        if num == 1:
            for i in range(6):
                e = GradeThree()
                e.x = self.x + random.randint(-200, 200)
                e.y = self.y + random.randint(-200, 200)
        if num == 2:
            for i in range(4):
                e = GradeTwo()
                e.x = self.x + random.randint(-200, 200)
                e.y = self.y + random.randint(-200, 200)
        if num == 3:
            for i in range(2):
                e = GradeOne()
                e.x = self.x + random.randint(-200, 200)
                e.y = self.y + random.randint(-200, 200)
        self.move1CD = 60 * 60
    
    # Executes a circular EnemyMove on the player's position (has high stun)
    def phase1Move2(self, player):
        img = [CMUImage(openImage(f"images/enemies/mahito/moves/p1m2/{i}.png"))
               for i in range(5)]
        EnemyMoves(player.x, player.y, 'oval', 250, 250, 10, 20, 10, 180, True,
                   0, 0, 60, img)
        self.move2CD = 30 * 60
        Sound("sounds/enemies/mahito/p1m2.mp3").play(restart=True)
    
    # Launches towards the player and deals a flurry of slashes (circular move)
    def phase2Move1(self, player):
        self.followingMove = 1
        self.followingMoveDuration = 120
        img = [CMUImage(openImage(f"images/enemies/mahito/moves/p2m1/{i}.png"))
               for i in range(4)]
        self.move1 = EnemyMoves(self.x, self.y, 'oval', 500, 500, 180, 4, 10,
                                8, False, 0, 0, 120, img)
        self.stun = 300
        self.move1CD = 40 * 60
        self.speed = 7
        Sound("sounds/enemies/mahito/p2m1.mp3").play(restart=True)
    
    # Boosts the damage the boss deals for mouse1 hits
    def phase2Move2(self, player):
        self.damageBoost = 45 * 60
        self.move2CD = 60 * 60
    
    # Casts a domain called "Self-Embodiment of Perfection"
    def phase3Move1(self, player):
        app.cutscene = True
        app.cutsceneLen = 60
        app.cutsceneImg = CMUImage(openImage("images/enemies/mahito/" +\
                                             "moves/p3m1/cutscene.png"))
        Sound("sounds/enemies/mahito/p3m1.mp3").play(restart=True, loop=False)
        self.move1 = EnemyDomains('hands', 20*60, app.domainSounds[3])
        self.move1CD = 150 * 60
        self.stun = 120
        self.domainCasted = True
        app.currentSound.pause()
        app.domainSounds[3].play(restart=True, loop=False)
    
    # Launches 8 circular EnemyMove restricting hands around the player
    def phase3Move2(self, player):
        img = [CMUImage(openImage(f"images/enemies/mahito/moves/p3m2/{i}.png"))
               for i in range(5)]
        for angle in range(0, 360, 45):
            cx = player.x + (150 * math.cos(math.radians(angle)))
            cy = player.y + (150 * math.sin(math.radians(angle)))
            EnemyMoves(cx, cy, 'oval', 200, 200, 10, 50, 10, 90, True, 0, 0, 30,
                       img)
        self.move2CD = 45 * 60
        Sound("sounds/enemies/mahito/p3m2.mp3").play(restart=True)

############################################################
### SUKUNA ###
############################################################
class Sukuna(Bosses):
    # Initializes important variables for Sukuna and appends it to enemyList
    def __init__(self):
        super().__init__(1000, 3)
        self.phase, self.mouse1CD, self.move1CD, self.move2CD = 1, 0, 0, 0
        self.move1Dist, self.move2Dist = 150, 185
        self.images, self.imgIndex, self.facingIndex = [[], []], 0, 1
        self.images[0] = [CMUImage(openImage("images/enemies/sukuna/walk/" +\
                          f"left{i}.png")) for i in range(6)]
        self.images[1] = [CMUImage(openImage("images/enemies/sukuna/walk/" +\
                          f"right{i}.png")) for i in range(6)]
    
    # Draws the walking animation of the boss
    def drawEnemy(self, app):
        drawImage(self.images[self.facingIndex][self.imgIndex],
                  self.x - app.scrollX, self.y - app.scrollY, align='center')
        super().drawEnemy(app)
    
    # Does the cooldowns for animation and moveDistance change
    def onStep(self, app):
        super().onStep(app)
        self.changeMoveDistance()
        self.imgCounter += 1
        if self.imgCounter == 10:
            self.imgIndex = (self.imgIndex + 1) % len(self.images)
            self.imgCounter = 0
    
    # Defines the behavior of the enemy in the game map
    def enemyBehavior(self, player):
        super().enemyBehavior(player)
        # Executes each move based on its cooldown, distance to player, and stun
        if self.move2CD == 0 and self.stun == 0 and\
           self.getDistToPlayer(player) <= self.move2Dist:
            self.executeMove2(player)
        if self.move1CD == 0 and self.stun == 0 and\
           self.getDistToPlayer(player) <= self.move1Dist:
            self.executeMove1(player)
        if self.mouse1CD == 0 and self.getDistToPlayer(player) <= 60 and\
           self.stun == 0:
            self.executeMouse1()
    
    # Changes the distance to player required to execute moves for each phase
    def changeMoveDistance(self):
        if self.phase == 1:
            self.move1Dist, self.move2Dist = 150, 185
        if self.phase == 2:
            self.move1Dist, self.move2Dist = 500, 400
        if self.phase == 3:
            self.move1Dist, self.move2Dist = float('inf'), 300
    
    # Executes a basic punch attack creating a rectangular EnemyMove
    def executeMouse1(self):
        # Offsets to the left if the enemy is facing left
        if self.facing == 'left':
            self.mouse1 = EnemyMoves(self.x-55, self.y, 'rect', 60,
                                 60, 10, 10, 10, 20, False, -5, 0, 0,
                                 ["images/dism0.png"])
        # Offsets to the right if the enemy is facing right
        elif self.facing == 'right':
            self.mouse1 = EnemyMoves(self.x+55, self.y, 'rect', 60,
                                 60, 10, 10, 10, 20, False, 5, 0, 0,
                                 ["images/dism0.png"])
        self.stun = 15
        self.mouse1CD = 90
    
    # Launches a rectangular blockable move on the player's position
    def phase1Move1(self, player):
        self.move1 = EnemyMoves(player.x, player.y, 'rect', 60, 60, 10, 35, 10,
                                45, False, 0, 0, 30,
            [CMUImage(openImage("images/enemies/sukuna/moves/p1m1/img.png"))])
        self.stun = 10
        self.move1CD = 35 * 60
        Sound("sounds/enemies/sukuna/p1m1.mp3").play(restart=True)
    
    # Launches a flurry of slashes in a cone shaped EnemyMove
    def phase1Move2(self, player):
        angle = self.getAngleToPlayer(player)
        img = [CMUImage(openImage(f"images/enemies/sukuna/moves/p1m2/{i}.png"))
               for i in range(2)]
        self.move2 = EnemyMoves(self.x, self.y, 'cone', 700, 700, 60, 4, 6, 5,
                                False, 0, 0, 60, img, angle-25, 50)
        self.stun = 70
        self.move2CD = 45 * 60
        Sound("sounds/enemies/sukuna/p1m2.mp3").play(restart=True)
    
    # Launches the projectile called 'fuga'
    def phase2Move1(self, player):
        # Initiates a cutscene
        app.cutscene = True
        app.cutsceneLen = 60
        app.cutsceneImg = CMUImage(openImage("images/globalmoves/fugaExe/" +\
                                             "cutscene.png"))
        Sound("sounds/characters/yuji/move6.mp3").play(restart=True,
                                                        loop=False)
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.move1 = EnemyProjectiles(self.x, self.y, 20, 20, 60, angle, 7,
                    'fuga', [CMUImage(openImage("images/globalmoves/fugaAim/" +\
                     f"{i}.png")) for i in range(3)])
        self.stun = 60
        self.move1CD = 40 * 60
    
    # Unleash 30 circles of dismantles around the map randomly
    def phase2Move2(self, player):
        img = [CMUImage(openImage(f"images/enemies/sukuna/moves/p2m2/{i}.png"))
               for i in range(4)]
        for i in range(30):
            randomX = random.randint(100, 1900)
            randomY = random.randint(100, 1900)
            EnemyMoves(randomX, randomY, 'oval', 200, 200, 60, 10, 10, 60,
                       False, 0, 0, 60, img)
        self.move2CD = 35 * 60
        Sound("sounds/enemies/sukuna/p2m2.mp3").play(restart=True)
    
    # Expands the domain called "Malevolent Shrine"
    def phase3Move1(self, player):
        # Initiates a cutscene
        app.cutscene = True
        app.cutsceneLen = 60
        app.cutsceneImg = CMUImage(openImage("images/enemies/sukuna/" +\
                                             "moves/p3m1/cutscene.png"))
        Sound("sounds/enemies/sukuna/p3m1.mp3").play(restart=True, loop=False)
        self.move1 = EnemyDomains('shrine', 20*60, app.domainSounds[1])
        self.move1CD = 150 * 60
        self.stun = 120
        app.currentSound.pause()
        app.domainSounds[1].play(restart=True, loop=False)
    
    # Unleashes a rectangular EnemyMove slash that cuts the world (one shots)
    def phase3Move2(self, player):
        img = [CMUImage(openImage("images/enemies/sukuna/moves/p3m2/img.png"))]
        if self.facing == 'left':
            self.mouse1 = EnemyMoves(self.x-225, self.y, 'rect', 400,
                                 250, 10, 250, 10, 20, True, 0, 0, 90, img)
        elif self.facing == 'right':
            self.mouse1 = EnemyMoves(self.x+225, self.y, 'rect', 400,
                                 250, 10, 250, 10, 20, True, 0, 0, 90, img)
        self.stun = 120
        self.move2CD = 90 * 60
        Sound("sounds/enemies/sukuna/p3m2.mp3").play(restart=True)

############################################################
### JOGO ###
############################################################
class Jogo(Bosses):
    # Initializes important variables for Jogo and appends it to enemyList
    def __init__(self):
        super().__init__(1000, 3)
        self.phase, self.mouse1CD, self.move1CD, self.move2CD = 1, 0, 0, 0
        self.move1Dist, self.move2Dist, self.burningHeat = 175, 300, 0
        self.images, self.imgIndex, self.facingIndex = [], 0, 1
        self.images.append(CMUImage(openImage("images/enemies/jogo/left.png")))
        self.images.append(CMUImage(openImage("images/enemies/jogo/right.png")))
    
    # Draws the walking animation of the boss
    def drawEnemy(self, app):
        drawImage(self.images[self.facingIndex], self.x - app.scrollX,
                  self.y - app.scrollY, align='center')
        super().drawEnemy(app)
        # Draws an opaque red circle around the boss if burningHeat is casted
        if self.burningHeat > 0:
            drawCircle(self.x - app.scrollX, self.y - app.scrollY, 75,
                       fill='red', border='black', dashes=True, opacity=35)
            drawImage(CMUImage(openImage("images/enemies/jogo/moves/p1m2/" +\
                      "img.png")), self.x - app.scrollX, self.y - app.scrollY,
                      align='center', opacity=50)
    
    # Does the cooldowns for moveDistance change
    def onStep(self, app):
        super().onStep(app)
        self.changeMoveDistance()
    
    # Defines the behavior of the enemy in the game map
    def enemyBehavior(self, player):
        super().enemyBehavior(player)
        # Executes each move based on its cooldown, distance to player, and stun
        if self.move2CD == 0 and self.stun == 0 and\
           self.getDistToPlayer(player) <= self.move2Dist:
            self.executeMove2(player)
        if self.move1CD == 0 and self.stun == 0 and\
           self.getDistToPlayer(player) <= self.move1Dist:
            self.executeMove1(player)
        if self.mouse1CD == 0 and self.getDistToPlayer(player) <= 50 and\
           self.stun == 0:
            self.executeMouse1()
        # Decreases the player's hp if nearby
        if self.burningHeat > 0:
            self.burningHeat -= 1
            if self.getDistToPlayer(player) <= 75: player.hp -= 1
    
    # Changes the distance to player required to execute moves for each phase
    def changeMoveDistance(self):
        if self.phase == 1:
            self.move1Dist, self.move2Dist = 175, 300
        if self.phase == 2:
            self.move1Dist, self.move2Dist = 275, 400
        if self.phase == 3:
            self.move1Dist, self.move2Dist = float('inf'), 350
    
    # Executes a basic punch attack creating a rectangular EnemyMove
    def executeMouse1(self):
        # Offsets to the left if the enemy is facing left
        if self.facing == 'left':
            self.mouse1 = EnemyMoves(self.x-50, self.y, 'rect', 50,
                                 50, 10, 12, 10, 20, False, -5, 0, 0,
                                     ["images/punch0.png"])
        # Offsets to the right if the enemy is facing right
        elif self.facing == 'right':
            self.mouse1 = EnemyMoves(self.x+50, self.y, 'rect', 50,
                                 50, 10, 12, 10, 20, False, 5, 0, 0,
                                     ["images/punch1.png"])
        self.stun = 15
        self.mouse1CD = 90
    
    # Shoots fire by initializing a cone EnemyMove
    def phase1Move1(self, player):
        angle = self.getAngleToPlayer(player)
        img = [CMUImage(openImage(f"images/enemies/jogo/moves/p1m1/{i}.png"))
               for i in range(5)]
        self.move1 = EnemyMoves(self.x, self.y, 'cone', 400, 400, 10, 20, 10,
                                45, False, 10, 10, 30, img, angle-30, 60)
        self.stun = 30 + 30
        self.move1CD = 20*60
        Sound("sounds/enemies/jogo/p1m1.mp3").play(restart=True)
    
    # Enables burning heat so that if a player comes close, they lose hp
    def phase1Move2(self, player):
        self.burningHeat = 10 * 60
        self.stun = 20
        self.move2CD = 75 * 60
    
    # Shoots fire in 4 directions around the boss using 4 cone EnemyMoves
    def phase2Move1(self, player):
        angle = self.getAngleToPlayer(player)
        img = [CMUImage(openImage(f"images/enemies/jogo/moves/p2m1/{i}.png"))
               for i in range(5)]
        for i in range(4):
            self.move1 = EnemyMoves(self.x, self.y, 'cone', 600, 600, 20, 2, 1,
                                   1, False, 0, 0, 90, img, angle-30 + 90*i, 60)
        self.move1CD = 25 * 60
        self.stun = 60 + 90
        Sound("sounds/enemies/jogo/p2m1.mp3").play(restart=True)
    
    # Erupts the ground where the player is standing (circular EnemyMove)
    def phase2Move2(self, player):
        img = [CMUImage(openImage(f"images/enemies/jogo/moves/p2m2/{i}.png"))
               for i in range(5)]
        self.move2 = EnemyMoves(player.x, player.y, 'oval', 400, 400, 10, 30,
                                10, 90, True, 20, 20, 60, img)
        self.move2CD = 37 * 60
        Sound("sounds/enemies/jogo/p2m2.mp3").play(restart=True)
    
    # Expands the domain called "Coffin of the Iron Mountain"
    def phase3Move1(self, player):
        # Initiates a cutscene
        app.cutscene = True
        app.cutsceneLen = 60
        app.cutsceneImg = CMUImage(openImage("images/enemies/jogo/" +\
                                             "moves/p3m1/cutscene.png"))
        Sound("sounds/enemies/jogo/p3m1.mp3").play(restart=True, loop=False)
        self.move1 = EnemyDomains('volcano', 20*60, app.domainSounds[4])
        self.move1CD = 150 * 60
        self.stun = 120
        app.currentSound.pause()
        app.domainSounds[4].play(restart=True, loop=False)
    
    # Launches a big circular move that damages both the player and boss
    def phase3Move2(self, player):
        img = [CMUImage(openImage(f"images/enemies/jogo/moves/p3m2/{i}.png"))
               for i in range(8)]
        self.move2 = EnemyMoves(player.x, player.y, 'oval', 750, 750, 120, 15,
                                24, 120, True, 15, 15, 120, img)
        PlayerMoves(player.x, player.y, 'oval', 750, 750, 120, 15, 24, 120,
                    True, 15, 15, 120, [])
        self.move2CD = 90 * 60
        self.stun = 60
        Sound("sounds/enemies/jogo/p3m2.mp3").play(restart=True)