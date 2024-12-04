from cmu_graphics import *
from PIL import Image
from math import *

class drawUtils:

    def __init__(self, superSecretCodebaseEasterEgg="112 is fun!"):
        pass

    # Thank you Mr Shikfa for showing me how to do this!
    def drawRoundedRect(self, x, y, width, height, radius, color,opacity=100):
        # Draw corners as circles
        drawCircle(x + radius, y + radius, radius, fill=color,opacity=opacity)  
        drawCircle(x + width - radius, y + radius, radius, fill=color,
                   opacity=opacity)  
        drawCircle(x + radius, y + height - radius, radius, fill=color,
                   opacity=opacity)  
        drawCircle(x + width - radius, y + height - radius, radius, fill=color,
                   opacity=opacity)  
        
        # Draw edges as rectangles
        drawRect(x + radius, y, abs(width - 2 * radius), height, fill=color,
                 opacity=opacity)  
        drawRect(x, y + radius, width, abs(height - 2 * radius), fill=color,
                 opacity=opacity)  

        # Fill the center
        drawRect(x + radius, y + radius, abs(width - 2 * radius), 
                                        abs(height - 2 * radius), fill=color,
                                        opacity=opacity)
        
    def drawArcArrow(self, centerX, centerY, radius, arrowSize=8, color="black"):
        # Draw the arc (quarter-circle instead of half-circle for better fit)
        drawArc(centerX - radius, centerY - radius, centerX + radius, centerY + radius,
                45, 270, fill=None, border=color)

        # Arrow tip at the end of the arc
        angle = radians(315)  # End of the arc
        arrowTipX = centerX + radius * cos(angle)
        arrowTipY = centerY - radius * sin(angle)

        # Calculate the points for the arrowhead
        arrowPoint1 = (
            arrowTipX - arrowSize * cos(angle - pi / 6),
            arrowTipY + arrowSize * sin(angle - pi / 6),
        )
        arrowPoint2 = (
            arrowTipX - arrowSize * cos(angle + pi / 6),
            arrowTipY + arrowSize * sin(angle + pi / 6),
        )

        # Draw the arrowhead with three lines
        drawLine(arrowTipX, arrowTipY, arrowPoint1[0], arrowPoint1[1], fill=color)
        drawLine(arrowTipX, arrowTipY, arrowPoint2[0], arrowPoint2[1], fill=color)



    def drawBrowserNavButtons(self,color='black'):
        
        # Button dimensions, i got these through math equations 
        #   (not magic numbers :))
        
        buttonSize = 30
        padding = 24
        buttonY = 50 
        

        # Back button
        backCenterX = buttonSize // 2 + 10
        self.drawRoundedRect(backCenterX - buttonSize // 2, buttonY - buttonSize // 2,
                            buttonSize, buttonSize, radius=10, color=color)
        self.drawArrow(backCenterX + 10, buttonY, backCenterX - 10, buttonY, arrowSize=8, color="black")

        # Forward button
        forwardCenterX = backCenterX + buttonSize + padding
        self.drawRoundedRect(forwardCenterX - buttonSize // 2, buttonY - buttonSize // 2,
                            buttonSize, buttonSize, radius=10, color=color)
        self.drawArrow(forwardCenterX - 10, buttonY, forwardCenterX + 10, buttonY, arrowSize=8, color="black")

        # Refresh button
        refreshCenterX = forwardCenterX + buttonSize + padding
        self.drawRoundedRect(refreshCenterX - buttonSize // 2, buttonY - buttonSize // 2,
                            buttonSize, buttonSize, radius=10, color=color)
        
        # Draw the letter "R" in the center of the refresh button
        drawLabel("R", refreshCenterX, buttonY, size=18)


    def drawArrow(self, x1, y1, x2, y2, arrowSize=10, color="black"):
        # Draw the arrow base
        drawLine(x1, y1, x2, y2, fill=color)

        # Calculate the direction of the arrow
        dx = x2 - x1
        dy = y2 - y1
        angle = atan2(dy, dx)

        # end points og the arrow head pieces
        arrowPoint1 = (
            x2 - arrowSize * cos(angle - pi / 6),  # x-coordinate
            y2 - arrowSize * sin(angle - pi / 6),  # y-coordinate
        )
        arrowPoint2 = (
            x2 - arrowSize * cos(angle + pi / 6),  # x-coordinate
            y2 - arrowSize * sin(angle + pi / 6),  # y-coordinate
        )

        # arrowhead
        drawLine(x2, y2, arrowPoint1[0], arrowPoint1[1], fill=color)  
        drawLine(x2, y2, arrowPoint2[0], arrowPoint2[1], fill=color)  

    # small helper function to check distances to centers of spheres
    def circularDistance(self,xy1,xy2):
        return ((xy1[0]-xy2[0])**2+(xy1[0]-xy2[0])**2)**0.5

