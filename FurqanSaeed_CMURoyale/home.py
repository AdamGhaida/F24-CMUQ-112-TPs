# Furqan Saeed
# faseed@andrew.cmu.edu

from cmu_graphics import *
import random
import play
import ai



def bg(app):
    diamondWH = app.h/11
    diamondSide = ((diamondWH**2)/2)**0.5 

    drawRect(app.x0, app.y0, app.w, app.h, fill=rgb(19, 96, 153))

    for i in range(11):
        for j in range(8):
            drawRect(app.x0 + diamondWH*j, app.y0 + diamondWH*i, diamondSide,
                     diamondSide, fill=rgb(19, 83, 139), align='top',
                     rotateAngle=45)
    
    drawRect(app.x0, app.y0, app.w, app.height, fill='white',
             align='top-right')
    drawRect(app.x0 + app.w, 0, app.width - app.x0 + app.w, app.height,
             fill='white')
    drawRect(app.x0, app.y0, app.w, app.h, border='black', fill=None)

    drawImage("Assets/miniArena.png", app.x0 + app.w/2, app.h/2,
              align='center', width=350, height=350)

def battleButton(app):
    drawRect(377, 640, app.w*0.5, app.h*0.1,
             fill=gradient(rgb(255, 208, 83), rgb(255, 188, 44), start='top'),
             align='center', border='black', borderWidth=app.w*0.001)
    drawLabel('Battle', app.x0 + app.w/2, app.h*0.8, fill=rgb(255, 255, 204),
              border='black', borderWidth=app.w*0.001, font='Supercell-Magic',
              size=app.h*0.05)


def nameCard(app):
    drawRect(app.x0 + app.w/2, app.h*0.15, app.w*0.4, app.h*0.08,
             fill=gradient(rgb(164,234,255), rgb(122,209,255), start='top'),
             align='center', border='black', borderWidth=app.w*0.001)
    drawLabel("User1", app.x0 + app.w/2, app.h*0.15, 
              font='Supercell-Magic', size=20, fill='white', border='black')
    
def gameName(app):
    drawLabel("CMU", app.x0 + app.w/2, app.h*0.1, font='Supercell-Magic',
              fill='chartreuse', borderWidth=app.w*0.001, border='black',
              size=app.h*0.1)
    drawLabel("ROYALE", app.x0 + app.w/2, app.h*0.205, font='Supercell-Magic',
              fill='chartreuse', borderWidth=app.w*0.001, border='black', 
              size=app.h*0.1)


def tutorialButton(app):
    drawImage("Assets/tutorialLogo.png", app.x0+app.w*0.08, app.h/2,
              align='center')


def drawtutorial(app):
    drawRect(app.x0+app.w/2, app.h/2, app.w*0.92, app.h*0.7, align='center',
             fill='grey')
    drawLabel("Tutorial", app.x0+app.w/2, app.h*0.2, align='center',
              font='Supercell-Magic', fill='white', border='black',
              size=30)
    drawImage("Assets/tutorial.png", app.x0+app.w/2, app.h/2,
              align='center', width=app.w*0.9, height=app.h*0.65)
    drawImage("Assets/crossButton.png", app.x0+app.w*0.9, app.h*0.2, 
              align='center')

def home(app):
    bg(app)
    battleButton(app)
    nameCard(app)
    tutorialButton(app)
    if app.menu:
        drawMenu(app)
    if app.tutorial:
        drawtutorial(app)


def checkClick(app, x, y):
    if not app.menu and not app.tutorial:
        if (254 <= x <= 500) and (600 <= y <= 680):
            app.menu = True
        elif (144 <= x <= 197) and (254 <= y <= 546):
            app.tutorial = True
    elif app.menu:
        if x < 150 or x > 603 or y < 120 or y > 680 or \
            (554 < x < 594 and 140 < y < 180):
            app.menu = False
        if 160 < x < 594 and 240 < y < 400:
            setBattle(app)
            app.ai = ai.lvl1(app)
            app.menu = False
        elif 160 < x < 594 and 480 < y < 640:
            setBattle(app)
            app.ai = ai.lvl2(app)
            app.menu = False
    elif app.tutorial:
        if x < 150 or x > 603 or y < 120 or y > 680 or \
            (554 < x < 594 and 140 < y < 180):
            app.tutorial = False


def setBattle(app):
    app.HomePage = False
    app.battleArena = True
    app.enemyDeck = play.randomizer(app)
    app.playerDeck = play.randomizer(app)
    app.playerCardSelected = None
    app.enemyCardSelected = None
    app.enemyCards = []
    app.playerCards = []
    app.playerTowers = [play.princessTower(237.5, 640.5, "player"),
                        play.princessTower(516.5, 640.5, "player"),
                        play.kingTower(377, 729, "player")]
    app.enemyTowers = [play.princessTower(237.5, 159.5, "enemy"),
                       play.princessTower(516.5, 159.5, "enemy"),
                       play.kingTower(377, 71, "enemy")]
    app.playerElixir = 0
    app.enemyElixir = 0
    app.enemyCardSelectedIndex = None
    app.playerCardSelectedIndex = None
    app.winner = None
    app.gameOver = False
    app.gameTimer = 0
    app.suddenDeath = False
    app.ultimateDeath = False
    app.x2Elixir = False
    app.x3Elixir = False
    app.highlightTile = (False, 0, 0)
    app.projectiles = []
    app.minutes = 3
    app.seconds = 30
    app.timer = "3:30"
    app.lobbyMusic[app.lobbyMusicPlaying].pause()
    app.battleMusicPlaying = random.choice([0,1,2])
    app.battleMusic[app.battleMusicPlaying].play()


def loadingScreen(app):
    if app.time == app.stepsPerSecond*1.5:
        app.loading = random.randint(app.loading+1, 17)
    elif app.time == app.stepsPerSecond*2:
        app.loading = random.randint(app.loading+1, 50)
    elif app.time == app.stepsPerSecond*2.5:
        app.loading = random.randint(app.loading+1, 99)
    elif app.time == app.stepsPerSecond*3.2:
        app.loading = 100
    elif app.time == app.stepsPerSecond*3.5:
        app.loadingScreen = False
        app.HomePage = True
        app.lobbyMusicPlaying = random.randint(0, len(app.lobbyMusic)-1)
        app.lobbyMusic[app.lobbyMusicPlaying].play(loop=True)

def drawLoadingScreen(app):
    drawImage("Assets/loadingScreen.png", app.x0, 0, width=app.w, height=app.h)
    drawRect(app.x0, app.h, app.w, app.h*0.05, fill='black', border='white',
             borderWidth=0.5, align='left-bottom')
    if app.loading != 0:
        drawRect(app.x0, app.h, app.w*(app.loading/100), app.h*0.05,
                 fill=rgb(27,112,218), align='left-bottom') 
        drawRect(app.x0+3, app.h*0.955, app.w*(app.loading/100)*0.97,
                 app.h*0.024, fill=rgb(125,179,239), border=None)
    drawLabel(f"{app.loading}%", app.x0+app.w*0.5, app.h*0.97,
              font='Supercell-Magic', fill='white', size=25, align='bottom',
              border='black')
    drawLabel(app.allTips[app.tip][:-1], app.x0+app.w/2, app.h*0.9,
              font='Supercell-Magic', fill='white', size=17, border='black',
              borderWidth=0.4)
    gameName(app)



def CMUROYALE(app):
    drawRect(app.x0, 0, app.w, app.h, fill='black')
    drawOval(app.x0+app.w/2, app.h/2, app.h*0.4, app.h*0.4, fill="white", 
             opacity=2.5)
    drawLabel("CMU", app.x0+app.w/2, app.h*0.4, font='Supercell-Magic', \
              align='center', fill='white', size=70)
    drawLabel("ROY", app.x0+app.w/2, app.h*0.5, font='Supercell-Magic', \
              align='center', fill='white', size=70)
    drawLabel("ALE", app.x0+app.w/2, app.h*0.6, font='Supercell-Magic', \
              align='center', fill='white', size=70)
    


def drawMenu(app):
    drawRect(app.x0+app.w/2, app.h/2, app.w*0.92, app.h*0.7, align='center',
             fill='grey')
    drawLabel("Menu", app.x0+app.w/2, app.h*0.2, align='center',
              font='Supercell-Magic', fill='white', border='black',
              size=30)
    
    drawRect(app.x0+app.w/2, app.h*0.4, app.w*0.88, app.h*0.2, 
             fill='lightBlue', align='center')
    drawLabel("Lvl 1", app.x0+app.w/2, app.h*0.4, align='center',
              font='Supercell-Magic', fill='white', border='black',
              size=30)
    
    drawRect(app.x0+app.w/2, app.h*0.7, app.w*0.88, app.h*0.2, 
             fill='lightBlue', align='center')
    drawLabel("Lvl 2", app.x0+app.w/2, app.h*0.7, align='center',
              font='Supercell-Magic', fill='white', border='black',
              size=30)
    
    drawImage("Assets/crossButton.png", app.x0+app.w*0.9, app.h*0.2, 
              align='center')