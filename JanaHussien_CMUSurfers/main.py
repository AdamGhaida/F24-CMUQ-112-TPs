from cmu_graphics import *
from player import *
from models import *
from managers import *
from camera import *

def reset(app):
    app.initialized, app.paused = False, False
    app.fpsCounter = FPSCounter()
    app.modelsManager = ModelsManager()
    app.camera = Camera()
    app.player = Player()
    app.playerModel = PlayerModel()

    app.modelsManager.entities.clear()
    app.modelsManager.spawnObstacleRow()
    app.modelsManager.spawnCoinRow(10)
    
    app.coins = 0
    app.speed = 0.1
    setActiveScreen('title')

    
def onAppStart(app):
    app.laneToX = {0: -0.54, 1: 0.75, 2: 2.04}
    app.width = 800
    app.height = 600
    app.highScore = 0
    reset(app)
    app.theme = Sound('sounds/maintheme.mp3')
    app.initialized = True
    app.stepsPerSecond = 60


###
# TITLE
###
def title_onScreenActivate(app):
    app.moneyBag = MoneyBag(0, z=-5)
    app.entities = [app.moneyBag]
    app.textSize = 30
    app.timer = 0 

    

def title_redrawAll(app):

    drawRect(0, 0, 800, 600,
            fill=gradient('yellow',  'orange', 'red', start='center'))

    for entity in app.entities:
        entity.redrawAll(app)
    
    drawLabel("CMU Surfers", 
                  app.width / 2, app.height / 2, 
                  size=app.textSize+1, bold = True, borderWidth = 2, align="center", fill="white")
    drawLabel("CMU Surfers", 
                app.width / 2, app.height / 2, 
                  size=app.textSize, bold = True, borderWidth = 2, align="center")
    drawLabel("Press ENTER to Start", app.width / 2, 2*app.height / 3, size=20, align="center", fill="chartreuse")

def title_onStep(app):
    app.timer +=1
    
    for entity in app.entities:
        entity.onStep(app) 
    
    app.textSize = 30 + 10 * (math.sin(app.timer / 30) + 1)

  
def title_onKeyPress(app, key):
    if key == "enter":
        app.entities.clear()
        setActiveScreen('game')


###
# GAME
###

def game_onScreenActivate(app):
    app.timer = 0
    app.score = 0
    app.setMaxShapeCount(5000000)
    app.theme.play()
    app.initialized = True
    # https://www.youtube.com/watch?v=zGhEyEJLChw


def game_onKeyPress(app, key):
    app.player.onKeyPress(key)
    if key == "r":
        reset(app)
    elif key == "p":
        app.paused = not app.paused

    

def game_onMouseDrag(app, mouseX, mouseY):
    app.camera.onMouseDrag(mouseX, mouseY)
    pass

def game_onStep(app):
    app.timer += 1
    app.fpsCounter.update()
    if not app.paused and app.initialized:
        app.score += int(app.speed*10) * app.player.scoreMultiplier
        app.player.onStep()
        app.camera.onStep(app)
        app.modelsManager.onStep(app)
        if app.player.checkOutOfFrame():
            if app.player.isOnHoverBoard:
                app.player.fakeDeath()
            else:
                app.highScore = max(app.highScore, app.score)
                app.theme.pause()
                setActiveScreen('gameOver')
        if app.timer % 60 == 0:
            app.modelsManager.spawnObstacleRow()
        elif app.timer % 30 == 0:
            app.modelsManager.spawnCoinRow(1)


def game_redrawAll(app):
    if app.initialized and not app.paused: 
        if app.player.isRolling:
            app.player.redrawAll(app)
            app.modelsManager.redrawAll(app)
        else:
            app.modelsManager.redrawAll(app)
            app.player.redrawAll(app)


        drawLabel(f"Score: {app.score}", 
            5, 5, size=20, align="left-top")

        drawLabel(f"Coins: {app.coins}", 
            app.width-5, 5, size=20, align="right-top")
        if app.player.activePowerUp:
            drawLabel(f"Power Up Time remaining: {str(15-app.player.powerUpTimer)}",app.width//2, 40, size=18, align="center")

            

    else:
        drawLabel("Paused", 
            app.width / 2, app.height / 3, size=40, align="center")
    
    app.fpsCounter.redrawAll(app)


###
# GAME OVER
###

def gameOver_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=gradient('black', 'red', start='center'))

    drawLabel("Game Over!", app.width / 2, app.height / 3,
              size=40, align="center", fill='white', bold=True)

    drawLabel("Press R to Return to Title Screen", app.width / 2, app.height / 2,
              size=20, align="center", fill='lightgray')

    drawLabel(f"High Score: {app.highScore}", app.width / 2, app.height / 1.5,
              size=24, align="center", fill='gold')

def gameOver_onKeyPress(app, key):
    if key == "r":
        reset(app)



def main():
    runAppWithScreens(initialScreen = 'title')
    

if __name__ == "__main__":
    main()