from cmu_graphics import *
import random
from models import Model, Coin, Train, Ramp, Duck, Jump, DuckNJump
from models import HoverBoard, Sneakers, ScoreBooster, CoinMagnet
from main import app


class Manager:
    def __init__(self):
        self.entities = []
        self.verticalOffset = 0
        self.horizontalOffset = 0

    def shiftEntities(self, direction, amount):
        pass
        # if direction == "vertical":
        #     self.verticalOffset += amount
        #     for entity in self.entities:
        #         entity.y += amount
        #         entity.maxY += amount
        #         entity.minY += amount
        # elif direction == "horizontal":
        #     self.horizontalOffset += amount
        #     for entity in self.entities:
        #         entity.x += amount
        #         entity.maxX += amount
        #         entity.minX += amount
        
                
    def setEntitiesY(self, val):
        for entity in self.entities:
            if type(entity) == Ramp:
                val -= 0.75
            entity.y = val


    def updateEntities(self):
        toRemove = []
        for entity in self.entities:
            entity.z += app.speed
            entity.maxZ += app.speed
            entity.minZ += app.speed
            if hasattr(entity, "isOffScreen") and entity.isOffScreen():
                toRemove.append(entity)
            else:
                # update bounding box
                entity.setBoundingBox()

        for entity in toRemove:
            if entity in self.entities:
                self.entities.remove(entity)

    def redrawAll(self, app):
        # objects in the player's current lane drawn infront when the 
        # same z value is present
        self.entities.sort(key=lambda entity: (entity.minZ, entity.lane == app.player.lane))
        for entity in self.entities:
            entity.redrawAll(app)
    
    def onStep(self, app):
        for entity in self.entities:
            entity.onStep(app)
        app.camera.onStep(app)
            
class ModelsManager(Manager):
    
    def __init__(self):
        super().__init__()

    def spawnCoin(self, x, y=0, z=-20):
        classList = [Coin, HoverBoard, Sneakers, ScoreBooster, CoinMagnet]
        
        powerUp = random.choices(classList, weights = [12, 2, 1, 1, 3], k = 1)[0](app.camera.y, lane=random.choice([0, 1, 2]))
        # check coin is not ontop of another entity
        for entity in self.entities:
            # prevent entities ontop of one another
            if Model.checkCollision(powerUp, entity):
                if type(entity) == Train:
                    if type(powerUp) == HoverBoard:
                        powerUp.y -= 1
                    elif type(powerUp) == CoinMagnet:
                        powerUp.y -= 0.8
                    else:
                        powerUp.y -= 2
                else:
                    return
        self.entities.append(powerUp)

    def spawnCoinRow(self, numRows=5, zStart=-21, zSpacing=2):
        for i in range(numRows):
            z = zStart + (i * zSpacing)

            for lane in {0, 1, 2}:
                spawn = random.choice([True, False])
                if spawn:
                    x = app.laneToX[lane]
                    self.spawnCoin(x, z=z)
        
    def spawnObstacleRow(self, z=-20):
        for lane in range(3):
            self.spawnObstacle(lane, z)


    def spawnObstacle(self, lane, z, obstacleClass=None, trainLength=None):
        # random obstacle class if none 
        if obstacleClass is None:
            obstacleClass = random.choice([Train, Train, Train, Duck, Jump, DuckNJump, None])

        if obstacleClass:
            # spawn the current obstacle
            newObstacle = obstacleClass(y=app.camera.y, lane=lane, z=z)
            for entity in self.entities:
                # prevent obstacles on top of one another
                if Model.checkCollision(newObstacle, entity):
                    return
            self.entities.append(newObstacle)

            if obstacleClass == Train:
                trainLen = abs(newObstacle.maxZ - newObstacle.minZ)

                # set train length on the first call
                if trainLength is None:
                    trainLength = random.randint(1, 10)

                # recursively spawn the next part of the train
                if trainLength > 1:
                    prevZ = newObstacle.maxZ  # position new train in front of the current one
                    self.spawnObstacle(lane, prevZ + 0.01, Train, trainLength - 1)
                else:
                    # spawn the ramp only after the last train is placed
                    if trainLength == 1:  # this ensures it's only the final call
                        spawnRamp = random.choice([True, True, False])
                        if spawnRamp:
                            self.spawnObstacle(lane=lane, z=newObstacle.maxZ, obstacleClass=Ramp)

    def onStep(self, app):
        super().updateEntities()
        
        
        for entity in self.entities:
            entity.onStep(app)
        if self.entities == []:
            self.spawnObstacleRow()





            
    

