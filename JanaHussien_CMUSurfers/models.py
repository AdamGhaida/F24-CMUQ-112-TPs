from cmu_graphics import *
import math
import random

class Model:
    def __init__(self, filepath, lane, y=0 + 2, z=-20, fill=rgb(255, 0, 0)):
        self.vertices, self.faces = self.loadOBJ(filepath)
        y -= 2
        self.y, self.z = y , z
        self.lane = lane
        self.x = {0: -1.5, 1: 0, 2: 1.5}[lane]
        self.fill = fill
        self.setBoundingBox()

        
    def __repr__(self):
        return (f"{self.__class__.__name__}, lane={self.lane}, "
                f"position=({self.x:.2f}, {self.y:.2f}, {self.z:.2f}), "
                f"minZ={self.minZ:.2f}), maxZ={self.maxZ:.2f})")
    def hash(self):
        return hash(str(self))
    # https://www.cs.cmu.edu/~mbz/personal/graphics/obj.html
    
    def loadOBJ(self, filepath):
        vertices = []
        faces = []
        scale = self.scale
        with open(filepath, 'r') as file:
            for line in file:
                if line.startswith('v '):  
                    _, x, y, z = line.strip().split()
                    x, y, z = float(x), float(y), float(z)
                    vertices.append((x*scale, y*scale, z*scale))
                
                elif line.startswith('f '):  
                    # indices to integers
                    indices = line.strip().split()[1:]
                    face = [int(index.split('/')[0]) - 1 for index in indices]
                    
                    # face is a triangle
                    if len(face) == 3:
                            faces.append(face)
                            
                    # split up polygons with more than 3 sides into triangles
                    elif len(face) > 3:
                        for i in range(1, len(face) - 1):
                            triangle = [face[0], face[i], face[i + 1]]
                            faces.append(triangle)
                    else:
                        
                        if self.isClockwise(vertices[face[0]], vertices[face[1]], vertices[face[2]]):
                            faces.append(face)
                        else:
                            faces.append([face[0], face[2], face[1]])

                            
                    
        return vertices, faces
    
    def isClockwise(self, v1, v2, v3):
        normal = getNormal(v1, v2, v3)
        return normal[2] < 0  

    
    def setBoundingBox(self):
        if not self.vertices:
            return None

        transformedVertices = [(x + self.x, y + self.y, z + self.z) for x, y, z in self.vertices]

        # find min and max x y z 
        self.minX = min(v[0] for v in transformedVertices)
        self.maxX = max(v[0] for v in transformedVertices)
        self.minY = min(v[1] for v in transformedVertices)
        self.maxY = max(v[1] for v in transformedVertices)
        self.minZ = min(v[2] for v in transformedVertices)
        self.maxZ = max(v[2] for v in transformedVertices)
         
    @staticmethod
    def checkCollision(self, other):
        #  one of the objects doesn't have a bounding box
        if not hasattr(self, 'minX') or not hasattr(other, 'minX'):
            return False  

        # check for overlap in all axe

        if (
            self.minX < other.maxX and self.maxX > other.minX and  # x
            self.minY < other.maxY and self.maxY > other.minY and  # y
            self.minZ < other.maxZ and self.maxZ > other.minZ      # z
        ):
            return True


    @staticmethod
    def rotateX(self, angle):
        # rotates vertices around the x-axis
        angle = math.radians(angle)
        cosTheta = math.cos(angle)
        sinTheta = math.sin(angle)
        rotatedVertices = []
        
        for x, y, z in self.vertices:
            newY = y * cosTheta - z * sinTheta
            newZ = y * sinTheta + z * cosTheta
            rotatedVertices.append((x, newY, newZ))
        
        return rotatedVertices
    
    @staticmethod
    def rotateY(self, angle, scaleFactor=1):
        angle = math.radians(angle)
        cosTheta = math.cos(angle)
        sinTheta = math.sin(angle)
        rotatedVertices = []
        
        for x, y, z in self.vertices:
            scaledX = x * scaleFactor
            scaledZ = z * scaleFactor
            
            newX = scaledX * cosTheta + scaledZ * sinTheta
            newZ = -scaledX * sinTheta + scaledZ * cosTheta
            
            rotatedVertices.append((newX / scaleFactor, y, newZ / scaleFactor))
        
        return rotatedVertices

    
    @staticmethod
    def rotatePivotY(self, angle):
        angle = math.radians(angle)
        cosTheta = math.cos(angle)
        sinTheta = math.sin(angle)
        rotatedVertices = []

        centerX = sum(x for x, _, _ in self.vertices) / len(self.vertices)
        centerY = sum(y for _, y, _ in self.vertices) / len(self.vertices)
        centerZ = sum(z for _, _, z in self.vertices) / len(self.vertices)

        translatedVertices = [
            (x - centerX, y - centerY, z - centerZ)
            for x, y, z in self.vertices
        ]

        for x, y, z in translatedVertices:
            newX = x * cosTheta + z * sinTheta
            newZ = -x * sinTheta + z * cosTheta
            rotatedVertices.append((newX, y, newZ))

        finalVertices = [
            (x + centerX, y + centerY, z + centerZ)
            for x, y, z in rotatedVertices
        ]

        return finalVertices
    
    def drawPoly(self, app, corners, fill):
        nearPlane = -0.001

        # clip vertices against the near plane
        clippedCorners = self.clipPolygon(corners, nearPlane)

        # skip if no valid vertices
        if len(clippedCorners) < 3:
            return

        if type(self) not in [MoneyBag, Train, Ramp, CoinMagnet, Sneakers] and not self.isFaceVisible(clippedCorners):
            return

        # clor based on light direction
        fill = self.applyLighting(clippedCorners, fill)

        # clipped vertices into 2D screen coordinates
        transformedCorners = self.transformTo2D(app, clippedCorners)

        # check if all transformed points are valid (not None')
        if self.arePointsValid(transformedCorners):
            self.drawTransformedPolygon(transformedCorners, fill)

    def clipPolygon(self, corners, nearPlane):
        # clip polygon just before the camera
        clippedCorners = []

        for i in range(len(corners)):
            curPoint = corners[i][0] + self.x, corners[i][1] + self.y, corners[i][2] + self.z
            newI = (i + 1) % len(corners)
            nextPoint = corners[(newI)][0] + self.x, corners[newI][1] + self.y, corners[newI][2] + self.z

            if self.isVisible(curPoint, nearPlane):
                clippedCorners.append(corners[i])
            if self.isEdgeCrossing(curPoint, nextPoint, nearPlane):
                intersection = self.getPlaneIntersection(curPoint, nextPoint, nearPlane)
                newPoint = intersection[0] - self.x, intersection[1] - self.y, intersection[2] - self.z
                clippedCorners.append(newPoint)

        return clippedCorners

    def isVisible(self, point, nearPlane):

        return point[2] < nearPlane

    def isEdgeCrossing(self, p1, p2, nearPlane):
        # an edge crosses the near clipping plane
        return (p1[2] < nearPlane) != (p2[2] < nearPlane)

    def getPlaneIntersection(self, p1, p2, nearPlane):
       # intersection of a point with the near clipping plane
        t = (nearPlane - p1[2]) / (p2[2] - p1[2])
        return [p1[i] + t * (p2[i] - p1[i]) for i in range(3)]

    # https://en.wikipedia.org/wiki/Back-face_culling

    def isFaceVisible(self, corners):
        v1, v2, v3 = corners[:3]

        # normal vector of the face
        normal = getNormal(v1, v2, v3)

        # vector from the first vertex to the camera
        cameraToVertex = (v1[0] + self.minX) - app.camera.x, (v1[1] + self.minY) - app.camera.y, (v1[2] + self.minZ) - app.camera.z
        
        # normalise    
        magnitude = sum(c**2 for c in cameraToVertex)**0.5
        cameraToVertex = [c / magnitude for c in cameraToVertex]

        # dot product between the camera vector and the face normal
        dotProduct = sum(cameraToVertex[i] * normal[i] for i in range(3))
    
        
        # face is visible if the dot product is positive
        return dotProduct >= 0


    def applyLighting(self, corners, fill):
         # light source is a plane above 
        lightPlaneNormal = [0, -1, -0.7]  # light is goign downwards
        lightPlaneIntensity = 0.7    # max light intensity

        normal = getNormal(*corners[:3])
    
        # dot product between the face normal and the light plane normal
        lightIntensity = max(0.33 ,sum(normal[i] * lightPlaneNormal[i] for i in range(3)) * lightPlaneIntensity)
        
        # old rgb values
        r, g, b = str(fill)[4:-1].split(',')
        
        # new rgb values based on intensity
        r, g, b = [int(int(c) * lightIntensity) for c in (r, g, b)]
        return rgb(r, g, b)


    def transformTo2D(self, app, points):
        # 3D coords to 2D
        transformedPoints = []
        for point in points:
            transformedPoint = self.get2DCoords(app, point)
            transformedPoints.append(transformedPoint)
        return transformedPoints

    def arePointsValid(self, points):
        # no invalid points (with None)
        for point in points:
            if None in point:
                return False
        return True

    def drawTransformedPolygon(self, points, fill):
        # draw the triangle using the transformed projected coords
        flattenedPoints = []
        for point in points:
            flattenedPoints.extend(point)  # add x and y to the list
                    #unpack
        drawPolygon(*flattenedPoints, fill=fill, border=None)


    # https://en.wikipedia.org/wiki/3D_projection
    def get2DCoords(self, app, point):
        aX, aY, aZ = point
        cX, cY, cZ = self.x + app.camera.x, self.y + app.camera.y, self.z

        eX, eY, eZ = (app.width // 2, 200, 540)
        x, y, z = aZ - cZ, aY - cY, aX - cX
        cX = dcos(app.camera.vViewAngle)
        cY = dcos(app.camera.hViewAngle)
        
        sX = dsin(app.camera.vViewAngle)
        sY = dsin(app.camera.hViewAngle)
        
        dX = (cY * x) - (sY * z)
        dY = sX * (cY * z + sY * x) + (cX * y)
        dZ = cX * (cY * z + sY * x) - (sX * y)
    
        # out of view or behind camera
        if dZ <= -30 or dZ >= 0:
            return [None, None]

        bX = (eZ / dZ * dX) + eX
        bY = (eZ / dZ * dY) + eY
        return [bX, bY]
            
    
    def calculateFaceDepth(self, corners, x, y, z):
    # calculate the average depth (z-value) for the face based on corner points
        totalDepth = 0
        for corner in corners:
            # use the z-coordinate after converting to camera-relative coordinates
            aX, aY, aZ = corner[0] - x, corner[1] - y, corner[2] - z
            cX, cY, cZ = app.camera.x, app.camera.y, app.camera.z
            totalDepth += math.sqrt((aX - cX) ** 2 + (aY - cY) ** 2 + (aZ - cZ) ** 2)
        
        # average depth
        return totalDepth / len(corners)
    
    def drawShape(self, app):
        x, y, z, fill = self.x, self.y, self.z, self.fill
        faces = self.faces

        faceDepths = []
        for face in faces:
            corners = [self.vertices[idx] for idx in face]
            depth = self.calculateFaceDepth(corners, x, y, z)
            faceDepths.append((depth, corners))
            
        #farthest faces first
        faceDepths.sort(reverse=True)
        
        for depth, face in faceDepths:
            self.drawPoly(app, face, fill)
        
            
    def redrawAll(self, app):
        self.drawShape(app)

    def onStep(self, app):
        pass

# get normal vector of a face
def getNormal(v1, v2, v3):
    edge1 = [v2[i] - v1[i] for i in range(3)]
    edge2 = [v3[i] - v1[i] for i in range(3)]

    # get the cross product
    normal = [
        edge1[1] * edge2[2] - edge1[2] * edge2[1], 
        edge1[2] * edge2[0] - edge1[0] * edge2[2], 
        edge1[0] * edge2[1] - edge1[1] * edge2[0]   
    ]

    # normalize
    magnitude = sum(c**2 for c in normal)**0.5
    return [n / (magnitude+0.000001) for n in normal]

# class PowerUp(Model):
   
class Train(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.07
        super().__init__("ModelObjs/train.obj", lane, z=z,fill=rgb(83,123,138))
        self.x = {0: -0.8, 1: 0.65, 2: 2.1}[lane]
        self.z -= 0.4
        self.vertices = Model.rotateY(self, 90) 

        
class Ramp(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.07
        super().__init__("ModelObjs/ramp.obj", lane, z=z,fill=rgb(182,115,33))
        self.x = {0: -1.5, 1: 0, 2: 1.5}[lane]
        self.y -= 0.7
        Model.setBoundingBox(self)






class Duck(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.05
        super().__init__("ModelObjs/duck.obj", lane, z=z,fill=rgb(139,68,19))
   
class Jump(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.05
        super().__init__("ModelObjs/jump.obj", lane, z=z,fill=rgb(139,68,19))

class DuckNJump(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.05
        super().__init__("ModelObjs/ducknjump.obj", lane, z=z,fill=rgb(139,68,19))  
        
class SprayPaintBag(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.8
        super().__init__("ModelObjs/sprayPaintBag.obj", lane, z=z,fill=rgb(139,68,19))  
        
    def onStep(self, app):
        self.vertices = Model.rotateY(self, 10)

class MoneyBag(Model):
    
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.4
        super().__init__("ModelObjs/moneyBag.obj", lane, z=z,fill=rgb(173,113,69))  
        self.x += 0.6
        self.y += 1

    def onStep(self, app):
        self.vertices = Model.rotatePivotY(self, 3)   
    
       
        

# represents the player in 3D space to detect collisoins more accurately
class PlayerModel():
    def __init__(self):
        self.minX = {0: -1.5, 1: 0, 2: 1.5}[app.player.lane] - 0.5
        self.maxX ={ 0: -1.5, 1: 0, 2: 1.5}[app.player.lane] + 0.5
        self.minY = 0
        self.maxY = 1
        self.minZ = -2.4
        self.maxZ = -1



class Coin(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.3
        super().__init__("ModelObjs/coin.obj", lane, y=2, z=z, fill=rgb(255, 223, 0))
        self.vertices = Model.rotateX(self, 90)
        
    def onStep(self, app):
        self.vertices = Model.rotateY(self, 3)
        if app.player.hasCoinMagnet and self.z > -5:
            playerX = {0: -1.5, 1: 0, 2: 1.5}[app.player.lane]
            step = 0.1  
            if app.player.isOnTrain:
                self.y = min(self.y + step, -2)
            else:
                self.y = min(self.y + step, 0)
            if self.x < playerX:
                self.x = min(self.x + step, playerX)
            elif self.x > playerX:
                self.x = max(self.x - step, playerX)
            self.lane = app.player.lane

        self.setBoundingBox()



     
class HoverBoard(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.15
        super().__init__("ModelObjs/hoverboard.obj", lane, z=z,fill=rgb(194,25,9)) 
        self.y -= 0.2
        
    def onStep(self, app):
        self.vertices = Model.rotatePivotY(self, 3)  
     
    def __repr__(self):
        return "Hover Board"

    def onStep(self, app):
        self.vertices = Model.rotatePivotY(self, 3)  
     
class ScoreBooster(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.1
        super().__init__("ModelObjs/scoreBooster.obj", lane, z=z,fill=rgb(254,233,42))  
    def onStep(self, app):
        self.vertices = Model.rotatePivotY(self, 3) 
    def __repr__(self):
        return "Score Booster"

     
class Sneakers(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.3
        super().__init__("ModelObjs/sneakers.obj", lane, z=z,fill=rgb(215,178,9))
          
    def onStep(self, app):
        self.vertices = Model.rotatePivotY(self, 3)  
    def __repr__(self):
        return "Jump Boost"
     
class CoinMagnet(Model):
    def __init__(self, y=0, lane=0, z=-20):
        self.scale = 0.4
        super().__init__("ModelObjs/coinMagnet.obj", lane, z=z,fill=rgb(198,21,1)) 
        self.y -= 0.2
        self.vertices = Model.rotateX(self, 70)

    def onStep(self, app):
        self.vertices = Model.rotatePivotY(self, 3)  
    def __repr__(self):
        return "Coin Magnet"