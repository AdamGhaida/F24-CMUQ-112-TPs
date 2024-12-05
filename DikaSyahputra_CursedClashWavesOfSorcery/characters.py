from cmu_graphics import *
import random
import math
from moves import *

from PIL import Image as PilImage
import os
import pathlib

def openImage(fileName):
    return PilImage.open(os.path.join(pathlib.Path(__file__).parent, fileName))

class Player:
    # Initializes important variables for players
    def __init__(self):
        # Sets the stun, iFrame, and move cooldowns
        self.stun, self.iFrameLen, self.mouse1CD = 0, 0, 0
        self.move1CD, self.move2CD, self.move3CD, self.move4CD = 0, 0, 0, 0
        self.move5CD, self.move6CD, self.move7CD, self.move8CD = 0, 0, 0, 0
        
        # Initializes the chosen move, blocking status, and autoMove
        self.choosingMove, self.isBlocking, self.autoMove = None, False, 0
        
        # Sets the coordinates, speed, and where the player is facing
        self.x, self.y, self.facing, self.speed = 1000, 1000, 'right', 5
        
        # Sets the awakening, dimensions, speed, special ability unlocked,
        # and the current move performed
        self.awakeningLen, self.width, self.height = 0, 50, 50
        self.performingMove, self.speed, self.specialUnlocked = None, 5, False
        
        # Sets the regeneration cooldowns
        self.hpRegenCD, self.energyRegenCD = 60, 15
        
        # Important variables used for animations and sprites
        self.baseImgPath, self.imageStep = "images/characters/", 0
        self.facingIndex, self.imageIndex, self.status = 1, 0, 'idle'
        
        # Sets how long a move is performed and how much hp/energy it takes
        self.performingMoveLen, self.takeHp, self.takeEnergy = 0, 0, 0
    
    # Changes the attributes of player every step
    def onStep(self):
        self.cooldown()
        self.regenerate()
        # Changes the frames of the graphics every 10 steps
        self.imageStep += 1
        if self.imageStep == 10:
            self.imageIndex += 1
            self.imageStep = 0
        # If the player isn't choosing a move, no hp/energy will be taken
        if self.choosingMove == None:
            self.takeHp, self.takeEnergy = 0, 0
    
    # onStep for cooldowns and duration reductions
    def cooldown(self):
        # Move cooldowns
        if self.mouse1CD > 0: self.mouse1CD -= 1
        if self.move1CD > 0: self.move1CD -= 1
        if self.move2CD > 0: self.move2CD -= 1
        if self.move3CD > 0: self.move3CD -= 1
        if self.move4CD > 0: self.move4CD -= 1
        if self.move5CD > 0: self.move5CD -= 1
        if self.move6CD > 0: self.move6CD -= 1
        if self.move7CD > 0: self.move7CD -= 1
        if self.move8CD > 0: self.move8CD -= 1
        # Status duration reductions (stun, iFrames)
        if self.stun > 0: self.stun -= 1
        if self.iFrameLen > 0: self.iFrameLen -= 1
        # If player is moving automatically, decreases the duration
        if self.autoMove > 0: self.autoMove -= 1
        if self.autoMove == 0: self.movingMove, self.speed = None, 5
        # Awakening duration reduction and cooldown
        if self.awakeningLen > 0: self.awakeningLen -= 1
        if self.awakeningLen == 0:
            self.awakeningBar, self.awakeningLen = 0, -1
        # Ensures that the awakeningBar does not go above the maximum
        if self.awakeningBar > self.maxAwakeningBar:
            self.awakeningBar = self.maxAwakeningBar
        # Duration reduction for the 'performing-a-move' animation
        if self.performingMoveLen > 0: self.performingMoveLen -= 1
    
    # Regenerates the hp and energy of the player
    def regenerate(self):
        # Regenerates 1 hp every second
        if self.hp < self.maxHp:
            self.hpRegenCD -= 1
            if self.hpRegenCD == 0:
                self.hpRegenCD = 60
                self.hp += 1
        # Ensures hp does not go above max
        elif self.hp > self.maxHp:
            self.hp = self.maxHp
        # Regenerates 1 energy every quarter second
        if self.energy < self.maxEnergy:
            self.energyRegenCD -= 1
            if self.energyRegenCD == 0:
                self.energyRegenCD = 15
                self.energy += 1
        # Ensures energy does not go above max
        elif self.energy > self.maxEnergy:
            self.energy = self.maxEnergy
    
    # Gets the angle of the player to the mouse
    def getAngle(self, app):
        xDist = app.mouseX - self.x + app.scrollX
        yDist = app.mouseY - self.y + app.scrollY
        return (math.atan2(yDist, xDist) * (-180 / math.pi)) % 360
    
    # Automatically moves the player to the cursor with a specified speed
    def autoMoveMouse(self, app, speed, move):
        angle = math.atan2(app.mouseY - self.y + app.scrollY,
                           app.mouseX - self.x + app.scrollX)
        dx = speed * math.cos(angle)
        dy = speed * math.sin(angle)
        move.x, move.y = move.x + dx, move.y + dy
        self.x, self.y = self.x + dx, self.y + dy
    
    # Gets the images sprite for the player
    def getImages(self):
        return self.getIdle(), self.getWalk(), self.getStun()
    
    # Draws the player based on the status of the player
    def drawPlayer(self, app):
        # If the player is performing a move, draws the sprite
        if self.performingMoveLen > 0:
            self.drawPerformingMove(app)
        # If the player is blocking, draws the player's blocking sprite
        elif self.isBlocking:
            drawImage(self.blockImg[self.facingIndex], self.x - app.scrollX,
                      self.y - app.scrollY, align='center')
        # Draws the stun sprite if stunned
        elif self.stun > 0:
            drawImage(self.stunImg[self.facingIndex], self.x - app.scrollX,
                      self.y - app.scrollY, align='center')
        # Draws the idle animation if idle
        elif self.status == 'idle':
            idleLength = len(self.idle[0])
            drawImage(self.idle[self.facingIndex][self.imageIndex % idleLength],
                      self.x - app.scrollX, self.y - app.scrollY,
                      align='center')
        # Draws the walk animation if walking
        elif self.status == 'walk':
            walkLength = len(self.walk[0])
            drawImage(self.walk[self.facingIndex][self.imageIndex % walkLength],
                      self.x - app.scrollX, self.y - app.scrollY,
                      align='center')
        # Draws any move that is being selected and aimed
        self.drawAim(app)
    
    # Draws the sprite of performing a move
    def drawPerformingMove(self, app):
        # Calculates the center X and Y coordinates of the player in the screen
        cx, cy = self.x - app.scrollX, self.y - app.scrollY
        self.drawPerformUnawakenedMove(app, cx, cy)
        self.drawPerformAwakenedMove(app, cx, cy)
    
    # Draws the performing an unawakened move sprite based on the players facing
    # direction
    def drawPerformUnawakenedMove(self, app, cx, cy):
        face = self.facingIndex
        if self.performingMove == 0:
            drawImage(self.performImg[face][0], cx, cy, align='center')
        elif self.performingMove == 1:
            drawImage(self.performImg[face][1], cx, cy, align='center')
        elif self.performingMove == 2:
            drawImage(self.performImg[face][2], cx, cy, align='center')
        elif self.performingMove == 3:
            drawImage(self.performImg[face][3], cx, cy, align='center')
        elif self.performingMove == 4:
            drawImage(self.performImg[face][4], cx, cy, align='center')
    
    # Draws the performing an awakened move sprite based on the players facing
    # direction
    def drawPerformAwakenedMove(self, app, cx, cy):
        face = self.facingIndex
        if self.performingMove == 5:
            drawImage(self.performImg[face][5], cx, cy, align='center')
        elif self.performingMove == 6:
            drawImage(self.performImg[face][6], cx, cy, align='center')
        elif self.performingMove == 7:
            drawImage(self.performImg[face][7], cx, cy, align='center')
        elif self.performingMove == 8:
            drawImage(self.performImg[face][8], cx, cy, align='center')
    
    # Unlocks the special ability move
    def specialMove(self):
        self.specialUnlocked = True
    
    # Draws any move highlight that is being selected and aimed
    def drawAim(self, app):
        if self.choosingMove == 1: self.drawMove1Aim(app)
        if self.choosingMove == 2: self.drawMove2Aim(app)
        if self.choosingMove == 3: self.drawMove3Aim(app)
        if self.choosingMove == 4: self.drawMove4Aim(app)
        if self.choosingMove == 5: self.drawMove5Aim(app)
        if self.choosingMove == 6: self.drawMove6Aim(app)
        if self.choosingMove == 7: self.drawMove7Aim(app)
        if self.choosingMove == 8: self.drawMove8Aim(app)
    
    # Draws an opaque white rectangle above the box corresponding to the move
    # that is being selected
    def drawSelectedBox(self, app):
        xCoords = [600 - (3 * 215 / 4) - 5, 600 - (1 * 215 / 4) - 2,
                   600 + (1 * 215 / 4) + 2, 600 + (3 * 215 / 4) + 5]
        if self.choosingMove == 1 or self.choosingMove == 5:
            drawRect(xCoords[0], 650, 70, 70, opacity=50, align='center',
                     fill='white')
        if self.choosingMove == 2 or self.choosingMove == 6:
            drawRect(xCoords[1], 650, 70, 70, opacity=50, align='center',
                     fill='white')
        if self.choosingMove == 3 or self.choosingMove == 7:
            drawRect(xCoords[2], 650, 70, 70, opacity=50, align='center',
                     fill='white')
        if self.choosingMove == 4 or self.choosingMove == 8:
            drawRect(xCoords[3], 650, 70, 70, opacity=50, align='center',
                     fill='white')
    
    # Awakens the player
    def awaken(self, app):
        self.awakeningLen = 30 * 60
        self.hp += (0.25 * self.maxHp)
        self.energy += (0.25 * self.maxEnergy)
    
    # When a move is chosen, an opaque white rectangle highlighting how much
    # hp/energy will be taken will be drawn on the hp and energy bar
    def drawHighlightBar(self, app):
        if self.takeHp > 0:
            drawRect((self.hp/self.maxHp)*250 + 132, 20,
                     (self.takeHp/self.maxHp)*250, 30, fill='white', opacity=90,
                     align='right-top')
        if self.takeEnergy > 0:
            drawRect((self.energy/self.maxEnergy)*250 + 132, 51,
                     (self.takeEnergy/self.maxEnergy)*250, 30, fill='white',
                     opacity=90, align='right-top')
    
    # Reduces the hp and energy based on how much the move will take from it
    def takePlayerBar(self):
        self.hp -= self.takeHp
        self.energy -= self.takeEnergy

############################################################
### PUNCHY BOY ###
############################################################
class Yuji(Player):
    # Initializes important variables for Punchy Boy
    def __init__(self):
        # Initializes maxHp, maxEnergy, and maxAwakeningBar
        self.maxHp, self.maxEnergy, self.maxAwakeningBar = 200, 150, 750
        self.hp, self.energy, self.awakeningBar = 200, 150, 0
        self.dmgMultiplierLen = 0
        super().__init__()
        # Initializes the move names
        self.moveNames = ["Barrage", "Quake",
                 "Black Flash", "Divergent Fist",
                 "Dismantle", "Fuga", "Wicker Basket",
                 "Domain Expansion"]
        super().__init__()
        # Gets the images for idle, walk, and stun sprite
        self.idle, self.walk, self.stunImg = self.getImages()
        self.auraIndex = 0
        # Gets the aura image
        self.auraImage = [CMUImage(openImage("images/characters/yuji/moves/3" +\
                          f"/{i}.png")) for i in range(5)]
        # Gets the perfoming a move, death, and blocking sprites and mouse1
        # images
        self.performImg = self.getPerformImg()
        self.punchImgLeft = [CMUImage(openImage("images/punch0.png"))]
        self.punchImgRight = [CMUImage(openImage("images/punch1.png"))]
        self.deathImg = CMUImage(openImage("images/characters/yuji/death.png"))
        self.blockImg = [CMUImage(openImage("images/characters/yuji/block" +\
                        f"{i}.png")) for i in range(2)]
    
    # Does changes for every step
    def onStep(self):
        super().onStep()
        if self.dmgMultiplierLen > 0:
            # Changes the frame of the aura GIF every 5 steps
            if self.imageStep % 5 == 0:
                self.auraIndex = (self.auraIndex + 1) % 5
        # Changes the punch images if the special ability is unlocked
        if self.specialUnlocked:
            self.punchImgLeft = [CMUImage(openImage("images/dism0.png"))]
            self.punchImgRight = [CMUImage(openImage("images/dism1.png"))]
        else:
            self.punchImgLeft = [CMUImage(openImage("images/punch0.png"))]
            self.punchImgRight = [CMUImage(openImage("images/punch1.png"))]
    
    # Draws the aura GIF if the dmgMultiplier duration is above 0
    def drawPlayer(self, app):
        super().drawPlayer(app)
        if self.dmgMultiplierLen > 0:
            drawImage(self.auraImage[self.auraIndex], self.x - app.scrollX,
                      self.y - app.scrollY, align='center', width=50, height=50,
                      opacity=50)
    
    # Gets the idle image sprites
    def getIdle(self):
        imgLst = [[], []]
        for i in range(4):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"yuji/idle/left{i}.png")))
        for i in range(4):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"yuji/idle/right{i}.png")))
        return imgLst
    
    # Gets the walking image sprites
    def getWalk(self):
        imgLst = [[], []]
        for i in range(8):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"yuji/walk/left{i}.png")))
        for i in range(8):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"yuji/walk/right{i}.png")))
        return imgLst
    
    # Gets the stunned image sprites
    def getStun(self):
        stunLst = [[], []]
        stunLst[0] = CMUImage(openImage(self.baseImgPath + "yuji/stun0.png"))
        stunLst[1] = CMUImage(openImage(self.baseImgPath + "yuji/stun1.png"))
        return stunLst
    
    # Gets the performing-a-move image sprites
    def getPerformImg(self):
        imgLst = [[], []]
        for i in range(9):
            imgLst[0].append(CMUImage(openImage("images/characters/yuji/" +\
                              f"perform/left{i}.png")))
        for i in range(9):
            imgLst[1].append(CMUImage(openImage("images/characters/yuji/" +\
                              f"perform/right{i}.png")))
        return imgLst
    
    # Awakens the player
    def awaken(self, app):
        super().awaken(app)
        # Triggers a cutscene of the player's awakening
        app.cutscene = True
        app.cutsceneLen = 120
        app.cutsceneImg = CMUImage(openImage("images/characters/yuji/" +\
                                             "awaken.png"))
        Sound("sounds/characters/yuji/awaken.mp3").play(restart=True,
                                                        loop=False)
    
    # Adds to the superclass' cooldown method by decreasing the dmgMultiplier
    # duration
    def cooldown(self):
        super().cooldown()
        self.dmgMultiplierLen -= 1
    
    # Launches a normal attack and offsets it according to where the player's
    # facing
    def mouse1(self, app):
        hitbox = 120 if self.specialUnlocked else 40
        dmg = 10 if self.specialUnlocked else 5
        if self.dmgMultiplierLen > 0: dmg *= 2
        startCoord = (0.5*hitbox) + 25
        if self.facing == 'left':
            mouse1 = PlayerMoves(self.x-startCoord, self.y, 'rect', hitbox,
                                 hitbox, 10, dmg, 10, 20, False, -5, 0, 0,
                                 self.punchImgLeft)
        elif self.facing == 'right':
            mouse1 = PlayerMoves(self.x+startCoord, self.y, 'rect', hitbox,
                                 hitbox, 10, dmg, 10, 20, False, 5, 0, 0,
                                 self.punchImgRight)
        self.stun, self.performingMoveLen = 15, 15
        self.mouse1CD, self.performingMove = 30, 0
    
    # Draws an opaque white rectangle as aiming the move (with facing offsets)
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove1Aim(self, app):
        self.takeEnergy, self.takeHp = 15, 0
        if self.facing == 'left':
            drawRect(self.x-55 - app.scrollX, self.y - app.scrollY, 60, 60,
                     fill='white', opacity=50, border='black', dashes=True,
                     align='center')
        elif self.facing == 'right':
            drawRect(self.x+55 - app.scrollX, self.y - app.scrollY, 60, 60,
                     fill='white', opacity=50, border='black', dashes=True,
                     align='center')
    
    # Unleashes a barrage of punches in a rectangular PlayerMove dealing damage
    # over time
    def move1(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            images = [[], []]
            for i in range(2):
                images[0].append(CMUImage(openImage("images/characters/yuji/" +\
                          f"moves/0/left{i}.png")))
            for i in range(2):
                images[1].append(CMUImage(openImage("images/characters/yuji/" +\
                          f"moves/0/right{i}.png")))
            self.choosingMove = None
            if self.facing == 'left':
                move1 = PlayerMoves(self.x-55, self.y, 'rect', 60, 60, 60, 4,
                                    5, 20, False, -3, 0, 0, images[0])
            elif self.facing == 'right':
                move1 = PlayerMoves(self.x+55, self.y, 'rect', 60, 60, 60, 4,
                                    5, 20, False, 3, 0, 0, images[1])
            self.stun, self.performingMoveLen = 60, 60
            self.move1CD, self.performingMove = 300, 1
            Sound("sounds/characters/yuji/move1.mp3").play(restart=True)
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove2Aim(self, app):
        self.takeEnergy, self.takeHp = 20, 0
        drawOval(self.x - app.scrollX, self.y - app.scrollY, 300, 300,
                 fill='white', opacity=50, border='black', dashes=True)
    
    # Unleashes a quake move around the player in a circular PlayerMove
    def move2(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            images = [CMUImage(openImage("images/characters/yuji/moves/1/" +\
                      f"{i}.png")) for i in range(4)]
            self.choosingMove = None
            move2 = PlayerMoves(self.x, self.y, 'oval', 300, 300, 10, 20, 10, 90,
                                True, 0, 0, 30, images)
            self.stun, self.performingMoveLen = 30, 30
            self.move2CD, self.performingMove = 600, 2
            Sound("sounds/characters/yuji/move2.mp3").play(restart=True)
    
    # Draws an opaque white rectangle as aiming the move (with facing offsets)
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove3Aim(self, app):
        self.takeEnergy, self.takeHp = 35, 0
        if self.facing == 'left':
            drawRect(self.x-40 - app.scrollX, self.y - app.scrollY, 40, 40,
                     align='center', fill='white', border='black', opacity=50,
                     dashes=True)
        elif self.facing == 'right':
            drawRect(self.x+40 - app.scrollX, self.y - app.scrollY, 40, 40,
                     align='center', fill='white', border='black', opacity=50,
                     dashes=True)
    
    # Unleashes a powerful punch that knocks enemies back in a rectangular
    # PlayerMove
    def move3(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            # Initiates the cutscene
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/yuji/" +\
                                                 "moves/2/cutscene.png"))
            Sound("sounds/characters/yuji/move3.mp3").play(restart=True,
                                                            loop=False)
            images = [CMUImage(openImage("images/characters/yuji/moves/2/" +\
                      f"{i}.png")) for i in range(1, 6)]
            self.choosingMove = None
            if self.facing == 'left':
                move3 = PlayerMoves(self.x-40, self.y, 'rect', 40, 40, 70, 25,
                                    10, 180, True, -150, 0, 30, images)
            elif self.facing == 'right':
                move3 = PlayerMoves(self.x+40, self.y, 'rect', 40, 40, 70, 25,
                                    10, 180, True, 150, 0, 30, images)
            self.stun, self.performingMoveLen = 60, 60
            self.move3CD, self.performingMove = 25 * 60, 3
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove4Aim(self, app):
        self.takeEnergy, self.takeHp = 30, 0
    
    # Increases dmgMultiplier duration for more mouse1 damage
    def move4(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/yuji/" +\
                                                 "moves/3/cutscene.png"))
            Sound("sounds/characters/yuji/move4.mp3").play(restart=True,
                                                            loop=False)
            self.dmgMultiplierLen, self.performingMoveLen = 10 * 60, 30
            self.move4CD, self.performingMove = 30 * 60, 4
    
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove5Aim(self, app):
        self.takeEnergy, self.takeHp = 20, 0
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 700, 700, angle-25,
                50, fill='white', opacity=50, border='black', dashes=True)
    
    # Unleashes a barrage of slashes in a cone PlayerMove dealing damage over
    # time
    def move5(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            angle = self.getAngle(app)
            img = [CMUImage(openImage(f"images/enemies/sukuna/moves/p1m2/{i}" +\
                                      ".png")) for i in range(2)]
            move2 = PlayerMoves(self.x, self.y, 'cone', 700, 700, 60, 4, 6, 5,
                                    False, 0, 0, 0, img, angle-25, 50)
            self.stun, self.performingMoveLen = 70, 70
            self.move5CD, self.performingMove = 10 * 60, 5
            Sound("sounds/characters/yuji/move5.mp3").play(restart=True)
    
    # Draws a dashed line as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove6Aim(self, app):
        self.takeEnergy, self.takeHp = 60, 0
        angle = math.atan2(app.mouseY - self.y + app.scrollY,
                app.mouseX - self.x + app.scrollX)
        endX = self.x - app.scrollX + (500 * math.cos(angle))
        endY = self.y - app.scrollY + (500 * math.sin(angle))
        drawLine(self.x - app.scrollX, self.y - app.scrollY, endX, endY,
                 dashes=True)
    
    # Unleashes a fire arrow 'fuga' projectile
    def move6(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            # Initiates a cutscene
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/globalmoves/fugaExe/" +\
                                                 "cutscene.png"))
            Sound("sounds/characters/yuji/move6.mp3").play(restart=True,
                                                            loop=False)
            self.choosingMove = None
            angle = math.atan2(app.mouseY - self.y + app.scrollY,
                               app.mouseX - self.x + app.scrollX)
            move6 = PlayerProjectiles(self.x, self.y, 20, 20, 60, angle, 7,
                    'fuga', [CMUImage(openImage("images/globalmoves/fugaAim/" +\
                                        f"{i}.png")) for i in range(3)])
            self.move6CD, self.performingMove = 60 * 60, 6
            self.stun, self.performingMoveLen = 90, 90
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove7Aim(self, app):
        self.takeEnergy, self.takeHp = 50, 0
        drawOval(self.x - app.scrollX, self.y - app.scrollY, 500, 500,
                 fill='white', opacity=50, border='black', dashes=True)
    
    # Unleashes a flurry of slashes in a circular PlayerMove around the player
    # dealing damage over time
    def move7(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            images = [CMUImage(openImage("images/characters/yuji/moves/6/" +\
                      f"{i}.png")) for i in range(4)]
            self.choosingMove = None
            move2 = PlayerMoves(self.x, self.y, 'oval', 500, 500, 60, 5, 6, 60,
                                True, 0, 0, 0, images)
            self.stun, self.performingMoveLen = 60, 60
            self.move7CD, self.performingMove = 600, 7
            Sound("sounds/characters/yuji/move7.mp3").play(restart=True)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove8Aim(self, app):
        self.takeEnergy, self.takeHp = 100, 0
    
    # Cast a domain called "Malevolent Shrine"
    def move8(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            # Initiates a cutscene
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/yuji/" +\
                                                 "moves/7/cutscene.png"))
            Sound("sounds/characters/yuji/move8.mp3").play(restart=True,
                                                            loop=False)
            self.choosingMove = None
            move8 = PlayerDomains('malevolent', 20*60, app.domainSounds[1])
            self.stun, self.iFrameLen, self.performingMoveLen = 120, 120, 120
            self.move8CD, self.performingMove = 150 * 60, 8
            app.currentSound.pause()
            app.domainSounds[1].play(restart=True, loop=False)

############################################################
### THESAURUS ###
############################################################
class Inumaki(Player):
    # Initializes important variables for Thesaurus
    def __init__(self):
        # Initializes maxHp, maxEnergy, and maxAwakeningBar
        self.maxHp, self.maxEnergy, self.maxAwakeningBar = 200, 150, 500
        self.hp, self.energy, self.awakeningBar = 200, 150, 0
        super().__init__()
        # Initializes the move names
        self.moveNames = ["'Don't Move'", "'Scream'",
                 "Cough Syrup", "'Blast Away'",
                 "'Get Crushed'", "'Twist'", "'Explode'",
                 "'Die'"]
        # Gets the images for idle, walk, and stun sprite
        self.idle, self.walk, self.stunImg = self.getImages()
        # Gets the perfoming a move, death, and blocking sprites
        self.performImg = self.getPerformImg()
        self.blockImg = [CMUImage(openImage("images/characters/inumaki/block" +\
                        f"{i}.png")) for i in range(2)]
        self.deathImg = CMUImage(openImage("images/characters/inumaki/death" +\
                                           ".png"))
    
    # Gets the performing-a-move image sprites
    def getPerformImg(self):
        imgLst = [[], []]
        for i in range(9):
            imgLst[0].append(CMUImage(openImage("images/characters/inumaki/" +\
                              f"perform/left{i}.png")))
        for i in range(9):
            imgLst[1].append(CMUImage(openImage("images/characters/inumaki/" +\
                              f"perform/right{i}.png")))
        return imgLst
    
    # Gets the idle image sprites
    def getIdle(self):
        imgLst = [[], []]
        for i in range(8):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"inumaki/idle/left{i}.png")))
        for i in range(8):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"inumaki/idle/right{i}.png")))
        return imgLst
    
    # Gets the walking image sprites
    def getWalk(self):
        imgLst = [[], []]
        for i in range(7):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"inumaki/walk/left{i}.png")))
        for i in range(7):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"inumaki/walk/right{i}.png")))
        return imgLst
    
    # Gets the stunned image sprites
    def getStun(self):
        stunLst = [[], []]
        stunLst[0] = CMUImage(openImage(self.baseImgPath + "inumaki/stun0.png"))
        stunLst[1] = CMUImage(openImage(self.baseImgPath + "inumaki/stun1.png"))
        return stunLst
    
    def awaken(self, app):
        super().awaken(app)
        app.cutscene = True
        app.cutsceneLen = 120
        app.cutsceneImg = CMUImage(openImage("images/characters/inumaki/" +\
                                             "awaken.png"))
        Sound("sounds/characters/inumaki/awaken.mp3").play(restart=True,
                                                        loop=False)
    
    # Launches a normal attack and offsets it according to where the player's
    # facing
    def mouse1(self, app):
        if self.facing == 'left':
            mouse1 = PlayerMoves(self.x-45, self.y, 'rect', 40,
                                 40, 10, 5, 10, 20, False, -5, 0, 0,
                        [CMUImage(openImage("images/punch0.png"))])
        elif self.facing == 'right':
            mouse1 = PlayerMoves(self.x+45, self.y, 'rect', 40,
                                 40, 10, 5, 10, 20, False, 5, 0, 0,
                        [CMUImage(openImage("images/punch1.png"))])
        self.stun = 15
        self.mouse1CD = 30
        self.performingMove, self.performingMoveLen = 0, 15
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove1Aim(self, app):
        self.takeEnergy = 15
        if not self.specialUnlocked: self.takeHp = 15
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 400, 400, angle-30,
                60, fill='white', opacity=50, border='black', dashes=True)
    
    # Launch a cone attack at the enemies stunning them for a long time
    def move1(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            img = [CMUImage(openImage("images/characters/inumaki/moves/0/img" +\
                                      ".png"))]
            angle = self.getAngle(app)
            move1 = PlayerMoves(self.x, self.y, 'cone', 400, 400, 10, 0, 0, 240,
                    True, 0, 0, 0, img, angle-30, 60)
            self.stun = 45
            self.move1CD = 15 * 60
            self.performingMove, self.performingMoveLen = 1, 30
            Sound("sounds/characters/inumaki/move1.mp3").play(restart=True)
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove2Aim(self, app):
        self.takeEnergy = 25
        if not self.specialUnlocked: self.takeHp = 25
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 700, 700, angle-35,
                70, fill='white', opacity=50, border='black', dashes=True)
    
    # Launch a cone attack at the enemies dealing damage to them
    def move2(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            angle = self.getAngle(app)
            img = [CMUImage(openImage("images/characters/inumaki/moves/1/img" +\
                                      ".png"))]
            move2 = PlayerMoves(self.x, self.y, 'cone', 700, 700, 10, 20, 10,
                                90, False, 0, 0, 0, img, angle-35, 70)
            self.stun = 75
            self.move2CD = 7 * 60
            self.performingMove, self.performingMoveLen = 2, 45
            Sound("sounds/characters/inumaki/move2.mp3").play(restart=True)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove3Aim(self, app):
        self.takeEnergy = 20
        if not self.specialUnlocked: self.takeHp = 0
    
    # Heals the player for 35 health points (hp)
    def move3(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            if self.maxHp - self.hp < 35:
                self.hp = self.maxHp
            else:
                self.hp += 35
            self.move3CD, self.stun = 35 * 60, 30
            self.performingMove, self.performingMoveLen = 3, 30
            Sound("sounds/characters/inumaki/move3.mp3").play(restart=True)
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove4Aim(self, app):
        self.takeEnergy = 35
        if not self.specialUnlocked: self.takeHp = 35
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 800, 800, angle-20,
                40, fill='white', opacity=50, border='black', dashes=True)
    
    # Launch a cone attack at the enemies dealing damage to them
    def move4(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            angle = self.getAngle(app)
            img = [CMUImage(openImage("images/characters/inumaki/moves/3/img" +\
                                      ".png"))]
            move4 = PlayerMoves(self.x, self.y, 'cone', 800, 800, 10, 30, 10,
                                120, True, 200, 200, 0, img, angle-20, 40)
            self.move4CD, self.stun = 25 * 60, 60
            self.performingMove, self.performingMoveLen = 4, 45
            Sound("sounds/characters/inumaki/move4.mp3").play(restart=True)
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove5Aim(self, app):
        self.takeEnergy = 45
        if not self.specialUnlocked: self.takeHp = 45
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 700, 700, angle-50,
                100, fill='white', opacity=50, border='black', dashes=True)
    
    # Launch a cone attack at the enemies dealing damage to them
    def move5(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            # Initiates a cutscene
            self.choosingMove = None
            angle = self.getAngle(app)
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/inumaki/" +\
                                                 "moves/4/cutscene.png"))
            Sound("sounds/characters/inumaki/move5.mp3").play(restart=True,
                                                            loop=False)
            img = [CMUImage(openImage("images/characters/inumaki/moves/4/img" +\
                                      ".png"))]
            move5 = PlayerMoves(self.x, self.y, 'cone', 700, 700, 10, 35, 10,
                                150, True, 0, 0, 0, img, angle-50, 100)
            self.move5CD, self.stun = 15 * 60, 75
            self.performingMove, self.performingMoveLen = 5, 45
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove6Aim(self, app):
        self.takeEnergy = 40
        if not self.specialUnlocked: self.takeHp = 40
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 800, 800, angle-45,
                90, fill='white', opacity=50, border='black', dashes=True)
    
    # Launch a cone attack at the enemies dealing damage to them
    def move6(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            # Initiates a cutscene
            self.choosingMove = None
            angle = self.getAngle(app)
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/inumaki/" +\
                                                 "moves/5/cutscene.png"))
            Sound("sounds/characters/inumaki/move6.mp3").play(restart=True,
                                                            loop=False)
            img = [CMUImage(openImage("images/characters/inumaki/moves/5/img" +\
                                      ".png"))]
            move6 = PlayerMoves(self.x, self.y, 'cone', 800, 800, 10, 40, 10,
                                120, True, 0, 0, 0, img, angle-45, 90)
            self.move6CD, self.stun = 22 * 60, 60
            self.performingMove, self.performingMoveLen = 6, 45
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove7Aim(self, app):
        self.takeEnergy = 50
        if not self.specialUnlocked: self.takeHp = 50
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 900, 900, angle-80,
                160, fill='white', opacity=50, border='black', dashes=True)
    
    # Launch a cone attack at the enemies dealing damage to them
    def move7(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            # Initiates a cutscene
            self.choosingMove = None
            angle = self.getAngle(app)
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/inumaki/" +\
                                                 "moves/6/cutscene.png"))
            Sound("sounds/characters/inumaki/move7.mp3").play(restart=True,
                                                            loop=False)
            img = [CMUImage(openImage("images/characters/inumaki/moves/6/img" +\
                                      ".png"))]
            move7 = PlayerMoves(self.x, self.y, 'cone', 900, 900, 10, 42, 10,
                                160, True, 2, 2, 0, img, angle-80, 160)
            self.move7CD, self.stun = 17 * 60, 80
            self.performingMove, self.performingMoveLen = 7, 45
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove8Aim(self, app):
        self.takeEnergy = 150
        if not self.specialUnlocked: self.takeHp = 150
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 500, 500, angle-15,
                30, fill='white', opacity=50, border='black', dashes=True)
    
    # Launch a cone attack at the enemies dealing damage to them
    def move8(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            # Initiates a cutscene
            self.choosingMove = None
            angle = self.getAngle(app)
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/inumaki/" +\
                                                 "moves/7/cutscene.png"))
            Sound("sounds/characters/inumaki/move8.mp3").play(restart=True,
                                                            loop=False)
            img = [CMUImage(openImage("images/characters/inumaki/moves/7/img" +\
                                      ".png"))]
            move8 = PlayerMoves(self.x, self.y, 'cone', 500, 500, 10, 500, 10,
                                120, True, 0, 0, 0, img, angle-15, 30)
            self.move8CD, self.stun = 5 * 60 * 60, 120
            self.performingMove, self.performingMoveLen = 8, 45

############################################################
### ZOOKEEPER ###
############################################################
class Megumi(Player):
    # Initializes important variables for Zookeeper
    def __init__(self):
        # Initializes maxHp, maxEnergy, and maxAwakeningBar
        self.maxHp, self.maxEnergy, self.maxAwakeningBar = 200, 200, 800
        self.hp, self.energy, self.awakeningBar = 200, 200, 0
        super().__init__()
        # Initializes the move names
        self.moveNames = ["Rabbits", "Nue",
                 "White Dog", "Black Dog",
                 "Elephant", "Sword", "Domain Expansion",
                 "Divine General"]
        # Gets the images for idle, walk, and stun sprite
        self.idle, self.walk, self.stunImg = self.getImages()
        # Gets the perfoming a move, death, and blocking sprites
        self.performImg = self.getPerformImg()
        self.blockImg = [CMUImage(openImage("images/characters/megumi/block" +\
                        f"{i}.png")) for i in range(2)]
        self.deathImg = CMUImage(openImage("images/characters/megumi/death" +\
                                           ".png"))
    
    # Gets the performing-a-move image sprites
    def getPerformImg(self):
        imgLst = [[], []]
        for i in range(9):
            imgLst[0].append(CMUImage(openImage("images/characters/megumi/" +\
                              f"perform/left{i}.png")))
        for i in range(9):
            imgLst[1].append(CMUImage(openImage("images/characters/megumi/" +\
                              f"perform/right{i}.png")))
        return imgLst
    
    # Gets the idle image sprites
    def getIdle(self):
        imgLst = [[], []]
        for i in range(4):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"megumi/idle/left{i}.png")))
        for i in range(4):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"megumi/idle/right{i}.png")))
        return imgLst
    
    # Gets the walking image sprites
    def getWalk(self):
        imgLst = [[], []]
        for i in range(8):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"megumi/walk/left{i}.png")))
        for i in range(8):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"megumi/walk/right{i}.png")))
        return imgLst
    
    # Gets the stunned image sprites
    def getStun(self):
        stunLst = [[], []]
        stunLst[0] = CMUImage(openImage(self.baseImgPath + "megumi/stun0.png"))
        stunLst[1] = CMUImage(openImage(self.baseImgPath + "megumi/stun1.png"))
        return stunLst
    
    def awaken(self, app):
        super().awaken(app)
        app.cutscene = True
        app.cutsceneLen = 120
        app.cutsceneImg = CMUImage(openImage("images/characters/megumi/" +\
                                             "awaken.png"))
        Sound("sounds/characters/megumi/awaken.mp3").play(restart=True,
                                                        loop=False)
    
    # Launches a normal attack and offsets it according to where the player's
    # facing
    def mouse1(self, app):
        if self.facing == 'left':
            mouse1 = PlayerMoves(self.x-45, self.y, 'rect', 40,
                                 40, 10, 5, 10, 20, False, -5, 0, 0,
                        [CMUImage(openImage("images/punch0.png"))])
        elif self.facing == 'right':
            mouse1 = PlayerMoves(self.x+45, self.y, 'rect', 40,
                                 40, 10, 5, 10, 20, False, 5, 0, 0,
                        [CMUImage(openImage("images/punch1.png"))])
        self.stun = 15
        self.mouse1CD = 30
        self.performingMove, self.performingMoveLen = 0, 15
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove1Aim(self, app):
        self.takeEnergy, self.takeHp = 15, 0
        drawOval(app.mouseX, app.mouseY, 200, 200, fill='white', opacity=50,
                 border='black', dashes=True)
    
    # Unleash an army of rabbits in a circular PlayerMove, dealing damage over
    # time
    def move1(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            img = [CMUImage(openImage("images/characters/megumi/moves/0/" +\
                   f"{i}.png")) for i in range(2)]
            self.choosingMove = None
            move1 = PlayerMoves(app.mouseX + app.scrollX,
                                app.mouseY + app.scrollY, 'oval', 200, 200, 60,
                                3, 5, 1, False, 0, 0, 0, img)
            self.move1CD, self.stun = 7 * 60, 30
            self.performingMove, self.performingMoveLen = 1, 30
            Sound("sounds/characters/megumi/move1.mp3").play(restart=True)
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove2Aim(self, app):
        self.takeEnergy, self.takeHp = 25, 0
        drawOval(app.mouseX, app.mouseY, 400, 400, fill='white', opacity=50,
                 border='black', dashes=True)
    
    # Teleports the player and unleash a high stun and damage move in a circular
    # PlayerMove
    def move2(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/megumi/" +\
                                                 "moves/1/cutscene.png"))
            Sound("sounds/characters/megumi/move2.mp3").play(restart=True,
                                                            loop=False)
            img = [CMUImage(openImage("images/characters/megumi/moves/1/" +\
                   f"{i}.png")) for i in range(5)]
            self.choosingMove = None
            move2 = PlayerMoves(app.mouseX + app.scrollX,
                                app.mouseY + app.scrollY, 'oval', 400, 400, 10,
                                25, 10, 90, True, 70, 70, 0, img)
            self.x, self.y = app.mouseX + app.scrollX, app.mouseY + app.scrollY
            self.move2CD, self.stun = 17 * 60, 30
            self.performingMove, self.performingMoveLen = 2, 30
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove3Aim(self, app):
        self.takeEnergy, self.takeHp = 30, 0
    
    # Summons a white dog that will go around and kill enemies for 20 seconds
    def move3(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            images = [[], []]
            for i in range(2):
                images[0].append(CMUImage(openImage("images/characters/" +\
                          f"megumi/moves/2/left{i}.png")))
            for i in range(2):
                images[1].append(CMUImage(openImage("images/characters/" +\
                          f"megumi/moves/2/right{i}.png")))
            move3 = PlayerEntities(self.x, self.y, 'dog', 20*60, images)
            self.move3CD, self.stun = 35 * 60, 60
            self.performingMove, self.performingMoveLen = 3, 60
            Sound("sounds/characters/megumi/move3.mp3").play(restart=True)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove4Aim(self, app):
        self.takeEnergy, self.takeHp = 35, 0
    
    # Summons a white dog that will go around and kill enemies for 20 seconds
    def move4(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            images = [[], []]
            for i in range(2):
                images[0].append(CMUImage(openImage("images/characters/" +\
                          f"megumi/moves/3/left{i}.png")))
            for i in range(2):
                images[1].append(CMUImage(openImage("images/characters/" +\
                          f"megumi/moves/3/right{i}.png")))
            move4 = PlayerEntities(self.x, self.y, 'dog', 20*60, images)
            self.move4CD, self.stun = 40 * 60, 60
            self.performingMove, self.performingMoveLen = 4, 60
            Sound("sounds/characters/megumi/move4.mp3").play(restart=True)
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove5Aim(self, app):
        self.takeEnergy, self.takeHp = 35, 0
        drawOval(app.mouseX, app.mouseY, 300, 300, fill='white', opacity=50,
                 border='black', dashes=True)
    
    # Summons a giant elephant on the cursor in a circular PlayerMove
    def move5(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/megumi/" +\
                                                 "moves/4/cutscene.png"))
            Sound("sounds/characters/megumi/move5.mp3").play(restart=True,
                                                            loop=False)
            img = [CMUImage(openImage("images/characters/megumi/moves/4/" +\
                   f"{i}.png")) for i in range(5)]
            move5 = PlayerMoves(app.mouseX + app.scrollX,
                                app.mouseY + app.scrollY, 'oval', 300, 300, 10,
                                60, 10, 90, True, 0, 0, 30, img)
            self.move5CD, self.stun = 12 * 60, 40
            self.performingMove, self.performingMoveLen = 5, 40
    
    # Draws an opaque white rectangle as aiming the move (with facing offsets)
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove6Aim(self, app):
        self.takeEnergy, self.takeHp = 15, 0
        if self.facing == 'left':
            drawRect(self.x-65 - app.scrollX, self.y - app.scrollY, 80, 100,
                     fill='white', opacity=50, border='black', dashes=True,
                     align='center')
        elif self.facing == 'right':
            drawRect(self.x+65 - app.scrollX, self.y - app.scrollY, 80, 100,
                     fill='white', opacity=50, border='black', dashes=True,
                     align='center')
    
    # Unleash a barrage of slashes using the player's sword in a rectangular
    # PlayerMove, dealing damage over time
    def move6(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            if self.facing == 'left':
                img = [CMUImage(openImage("images/characters/yuta/moves/0 1/" +\
                       f"left{i}.png")) for i in range(2)]
                move6 = PlayerMoves(self.x-65, self.y, 'rect', 80, 100, 60, 6,
                                    5, 20, False, -3, 0, 0, img)
            elif self.facing == 'right':
                img = [CMUImage(openImage("images/characters/yuta/moves/0 1/"+\
                       f"right{i}.png")) for i in range(2)]
                move6 = PlayerMoves(self.x+65, self.y, 'rect', 80, 100, 60, 6,
                                    5, 20, False, 3, 0, 0, img)
            self.move6CD, self.stun = 10 * 60, 60
            self.performingMove, self.performingMoveLen = 6, 60
            Sound("sounds/characters/megumi/move6.mp3").play(restart=True)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove7Aim(self, app):
        self.takeEnergy, self.takeHp = 150, 0
    
    # Cast your domain called "Chimera Shadow Garden"
    def move7(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/megumi/" +\
                                                 "moves/6/cutscene.png"))
            Sound("sounds/characters/megumi/move7.mp3").play(restart=True,
                                                            loop=False)
            move7 = PlayerDomains('shadow', 20*60, app.domainSounds[2])
            self.stun, self.iFrameLen = 120, 20*60
            self.move7CD = 150 * 60
            self.performingMove, self.performingMoveLen = 7, 120
            app.currentSound.pause()
            app.domainSounds[2].play(restart=True, loop=False)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove8Aim(self, app):
        self.takeEnergy, self.takeHp = 200, 0
    
    # Summon the Divine General
    def move8(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            app.mahoragaCutsceneIndex = 0
            self.takePlayerBar()
            self.choosingMove = None
            Sound("sounds/mahowind.mp3").play(restart=True)
            if self.specialUnlocked:
                app.mahoragaCutsceneLen = 600
                app.player = Mahoraga()
                app.deathTimer = 90 * 60
            else:
                app.mahoragaCutsceneLen = 660
                self.hp = 0

### DON'T TELL ABDULRAHMAN ###
class Mahoraga(Player):
    # Initializes important variables for Divine General
    def __init__(self):
        # Initializes maxHp, maxEnergy, and maxAwakeningBar
        self.maxHp, self.maxEnergy, self.hp, self.energy = 500, 400, 500, 400
        self.maxAwakeningBar, self.awakeningBar, self.spins = 25, 0, 0
        # Initializes the move names
        self.moveNames = ["Earthquake", "Blitz Slash", "World Slash", "Adapt"]
        # Gets the images for idle, walk, and stun sprite
        self.idle, self.walk, self.stunImg = self.getImages()
        super().__init__()
        # Gets the perfoming a move, death, and blocking sprites
        self.performImg = self.getPerformImg()
        self.blockImg = [CMUImage(openImage("images/characters/mahoraga/bloc" +\
                        f"k{i}.png")) for i in range(2)]
        self.deathImg = CMUImage(openImage("images/characters/megumi/death" +\
                                           ".png"))
    
    # Gets the performing-a-move image sprites
    def getPerformImg(self):
        imgLst = [[], []]
        for i in range(5):
            imgLst[0].append(CMUImage(openImage("images/characters/mahoraga/" +\
                              f"perform/left{i}.png")))
        for i in range(5):
            imgLst[1].append(CMUImage(openImage("images/characters/mahoraga/" +\
                              f"perform/right{i}.png")))
        return imgLst
    
    # Gets the idle image sprites
    def getIdle(self):
        imgLst = [[], []]
        imgLst[0].append(CMUImage(openImage("images/characters/" +\
                                            "mahoraga/idle0.png")))
        imgLst[1].append(CMUImage(openImage("images/characters/" +\
                                            "mahoraga/idle1.png")))
        return imgLst
    
    # Gets the walking image sprites
    def getWalk(self):
        imgLst = [[], []]
        for i in range(4):
            imgLst[0].append(CMUImage(openImage("images/characters/" +\
                                             f"mahoraga/walk/left{i}.png")))
        for i in range(4):
            imgLst[1].append(CMUImage(openImage("images/characters/" +\
                                             f"mahoraga/walk/right{i}.png")))
        return imgLst
    
    # Gets the stunned image sprites
    def getStun(self):
        stunLst = [[], []]
        stunLst[0].append(CMUImage(openImage("images/characters/" +\
                                            "mahoraga/idle0.png")))
        stunLst[1].append(CMUImage(openImage("images/characters/" +\
                                            "mahoraga/idle1.png")))
        return stunLst
    
    def awaken(self, app):
        self.spins += 1
        self.awakeningBar = 0
        app.cutscene = True
        app.cutsceneLen = 120
        app.cutsceneImg = CMUImage(openImage("images/characters/mahoraga/" +\
                                             "awaken.png"))
        Sound("sounds/characters/mahoraga/awaken.mp3").play(restart=True,
                                                        loop=False)
    
    def onStep(self):
        self.cooldown()
        self.imageStep += 1
        if self.imageStep == 10:
            self.imageIndex += 1
            self.imageStep = 0
        if self.spins >= 8: self.iFrameLen = 60
        if self.stun > 0: self.stun = 0
    
    # Launches a normal attack and offsets it according to where the player's
    # facing
    def mouse1(self, app):
        if self.facing == 'left':
            mouse1 = PlayerMoves(self.x-85, self.y, 'rect', 120,
                                 120, 10, 20, 10, 20, False, -5, 0, 0,
                        [CMUImage(openImage("images/dism0.png"))])
        elif self.facing == 'right':
            mouse1 = PlayerMoves(self.x+85, self.y, 'rect', 120,
                                 120, 10, 20, 10, 20, False, 5, 0, 0,
                        [CMUImage(openImage("images/dism1.png"))])
        self.stun = 15
        self.mouse1CD = 30
        self.performingMove, self.performingMoveLen = 0, 15
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove1Aim(self, app):
        self.takeEnergy, self.takeHp = 50, 0
        drawOval(self.x - app.scrollX, self.y - app.scrollY, 300, 300,
                 fill='white', opacity=50, border='black', dashes=True)
    
    def move1(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            images = [CMUImage(openImage("images/characters/mahoraga/moves/0" +\
                                         "/img.png"))]
            self.choosingMove = None
            move1 = PlayerMoves(self.x, self.y, 'oval', 300, 300, 60, 5, 2, 90,
                                True, 0, 0, 30, images)
            self.performingMove, self.performingMoveLen = 1, 30
            Sound("sounds/characters/mahoraga/move1.mp3").play(restart=True)
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove2Aim(self, app):
        self.takeEnergy, self.takeHp = 75, 0
        drawOval(app.mouseX, app.mouseY, 400, 400, fill='white', opacity=50,
                 border='black', dashes=True)
    
    def move2(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            img = [CMUImage(openImage("images/characters/mahoraga/moves/1/" +\
                                         "img.png"))]
            self.choosingMove = None
            move2 = PlayerMoves(app.mouseX + app.scrollX,
                                app.mouseY + app.scrollY, 'oval', 400, 400, 10,
                                75, 10, 90, True, 100, 100, 0, img)
            self.x, self.y = app.mouseX + app.scrollX, app.mouseY + app.scrollY
            self.performingMove, self.performingMoveLen = 2, 30
            Sound("sounds/characters/mahoraga/move2.mp3").play(restart=True)
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove3Aim(self, app):
        self.takeEnergy, self.takeHp = 200, 0
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 900, 900, angle-50,
                100, fill='white', opacity=50, border='black', dashes=True)
    
    def move3(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            img = [CMUImage(openImage("images/characters/mahoraga/moves/2/" +\
                                         f"{i}.png")) for i in range(5)]
            angle = self.getAngle(app)
            move3 = PlayerMoves(self.x, self.y, 'cone', 900, 900, 10, 250, 10,
                                90, True, 0, 0, 0, img, angle-50, 100)
            self.performingMove, self.performingMoveLen = 3, 30
            Sound("sounds/characters/mahoraga/move3.mp3").play(restart=True)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove4Aim(self, app):
        self.takeEnergy, self.takeHp = 35, 0
    
    def move4(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.deathTimer += 15 * 60
            self.hp += self.spins * 15
            self.spins = 0
            self.move4CD = 45 * 60
            self.performingMove, self.performingMoveLen = 4, 30
            Sound("sounds/characters/mahoraga/move4.mp3").play(restart=True)
    
############################################################
### CURSED CHILD ###
############################################################
class Yuta(Player):
    # Initializes important variables for Cursed Child
    def __init__(self):
        # Initializes maxHp, maxEnergy, and maxAwakeningBar
        self.maxHp, self.maxEnergy, self.maxAwakeningBar = 225, 200, 900
        self.hp, self.energy, self.awakeningBar = 225, 200, 0
        # Initializes the move names
        self.moveNames = ["Barrage", "Slash Flurry",
                 "RCT (Heal)", "Beatdown",
                 "Thin Ice Breaker", "Jacob's Ladder", "'Die'",
                 "True Love"]
        super().__init__()
        # Gets the images for idle, walk, and stun sprite
        self.idle, self.walk, self.stunImg = self.getImages()
        # Gets the perfoming a move, death, and blocking sprites
        self.performImg = self.getPerformImg()
        self.blockImg = [CMUImage(openImage("images/characters/yuta/block" +\
                        f"{i}.png")) for i in range(2)]
        self.deathImg = CMUImage(openImage("images/characters/yuta/death.png"))
    
    # Gets the performing-a-move image sprites
    def getPerformImg(self):
        imgLst = [[], []]
        for i in range(9):
            imgLst[0].append(CMUImage(openImage("images/characters/yuta/" +\
                              f"perform/left{i}.png")))
        for i in range(9):
            imgLst[1].append(CMUImage(openImage("images/characters/yuta/" +\
                              f"perform/right{i}.png")))
        return imgLst
    
    def specialMove(self):
        super().specialMove()
        self.moveNames[7] = "???"
    
    # Gets the idle image sprites
    def getIdle(self):
        imgLst = [[], []]
        for i in range(9):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"yuta/idle/left{i}.png")))
        for i in range(9):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"yuta/idle/right{i}.png")))
        return imgLst
    
    # Gets the walking image sprites
    def getWalk(self):
        imgLst = [[], []]
        for i in range(9):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"yuta/idle/left{i}.png")))
        for i in range(9):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"yuta/idle/right{i}.png")))
        return imgLst
    
    # Gets the stunned image sprites
    def getStun(self):
        stunLst = [[], []]
        stunLst[0] = CMUImage(openImage(self.baseImgPath + "yuta/stun0.png"))
        stunLst[1] = CMUImage(openImage(self.baseImgPath + "yuta/stun1.png"))
        return stunLst
    
    def awaken(self, app):
        super().awaken(app)
        app.cutscene = True
        app.cutsceneLen = 120
        app.cutsceneImg = CMUImage(openImage("images/characters/yuta/" +\
                                             "awaken.png"))
        Sound("sounds/characters/yuta/awaken.mp3").play(restart=True,
                                                        loop=False)
    
    # Launches a normal attack and offsets it according to where the player's
    # facing
    def mouse1(self, app):
        if self.facing == 'left':
            mouse1 = PlayerMoves(self.x-60, self.y, 'rect', 70,
                                 70, 10, 7, 10, 20, False, -5, 0, 0,
                        [CMUImage(openImage("images/slash0.png"))])
        elif self.facing == 'right':
            mouse1 = PlayerMoves(self.x+60, self.y, 'rect', 70,
                                 70, 10, 7, 10, 20, False, 5, 0, 0,
                        [CMUImage(openImage("images/slash1.png"))])
        self.stun = 15
        self.mouse1CD = 30
        self.performingMove, self.performingMoveLen = 0, 15
    
    # Draws an opaque white rectangle as aiming the move (with facing offsets)
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove1Aim(self, app):
        self.takeEnergy, self.takeHp = 15, 0
        if self.facing == 'left':
            drawRect(self.x-70 - app.scrollX, self.y - app.scrollY, 90, 110,
                     fill='white', opacity=50, border='black', dashes=True,
                     align='center')
        elif self.facing == 'right':
            drawRect(self.x+70 - app.scrollX, self.y - app.scrollY, 90, 110,
                     fill='white', opacity=50, border='black', dashes=True,
                     align='center')
    
    def move1(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            if self.facing == 'left':
                img = [CMUImage(openImage("images/characters/yuta/moves/0 1/" +\
                       f"left{i}.png")) for i in range(2)]
                move1 = PlayerMoves(self.x-65, self.y, 'rect', 80, 100, 60, 6,
                                    5, 20, False, -3, 0, 0, img)
            elif self.facing == 'right':
                img = [CMUImage(openImage("images/characters/yuta/moves/0 1/" +\
                       f"right{i}.png")) for i in range(2)]
                move1 = PlayerMoves(self.x+65, self.y, 'rect', 80, 100, 60, 6,
                                    5, 20, False, 3, 0, 0, img)
            self.stun = 60
            self.move1CD = 7 * 60
            self.performingMove, self.performingMoveLen = 1, 60
            Sound("sounds/characters/yuta/move1.mp3").play(restart=True)
    
    # Draws an opaque white rectangle as aiming the move (with facing offsets)
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove2Aim(self, app):
        self.takeEnergy, self.takeHp = 20, 0
        if self.facing == 'left':
            drawRect(self.x-70 - app.scrollX, self.y - app.scrollY, 90, 110,
                     fill='white', opacity=50, border='black', dashes=True,
                     align='center')
        elif self.facing == 'right':
            drawRect(self.x+70 - app.scrollX, self.y - app.scrollY, 90, 110,
                     fill='white', opacity=50, border='black', dashes=True,
                     align='center')
    
    def move2(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            if self.facing == 'left':
                img = [CMUImage(openImage("images/characters/yuta/moves/0 1/" +\
                       f"left{i}.png")) for i in range(2)]
                move2 = PlayerMoves(self.x-70, self.y, 'rect', 90, 110, 60, 10,
                                    5, 60, False, 30, 30, 0, img)
            elif self.facing == 'right':
                img = [CMUImage(openImage("images/characters/yuta/moves/0 1/" +\
                       f"right{i}.png")) for i in range(2)]
                move2 = PlayerMoves(self.x+70, self.y, 'rect', 90, 110, 60, 10,
                                    5, 60, False, 30, 30, 0, img)
            self.movingMove, self.speed, self.stun = move2, 10, 90
            self.autoMove, self.move2CD = 60, 16 * 60
            self.performingMove, self.performingMoveLen = 2, 90
            Sound("sounds/characters/yuta/move2.mp3").play(restart=True)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove3Aim(self, app):
        self.takeEnergy, self.takeHp = 35, 0
    
    def move3(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            if self.maxHp - self.hp < 35:
                self.hp = self.maxHp
            else:
                self.hp += 35
            self.move3CD, self.stun = 35 * 60, 30
            self.performingMove, self.performingMoveLen = 3, 30
            Sound("sounds/characters/yuta/move3.mp3").play(restart=True)
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove4Aim(self, app):
        self.takeEnergy, self.takeHp = 40, 0
        drawOval(app.mouseX, app.mouseY, 300, 300, fill='white', opacity=50,
                 border='black', dashes=True)
    
    def move4(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/yuta/" +\
                                                 "moves/3/cutscene.png"))
            Sound("sounds/characters/yuta/move4.mp3").play(restart=True,
                                                            loop=False)
            img = [CMUImage(openImage(f"images/characters/yuta/moves/3/{i}" +\
                                      ".png")) for i in range(10)]
            move4 = PlayerMoves(app.mouseX + app.scrollX,
                                app.mouseY + app.scrollY, 'oval', 300, 300, 90,
                                15, 15, 60, True, 15, 15, 0, img)
            self.move4CD, self.stun = 40 * 60, 60
            self.performingMove, self.performingMoveLen = 4, 60
    
    # Draws an opaque white rectangle as aiming the move (with facing offsets)
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove5Aim(self, app):
        self.takeEnergy, self.takeHp = 40, 0
        if self.facing == 'left':
            drawRect(self.x-40 - app.scrollX, self.y - app.scrollY, 40, 40,
                     align='center', fill='white', border='black', opacity=50,
                     dashes=True)
        elif self.facing == 'right':
            drawRect(self.x+40 - app.scrollX, self.y - app.scrollY, 40, 40,
                     align='center', fill='white', border='black', opacity=50,
                     dashes=True)
    
    def move5(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            img = [CMUImage(openImage(f"images/characters/yuta/moves/4/{i}" +\
                                      ".png")) for i in range(5)]
            if self.facing == 'left':
                move5 = PlayerMoves(self.x-40, self.y, 'rect', 40, 40, 10, 70,
                                    10, 60, True, 0, 0, 30, img)
            elif self.facing == 'right':
                move5 = PlayerMoves(self.x+40, self.y, 'rect', 40, 40, 10, 70,
                                    10, 60, True, 0, 0, 30, img)
            self.stun = 60
            self.move5CD = 15 * 60
            self.performingMove, self.performingMoveLen = 5, 60
            Sound("sounds/characters/yuta/move5.mp3").play(restart=True)
    
    # Draws an opaque white circle as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove6Aim(self, app):
        self.takeEnergy, self.takeHp = 65, 0
        drawOval(app.mouseX, app.mouseY, 500, 500, fill='white', opacity=50,
                 border='black', dashes=True)
    
    def move6(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            img = [CMUImage(openImage(f"images/characters/yuta/moves/5/{i}" +\
                                      ".png")) for i in range(2)]
            move6 = PlayerMoves(app.mouseX + app.scrollX,
                                app.mouseY + app.scrollY, 'oval', 500, 500, 120,
                                10, 12, 6, True, 5, 5, 30, img)
            self.move6CD, self.stun = 20 * 60, 60
            self.performingMove, self.performingMoveLen = 6, 60
            Sound("sounds/characters/yuta/move6.mp3").play(restart=True)
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove7Aim(self, app):
        self.takeEnergy, self.takeHp = 85, 0
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 800, 800, angle-45,
                90, fill='white', opacity=50, border='black', dashes=True)
    
    def move7(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/yuta/" +\
                                                 "moves/6/cutscene.png"))
            Sound("sounds/characters/yuta/move7.mp3").play(restart=True,
                                                            loop=False)
            img = [CMUImage(openImage("images/characters/inumaki/moves/5/img" +\
                                      ".png"))]
            angle = self.getAngle(app)
            move7 = PlayerMoves(self.x, self.y, 'cone', 800, 800, 10, 150, 10, 90,
                                True, 0, 0, 0, img, angle-45, 90)
            self.move7CD, self.stun = 180 * 60, 60
            self.performingMove, self.performingMoveLen = 7, 60
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove8Aim(self, app):
        # Draws an opaque white rectangle as aiming the move with facing offsets
        # if special ability is unlocked
        if not self.specialUnlocked:
            self.takeEnergy, self.takeHp = 150, 0
            if self.facing == 'left':
                drawRect(self.x-750 - app.scrollX, self.y - app.scrollY, 1500,
                     300, fill='white', opacity=50, border='black', dashes=True,
                     align='center')
            elif self.facing == 'right':
                drawRect(self.x+750 - app.scrollX, self.y - app.scrollY, 1500,
                     300, fill='white', opacity=50, border='black', dashes=True,
                     align='center')
    
    def move8(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            if self.specialUnlocked:
                app.cutscene, app.cutsceneLen = True, 60
                app.cutsceneImg = CMUImage(openImage("images/characters/yuta" +\
                                                 "/moves/7/special.png"))
                Sound("sounds/characters/yuta/special.mp3").play(restart=True,
                                                            loop=False)
                self.becomeHim(app)
            else:
                app.cutscene, app.cutsceneLen = True, 60
                app.cutsceneImg = CMUImage(openImage("images/characters/yuta" +\
                                                 "/moves/7/cutscene.png"))
                Sound("sounds/characters/yuta/move8.mp3").play(restart=True,
                                                            loop=False)
                self.trueLove(app)
            self.move8CD = 75 * 60
    
    def trueLove(self, app):
        if self.facing == 'left':
            img = [CMUImage(openImage("images/characters/yuta/moves/7/left" +\
                   f"{i}.png")) for i in range(2)]
            move8 = PlayerMoves(self.x-750, self.y, 'rect', 1500, 300, 300, 13,
                                15, 60, True, 0, 0, 15, img)
        elif self.facing == 'right':
            img = [CMUImage(openImage("images/characters/yuta/moves/7/right" +\
                   f"{i}.png")) for i in range(2)]
            move8 = PlayerMoves(self.x+750, self.y, 'rect', 1500, 300, 300, 13,
                                15, 60, True, 0, 0, 15, img)
        self.stun = 300
        self.performingMove, self.performingMoveLen = 8, 300
        self.iFrameLen = 300
    
    def becomeHim(self, app):
        app.player = Gojo()
        app.player.x, app.player.y = self.x, self.y
        app.player.awakeningLen, app.deathTimer = 30 * 60, 10 * 60
        app.player.specialUnlocked = True

############################################################
### THE STRONGEST ###
############################################################
class Gojo(Player):
    # Initializes important variables for The Strongest
    def __init__(self):
        # Initializes maxHp, maxEnergy, and maxAwakeningBar
        self.maxHp, self.maxEnergy, self.maxAwakeningBar = 225, 200, 1000
        self.hp, self.energy, self.awakeningBar = 225, 200, 0
        super().__init__()
        # Initializes the move names
        self.moveNames = ["Air Palm", "Blue",
                 "Red", "Infinity",
                 "Max Blue", "Max Red", "Hollow Purple",
                 "Domain Expansion"]
        # Gets the images for idle, walk, and stun sprite
        self.idle, self.walk, self.stunImg = self.getImages()
        # Gets the perfoming a move, death, and blocking sprites
        self.deathImg = CMUImage(openImage("images/characters/gojo/death.png"))
        self.blockImg = [CMUImage(openImage("images/characters/gojo/block" +\
                        f"{i}.png")) for i in range(2)]
        self.performImg = self.getPerformImg()
        self.infinity = 0
    
    # Gets the performing-a-move image sprites
    def getPerformImg(self):
        imgLst = [[], []]
        for i in range(9):
            imgLst[0].append(CMUImage(openImage("images/characters/gojo/" +\
                              f"perform/left{i}.png")))
        for i in range(9):
            imgLst[1].append(CMUImage(openImage("images/characters/gojo/" +\
                              f"perform/right{i}.png")))
        return imgLst
    
    # Gets the idle image sprites
    def getIdle(self):
        imgLst = [[], []]
        for i in range(4):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"gojo/idle/left{i}.png")))
        for i in range(4):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"gojo/idle/right{i}.png")))
        return imgLst
    
    # Gets the walking image sprites
    def getWalk(self):
        imgLst = [[], []]
        for i in range(8):
            imgLst[0].append(CMUImage(openImage(self.baseImgPath +\
                                             f"gojo/walk/left{i}.png")))
        for i in range(8):
            imgLst[1].append(CMUImage(openImage(self.baseImgPath +\
                                             f"gojo/walk/right{i}.png")))
        return imgLst
    
    # Gets the stunned image sprites
    def getStun(self):
        stunLst = [[], []]
        stunLst[0] = CMUImage(openImage(self.baseImgPath + "gojo/stun0.png"))
        stunLst[1] = CMUImage(openImage(self.baseImgPath + "gojo/stun1.png"))
        return stunLst
    
    def awaken(self, app):
        super().awaken(app)
        app.cutscene = True
        app.cutsceneLen = 120
        app.cutsceneImg = CMUImage(openImage("images/characters/gojo/" +\
                                             "awaken.png"))
        Sound("sounds/characters/gojo/awaken.mp3").play(restart=True,
                                                        loop=False)
    
    def onStep(self):
        super().onStep()
        if self.infinity > 0: self.infinity -= 1
    
    def drawPlayer(self, app):
        super().drawPlayer(app)
        if self.infinity > 0:
            drawImage(CMUImage(openImage("images/characters/gojo/moves/3/" +\
                      "img.png")), self.x - app.scrollX, self.y - app.scrollY,
                      align='center', opacity=50)
    
    # Launches a normal attack and offsets it according to where the player's
    # facing
    def mouse1(self, app):
        if self.facing == 'left':
            mouse1 = PlayerMoves(self.x-45, self.y, 'rect', 40,
                        40, 10, 7, 10, 20, False, -5, 0, 0,
                        [CMUImage(openImage("images/punch0.png"))])
        elif self.facing == 'right':
            mouse1 = PlayerMoves(self.x+45, self.y, 'rect', 40,
                        40, 10, 7, 10, 20, False, 5, 0, 0,
                        [CMUImage(openImage("images/punch1.png"))])
        self.stun = 15
        self.mouse1CD = 30
        self.performingMove, self.performingMoveLen = 0, 15
    
    # Draws an opaque white arc as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove1Aim(self, app):
        self.takeEnergy, self.takeHp = 15, 0
        angle = self.getAngle(app)
        drawArc(self.x - app.scrollX, self.y - app.scrollY, 800, 800, angle-20,
                40, fill='white', opacity=50, border='black', dashes=True)
    
    def move1(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            angle = self.getAngle(app)
            img = [CMUImage(openImage("images/characters/gojo/moves/0/img" +\
                                      ".png"))]
            move1 = PlayerMoves(self.x, self.y, 'cone', 800, 800, 10, 35, 10,
                                60, False, 45, 45, 30, img, angle-20, 40)
            self.move1CD, self.stun = 5 * 60, 45
            self.performingMove, self.performingMoveLen = 1, 45
            Sound("sounds/characters/gojo/move1.mp3").play(restart=True)
    
    # Draws a dashed line as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove2Aim(self, app):
        self.takeEnergy, self.takeHp = 20, 0
        angle = math.atan2(app.mouseY - self.y + app.scrollY,
                           app.mouseX - self.x + app.scrollX)
        endX = self.x - app.scrollX + (400 * math.cos(angle))
        endY = self.y - app.scrollY + (400 * math.sin(angle))
        drawLine(self.x - app.scrollX, self.y - app.scrollY, endX, endY,
                 dashes=True)
    
    def move2(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            angle = math.atan2(app.mouseY - self.y + app.scrollY,
                               app.mouseX - self.x + app.scrollX)
            img = [CMUImage(openImage(f"images/characters/gojo/moves/1/{i}" +\
                                      ".png")) for i in range(4)]
            move2 = PlayerProjectiles(self.x, self.y, 20, 20, 60, angle, 7,
                                      'blue', img)
            self.move2CD, self.stun = 7 * 60, 30
            self.performingMove, self.performingMoveLen = 2, 30
            Sound("sounds/characters/gojo/move2.mp3").play(restart=True)
    
    # Draws a dashed line as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove3Aim(self, app):
        self.takeEnergy, self.takeHp = 25, 0
        angle = math.atan2(app.mouseY - self.y + app.scrollY,
                           app.mouseX - self.x + app.scrollX)
        endX = self.x - app.scrollX + (400 * math.cos(angle))
        endY = self.y - app.scrollY + (400 * math.sin(angle))
        drawLine(self.x - app.scrollX, self.y - app.scrollY, endX, endY,
                 dashes=True)
    
    def move3(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            angle = math.atan2(app.mouseY - self.y + app.scrollY,
                               app.mouseX - self.x + app.scrollX)
            img = [CMUImage(openImage(f"images/characters/gojo/moves/2/{i}" +\
                                      ".png")) for i in range(3)]
            move3 = PlayerProjectiles(self.x, self.y, 20, 20, 60, angle, 7,
                                      'red', img)
            self.move3CD, self.stun = 10 * 60, 30
            self.performingMove, self.performingMoveLen = 3, 30
            Sound("sounds/characters/gojo/move3.mp3").play(restart=True)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove4Aim(self, app):
        self.takeEnergy, self.takeHp = 50, 0
    
    def move4(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            self.iFrameLen = 30 * 60
            self.infinity = 30 * 60
            self.move4CD, self.stun = 60 * 60, 60
            self.performingMove, self.performingMoveLen = 4, 60
            Sound("sounds/characters/gojo/move4.mp3").play(restart=True)
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove5Aim(self, app):
        self.takeEnergy, self.takeHp = 40, 0
    
    def move5(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            duration = 90 if not self.specialUnlocked else 240
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/gojo/" +\
                                                 "moves/4/cutscene.png"))
            Sound("sounds/characters/gojo/move5.mp3").play(restart=True,
                                                           loop=False)
            move4 = PlayerEntities(self.x, self.y, 'maxBlue', duration, [])
            self.move5CD, self.stun = 14 * 60, 60
            self.performingMove, self.performingMoveLen = 5, 60
    
    # Draws a dashed line as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove6Aim(self, app):
        self.takeEnergy, self.takeHp = 45, 0
        angle = math.atan2(app.mouseY - self.y + app.scrollY,
                           app.mouseX - self.x + app.scrollX)
        endX = self.x - app.scrollX + (1000 * math.cos(angle))
        endY = self.y - app.scrollY + (1000 * math.sin(angle))
        drawLine(self.x - app.scrollX, self.y - app.scrollY, endX, endY,
                 dashes=True)
    
    def move6(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/gojo/" +\
                                                 "moves/5/cutscene.png"))
            Sound("sounds/characters/gojo/move6.mp3").play(restart=True,
                                                           loop=False)
            img = [CMUImage(openImage(f"images/characters/gojo/moves/5/img" +\
                                      ".png"))]
            angle = math.atan2(app.mouseY - self.y + app.scrollY,
                               app.mouseX - self.x + app.scrollX)
            move7 = PlayerProjectiles(self.x, self.y, 70, 70, 60, angle, 30,
                                      'maxRed', img)
            self.move6CD, self.stun = 25 * 60, 60
            self.performingMove, self.performingMoveLen = 6, 60
    
    # Draws a dashed line as aiming the move
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove7Aim(self, app):
        self.takeEnergy, self.takeHp = 100, 0
        angle = math.atan2(app.mouseY - self.y + app.scrollY,
                           app.mouseX - self.x + app.scrollX)
        endX = self.x - app.scrollX + (800 * math.cos(angle))
        endY = self.y - app.scrollY + (800 * math.sin(angle))
        drawLine(self.x - app.scrollX, self.y - app.scrollY, endX, endY,
                 dashes=True)
    
    def move7(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/gojo/" +\
                                                 "moves/6/cutscene.png"))
            Sound("sounds/characters/gojo/move7.mp3").play(restart=True,
                                                           loop=False)
            img = [CMUImage(openImage(f"images/characters/gojo/moves/6/{i}" +\
                                      ".png")) for i in range(3)]
            angle = math.atan2(app.mouseY - self.y + app.scrollY,
                               app.mouseX - self.x + app.scrollX)
            move7 = PlayerProjectiles(self.x, self.y, 300, 300, 240, angle, 14,
                                      'purple', img)
            self.move7CD, self.stun = 60 * 60, 90
            self.performingMove, self.performingMoveLen = 7, 90
    
    # Initializes takeEnergy and takeHp to highlight how much the move will take
    def drawMove8Aim(self, app):
        self.takeEnergy, self.takeHp = 150, 0
    
    def move8(self, app):
        if self.energy >= self.takeEnergy and self.hp >= self.takeHp:
            self.takePlayerBar()
            self.choosingMove = None
            app.cutscene = True
            app.cutsceneLen = 60
            app.cutsceneImg = CMUImage(openImage("images/characters/gojo/" +\
                                                 "moves/7/cutscene.png"))
            Sound("sounds/characters/gojo/move8.mp3").play(restart=True,
                                                           loop=False)
            move8 = PlayerDomains('limitless', 20*60, app.domainSounds[0])
            self.stun, self.iFrameLen = 120, 120
            self.move8CD = 150 * 60
            self.performingMove, self.performingMoveLen = 8, 120
            app.currentSound.pause()
            app.domainSounds[0].play(restart=True, loop=False)