from cmu_graphics import *
import random
import math

from PIL import Image as PilImage
import os
import pathlib

def openImage(fileName):
    return PilImage.open(os.path.join(pathlib.Path(__file__).parent, fileName))

############################################################
### MOVES ###
############################################################
class Moves:
    # Initializes important variables for a move entity
    def __init__(self, x, y, shape, width, height, duration, dmg, dps, stun,
                 heavyAtk, knockbackX, knockbackY, imgLst, startAngle=0,
                 sweepAngle=0):
        # Initializes the center coordinate, shape, width, height, and duration
        self.x, self.y, self.shape = x, y, shape
        self.width, self.height, self.duration = width, height, duration
        # Initializes its damage over time, damage, stun deal, and if it's a
        # heavy attack or not
        self.dps, self.dmg, self.stun, self.heavyAtk = dps, dmg, stun, heavyAtk
        # Initializes its knockback relative to X and Y
        self.knockbackX, self.knockbackY = knockbackX, knockbackY
        self.startAngle = startAngle
        self.sweepAngle = sweepAngle
        # Initializes variables related to the move's image
        self.imgLst, self.imgIndex, self.imgCounter = imgLst, 0, 0
    
    # An onStep for changing the images
    def imgOnStep(self):
        # Increases the imgCounter if the length of the image is more than 0
        if len(self.imgLst) > 0:
            self.imgCounter += 1
            # Changes the image index every 2 steps
            if self.imgCounter == 2:
                self.imgIndex = (self.imgIndex + 1) % len(self.imgLst)
                self.imgCounter = 0
    
    # Inflicts damage to another entity (enemy or player)
    def inflictDamage(self, other, app):
        # Only inflicts damage if the enemy is not in iFrame (invincible)
        if other.iFrameLen == 0:
            # Calculates the angular knockback if the knockbacks are equal
            if self.knockbackX == self.knockbackY:
                angle = math.atan2(other.y - self.y, other.x - self.x)
                newKnockbackX = self.knockbackX * math.cos(angle)
                newKnockbackY = self.knockbackY * math.sin(angle)
            else:
                newKnockbackX, newKnockbackY = self.knockbackX, self.knockbackY
            # Inflicts damage to the entity if they are not blocking or if the
            # move is a heavy attack
            if not other.isBlocking or self.heavyAtk:
                other.hp -= self.dmg
                other.stun = self.stun
                # Ensures damage over time
                other.iFrameLen = self.dps
                other.x += newKnockbackX
                other.y += newKnockbackY
                Sound("sounds/hit.mp3").play()
    
    # Gets a list of the corner coordinates of a certain rectangular entity
    @staticmethod
    def getRectHitboxCorner(obj):
        objRight = obj.x + obj.width/2
        objLeft = obj.x - obj.width/2
        objTop = obj.y - obj.height/2
        objBottom = obj.y + obj.height/2
        return [objRight, objLeft, objTop, objBottom]
    
    # Gets a list of the distance of rectangle corners to the center of the move
    def cornerDistToCenter(self, corners):
        cornerDist = []
        for i in range(0, 2):
            for j in range(2, 4):
                dist = ((corners[i]-self.x)**2 + (corners[j]-self.y)**2)**0.5
                cornerDist.append(dist)
        return cornerDist
    
    # Gets a list of angles of the rectangle corners to the center of the move
    def angleToCenter(self, corners):
        cornerAngles = []
        for i in range(0, 2):
            for j in range(2, 4):
                xDist, yDist = corners[i]-self.x, corners[j]-self.y
                cornerAngles.append(math.atan2(yDist, xDist) * (-180 / math.pi)\
                                    % 360)
        return cornerAngles
    
    # Calculates the rectangle to rectangle collision of the move and an entity
    def rectCollision(self, other):
        right0 = self.x + self.width/2
        bottom0 = self.y + self.height/2
        right1 = other.x + 50/2
        bottom1 = other.y + 50/2
        if ((right1 >= self.x - self.width/2) and right0 >= other.x - 50/2 and\
            (bottom1 >= self.y - self.height) and (bottom0 >= other.y - 50/2)):
            return True
    
    # Calculates the arc to rectangle collision of the move and an entity
    def coneCollision(self, other):
        rectCornerLoc = self.getRectHitboxCorner(other)
        cornerDist = self.cornerDistToCenter(rectCornerLoc)
        cornerAngle = self.angleToCenter(rectCornerLoc)
        coneAngle = self.sweepAngle
        coneStart = self.startAngle
        # Loops through every corner's data
        for i in range(4):
            # Calculates its distance and angle (accounts for negative angles)
            if cornerDist[i] <= self.width/2 and\
           ((coneStart) < cornerAngle[i] < (coneStart+coneAngle) or\
            (coneStart-360) < cornerAngle[i] < (coneStart+coneAngle-360) or\
            (coneStart) < cornerAngle[i]-360 < (coneStart+coneAngle) or\
            (coneStart-360) < cornerAngle[i]-360 < (coneStart+coneAngle-360)):
                return True
    
    # Calculates the circle to rectangle collision of the move and an entity
    def ovalCollision(self, other):
        rectCornerLoc = self.getRectHitboxCorner(other)
        cornerDist = self.cornerDistToCenter(rectCornerLoc)
        for dist in cornerDist:
            if dist <= self.width/2:
                return True
    
    # Draws the move on the map given the conditions
    def drawMove(self, app):
        if self.windup > 0:
            # Draws a black bordered shape based on its width and height if it's
            # still in windup stage
            if self.shape == 'rect':
                drawRect(self.x - app.scrollX, self.y - app.scrollY, self.width,
                         self.height, border='black', align='center', fill=None)
            if self.shape == 'oval':
                drawOval(self.x - app.scrollX, self.y - app.scrollY, self.width,
                         self.height, border='black', fill=None)
            if self.shape == 'cone':
                drawArc(self.x - app.scrollX, self.y - app.scrollY, self.width,
                        self.height, self.startAngle, self.sweepAngle,
                        fill=None, border='black')
        else:
            # Draws the move's image based on image index if the duration is
            # greater than 0 and not in a windup stage
            if self.duration > 0 and self.imgLst != []:
                drawImage(self.imgLst[self.imgIndex],
                    self.x - app.scrollX, self.y - app.scrollY, align='center',
                    rotateAngle=360 - self.startAngle - (self.sweepAngle / 2))
    
class PlayerMoves(Moves):
    playerMoves = []
    # Initializes important variables for a move entity casted by players
    def __init__(self, x, y, shape, width, height, duration, dmg, dps, stun,
                 heavyAtk, knockbackX, knockbackY, windup, imgLst, startAngle=0,
                 sweepAngle=0):
        # Calls the superclass' __init__()
        super().__init__(x, y, shape, width, height, duration, dmg, dps, stun,
                       heavyAtk, knockbackX, knockbackY, imgLst, startAngle,
                         sweepAngle)
        # Stores the windup variable and appends the move to playerMoves list
        self.windup = windup
        PlayerMoves.playerMoves.append(self)
    
    # Identifies any collision with the enemy based on the move's shape. Every
    # hit will increase the player's awakening bar by the damage they dealt
    def collision(self, player, enemy, app):
        if enemy.iFrameLen == 0:
            # If the shape is 'cone', then do the cone (arc) collision
            if self.shape == 'cone' and self.coneCollision(enemy):
                self.inflictDamage(enemy, app)
                if player.awakeningLen <= 0: player.awakeningBar += self.dmg
            # If the shape is 'oval', then do the oval (circle) collision
            elif self.shape == 'oval' and self.ovalCollision(enemy):
                self.inflictDamage(enemy, app)
                if player.awakeningLen <= 0: player.awakeningBar += self.dmg
            # If the shape is 'rect', then do the rectangular collision
            elif self.shape == 'rect' and self.rectCollision(enemy):
                self.inflictDamage(enemy, app)
                if player.awakeningLen <= 0: player.awakeningBar += self.dmg
    
class EnemyMoves(Moves):
    enemyMoves = []
    # Initializes important variables for a move entity casted by enemies
    def __init__(self, x, y, shape, width, height, duration, dmg, dps, stun,
                 heavyAtk, knockbackX, knockbackY, windup, imgLst, startAngle=0,
                 sweepAngle=0):
        # Calls the superclass' __init__()
        super().__init__(x, y, shape, width, height, duration, dmg, dps, stun,
                      heavyAtk, knockbackX, knockbackY, imgLst,
                         startAngle, sweepAngle)
        # Stores the windup variable and appends the move to enemyMoves list
        EnemyMoves.enemyMoves.append(self)
        self.windup = windup
    
    # Identifies any collision with the player based on the move's shape
    def collision(self, player, app):
        # Decreases the duration only if the windup is 0
        if self.windup > 0: self.windup -= 1
        if self.windup == 0:
            self.duration -= 1
            if player.iFrameLen == 0:
                # If the shape is 'cone', then do the cone (arc) collision
                if self.shape == 'cone' and self.coneCollision(player):
                    self.inflictDamage(player, app)
                # If the shape is 'oval', then do the oval (circle) collision
                elif self.shape == 'oval' and self.ovalCollision(player):
                    self.inflictDamage(player, app)
                # If the shape is 'rect', then do the rectangular collision
                elif self.shape == 'rect' and self.rectCollision(player):
                    self.inflictDamage(player, app)

class PlayerEntities:
    playerEntities = []
    # Initializes important variables for a ally entity casted by players
    def __init__(self, x, y, name, duration, images):
        # Gets the x, y coordinate, name, duration, and images
        self.x, self.y, self.name, self.duration = x, y, name, duration
        self.facingIndex = 1
        self.images, self.imgIndex, self.imgCounter = images, 0, 0
        # Initializes a move if the name is 'maxBlue' and its own different img
        if self.name == 'maxBlue':
            img = [CMUImage(openImage("images/characters/gojo/moves/4/" +\
                   f"{i}.png")) for i in range(3)]
            # Negative knockback to suck the enemies in
            self.maxBlueInner = PlayerMoves(x, y, 'oval', 150, 150, duration, 3,
                                            6, 5, True, -15, -15, 0, [])
            self.maxBlueOuter = PlayerMoves(x, y, 'oval', 250, 250, duration, 0,
                                            7, 0, True, -15, -15, 0, img)
            # Follows the mouse only for this fixed amount of time
            self.moveableDuration = 90
        # Initializes move cooldown and stun if it's a dog
        elif self.name == 'dog':
            self.moveCD, self.stun = 0, 0
        PlayerEntities.playerEntities.append(self)
    
    # Does the cooldown onStep for the entities
    def cooldown(self):
        if len(self.images) > 0:
            self.imgCounter += 1
            # Increases the image index every 10 steps
            if self.imgCounter == 10:
                self.imgIndex = (self.imgIndex + 1) % len(self.images)
                self.imgCounter = 0
        if self.duration > 0: self.duration -= 1
        # Decreases moveCD for dogs and moveableDuration for maxBlues
        if self.name == 'dog' and self.moveCD > 0: self.moveCD -= 1
        if self.name == 'maxBlue' and self.moveableDuration > 0:
            self.moveableDuration -= 1
        # Removes the entity if its duration is 0
        if self.duration == 0: PlayerEntities.playerEntities.remove(self)
    
    # Does the movement behavior for all entities
    def autoMove(self, app, enemies):
        if self.name == 'maxBlue':
            self.autoMoveMaxBlue(app, enemies)
        elif self.name == 'dog':
            self.autoMoveDog(enemies)
    
    # Returns the minimum distance from each enemy present in the game with its
    # X and Y coordinate
    def getMinDist(self, enemies):
        minDist = None
        enemyX = 0
        enemyY = 0
        for enemy in enemies:
            dist = ((enemy.x - self.x)**2 + (enemy.y - self.y)**2)**0.5
            if minDist == None or dist < minDist:
                enemyX, enemyY, minDist = enemy.x, enemy.y, dist
        return enemyX, enemyY, minDist
    
    # Moves the entity 'maxBlue' according to the cursor's movements
    def autoMoveMaxBlue(self, app, enemies):
        if self.moveableDuration > 0:
            # Calculates the angle with of the mouse with respect to the center
            angle = math.atan2(app.mouseY - self.y + app.scrollY,
                               app.mouseX - self.x + app.scrollX)
            # Only moves maxBlue at a set average angular speed of 12 pixels
            self.x += 12 * math.cos(angle)
            self.y += 12 * math.sin(angle)
            self.maxBlueInner.x += 12 * math.cos(angle)
            self.maxBlueInner.y += 12 * math.sin(angle)
            self.maxBlueOuter.x += 12 * math.cos(angle)
            self.maxBlueOuter.y += 12 * math.sin(angle)
    
    # Moves the entity dogs according to the minimum distance to an enemy
    def autoMoveDog(self, enemies):
        enemyX, enemyY, minDist = self.getMinDist(enemies)
        # Gets the angle to the enemy and set the overall angular speed of 6 px
        angle = math.atan2(enemyY - self.y, enemyX - self.x)
        dx = 6 * math.cos(angle)
        dy = 6 * math.sin(angle)
        # If the distance is more than 50, move the dogs with the speed
        if ((self.x - enemyX)**2 + (self.y - enemyY)**2)**0.5 > 50:
            self.x, self.y = self.x + dx, self.y + dy
        # Resets the facing variable of the dogs
        if dx < 0: facing, self.facingIndex = 'left', 0
        elif dx > 0: facing, self.facingIndex = 'right', 1
        # Attacks if the closest enemy is within 50 pixels away
        if ((self.x - enemyX)**2 + (self.y - enemyY)**2)**0.5 <= 50:
            self.dogAttack(facing)
    
    # Launches a PlayerMoves attack based on its facing variable
    def dogAttack(self, facing):
        if self.moveCD == 0:
            img = [CMUImage(openImage("images/globalmoves/dogatk.png"))]
            # Initializes a rectangular move offset to the left if facing left
            if facing == 'left':
                dogMove = PlayerMoves(self.x-50, self.y, 'rect', 50, 50, 10, 25,
                                      10, 10, True, 5, 0, 0, img)
            # Initializes a rectangular move offset to the right if facing right
            elif facing == 'right':
                dogMove = PlayerMoves(self.x+50, self.y, 'rect', 50, 50, 10, 25,
                                      10, 10, True, -5, 0, 0, img)
            self.moveCD = 90
            self.stun = 45
    
    # Draws the dog entity based on its facing and image index
    def drawEntity(self, app):
        if self.name == 'dog' and self.duration > 0:
            drawImage(self.images[self.facingIndex][self.imgIndex],
                    self.x - app.scrollX, self.y - app.scrollY, align='center')

class Domains:
    domains = []
    # Initializes name, duration, and sound for a domain. Appends it to a list
    # of domains
    def __init__(self, name, duration, sound):
        self.name, self.duration, self.sound = name, duration, sound
        Domains.domains.append(self)
    
    # Decreases the duration and removes it if it hits 0
    def onStep(self):
        self.duration -= 1
        if self.duration == 0: Domains.domains.remove(self)
    
class PlayerDomains(Domains):
    playerDomains = []
    # Initializes name, duration, and sound for a domain. Appends it to a list
    # of playerDomains
    def __init__(self, name, duration, sound):
        super().__init__(name, duration, sound)
        PlayerDomains.playerDomains.append(self)
    
    # Draws the domain as the game map if unleashed according to domainImages
    def drawDomain(self, app):
        if self.name == 'limitless': drawImage(app.domainImages[0], 0, 0)
        elif self.name == 'malevolent': drawImage(app.domainImages[1], 0, 0)
        elif self.name == 'shadow': drawImage(app.domainImages[2], 0, 0)
    
    # Does specific commands and changes of the domain for every step
    def onStep(self, app, enemies):
        self.duration -= 1
        # Does the specific commands based on the domain's name
        if self.name == 'limitless': self.limitlessOnStep(app, enemies)
        if self.name == 'malevolent': self.malevolentOnStep(app)
        if self.name == 'shadow': self.shadowOnStep(app)
        # Removes domain from domains and playerDomains if its duration is 0
        if self.duration == 0:
            self.sound.pause()
            app.currentSound = app.battleSounds[random.randint(0, 3)]
            app.currentSound.play(restart=True, loop=True)
            Domains.domains.remove(self)
            PlayerDomains.playerDomains.remove(self)
    
    # Does the 'Unlimited Void' domain commands every step
    def limitlessOnStep(self, app, enemies):
        # Stuns all enemies for 10 seconds
        if self.duration % 1 == 0:
            for enemy in enemies:
                enemy.stun = 600
        # Deals a map-wide PlayerMove damage upon the end of its duration
        if self.duration == 0:
            PlayerMoves(1000, 1000, 'rect', 2000, 2000, 1, 350, 1, 600, True,
                        0, 0, 0, [])
    
    # Does the 'Malevolent Shrine' domain commands every step
    def malevolentOnStep(self, app):
        # Unleashes a map-wide PlayerMove every half-second
        if self.duration % 30 == 0:
            img = [CMUImage(openImage("images/enemies/sukuna/moves/p3m1/" +\
                   f"{i}.png")) for i in range(2)]
            PlayerMoves(1000, 1000, 'rect', 2000, 2000, 4, 2, 4, 12, False, 0,
                        0, 0, img)
    
    # Does the 'Chimera Shadow Garden' domain commands every step
    def shadowOnStep(self, app):
        # Randomly spawns moves every half-second at a random X and Y
        if self.duration % 30 == 0:
            num = random.randint(1, 2)
            randomX = random.randint(200, 1800)
            randomY = random.randint(200, 1800)
            # Spawns the rabbits PlayerMoves based on the randomized X and Y
            if num == 1:
                img = [CMUImage(openImage("images/characters/megumi/moves/0/" +\
                       f"{i}.png")) for i in range(2)]
                PlayerMoves(randomX, randomY, 'oval', 200, 200, 60, 3, 5, 1,
                            False, 0, 0, 0, img)
            # Spawns the hawk PlayerMoves based on the randomized X and Y
            else:
                img = [CMUImage(openImage("images/characters/megumi/moves/1/" +\
                       f"{i}.png")) for i in range(5)]
                PlayerMoves(randomX, randomY, 'oval', 200, 200, 10, 25, 10, 90,
                            True, 0, 0, 0, img)
        # Spawns a dog every 2 seconds
        if self.duration % 120 == 0:
            self.spawnDog()
    
    # Randomly spawns a random dog at random X and Y coordinates in the map
    def spawnDog(self):
        # Randomizes the X and Y coordinates
        randomX, randomY = random.randint(25, 1975), random.randint(25, 1975)
        # Spawns the white dog based on the randomized X and Y
        if random.randint(0, 1) == 0:
            images = [[], []]
            for i in range(2):
                images[0].append(CMUImage(openImage("images/characters/megum" +\
                      f"i/moves/2/left{i}.png")))
            for i in range(2):
                images[1].append(CMUImage(openImage("images/characters/megum" +\
                      f"i/moves/2/right{i}.png")))
            PlayerEntities(randomX, randomY, 'dog', 20*60, images)
        # Spawns the black dog based on the randomized X and Y
        else:
            images = [[], []]
            for i in range(2):
                images[0].append(CMUImage(openImage("images/characters/megum" +\
                      f"i/moves/3/left{i}.png")))
            for i in range(2):
                images[1].append(CMUImage(openImage("images/characters/megum" +\
                      f"i/moves/3/right{i}.png")))
            PlayerEntities(randomX, randomY, 'dog', 20*60, images)

class EnemyDomains(Domains):
    enemyDomains = []
    # Initializes name, duration, and sound for a domain. Appends it to a list
    # of enemyDomains
    def __init__(self, name, duration, sound):
        super().__init__(name, duration, sound)
        EnemyDomains.enemyDomains.append(self)
    
    # Draws the domain as the game map if unleashed according to domainImages
    def drawDomain(self, app):
        if self.name == 'hands': drawImage(app.domainImages[3], 0, 0)
        elif self.name == 'shrine': drawImage(app.domainImages[1], 0, 0)
        elif self.name == 'volcano': drawImage(app.domainImages[4], 0, 0)
    
    # Does specific commands and changes of the domain for every step
    def onStep(self, app):
        self.duration -= 1
        # Does the specific commands based on the domain's name
        if self.name == 'shrine': self.shrineOnStep(app)
        if self.name == 'hands': self.handsOnStep(app)
        if self.name == 'volcano': self.volcanoOnStep(app)
        # Removes domain from domains and enemyDomains if its duration is 0
        if self.duration == 0:
            self.sound.pause()
            app.currentSound = app.battleSounds[random.randint(0, 3)]
            app.currentSound.play(restart=True, loop=True)
            Domains.domains.remove(self)
            EnemyDomains.enemyDomains.remove(self)
    
    # Does the 'Malevolent Shrine' domain commands every step
    def shrineOnStep(self, app):
        # Unleashes a map-wide EnemyMove every half-second
        if self.duration % 30 == 0:
            img = [CMUImage(openImage("images/enemies/sukuna/moves/p3m1/" +\
                   f"{i}.png")) for i in range(2)]
            EnemyMoves(1000, 1000, 'rect', 2000, 2000, 4, 2, 4, 7, False, 0, 0,
                       0, img)
            app.player.hp -= 1
    
    # Does the 'Self-Embodiment of Perfection' domain commands every step
    def handsOnStep(self, app):
        # Unleashes a random 'hands' circular EnemyMove every half-second at a
        # random X and Y coordinate in the map
        if self.duration % 30 == 0:
            img = [CMUImage(openImage("images/enemies/mahito/moves/p3m1/" +\
                   f"{i}.png")) for i in range(5)]
            randomX = random.randint(100, 1900)
            randomY = random.randint(100, 1900)
            EnemyMoves(randomX, randomY, 'oval', 200, 200, 10, 50, 10, 90, True,
                       0, 0, 60, img)
    
    # Does the 'Coffin of the Iron Mountain' domain commands every step
    def volcanoOnStep(self, app):
        # Unleashes a random 'lava' circular EnemyMove every half-second at a
        # random X and Y coordinate in the map
        if self.duration % 30 == 0:
            img = [CMUImage(openImage("images/enemies/jogo/moves/p3m1/" +\
                   f"{i}.png")) for i in range(5)]
            randomX = random.randint(100, 1900)
            randomY = random.randint(100, 1900)
            EnemyMoves(randomX, randomY, 'oval', 200, 200, 10, 1,
                       1, 0, True, 3, 3, 60, img)

class Projectiles(Moves):
    # Initializes important variables for a projectile
    def __init__(self, x, y, width, height, duration, moveAngle, speed):
        self.x, self.y, self.moveAngle, self.speed = x, y, moveAngle, speed
        self.width, self.height, self.duration = width, height, duration
    
    # Moves the projectile based on its speed if its windup variable (as a move)
    # is 0
    def onStep(self, app):
        if self.projectile.windup == 0:
            self.x += self.speed * math.cos(self.moveAngle)
            self.y += self.speed * math.sin(self.moveAngle)
            self.projectile.x, self.projectile.y = self.x, self.y
            self.duration -= 1
    
class PlayerProjectiles(Projectiles):
    playerProjectiles = []
    # Initializes important variables for a projectile
    def __init__(self, x, y, width, height, duration, moveAngle, speed, name,
                 img):
        # Calls the superclass' __init__() and name
        super().__init__(x, y, width, height, duration, moveAngle, speed)
        self.name = name
        rotation = moveAngle * (-180 / math.pi)
        # Makes the projectile have no damage if its name isn't purple or maxRed
        if name != 'purple' and name != 'maxRed':
            # Initializes a widup if its name is fuga
            windup = 60 if name == 'fuga' else 0
            self.projectile = PlayerMoves(x, y, 'oval', width, height, duration,
                                0, 0, 0, True, 0, 0, windup, img, rotation)
        else:
            # Sets the windup and dmg depending on the name of the projectile
            windup = 60 if name == 'purple' else 15
            dmg = 350 if name == 'purple' else 60
            self.projectile = PlayerMoves(x, y, 'oval', width, height, duration,
                            dmg, 60, 60, True, 0, 0, windup, img, rotation)
            # Gets an existing maxBlue ally entity's center coordinates
            if self.name == 'maxRed':
                self.maxBlueEntity = self.getMaxBlueCoords()
        # Adds this projectile to the playerProjectiles list
        PlayerProjectiles.playerProjectiles.append(self)
    
    # Does specific commands and changes for each step depending on the name
    def onStep(self, app):
        super().onStep(app)
        if self.name == 'blue': self.blueOnStep()
        if self.name == 'red': self.redOnStep()
        if self.name == 'fuga': self.fugaOnStep()
        if self.name == 'maxRed': self.maxRedOnStep(app)
        # Removes from the list if the duration is over
        if self.duration == 0: PlayerProjectiles.playerProjectiles.remove(self)
    
    # Finds if there is a maxBlue entity in playerEntities and returns it
    def getMaxBlueCoords(self):
        for entity in PlayerEntities.playerEntities:
            if entity.name == 'maxBlue': return entity
    
    # Does specific commands for a 'maxRed' projectile every step
    def maxRedOnStep(self, app):
        # Creates a HollowNuke if collides with a maxBlue and the player has
        # their special ability
        if app.player.specialUnlocked and self.maxBlueEntity != None:
            if ((self.maxBlueEntity.x - self.x)**2 +\
                (self.maxBlueEntity.y - self.y)**2)**0.5 <= 160:
                self.maxBlueEntity.duration, self.projectile.duration = 0, 0
                self.duration = 0
                HollowNuke(self.maxBlueEntity.x, self.maxBlueEntity.y)
                # Resets the awakening to balance
                app.player.awakeningLen = 0
    
    # Does specific commands for a 'blue' projectile every step
    def blueOnStep(self):
        # Explodes into a blue circular player move and sucks enemies in if
        # duration is over
        if self.duration == 0:
            img = [CMUImage(openImage("images/characters/gojo/moves/1/" +\
                   f"exe{i}.png")) for i in range(5)]
            PlayerMoves(self.x, self.y, 'oval', 185, 185, 10, 30, 10, 60,
                        True, -50, -50, 0, img)
            self.duration = 0
            Sound("sounds/globalMoves/blue.mp3").play(restart=True)
    
    # Does specific commands for a 'red' projectile every step
    def redOnStep(self):
        # Explodes into a red circular plaeyer move and blows enemies away if
        # duration is over
        if self.duration == 0:
            img = [CMUImage(openImage("images/characters/gojo/moves/2/" +\
                   f"exe{i}.png")) for i in range(5)]
            PlayerMoves(self.x, self.y, 'oval', 215, 215, 10, 45, 10, 90,
                        True, 50, 50, 0, img)
            self.duration = 0
            Sound("sounds/globalMoves/red.mp3").play(restart=True)
    
    # Does specific commands for a 'fuga' projectile every step
    def fugaOnStep(self):
        # Explodes into a circular player move that deals high damage to enemies
        # if the duration is over
        if self.duration == 0:
            PlayerMoves(self.x, self.y, 'oval', 500, 500, 10, 80, 10, 180,
                        True, 100, 100, 0,
                        [CMUImage(openImage("images/globalmoves/fugaExe/" +\
                        f"{i}.png")) for i in range(5)])
            self.duration = 0
            Sound("sounds/globalMoves/fugaExe.mp3").play(restart=True)

class EnemyProjectiles(Projectiles):
    enemyProjectiles = []
    # Initializes important variables for a projectile
    def __init__(self, x, y, width, height, duration, moveAngle, speed, name,
                 img):
        # Calls the superclass' __init__() and name
        super().__init__(x, y, width, height, duration, moveAngle, speed)
        self.name = name
        # Since the only EnemyProjectile is fuga, it initializes the projectile
        # as the 'fuga' projectile for enemies
        rotation = moveAngle * (-180 / math.pi)
        self.projectile = EnemyMoves(x, y, 'oval', width, height, duration, 0,
                                      0, 0, True, 0, 0, 60, img, rotation)
        # Adds this projectile to the enemyProjectiles list
        EnemyProjectiles.enemyProjectiles.append(self)
    
    # Does specific commands and changes for each step depending on the name
    def onStep(self, app):
        super().onStep(app)
        if self.name == 'fuga': self.fugaOnStep()
        # Removes from the list if the duration is over
        if self.duration == 0: EnemyProjectiles.enemyProjectiles.remove(self)
    
    # Does specific commands for a 'fuga' projectile every step
    def fugaOnStep(self):
        # Explodes into a circular enemy move that deals high damage to player
        # if the duration is over
        if self.duration == 0:
            EnemyMoves(self.x, self.y, 'oval', 500, 500, 10, 50, 10, 120,
                       True, 30, 30, 0,
                       [CMUImage(openImage("images/globalmoves/fugaExe/" +\
                        f"{i}.png")) for i in range(5)])
            self.duration = 0
            Sound("sounds/globalMoves/fugaExe.mp3").play(restart=True)

class HollowNuke:
    hollowNukes = []
    # Initializes important variables for a HollowNuke and stores it in a list
    def __init__(self, x, y):
        self.x, self.y, self.duration = x, y, 360
        HollowNuke.hollowNukes.append(self)
        # Gets the cutscene images to be initiated
        self.cutscenes = [CMUImage(openImage("images/globalmoves/hollowNuke/" +\
                          f"cutscene/{i}.png")) for i in range(9)]
        self.cutsceneIndex = 0
        # Gets the hollow purple orb images that will be on the game map
        self.nukeImg = [CMUImage(openImage("images/globalmoves/hollowNuke/" +\
                                           f"{i}.png")) for i in range(4)]
        self.imgIndex, self.imgCounter = 0, 0
    
    # Initiates a cutscene for half a second and plays a dramatic boom sound
    def cutsceneInit(self, app):
        app.cutscene = True
        app.cutsceneLen = 30
        Sound("sounds/mahoboom.mp3").play(restart=True)
    
    # Does specific commands and changes for each step for a HollowNuke
    def onStep(self, app):
        if self.duration > 0: self.duration -= 1
        # Initiates a different cutscene every half second
        if self.duration % 30 == 0 and self.cutsceneIndex <= 8:
            self.cutsceneInit(app)
            app.cutsceneImg = self.cutscenes[self.cutsceneIndex]
            self.cutsceneIndex += 1
        # Explodes and damages all enemies and players when the duration is over
        if self.duration == 0:
            app.player.hp, app.player.stun = 15, 240
            for enemy in app.enemyList:
                enemy.hp, enemy.stun = 1, 300
            # Removes the HollowNuke from the list
            HollowNuke.hollowNukes.remove(self)
            Sound("sounds/globalMoves/nukeExe.mp3").play(restart=True)
        # Changes the frame of the image every 2 steps
        self.imgCounter += 1
        if self.imgCounter == 2:
            self.imgCounter = 0
            self.imgIndex = (self.imgIndex + 1) % len(self.nukeImg)
    
    # Draws the Hollow Purple orb on the game map based on the X and Y coords
    def drawNuke(self, app):
        drawImage(self.nukeImg[self.imgIndex], self.x - app.scrollX,
             self.y - app.scrollY, align='center', width=500, height=500)
        # Adds a dramatic white screen that increases in opacity
        if self.duration <= 100:
            drawRect(0, 0, app.width, app.height, fill='white',
                     opacity=100-self.duration)