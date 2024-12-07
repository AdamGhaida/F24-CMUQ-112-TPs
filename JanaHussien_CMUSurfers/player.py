from cmu_graphics import *
from models import Model
from models import Coin, Train, Ramp, Duck, Jump, DuckNJump
from models import HoverBoard, Sneakers, ScoreBooster, CoinMagnet


class Player:
    def __init__(self):
        self.scoreMultiplier = 1
        self.rollTimer = 0
        self.hasCoinMagnet = False
        self.lane = 1
        self.y = 460
        self.isOnHoverBoard = False
        self.velocity = 0
        self.isJumping = False
        self.isRolling = False
        self.isFalling = False
        self.gravity = -1
        self.jumpVelocity = 9.5
        self.x = app.width//2
        self.isSwitchingLanes = False
        self.onCollideCooldown = False
        self.JakeImgIndex = 0
        self.isOnTrain = False
        self.laneToOffsets = {0: 1.1, 1: 0, 2:-1.1} 
        self.isOnRamp = False
        self.time = 0
        self.powerUpTimer = 0


    
        self.JakeReg = [f'PlayerSprites/Reg/Jake{i}.png' for i in range(15)]
        self.JakeRegRoll = [f'PlayerSprites/RegRoll/Jake{i}.png' for i in range(15)]
        self.JakeBoardReg = [f'PlayerSprites/BoardReg/Jake{i}.png' for i in range(24)]
        self.JakeBoardRoll = [f'PlayerSprites/BoardRoll/Jake{i}.png' for i in range(14)]
        self.curSprite = self.JakeReg
        self.JakeImgIndex = 0
        
        self.activePowerUp = None
        self.powerUpTimer = 0
        self.isInvincible = False
        self.speedBoost = 0
        
    def getPowerUpName(self):
        if self.activePowerUp:
            return str(self.activePowerUp)
        return "No Power-Up"
    
    def activatePowerUp(self, powerUpType):
        if self.activePowerUp == None:
            self.activePowerUp = powerUpType
        
        if powerUpType == ScoreBooster:
            self.scoreMultiplier = 5
        
        elif powerUpType == Sneakers:
            self.jumpVelocity += 5
    
        elif powerUpType == HoverBoard:
            self.isInvincible = True
            self.isOnHoverBoard = True
            self.speedBoost = 2
            
        elif powerUpType == CoinMagnet:
            self.hasCoinMagnet = True
        
    def fakeDeath(self):
        self.deactivatePowerUp()

        app.modelsManager.entities.clear()
        app.modelsManager.spawnObstacleRow()
        app.modelsManager.spawnCoinRow(5)

    def deactivatePowerUp(self):
        self.activePowerUp = None
        self.powerUpTimer = 0
        self.time = 0
        self.isInvincible = False
        self.coinMultiplier = 1
        self.jumpVelocity = 9.5
        self.isOnHoverBoard = False
        self.hasCoinMagnet = False
        if self.isRolling:
            self.curSprite = self.JakeRegRoll
            self.JakeImgIndex = 0
        else:
            self.curSprite = self.JakeReg
            self.JakeImgIndex = 0
        



    def onKeyPress(self, key):
        if key == "up" and not self.isJumping and not self.isFalling:
            self.isJumping = True
            self.velocity = self.jumpVelocity
        elif key == "down" and not self.isJumping and not self.isFalling:
            self.isRolling = True
            if self.isOnHoverBoard:
                self.curSprite = self.JakeBoardRoll
                self.JakeImgIndex = 0
            else:
                self.curSprite = self.JakeRegRoll
                self.JakeImgIndex = 0
            
        if key == "right" and self.lane < 2:
            self.lane += 1
            self.isSwitchingLanes = "R"
            
        elif key == "left" and self.lane > 0:
            self.lane -= 1
            self.isSwitchingLanes = "L"
        
            
        
    def onStep(self):
        if self.y <= 406 and self.hasTrainBelow():
            self.isOnTrain = True
            self.isOnRamp = False
        
            
        if self.isSwitchingLanes and self.y > 460 and not self.hasTrainBelow():
            self.isOnTrain = False
            self.isFalling = True
            
        if self.y <= 406 and not self.isOnTrain:
            self.isFalling = True
            
        if self.isOnTrain and not self.hasTrainBelow() and not self.isOnRamp:
            self.isFalling = True
            self.isOnTrain = False

        # power up
        
        if self.activatePowerUp != None:
    
            self.time += 1
            if self.time % 30 == 0:
                self.powerUpTimer += 1
            if self.powerUpTimer > 15:
                self.deactivatePowerUp()
        if self.isRolling:
            self.rollTimer += 1
        if self.rollTimer % 30 == 0:
            self.rollTimer = 0
            self.isRolling = False
            if self.isOnHoverBoard:
                self.curSprite = self.JakeBoardReg
                
            else:
                self.curSprite = self.JakeReg
        
        
        # handle jumping and falling

        if self.isJumping:
            self.jump(1)
        elif self.isFalling:
            self.jump(-1)
        else:
            self.JakeImgIndex = (self.JakeImgIndex + 1) % len(self.curSprite)



        # handle lane switching

        if self.isSwitchingLanes:
            laneWidth = app.width / 9 
            targetX = app.width / 2 + (self.lane - 1) * laneWidth  # target position for the lane
            if self.isSwitchingLanes == "R":
                self.smallSwitchLane(1, targetX)

            elif self.isSwitchingLanes == "L":
                self.smallSwitchLane(-1, targetX)
                


    # right = positive, left = negative
    def smallSwitchLane(self, dir, targetX):
        self.x += dir * 8.5
        app.camera.x += dir * -0.1
        app.playerModel.minX += 0.1 * dir
        app.playerModel.maxX += 0.1 * dir

        
        if dir == 1 and self.x >= targetX or dir == -1 and self.x <= targetX: 
            self.x = targetX
            self.isSwitchingLanes = False
            self.horizontalOffset = self.laneToOffsets[self.lane]
        
    def jump(self, sign, amount=0.1):
        app.camera.vViewAngle += sign * amount
        app.camera.y += sign * amount

        app.playerModel.minY += sign * amount * self.velocity / 12 + self.y
        app.playerModel.maxY += sign * amount * self.velocity / 12 + self.y

        self.y += -1 * sign * self.velocity
        self.velocity += sign * self.gravity 
        
        if sign == 1 and self.velocity < 0:
            self.isJumping = False
            self.isFalling = True
        # falling
        elif sign == -1:
            if self.isOnTrain and self.y >= 403:
                self.y = 403
                self.isFalling = False
                self.velocity = 0
                app.camera.y = 3
            elif not self.isOnTrain and self.y >= 460:
                self.y = 459    
                self.isFalling = False
                self.velocity = 0
                app.camera.y = 2
                app.camera.vViewAngle = -13
                app.playerModel.minY = 0
                app.playerModel.maxY = 1
                return


    def redrawAll(self, app): 
        if self.curSprite == self.JakeRegRoll:
            width, height = 100, 100
        else:
            width, height = 200, 200
        drawImage(self.curSprite[self.JakeImgIndex], self.x, self.y, align='center', width=width, height=height)
            
    # handle collisons and delete out of frame entities
    def checkOutOfFrame(self):
        toRemove = []
        playerZRange = (-2.4, -2)  # player's z range
        if self.y <= 406 and not self.isJumping:
            self.isOnTrain = True
        if not self.isOnTrain and self.isFalling and self.y >= 460:
            self.y = 460
            app.camera.y = 2
            self.isFalling = False    
        elif self.isOnTrain and self.isFalling and self.y >= 400:
            self.y = 400
            app.camera.y = 3
            app.isFalling = False
            
        for entity in app.modelsManager.entities:
            entityZRange = (entity.minZ, entity.maxZ)
            
            # Check for collision on the z-axis
            if self.lane == entity.lane and self.y > 400 and \
                (playerZRange[0] < entityZRange[1] and playerZRange[1] > entityZRange[0]):
                self.isOnRamp = False

                if type(entity) == Train and self.y >= 459 and not self.isOnTrain:
                    return True
            
                if type(entity) == Duck and not self.isRolling:
                    return True
                
                elif type(entity) == Jump:
                    if self.y > 440:
                        return True

                
                elif type(entity) == Ramp:
                    
                    if not self.isOnRamp:  
                        self.isOnRamp = True                    
                    if self.y > 400:  
                        self.y -= 3
                        app.camera.y += 0.05
                        
                if type(entity) == DuckNJump and not (self.isRolling or self.y < 440):
                    return True
                if type(entity) == Train and self.hasTrainBelow():
                    self.isOnTrain = True
                
                    

                    
                # power ups and coins
            elif self.lane == entity.lane and type(entity) not in [Train, Ramp, Duck, Jump, DuckNJump]\
                and -1 >= entity.minZ >= -2.4:
                toRemove.append(entity)
                if type(entity) == Coin:    
                    app.coins += 1
                else:
                    self.activatePowerUp(type(entity))

            if entity.minZ > 2:
                toRemove.append(entity)   
                         
        for entity in toRemove:
            if entity in app.modelsManager.entities:
                app.modelsManager.entities.remove(entity)

        return False

    def hasTrainBelow(self):
        for entity in app.modelsManager.entities:
            
            if self.lane == entity.lane and type(entity) == Train:
                # Check if the player is above the train

                if -0.4 > entity.maxZ > -2.4 and -4.4 < entity.minZ < -2.4:
                    return True
                
        return False



