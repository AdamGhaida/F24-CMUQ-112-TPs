from cmu_graphics import *
import time

class Camera:
    def __init__(self):
        self.hViewAngle = -90
        self.vViewAngle = -13
        self.x = 0
        self.y = 2
        self.z = 0
        self.oldX = 0
        self.oldY = 0

    def onMouseDrag(self, mouseX, mouseY):
        xChange = mouseX - self.oldX
        yChange = self.oldY - mouseY
        
        self.oldX = mouseX
        self.oldY = mouseY
        
        maxChange = 10
        
        if xChange > maxChange:
            xChange = maxChange
        elif xChange < -1 * maxChange:
            xChange = -1 * maxChange
        self.hViewAngle += xChange
        
        if yChange > maxChange:
            yChange = maxChange
        elif yChange < -1 *maxChange:
            yChange = -1 * maxChange
        self.vViewAngle += yChange
    
    def onStep(self, app):
        pass

class FPSCounter:
    def __init__(self):
        self.frameCount = 0
        self.startTime = time.time()
        self.fps = 0
        self.elapsedTime = 0

    def update(self):
        self.frameCount += 1
        curTime = time.time()
        self.elapsedTime = curTime - self.startTime

        if self.elapsedTime >= 1.0:
            self.fps = self.frameCount / self.elapsedTime
            self.startTime = curTime
            self.frameCount = 0

    def getFPS(self):
        return self.fps


    def redrawAll(self, app):
        drawLabel(f"FPS: {self.getFPS():.0f}", 5, app.height-5, size=16, align="bottom-left")



