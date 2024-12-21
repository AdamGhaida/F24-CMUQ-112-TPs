from cmu_graphics import *
import math
import pathlib

GAMEPATH = str(pathlib.Path(__file__).parent.resolve()).replace('\\', '/')
myApp = None

class Door:
    def __init__(self, x, y, level, w = 50, h = 50):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.level = level

    def draw(self):
        x = self.x - myApp.viewLeft
        y = self.y - myApp.viewTop
        drawRect(x, y - self.h, self.w, self.h, fill=myApp.colors[0])
        drawCircle(x + self.w / 2, y - self.h, self.w / 2, fill=myApp.colors[0])
    
    def isInside(self, x, y):
        return self.x <= x <= self.x + self.w and self.y - self.h <= y <= self.y

class Mover:
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

        self.vy = 0
        self.ay = 0.4

        self.vx = 0        
    
    def __repr__(self):
        return f"Mover(x={self.x}, y={self.y}, w={self.w}, h={self.h}, color={self.color}, vy={self.vy}, ay={self.ay}, vx={self.vx})"
    
    def __hash__(self):
        return hash(self.__repr__())

    def getLeft(self):
        return self.x

    def getTop(self):
        return self.y - self.h
    
    def getRight(self):
        return self.x + self.w
        
    def getBottom(self):
        return self.y

    def draw(self):
        x = self.getLeft() - myApp.viewLeft
        y = self.getTop() - myApp.viewTop
        drawRect(x, y, self.w, self.h, fill=self.color, border='white')

    def onStep(self):
        prevY = self.y
        self.y += self.vy * myApp.speed
        self.vy += self.ay * myApp.speed

        #print(f"hue y={self.y}, vy={self.vy}")

        # Y coordinate
        if getGround(self.getLeft(), self.getBottom(), self) != False:
            val = getGround(self.getLeft(), self.getBottom()) - 1
            if abs(self.y - prevY) >= val:
                self.y -= val
                self.vy = 0
        elif getGround(self.getRight(), self.getBottom(), self) != False:
            val = getGround(self.getRight(), self.getBottom()) - 1
            if abs(self.y - prevY) >= val:
                self.y -= val
                self.vy = 0        
        elif getGroundBottom(self.getLeft(), self.getTop(), self) != False and self.vy < 0:
            val = getGroundBottom(self.getLeft(), self.getTop()) - 1
            if abs(self.y - prevY) >= val:
                self.y += val
                self.vy = 0
        elif getGroundBottom(self.getRight(), self.getTop(), self) != False and self.vy < 0:
            val = getGroundBottom(self.getRight(), self.getTop()) - 1
            if abs(self.y - prevY) >= val:
                self.y += val
                self.vy = 0

        # X coordinate

        for _ in range(3):
            self.x += 1 * self.vx * myApp.speed
            
            while self.vx < 0:
                x1, y1, x2, y2 = self.getLeft(), self.getTop(), self.getRight(), self.getBottom()
                if "right" not in getAllSides(x1, y1, x2, y2, self) and "right" not in getAllSides(x1, y1, x2, y2, self):
                    break
                else:
                    self.x += 1
                
            while self.vx > 0:
                x1, y1, x2, y2 = self.getLeft(), self.getTop(), self.getRight(), self.getBottom()
                if "left" not in getAllSides(x1, y1, x2, y2, self) and "left" not in getAllSides(x1, y1, x2, y2, self):
                    break
                else:
                    self.x -= 1
            
class Hero(Mover):
    def __init__(self, x, y):
        w = 20
        h = 50
        super().__init__(x, y, w, h, rgb(10,10,10))
        self.dead = False
        self.won = False
        self.onLadder = False
        self.margin = w // 2

        self.imageUrls = [None] + [f'{GAMEPATH}/pic/hue_{i}.png' for i in range(1, 19)]

        self.direction = "right"
        self.condition = "steady"

        self.steps = 0

    def __repr__(self):
        return f"Hero(x={self.x}, y={self.y}, w={self.w}, h={self.h}, dead={self.dead}, color={self.color}, vy={self.vy}, ay={self.ay}, vx={self.vx})"
    
    def onGround(self):
        return "top" in getAllSides(self.getLeft(), self.getBottom()) or "top" in getAllSides(self.getRight(), self.getBottom())

    def jump(self):
        if self.onGround():
            self.condition = 'jump'
            self.vy = -8

    def onStep(self):
        if myApp.debugging:
            print(self.condition)
        
        self.steps += 1
        if self.dead or self.won:
            return
        super().onStep()
        
        if self.condition != 'ladder' and self.condition != 'steady-ladder' and myApp.speed == 1:
            if self.onGround():
                self.condition = 'steady'
            else:
                self.condition = 'jump'

        for s in myApp.spikes:
            if s.isTouching(self.x, self.y) or s.isTouching(self.x + self.w, self.y):
                self.dead = True
                return
        
        for las in myApp.lasers:
            if las.isTouching(self):
                self.dead = True
                return
    
    def draw(self):
        x = self.getLeft() - myApp.viewLeft
        y = self.getTop() - myApp.viewTop

        ids = []

        if self.condition == 'walk': 
            if self.direction == 'right':
                ids = [1, 2]
            else:
                ids = [3, 4]
        
        elif self.condition == 'steady':
            ids = [5]
            if self.direction == 'left':
                ids[0] += 1

        elif self.condition == 'ladder':
            ids = [7, 8]
        
        elif self.condition == 'steady-ladder':
            ids = [7]

        elif self.condition == 'jump':
            ids = [9]
            if self.direction == 'left':
                ids[0] += 1

        elif self.condition == 'push':
            if self.direction == 'right':
                ids = [11, 12]
            else:
                ids = [13, 14]

        elif self.condition == 'pull':
            if self.direction == 'right':
                ids = [15, 16]
            else:
                ids = [17, 18]

        length = int(5 / myApp.speed)
        i = (self.steps // length) % len(ids)
        #drawRect(x, y, self.w, self.h, fill='white')
        drawImage(self.imageUrls[ids[i]], x - self.margin, y, width=self.w + 2 * self.margin, height=self.h, align='top-left')

class Spike:
    def __init__(self, x, y, cnt, color='black'):
        self.x = x
        self.y = y
        self.w = 10
        self.cnt = cnt
        self.color = color
    
    def __repr__(self):
        return f"Spike(x={self.x}, y={self.y}, w={self.w}, cnt={self.cnt}, color={self.color})"
    
    def draw(self):
        for i in range(self.cnt):
            x = self.x + self.w * i - myApp.viewLeft
            y = self.y - myApp.viewTop
            drawPolygon(x, y, x + self.w, y, x + self.w / 2, y - self.w, fill=self.color)

    def isTouching(self, x, y):
        if self.color == myApp.background:
            return False
        
        if y < self.y - self.w or y > self.y:
            return False
        
        if self.x + self.w / 2 <= x <= self.x + (self.cnt - 0.5) * self.w:
            return True
        
        if self.x <= x <= self.x + self.w / 2:
            return y >= -2 * x + 2 * self.x + self.y
        
        if self.x + (self.cnt - 0.5) * self.w <= x <= self.x + self.cnt * self.w:
            return y >= 2 * x - 2 * (self.x + self.cnt * self.w) + self.y
        
        return False

class Ground(Mover):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, 'black')
    
    def __repr__(self):
        return f"Ground(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def draw(self):
        x = self.x - myApp.viewLeft
        y = self.y - myApp.viewTop
        drawRect(x, y, self.w, self.h, fill='black')
    
    def getDelta(self, x, y):
        if self.isInside(x, y):
            return y - self.y + 1
        return 0

    def getDeltaBottom(self, x, y):
        if self.isInside(x, y):
            return self.y + self.h - y + 1
        return 0       
    
    def isTouchingTop(self, x1, y1, x2 = None, y2 = None):
        if x2 == None:
            x2, y2 = x1, y1
        return y1 <= self.y <= y2 and max(self.x, x1) <= min(self.x + self.w, x2)
    
    def isTouchingBottom(self, x1, y1, x2 = None, y2 = None):
        if x2 == None:
            x2, y2 = x1, y1
        return y1 <= self.y + self.h <= y2 and max(self.x, x1) <= min(self.x + self.w, x2)
    
    def isTouchingLeft(self, x1, y1, x2 = None, y2 = None):
        if x2 == None:
            x2, y2 = x1, y1
        return x1 <= self.x <= x2 and max(self.y + 1, y1) <= min(self.y + self.h - 1, y2)

    def isTouchingRight(self, x1, y1, x2 = None, y2 = None):
        if x2 == None:
            x2, y2 = x1, y1
        return x1 <= self.x + self.w <= x2 and max(self.y + 1, y1) <= min(self.y + self.h - 1, y2)

    def isInside(self, x1, y1, x2 = None, y2 = None):
        if x2 == None:
            x2, y2 = x1, y1
        return self.x <= x1 <= x2 <= self.x + self.w and self.y <= y1 <= y2 <= self.y + self.h
    
    def getSides(self, x1, y1, x2 = None, y2 = None):
        if x2 == None:
            x2, y2 = x1, y1
        res = set()
        if self.isTouchingTop(x1, y1, x2, y2):
            res.add("top")

        if self.isTouchingBottom(x1, y1, x2, y2):
            res.add("bottom")
        
        if self.isTouchingLeft(x1, y1, x2, y2):
            res.add("left")
        
        if self.isTouchingRight(x1, y1, x2, y2):
            res.add("right")
        
        if self.isInside(x1, y1, x2, y2):
            res.add("inside")
        
        return res

    def isTouching(self, x, y):
        return self.isInside(x, y)
    
def getGround(x, y, skip=None): # return delta + 1 or False (weird, but works)
    for g in myApp.grounds:
        if g == skip:
            continue
        if g.isTouching(x, y):
            return g.getDelta(x, y)
        
    for bar in myApp.barriers:
        if bar == skip:
            continue
        if bar.color != myApp.background and bar.isTouching(x, y):
            return bar.getDelta(x, y)
    
    for bl in myApp.blocks:
        if bl == skip:
            continue
        if bl.color != myApp.background and bl.isTouching(x, y):
            return bl.getDelta(x, y)
    
    for ga in myApp.gates:
        if ga == skip:
            continue
        if ga.isTouching(x, y):
            return ga.getDelta(x, y) # changed from getDeltaBottom to getDelta
    
    return False

def getGroundBottom(x, y, skip=None):
    for g in myApp.grounds:
        if g == skip:
            continue
        if g.isTouching(x, y):
            return g.getDeltaBottom(x, y)
        
    for bar in myApp.barriers:
        if bar == skip:
            continue
        if bar.color != myApp.background and bar.isTouching(x, y):
            return bar.getDeltaBottom(x, y)
    
    for bl in myApp.blocks:
        if bl == skip:
            continue
        if bl.color != myApp.background and bl.isTouching(x, y):
            return bl.getDeltaBottom(x, y)
    
    for ga in myApp.gates:
        if ga == skip:
            continue
        if ga.isTouching(x, y):
            return ga.getDeltaBottom(x, y)
        
    return False

def getAllSides(x1, y1, x2 = None, y2 = None, skip = None):
    if x2 == None:
        x2, y2 = x1, y1
    #print(x1, y1, x2, y2)
    res = set()
    for g in myApp.grounds:
        if g == skip:
            continue
        res = res.union(g.getSides(x1, y1, x2, y2))
    
    for bar in myApp.barriers:
        if bar == skip:
            continue
        if bar.color != myApp.background:
            res = res.union(bar.getSides(x1, y1, x2, y2))

    for bl in myApp.blocks:
        if bl == skip:
            continue
        if bl.color != myApp.background:
            res = res.union(bl.getSides(x1, y1, x2, y2))

    for ga in myApp.gates:
        if ga == skip:
            continue
        res = res.union(ga.getSides(x1, y1, x2, y2))
    
    return res

class Barrier(Ground):
    def __init__(self, x, y, cnt=1, color='black', w=50):
        super().__init__(x, y, w, cnt * w)
        self.y -= cnt * w
        self.cnt = cnt
        self.color = color
    
    def __repr__(self):
        return f"Barrier(x={self.x}, y={self.y}, w={self.w}, cnt={self.cnt}, color={self.color})"
    
    def draw(self):
        opacity = 100
        if self.color == myApp.background and not myApp.mousePressed:
            opacity = 50
             
        x = self.x - myApp.viewLeft
        y = self.y - myApp.viewTop

        drawRect(x, y, self.w, self.h, fill=self.color, opacity=opacity)

        for r in range(self.cnt):
            for c in range(3):
                color = myApp.background
                if color == self.color and myApp.mousePressed:
                    color = myApp.colors[0]
                if c % 2 == 0:
                    drawLine(x + self.w / 2, y, x + self.w / 2, y + self.w / 3, fill=color, opacity=opacity)
                else:
                    drawLine(x + self.w / 4, y, x + self.w / 4, y + self.w / 3, fill=color, opacity=opacity)
                    drawLine(x + self.w * 3 / 4, y, x + self.w * 3 / 4, y + self.w / 3, fill=color, opacity=opacity)
                y += self.w / 3
                if r < self.cnt - 1 or c < 2:
                    drawLine(x, y, x + self.w, y, fill=color, opacity=opacity)

class Block(Barrier):
    nxtID = 0
    def __init__(self, x, y, cnt, color):
        super().__init__(x, y, cnt, color)
        self.dead = False
        self.id = self.nxtID
        self.nxtID += 1

    def __repr__(self):
        return f"Block(x={self.x}, y={self.y}, w={self.w}, cnt={self.cnt}, color={self.color}, id={self.id}, dead={self.dead})"
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.x == other.x and self.y == other.y and self.cnt == other.cnt and self.color == other.color and self.dead == other.dead
    
    def __lt__(self, other):
        if type(self) != type(other):
            return False

        if self.color != myApp.background and other.color == myApp.background:
            return True

        if self.color == myApp.background and other.color != myApp.background:
            return False
        
        if self.y + self.h != other.y + other.h:
            return self.y + self.h < other.y + other.h

        if self.x != other.x:
            return self.x < other.x

        return self.cnt < other.cnt
    
    def __le__(self, other):
        return self < other or self == other
    
    def __hash__(self):
        return self.id

    def getTop(self):
        return self.y
    
    def getBottom(self):
        return self.y + self.h
    
    def draw(self):
        opacity = 100
        if self.color == myApp.background and not myApp.mousePressed:
            return
            #opacity = 50
            
        x = self.x - myApp.viewLeft
        y = self.y - myApp.viewTop

        drawRect(x, y, self.w, self.h, fill=self.color, opacity=opacity)

        color = myApp.background
        if color == self.color and myApp.mousePressed:
            color = myApp.colors[0]

        if self.cnt >= 2:
            for i in range(1, 4):
                drawLine(x + self.w * i / 4, y, x + self.w * i / 4, y + self.h, fill=color, opacity=opacity)
            
            drawLine(x, y + self.w / 4, x + self.w, y + self.w / 4, fill=color, opacity=opacity)
            drawLine(x, y + self.h - self.w / 4, x + self.w, y + self.h - self.w / 4, fill=color, opacity=opacity)
        else:
            drawLine(x + self.w * 1 / 4, y, x + self.w * 1 / 4, y + self.h, fill=color, opacity=opacity)
            drawLine(x + self.w * 3 / 4, y, x + self.w * 3 / 4, y + self.h, fill=color, opacity=opacity)

            drawLine(x + self.w / 4, y, x + self.w * 3 / 4, y + self.h - self.w * 3 / 8, fill=color, opacity=opacity)
            drawLine(x + self.w / 4, y + self.w * 3 / 8, x + self.w * 3 / 4, y + self.h, fill=color, opacity=opacity)

            drawLine(x + self.w / 2, y, x + self.w / 2, y + self.h * 5 / 16, fill=color, opacity=opacity)
            drawLine(x + self.w / 2, y + self.h * 11 / 16, x + self.w / 2, y + self.h, fill=color, opacity=opacity)

    def onStep(self):
        if self.y > 1700:
            self.destructButton()
            return
            
        x1, y1 = myApp.hue.getLeft(), myApp.hue.getTop()
        x2, y2 = myApp.hue.getRight(), myApp.hue.getBottom()

        if myApp.shiftPressed and self.color != myApp.background:
            if myApp.hue.vx > 0:
                # pulling
                if self.isTouchingRight(x1 - 3, y1, x2 - 3, y2) and myApp.hue.direction == 'left':
                    self.vx = myApp.hue.vx
                else: # pushing
                    ind = myApp.blockMap[self]
                    leftBlock = myApp.blockGroups[ind][0]
                    if leftBlock.isTouchingLeft(x1 + 3, y1, x2 + 3, y2) or self.isTouchingLeft(x1 + 3, y1, x2 + 3, y2):
                        self.vx = myApp.hue.vx
            elif myApp.hue.vx < 0:
                # pulling
                if self.isTouchingLeft(x1 + 3, y1, x2 + 3, y2) and myApp.hue.direction == 'right':
                    self.vx = myApp.hue.vx
                else: # pushing
                    ind = myApp.blockMap[self]
                    rightBlock = myApp.blockGroups[ind][-1]
                    if rightBlock.isTouchingRight(x1 - 3, y1, x2 - 3, y2) or self.isTouchingRight(x1 - 3, y1, x2 - 3, y2):
                        self.vx = myApp.hue.vx
        else:
            self.vx = 0
        
        if self.vx != 0 and myApp.debugging:
            print(str(self))
        
        super().onStep()

    def destructButton(self):
        myApp.blocks.remove(self)

class Ladder:
    def __init__(self, x, y, h, w = 40):
        self.x = x
        self.y = y
        self.h = h
        self.w = w
    
    def draw(self):
        x = self.x - myApp.viewLeft
        y = self.y - myApp.viewTop
        drawLine(x, y, x, y - self.h * self.w, fill='black')
        drawLine(x + self.w, y, x + self.w, y - self.h * self.w, fill='black')

        for _ in range(self.h * 3 - 1):
            y -= self.w / 3
            drawLine(x, y, x + self.w, y)
    
    def isInside(self, x, y):
        return self.x <= x <= self.x + self.w and self.y - self.h * self.w <= y <= self.y

class Laser:
    def __init__(self, x1, y1, x2, y2, color, r=15):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.r = r
    
    def draw(self):
        x1 = self.x1 - myApp.viewLeft
        y1 = self.y1 - myApp.viewTop
        x2 = self.x2 - myApp.viewLeft
        y2 = self.y2 - myApp.viewTop

        drawRect(x1, y1, self.r * 2, self.r * 2, align='center', fill=myApp.background)
        if myApp.mousePressed:
            drawRect(x1, y1, self.r * 2, self.r * 2, align='center', fill='black', opacity=50)
        
        drawCircle(x1, y1, self.r, fill=self.color, border='black')
        
        if self.color != myApp.background:
            drawLine(x1, y1, x2, y2, fill=self.color, lineWidth=5)
        
        t = 8
        dx, dy = 0, 0
        if self.x1 == self.x2:
            dy += (self.r + t / 2) * (-1 if self.y1 > self.y2 else 1)
        else:
            dx += (self.r + t / 2) * (-1 if self.x1 > self.x2 else 1)

        drawRect(x1 + dx, y1 + dy, t, t, fill='black', align='center')

    def isTouching(self, hue):
        if self.color == myApp.background:
            return False
        
        if self.x1 == self.x2: #vertical laser
            if not (hue.x <= self.x1 <= hue.x + hue.w):
                return False
            ly = min(self.y1, self.y2)
            ry = max(self.y1, self.y2)
            return max(ly, hue.y - hue.h) <= min(ry, hue.y)
        
        if self.y1 == self.y2: #horizontal laser
            if not (hue.y - hue.h <= self.y1 <= hue.y):
                return False
            lx = min(self.x1, self.x2)
            rx = max(self.x1, self.x2)
            return max(lx, hue.x) <= min(rx, hue.x + hue.w)

class Gate(Ground):
    def __init__(self, x, y1, y2, button, w=20):
        super().__init__(x - w / 2, y1, w, y2 - y1)
        self.originalH = y2 - y1
        self.button = button
        self.vh = 1

        if myApp.debugging:
            print(self.x, self.y, self.w, self.h)

    def __repr__(self):
        return f"Gate(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def draw(self):
        x = self.x - myApp.viewLeft
        y = self.y - myApp.viewTop

        drawRect(x - self.w / 2, y - self.w, self.w * 2, self.w)

        drawRect(x, y, self.w, self.h)

    def onStep(self):
        self.h += self.vh
        self.h = max(1, self.h)
        self.h = min(self.originalH, self.h)

class Button:
    def __init__(self, x, y, gate, w=80, h=10):
        self.x = x
        self.y = y
        self.gate = gate
        self.w = w
        self.h = h
        self.isActive = False

    def __repr__(self):
        return f"Button(x={self.x}, y={self.y}, w={self.w}, h={self.h}, isActive={self.isActive})"

    def draw(self):
        if self.isActive:
            return

        x = self.x - myApp.viewLeft
        y = self.y - myApp.viewTop
        h = self.h
        drawRect(x + h, y - self.h, self.w - 2 * h, self.h)
        drawCircle(x + h, y, h)
        drawCircle(x + self.w - h, y, h)

    def isTouching(self, x, y):
        return self.x <= x <= self.x + self.w and self.y - self.h <= y <= self.y

    def onStep(self):
        if self.isTouching(myApp.hue.x, myApp.hue.y) or self.isTouching(myApp.hue.x + myApp.hue.w, myApp.hue.y):
            self.isActive = True
            self.gate.vh = -1
            return
        
        if 'bottom' in getAllSides(self.x, self.y - self.h, self.x + self.w, self.y):
            self.isActive = True
            self.gate.vh = -1
        else:
            self.isActive = False
            self.gate.vh = 1

def startLevel(app, level):
    app.hue = Hero(0, 0)
    app.grounds = []
    app.spikes = []
    app.barriers = []
    app.blocks = []
    app.ladders = []
    app.lasers = []
    app.door = Door(0, 0, level)
    app.level = level
    app.legal = True
    
    gates = []
    buttons = []

    if app.level == 1:
        app.colorSize = 2
    else:
        app.colorSize = 8

    global GAMEPATH
    f = open(f"{GAMEPATH}/levels/level{level}.txt", "r")
    for s in f.read().splitlines():
        data = list(s.split())
        obj = data[0]
        data = list(int(s) for s in data[1:])
        
        if app.debugging:
            print(obj, data)

        if obj == 'hero':
            app.hue = Hero(data[0], data[1])
        
        if obj == 'ground':
            app.grounds.append(Ground(data[0], data[1], data[2], data[3]))
        
        if obj == 'spike':
            color = ('black' if len(data) == 3 else app.colors[data[3]])
            app.spikes.append(Spike(data[0], data[1], data[2], color))

        if obj == 'barrier':
            app.barriers.append(Barrier(data[0], data[1], data[2], app.colors[data[3]]))
        
        if obj == 'block':
            app.blocks.append(Block(data[0], data[1], data[2], app.colors[data[3]]))
        
        if obj == 'ladder':
            app.ladders.append(Ladder(data[0], data[1], data[2]))

        if obj == 'laser':
            app.lasers.append(Laser(data[0], data[1], data[2], data[3], app.colors[data[4]]))

        if obj == 'gate':
            gates.append(Gate(data[0], data[1], data[2], 5))

        if obj == 'button':
            buttons.append(Button(data[0], data[1], 5))
        
        if obj == 'door':
            app.door = Door(data[0], data[1], level)

    app.gates = gates
    app.buttons = buttons
    app.background = app.colors[0]

    assert(len(gates) == len(buttons))
    for i in range(len(gates)):
        ga = gates[i]
        bu = buttons[i]
        app.gates[i].button = bu
        app.buttons[i].gate = ga

    app.hue.onLadder = False

    app.blockGroups = []
    findBlockGroups(app)

def isSorted(a):
    for i in range(1, len(a)):
        if a[i] < a[i - 1]:
            return False
    return True

def findBlockGroups(app):
    if not isSorted(app.blocks):
        app.blocks.sort()

    prevSize = len(app.blockGroups)
    app.blockGroups = []
    app.blockMap = dict()

    last = len(app.blocks) - 1
    while last >= 0 and app.blocks[last - 1].color == myApp.background:
        last -= 1

    i = 0
    while i <= last:
        j = i + 1
        while j <= last and app.blocks[j].color != myApp.background and app.blocks[j - 1].isTouchingRight(app.blocks[j].x - 2, app.blocks[j].y, app.blocks[j].x + app.blocks[j].w - 2, app.blocks[j].y + app.blocks[j].h):
            j += 1
        
        app.blockGroups.append(app.blocks[i:j])
        while i < j:
            app.blockMap[app.blocks[i]] = len(app.blockGroups) - 1
            i += 1
    
    if app.debugging and len(app.blockGroups) == 4 and prevSize == 5:
        for bl in app.blocks:
            print(str(bl))

def reset(app):
    global myApp
    myApp = app

    app.viewLeft = 0
    app.viewTop = -150
    app.speed = 1

    app.mousePressed = False
    app.shiftPressed = False
    app.background = app.colors[0]
    app.mouseColor = 0

    app.colorSize = 8

    startLevel(app, app.level)
    viewCheck(app)

def onAppStart(app):
    app.theme = Sound('sounds/hue_soundtrack.mp3')
    app.theme.play()

    app.debugging = False
    app.maxLevel = 2

    if app.debugging:
        print("onAppStart()")

    app.stepsPerSecond = 60
    app.level = 1

    app.colors = ['gray', 'deepSkyBlue', 'orange', 'magenta', 'deepPink', 'red', 'blue', 'yellow', 'lawnGreen']
    app.background = app.colors[0]

    app.permutation = [1, 8, 7, 2, 5, 3, 4, 6]
    app.revPermutation = [1, 4, 6, 7, 5, 8, 3, 2]

    reset(app)

def checkLegality(app):
    for fx in range(2):
        for fy in range(2):
            x = app.hue.x + fx * app.hue.w
            y = app.hue.y - fy * app.hue.h - 1
            
            res = set()
            for ba in app.barriers:
                res = res.union(ba.getSides(x, y))
            
            for bl in app.blocks:
                res = res.union(bl.getSides(x, y))
            
            if "left" in res:
                return False

            if "right" in res:
                return False
            
            if "inside" in res:
                return False
            
    return True

def onMousePress(app, mouseX, mouseY):
    app.legal = checkLegality(app)

    if app.debugging:
        print("mouse pressed", mouseX, mouseY)

    app.speed = 0.1
    app.mousePressed = True
    app.mouseColor = getNextColor(app, mouseX, mouseY)

def onMouseDrag(app, mouseX, mouseY):
    if app.debugging:
        print("mouse dragging", mouseX, mouseY)

    app.mouseColor = getNextColor(app, mouseX, mouseY)

def getNextColor(app, mouseX, mouseY):
    x0 = app.hue.x + app.hue.w / 2
    y0 = app.hue.y - app.hue.h / 2
    dx = mouseX - x0 + app.viewLeft
    dy = mouseY - y0 + app.viewTop
    dy = -dy

    hypotenuse = math.sqrt(dx * dx + dy * dy)

    #print("released", mouseX, mouseY, hypotenuse)
    #print(dx, dy)

    if hypotenuse > 250 or hypotenuse == 0:
        return -1

    angle = math.acos(dx / hypotenuse)
    angle = math.degrees(angle)

    if dy < 0:
        angle = 360 - angle
    angle -= 22.5
    if angle < 0:
        angle += 360
    
    id = int(angle / 45)

    if app.permutation[id] > app.colorSize:
        return -1

    return id + 1

def onMouseRelease(app, mouseX, mouseY):
    if app.debugging:
        print("mouse released", mouseX, mouseY)

    app.mousePressed = False

    app.speed = 1
    app.hue.vx = 0

    id = getNextColor(app, mouseX, mouseY)
    app.mouseColor = 0
    if id != -1 and app.legal:
        id = app.permutation[id - 1]
        app.background = app.colors[id]

def onKeyPress(app, key):
    if app.debugging:
        print(f"{key} pressed")

    if key == 'r':
        reset(app)

    if key == 'enter' and app.hue.won and app.level < app.maxLevel:
        startLevel(app, app.level + 1)

    if app.hue.dead or app.hue.won:
        return
    
    if key == 'w' and app.door.isInside(app.hue.x + app.hue.w / 2, app.hue.y - app.hue.h / 2):
        app.hue.won = True

    viewCheck(app)

def onKeyRelease(app, key):
    if app.debugging:
        print(f"{key} released")

    if app.hue.dead or app.hue.won:
        return

    viewCheck(app)
    
    if (key == 'd' or key == 'a' or key == 'D' or key == 'A') and app.speed == 1:
        app.hue.vx = 0
        app.shiftPressed = False
        app.hue.condition = 'steady'
    
    if (key == 'w' or key == 's') and app.speed == 1:
        app.hue.vy = 0
        app.hue.condition = 'steady-ladder'
        app.hue.onLadder = True
        #app.hue.direction = 'right'

def onKeyHold(app, keys):
    if app.debugging:
        print(f"{keys} on hold")
        
    if app.hue.dead or app.hue.won:
        return

    viewCheck(app)

    if app.speed != 1:
        return
        pass

    if 'd' in keys:
        app.hue.vx = 1
        app.hue.direction = 'right'
        if app.hue.onGround():
            app.hue.condition = 'walk'
        else:
            app.hue.condition = ('ladder' if app.hue.onLadder else 'jump')
    
    if 'a' in keys:
        app.hue.vx = -1
        app.hue.direction = 'left'
        if app.hue.onGround():
            app.hue.condition = 'walk'
        else:
            app.hue.condition = ('ladder' if app.hue.onLadder else 'jump')

    if 'D' in keys:
        app.hue.vx = 0.5
        app.shiftPressed = True
        #app.hue.direction = 'right'
        if app.hue.onGround():
            if app.hue.direction == 'left':
                app.hue.condition = 'pull'
            else:
                app.hue.condition = 'push'
        else:
            app.hue.condition = ('ladder' if app.hue.onLadder else 'jump')
    
    if 'A' in keys:
        app.hue.vx = -0.5
        app.shiftPressed = True
        #app.hue.direction = 'left'
        if app.hue.onGround():
            if app.hue.direction == 'right':
                app.hue.condition = 'pull'
            else:
                app.hue.condition = 'push'
        else:
            app.hue.condition = ('ladder' if app.hue.onLadder else 'jump')

    if 'w' in keys and app.hue.onLadder:
        app.hue.vy = -3
        app.hue.direction = ''
        app.hue.condition = 'ladder'
    
    if 's' in keys and app.hue.onLadder:
        app.hue.vy = 3
        app.hue.direction = ''
        app.hue.condition = 'ladder'

    if 'space' in keys and not app.hue.onLadder:
        app.hue.jump()
        # app.hue.condition = 'jump' (will be added inside hue.jump())
    
def viewCheck(app):
    x = app.hue.x - app.viewLeft
    p = 0.25
    if x < app.width * p:
        app.viewLeft += x - app.width * p
    elif x > app.width * (1 - p):
        app.viewLeft += x - app.width * (1 - p)

    y = app.hue.y - app.viewTop
    if y < app.height * p:
        app.viewTop += y - app.height * p
    elif y > app.height * (1 - p):
        app.viewTop += y - app.height * (1 - p)

def onStep(app):
    if app.debugging:
        print("onStep()")
    
    if app.hue.dead or app.hue.won:
        return
    if app.hue.y > 1700:
        app.hue.dead = True

    app.legal = checkLegality(app)

    app.hue.onLadder = False
    for l in app.ladders:
        if l.isInside(app.hue.x + app.hue.w / 2, app.hue.y):
            app.hue.onLadder = True
            break
    
    app.hue.ay = (0 if app.hue.onLadder else 0.4)

    app.hue.onStep()
    viewCheck(app)

    findBlockGroups(app)

    for bl in app.blocks:
        bl.onStep()

    for ga in app.gates:
        ga.onStep()

    for bu in app.buttons:
        bu.onStep()

def drawPalette(app):
    x0 = app.hue.x + app.hue.w / 2 - app.viewLeft
    y0 = app.hue.y - app.hue.h / 2 - app.viewTop

    for i in range(8):
        r1 = 40
        r2 = 20

        if i + 1 == app.mouseColor:
            r1 += 15

        alpha, beta = math.radians(i * 45 + 22.5), math.radians((i + 1) * 45 + 22.5)
        x1 = x0 + r1 * math.cos(alpha)
        y1 = y0 - r1 * math.sin(alpha)

        x2 = x0 + (r1 + r2) * math.cos(alpha)
        y2 = y0 - (r1 + r2) * math.sin(alpha)

        x3 = x0 + (r1 + r2) * math.cos(beta)
        y3 = y0 - (r1 + r2) * math.sin(beta)

        x4 = x0 + r1 * math.cos(beta)
        y4 = y0 - r1 * math.sin(beta)

        curColor = app.colors[app.permutation[i]]
        if app.permutation[i] > app.colorSize:
            curColor = 'black'
        drawPolygon(x1, y1, x2, y2, x3, y3, x4, y4, fill=curColor, border='white')

def redrawAll(app):
    if app.debugging:
        print("redrawAll()")
    
    if app.mousePressed:
        drawRect(0, 0, app.width, app.height, opacity=50)
    
    app.door.draw()

    for g in app.grounds:
        g.draw()

    for lad in app.ladders:
        lad.draw()

    for s in app.spikes:
        s.draw()

    for bar in app.barriers:
        bar.draw()

    for bl in app.blocks:
        bl.draw()

    for las in app.lasers:
        las.draw()

    for ga in app.gates:
        ga.draw()
    
    for bu in app.buttons:
        bu.draw()

    app.hue.draw()

    if app.hue.dead:
        drawRect(0, 0, app.width, app.height, fill='black', opacity=50)
        drawLabel("Game Over", app.width / 2, app.height / 2, fill='white', size=50)
        drawLabel("Press r to start again", app.width / 2, app.height * 4 / 5, fill='white', size=20)

    if app.hue.won:
        drawRect(0, 0, app.width, app.height, fill='black', opacity=50)
        
        if app.level < app.maxLevel:
            drawLabel("Level Completed!", app.width / 2, app.height / 2, fill='white', size=50)
            drawLabel("Press Enter to start next level", app.width / 2, app.height * 4 / 5, fill='white', size=20)
        else:
            drawLabel("Game Completed!", app.width / 2, app.height / 2, fill='white', size=50)
            drawLabel("Congratulations!", app.width / 2, app.height * 4 / 5, fill='white', size=20)

    if app.mousePressed and app.legal:
        drawPalette(app)

def main():
    runApp(width=800, height=600)

main()
