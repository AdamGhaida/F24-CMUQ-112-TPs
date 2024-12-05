# Furqan Saeed
# faseed@andrew.cmu.edu

from cmu_graphics import *
import math
import string
import random
import home
import time


##########################
# Draw arena to fight in #
##########################

# 30 * 18


def bg(app):

    drawImage("Assets/wallpaper.jpg", 0, 0, width=app.width, height=app.height)
    drawImage("Assets/arenaBase.png", app.x0-50, 0)
    drawRect(81, 0, 50, app.h, border=None, fill=rgb(86,68,49))




    #Set base for elixir count to draw
    y0 = app.h
    x0 = app.x0
    barH = app.h/10
    if int(app.playerElixir) == 0:
        pass
    else:
        drawRect(x0, y0, 50, barH*int(app.playerElixir), align='bottom-right',
                 fill=rgb(201,31,206), border=None)

    if math.isclose((app.playerElixir-int(app.playerElixir))*barH, 0,
                    abs_tol = 0.0001):
        pass
    else:
        # Grey bar showing the elixir filling up
        drawRect(x0, y0-barH*int(app.playerElixir), 50,
                 (app.playerElixir-int(app.playerElixir))*barH,
                 fill=rgb(128,92,91), border=None, align='bottom-right')
        

    #Set base Y for lines of Elixir to draw
    y0 = app.h - app.h/10
    for i in range(9):
        drawLine(x0, y0 - (app.h/10)*i, x0-50, y0 - barH*i,
                 fill='black')
        
    # Border for elixir bar
    drawRect(81, 0, 50, app.h, fill=None, border='black')

    # Draw Elixir Icon and count of how much elixir the player has
    drawImage(app.elixirIcon, x0-50, app.h+10, align='bottom', 
              width=64, height=64)
    drawLabel(int(app.playerElixir), x0-70, app.h-20, align='bottom',
              font='Supercell-Magic', size=32, fill='white', border='black')

    # Drawing the deck
    for i in range(4):
        y = 24 + i*190
        if str(app.playerCardSelected) == str(app.playerDeck[i]):
            y -= 10
        app.playerDeck[i].drawCard(648, y)

    # Drawing "up next" Card  
    app.playerDeck[4].drawCard(820, 694.5, h=105.5, w=86)
    drawLabel("Up Next:", 872, 680, size=12, font='Supercell-Magic',
              fill='white', border='black', borderWidth=0.5)

    # Drawing the clock and red halo for sudden death
    drawRect(820, 0, 120, 70, align='top-left', fill='black',
                border='black', borderWidth=3, opacity=50)
    drawLabel(app.timer, 840, 35, size=25, fill='white',
              font='Supercell-Magic', align='top-left',
              border='black', borderWidth=1)
    if not app.suddenDeath:
        drawLabel("Time left:", 825, 10, size=15, fill=rgb(209, 171, 56),
                font='Supercell-Magic', align='top-left',
                border='black', borderWidth=1)
    else:
        drawLabel("Sudden Death", 825, 10, size=10, fill=rgb(255, 0, 0),
                font='Supercell-Magic', align='top-left',
                border='black', borderWidth=1)
        drawRect(app.x0, 0, app.w, app.h, fill=rgb(255,0,0), opacity=5)

    


#################
# Arena drawing #
#################

    # drawRect(app.x0, 0, 50, app.h, align='top-right', fill=None,
    #          border='black')

    # # The background of the whole arena
    # drawRect(app.x0, app.y0, app.w, app.h, fill=rgb(156,140,88))

    # drawRect(app.playgroundX0, app.playgroundY0, app.playgroundW,
    #          app.playgroundH, fill=rgb(183,196,82))
    
    # cellSize = app.playgroundW/18
    
    # # The tiles
    # # (Use two loops twice for optimization of decreasing total objects)
    # for row in range(0, 14, 2):
    #     for col in range(1, app.arenaCols, 2):
    #         drawRect(app.playgroundX0+cellSize*col,
    #                  app.playgroundY0+cellSize*row,
    #                  cellSize,cellSize, fill=rgb(170,189,73),border=None)
    
    # for row in range(16, app.arenaRows, 2):
    #     for col in range(1, app.arenaCols, 2):
    #         drawRect(app.playgroundX0+cellSize*col,
    #                  app.playgroundY0+cellSize*row,
    #                  cellSize,cellSize, fill=rgb(170,189,73),border=None)
    
    # for row in range(1, 15, 2):
    #     for col in range(0, app.arenaCols, 2):
    #         drawRect(app.playgroundX0+cellSize*col,
    #                  app.playgroundY0+cellSize*row,
    #                  cellSize,cellSize, fill=rgb(170,189,73),border=None)
            
    # for row in range(17, app.arenaRows, 2):
    #     for col in range(0, app.arenaCols, 2):
    #         drawRect(app.playgroundX0+cellSize*col,
    #                  app.playgroundY0+cellSize*row,
    #                  cellSize,cellSize, fill=rgb(170,189,73),border=None)
    

    # # The Main Path
    # drawRect(app.playgroundX0+cellSize*14, app.playgroundY0+cellSize*2,
    #          cellSize, cellSize*26, fill='black', opacity=20)
    
    # drawRect(app.playgroundX0+cellSize*3, app.playgroundY0+cellSize*2,
    #          cellSize, cellSize*26, fill='black', opacity=20)
    
    # drawRect(app.playgroundX0+cellSize*4, app.playgroundY0+cellSize*2,
    #          cellSize*10, cellSize, fill='black', opacity=20)
    
    # drawRect(app.playgroundX0+cellSize*4, app.playgroundY0+cellSize*27,
    #          cellSize*10, cellSize, fill='black', opacity=20)
    
    # drawRect(app.playgroundX0+cellSize*2, app.playgroundY0+cellSize*4,
    #          cellSize*3, cellSize*3, fill='black', opacity=50)
    
    # drawRect(app.playgroundX0+cellSize*13, app.playgroundY0+cellSize*4,
    #          cellSize*3, cellSize*3, fill='black', opacity=50)
    
    # drawRect(app.playgroundX0+cellSize*2, app.playgroundY0+cellSize*23,
    #          cellSize*3, cellSize*3, fill='black', opacity=50)
    
    # drawRect(app.playgroundX0+cellSize*13, app.playgroundY0+cellSize*23,
    #          cellSize*3, cellSize*3, fill='black', opacity=50)
    
    # drawRect(app.playgroundX0+cellSize*7, app.playgroundY0,
    #          cellSize*4, cellSize*4, fill='black', opacity=50)
    
    # drawRect(app.playgroundX0+cellSize*7, app.playgroundY0+cellSize*26,
    #          cellSize*4, cellSize*4, fill='black', opacity=50)
    

    # # The lake
    # drawRect(app.x0+app.w/2,app.h/2,app.w,2*cellSize,
    #          fill=rgb(0,233,200), border=None, align='center')

    
    
    # # The Bridges
    # drawRect(app.playgroundX0+cellSize*2.2, app.playgroundY0+cellSize*13.2,
    #          cellSize*2.7,cellSize*3.7, fill=rgb(224,186,108))
    
    # drawRect(app.playgroundX0+cellSize*13.2,
    #          app.playgroundY0+cellSize*13.2,cellSize*2.7,cellSize*3.7,
    #          fill=rgb(224,186,108))

    
    # # The Deck bg
    # drawRect(app.x1, 0, app.w*0.4, app.h, fill=rgb(141,107,79))
    # cardX = app.x1+app.w*0.05
    # cardY = app.h*0.03
    # for i in range(4):
    #     drawRect(cardX, cardY + app.h*0.2375*i, app.w*0.3, app.h*0.225,
    #             fill=rgb(84,59,40))


def drawArena(app):
    bg(app)


def drawxElixir(app):
    if app.x2Elixir:
        drawLabel("2x Elixir", app.x0+app.w/2, app.h/2, font='Supercell-Magic',
                  size=20, fill=rgb(201,31,206))
    else:
        drawLabel("3x Elixir", app.x0+app.w/2, app.h/2, font='Supercell-Magic',
                  size=20, fill=rgb(201,31,206))


def drawGameOver(app):
    drawRect(81, 0, 859, app.h, fill='grey', opacity=40)
    drawImage("Assets/cushionE.png", 510.5, app.h*0.3,
              align='center')
    drawImage("Assets/cushionP.png", 510.5, app.h*0.7,
              align='center')
    drawLabel("VS", 510.5, app.h*0.42, fill='gold', font='Supercell-Magic',
              size=20, border='black', borderWidth=0.5)
    if app.winner == "player":
        drawLabel("Winner!", 510.5, app.h*0.47, fill='gold',
                  font='Supercell-Magic', size=30, border='black',
                  borderWidth=0.5)
    elif app.winner == "enemy":
        drawLabel("Trainer Ryan!", 510.5, app.h*0.45, fill='gold',
                  font='Supercell-Magic', size=20, border='black',
                  borderWidth=0.5)
    elif app.winner == "draw":
        drawLabel("Draw", 510.5, app.h*0.45, fill='gold',
                  font='Supercell-Magic', size=20, border='black',
                  borderWidth=0.5)
    
    eCrowns = 0
    pCrowns = 0
    if app.playerTowers[2].alive == False:
        eCrowns = 3
    else:
        for i in app.playerTowers:
            if i.alive == False:
                eCrowns += 1

    if app.enemyTowers[2].alive == False:
        pCrowns = 3
    else:
        for i in app.enemyTowers:
            if i.alive == False:
                pCrowns += 1

    if eCrowns == 1:
        drawImage("Assets/rCrown.png", 390, 160, align="center")
    elif eCrowns == 2:
        drawImage("Assets/rCrown.png", 390, 160, align="center")
        drawImage("Assets/rCrown.png", 510.5, 150, align="center")
    elif eCrowns == 3:
        drawImage("Assets/rCrown.png", 390, 160, align="center")
        drawImage("Assets/rCrown.png", 510.5, 150, align="center")
        drawImage("Assets/rCrown.png", 631, 160, align="center")
 
    if pCrowns == 1:
        drawImage("Assets/bCrown.png", 395, 490, align="center")
    elif pCrowns == 2:
        drawImage("Assets/bCrown.png", 395, 490, align="center")
        drawImage("Assets/bCrown.png", 515, 460, align="center")
    elif pCrowns == 3:
        drawImage("Assets/bCrown.png", 395, 490, align="center")
        drawImage("Assets/bCrown.png", 515, 460, align="center")
        drawImage("Assets/bCrown.png", 631, 490, align="center")



    drawRect(510.5, 704, 128, 50, align='center', fill=rgb(27,112,218))
    drawLabel("OK", 510.5, 704, align='center', size=25, fill='white',
              font='Supercell-Magic', border='black', borderWidth=0.6)