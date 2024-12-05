# Furqan Saeed
# faseed@andrew.cmu.edu

from cmu_graphics import *
import math
import string
import random
import home
import time
import play
import arena

def onAppStart(app):
    
    
    openingSound = Sound("Assets/openingSound.mp3")
    openingSound.play()
    app.lobbyMusic = [Sound("Assets/lobbyMusic1.mp3"), 
                      Sound("Assets/lobbyMusic2.mp3"),
                      Sound("Assets/lobbyMusic3.mp3")] 
    app.lobbyMusicPlaying = 0
    app.battleMusic = [Sound("Assets/battleMusic1.mp3"), 
                      Sound("Assets/battleMusic2.mp3"),
                      Sound("Assets/battleMusic3.mp3")]
    app.suddenDeathMusic = Sound("Assets/suddenDeathMusic.mp3")
    app.battleMusicPlaying = 0


    # Initialisation Methods
    getCanvasDetails(app)
    app.stepsPerSecond = 30
    
    # Modes
    app.CMUROYALE = True
    app.loadingScreen = False
    app.HomePage = False
    app.battleArena = False
    app.suddenDeath = False
    app.ultimateDeath = False
    
    # Arena Specific variables
    app.arenaRows = 30
    app.arenaCols = 18
    
    # Other Variables
    app.time = 0
    app.gameTimer = 0
    app.minutes = 3
    app.seconds = 30
    app.timer = "3:30"
    app.playerElixir = 0
    app.enemyElixir = 0
    app.enemyCards = []
    app.playerCards = [] # The cards on the arena that the player has played
    app.playerDeck = []
    app.enemyDeck = [] # The deck the AI uses
    app.projectiles = []
    app.playerCardSelected = None
    app.playerCardSelectedIndex = None
    app.enemyCardSelected = None
    app.enemyCardSelectedIndex = None
    app.gameOver = False
    app.ai = None
    app.playerTowers = [play.princessTower(237.5, 640.5, "player"),
                        play.princessTower(516.5, 640.5, "player"),
                        play.kingTower(377, 729, "player")]
    
    app.enemyTowers = [play.princessTower(237.5, 159.5, "enemy"),
                       play.princessTower(516.5, 159.5, "enemy"),
                       play.kingTower(377, 71, "enemy")]
    app.loading = 0
    app.highlightTile = (False, 0, 0)
    app.x2Elixir = False
    app.x3Elixir = False
    app.menu = False
    app.tutorial = False
    # The towers that die during ultimate death, their count
    app.utDeathP = 0
    app.utDeathE = 0


    # Assets
    app.elixirIcon = "Assets/elixirIcon.png"
    app.tips = open("Assets/tips.txt", "r")
    app.allTips = app.tips.readlines()
    app.tips.close()
    # Choose a random tip from all the tips in tips.txt
    app.tip = random.randint(0, 19)




def getCanvasDetails(app):
    # App details
    app.h = app.height
    app.w = app.h/19.5 * 12
    app.x0 = app.width/2 - app.w/2 - app.w/4
    app.y0 = 0
    app.x1 = app.x0 + app.w
    app.y1 = 0
    
    # Arena Details
    app.playgroundH = app.h*0.95
    app.playgroundW = app.playgroundH/30 * 18
    app.playgroundX0 = app.x0 + (app.w-app.playgroundW)/2
    app.playgroundY0 = app.y0 + (app.h-app.playgroundH)/2


def redrawAll(app):    
    if app.CMUROYALE:
        home.CMUROYALE(app)
    
    if app.loadingScreen:
        home.drawLoadingScreen(app)

    # If the game is in the homepage
    if app.HomePage:
        home.home(app)
        
    
    # If the player is in a match
    if app.battleArena:
        arena.drawArena(app)
        
        for tower in app.playerTowers:
            tower.draw()
        
        for tower in app.enemyTowers:
            tower.draw()

        for card in app.playerCards:
            card.draw()
            
        for card in app.enemyCards:
            card.draw()
        
        for proj in app.projectiles:
            proj.draw()
        
        if app.highlightTile[0] == True and not app.gameOver:
            drawRect(app.highlightTile[1], app.highlightTile[2], 25, 25,
                     fill=None, border='white', align='center')

        if app.x2Elixir or app.x3Elixir:
            arena.drawxElixir(app)

        if app.gameOver:
            arena.drawGameOver(app)

def onMousePress(app, x, y):

    if app.HomePage:
        home.checkClick(app, x, y)


    if app.battleArena:
        play.checkClick(app, x, y)
            

def onStep(app):
    getCanvasDetails(app)
    app.time += 1

    if app.time == app.stepsPerSecond*1.5:
        app.CMUROYALE = False
        app.loadingScreen = True
    if app.loadingScreen:
        home.loadingScreen(app)



    if app.battleArena:

        if app.gameOver:
            return
        
        if not app.ultimateDeath:
            play.timerOnStep(app)
            
            play.elixirOnStep(app)

            app.ai.onStep(app)

            #Movement of cards on the arena
            for card in app.playerCards[:]:
                if card.alive == False:
                    app.playerCards.remove(card)
                card.onStep(app)
                
            for card in app.enemyCards[:]:
                if card.alive == False:
                    app.enemyCards.remove(card)
                card.onStep(app)

            for tower in app.playerTowers[:]:
                tower.onStep(app)
            
            for tower in app.enemyTowers[:]:
                tower.onStep(app)

            for projectile in app.projectiles[:]:
                if projectile.exists == False:
                    app.projectiles.remove(projectile)
                projectile.onStep(app)

            if app.suddenDeath:
                play.winnerCheck(app)

            # Checks if king towers are dead, if so then who is winner
            if app.enemyTowers[2].alive == False:
                app.gameOver = True
                app.winner = "player"
                if not app.suddenDeath:
                    app.battleMusic[app.battleMusicPlaying].pause()
                else:
                    app.suddenDeathMusic.pause()
            elif app.playerTowers[2].alive == False:
                app.gameOver = True
                app.winner = "enemy"
                if not app.suddenDeath:
                    app.battleMusic[app.battleMusicPlaying].pause()
                else:
                    app.suddenDeathMusic.pause()
        else:
            play.ultimateDeathOnStep(app)



def onKeyPress(app, key):
    if key in "Rr":
        onAppStart(app)

def onMouseMove(app, x, y):
    if app.battleArena:
        if app.playerCardSelected != None:
            play.highlightTile(app, x, y)

def onMouseRelease(app, x1, y1):
    pass







runApp(width=1000, height=800)