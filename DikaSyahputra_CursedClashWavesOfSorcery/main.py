from cmu_graphics import *
import random
import math
from moves import *
from characters import *
from enemies import *
from PIL import Image as PilImage
import os
import pathlib

def openImage(fileName):
    return PilImage.open(os.path.join(pathlib.Path(__file__).parent, fileName))

############################################################
### HELPER FUNCTIONS ###
############################################################

# Resets the current global sound playing to either nothing or a new sound
def soundReset(app, sound=None, restart=False, loop=False):
    if app.currentSound != None: app.currentSound.pause()
    if sound != None:
        app.currentSound = sound
        app.currentSound.play(restart=restart, loop=loop)

# Resets all the displayable menus of the game
def menuReset(app):
    app.creditsMenu = False
    app.tutorialMenu = False
    app.charaSelection = False
    app.shopMenu = False
    app.playingGame = False
    app.mainMenu = False
    app.gameOver = False
    app.cutScene = False
    app.movesHelpMenu = False

# Randomizes 30 keys from 'A' to 'Z' for the domain clash mechanic
def randomizeClashKeys(app):
    txt = ""
    for i in range(30):
        txt += chr(random.randint(65, 90))
    return txt

# Clears the entities, moves, domains, and resets the player's state in-game
def resetGameState(app):
    app.deathTimer = -1
    PlayerDomains.playerDomains, EnemyDomains.enemyDomains,  = [], []
    Enemy.enemyList, PlayerMoves.playerMoves, EnemyMoves.enemyMoves = [], [], []
    Domains.domains, app.player.stun, app.player.performingMoveLen = [], 0, 0
    PlayerEntities.playerEntities, PlayerProjectiles.playerProjectiles = [], []
    EnemyProjectiles.enemyProjectiles = []

# Initializes the start of the game
def startGame(app):
    menuReset(app)
    # Selects the character the user will play
    if app.charaSelectIndex == 0: app.player = Yuta()
    if app.charaSelectIndex == 1: app.player = Gojo()
    if app.charaSelectIndex == 2: app.player = Inumaki()
    if app.charaSelectIndex == 3: app.player = Megumi()
    if app.charaSelectIndex == 4: app.player = Yuji()
    # Initializes the moves they have, their next move, current wave, and points
    app.unlockedMove = {1}
    app.nextMove = 2
    app.currentWave = 0
    app.points = 0
    # Sets the boundaries of view of the player with respect to the 2k by 2k map
    app.scrollX, app.scrollY = 400, 640
    resetGameState(app)
    # Generates enemies and unpauses the game incase it was paused
    generateEnemies(app)
    app.paused = False
    app.playingGame = True

# Randomly generate enemies based on the current wave
def generateEnemies(app):
    resetGameState(app)
    app.currentWave += 1
    # If the wave is not a "Boss Wave"
    if app.currentWave % 5 != 0:
        if app.currentWave % 9 == 0:
            for i in range(app.currentWave // 9):
                GradeOne()
                GradeTwo()
                GradeThree()
        elif app.currentWave % 3 == 0:
            for i in range(app.currentWave // 3):
                GradeTwo()
                GradeThree()
        else:
            for i in range((app.currentWave + 1) // 2): GradeThree()
    else:
        # Randomly spawns one of three bosses if it's a "Boss Wave"
        num = random.randint(1, 3)
        if num == 1: Mahito()
        if num == 2: Sukuna()
        if num == 3: Jogo()
    app.enemyList = Enemy.enemyList

# Resets the selected buttons in the main menu
def resetMainMenuButtons(app):
    app.playButton = False
    app.tutorialButton = False
    app.creditsButton = False

# Resets the selected buttons in the shop menu
def resetShopButtons(app):
    app.newMoveButton = False
    app.awakeningButton = False
    app.specialButton = False

# Draws the user interface in the shop menu
def drawShopMenu(app):
    drawImage(app.imagesPath + "shop.png", 0, 0, width=app.width,
              height=app.height)
    # Draws an opaque white rectangle over a selected button
    drawRect(app.width/2, 445 * 0.8, 350 * 0.8, 85 * 0.8, opacity=25,
             align='center', fill='white' if app.newMoveButton else None)
    drawRect(app.width/2, 560 * 0.8, 360 * 0.8, 85 * 0.8, opacity=25,
             align='center', fill='white' if app.awakeningButton else None)
    drawRect(app.width/2, 680 * 0.8, 650 * 0.8, 85 * 0.8, opacity=25,
             align='center', fill='white' if app.specialButton else None)
    drawLabel(f"Points Owned: {app.points}", app.width/2, 820 * 0.8, size=25)
    drawLabel("Kids, don't gamble...", app.width/2, 820 * 0.8 + 20, size=25)

# Draws the user interface in the main menu
def drawMainMenu(app):
    drawImage(app.imagesPath + "menu.png", 0, 0, width=app.width,
              height=app.height)
    # Draws an opaque white rectangle over a selected button
    drawRect(app.width/2, 530 * 0.8, 400 * 0.8, 85 * 0.8, opacity=25, align='center',
             fill='white' if app.playButton else None)
    drawRect(app.width/2, 665 * 0.8, 400 * 0.8, 85 * 0.8, opacity=25, align='center',
             fill='white' if app.tutorialButton else None)
    drawRect(app.width/2, 805 * 0.8, 400 * 0.8, 85 * 0.8, opacity=25, align='center',
             fill='white' if app.creditsButton else None)

# Draws the user interface in the character selection menu
def drawCharacterSelection(app):
    # Draws the current frame of the displayed character's splash art image
    img = CMUImage(openImage(app.charaSelectImages[app.charaSelectImgIndex]))
    drawImage(img, app.width/2, app.height/2, width=app.width,
              height=app.height, align='center')
    # Draws a frame surrounding the splash art
    drawImage(CMUImage(openImage('images/chara selection/' +\
                                 f'{app.charaSelectIndex}/frame.png')),
              app.width/2, app.height/2, width=app.width, height=app.height,
              align='center')

# Resets the character selection images based on the selected character's index
def resetCharaSelection(app):
    app.charaSelectCounter = 0
    app.charaSelectImages = [f'images/chara selection/' +\
                             f'{app.charaSelectIndex}/' +\
                             f'{i}.png' for i in range(120)]

# Draws the move selection UI at the bottom of the screen while playing the game
def drawMoveSelectionUI(app):
    # Writes [LOCKED] if the move has not been unlocked yet
    if app.player.awakeningLen <= 0:
        txt1 = app.player.moveNames[0] if 1 in app.unlockedMove else "[LOCKED]"
        txt2 = app.player.moveNames[1] if 2 in app.unlockedMove else "[LOCKED]"
        txt3 = app.player.moveNames[2] if 3 in app.unlockedMove else "[LOCKED]"
        txt4 = app.player.moveNames[3] if 4 in app.unlockedMove else "[LOCKED]"
    else:
        txt1 = app.player.moveNames[4] if 5 in app.unlockedMove else "[LOCKED]"
        txt2 = app.player.moveNames[5] if 6 in app.unlockedMove else "[LOCKED]"
        txt3 = app.player.moveNames[6] if 7 in app.unlockedMove else "[LOCKED]"
        txt4 = app.player.moveNames[7] if 8 in app.unlockedMove else "[LOCKED]"
    drawImage(CMUImage(openImage("images/moveUI.png")), 600,650, align='center')
    # Splits the labels into the 4 squares at the bottom of the screen
    drawLabel(txt1, 600 - (3 * 215 / 4) - 5, 650, fill='white')
    drawLabel(txt2, 600 - (1 * 215 / 4) - 2, 650, fill='white')
    drawLabel(txt3, 600 + (1 * 215 / 4) + 2, 650, fill='white')
    drawLabel(txt4, 600 + (3 * 215 / 4) + 5, 650, fill='white')

# Darkens the square respective to the move if it is on cooldown
def drawCooldownBar(app):
    # Gets the center x coordinate of each boxes to be passed on
    xCoords = [600 - (3 * 215 / 4) - 5, 600 - (1 * 215 / 4) - 2,
               600 + (1 * 215 / 4) + 2, 600 + (3 * 215 / 4) + 5]
    # Draws the normal move cooldown if not awakened and vice versa
    if app.player.awakeningLen <= 0: normalCooldownBar(app, xCoords)
    if app.player.awakeningLen > 0: awakeningCooldownBar(app, xCoords)

# Draws a dark opaque rectangle on a box respective to an unawakened move along
# with its cooldown in seconds
def normalCooldownBar(app, xCoords):
    if app.player.move1CD > 0:
        drawRect(xCoords[0], 650, 70, 70, opacity=75, align='center')
        drawLabel(app.player.move1CD//60, xCoords[0], 650, fill='white')
    if app.player.move2CD > 0:
        drawRect(xCoords[1], 650, 70, 70, opacity=75, align='center')
        drawLabel(app.player.move2CD//60, xCoords[1], 650, fill='white')
    if app.player.move3CD > 0:
        drawRect(xCoords[2], 650, 70, 70, opacity=75, align='center')
        drawLabel(app.player.move3CD//60, xCoords[2], 650, fill='white')
    if app.player.move4CD > 0:
        drawRect(xCoords[3], 650, 70, 70, opacity=75, align='center')
        drawLabel(app.player.move4CD//60, xCoords[3], 650, fill='white')

# Draws a dark opaque rectangle on a box respective to an awakened move along
# with its cooldown in seconds
def awakeningCooldownBar(app, xCoords):
    if app.player.move5CD > 0:
        drawRect(xCoords[0], 650, 70, 70, opacity=75, align='center')
        drawLabel(app.player.move5CD//60, xCoords[0], 650, fill='white')
    if app.player.move6CD > 0:
        drawRect(xCoords[1], 650, 70, 70, opacity=75, align='center')
        drawLabel(app.player.move6CD//60, xCoords[1], 650, fill='white')
    if app.player.move7CD > 0:
        drawRect(xCoords[2], 650, 70, 70, opacity=75, align='center')
        drawLabel(app.player.move7CD//60, xCoords[2], 650, fill='white')
    if app.player.move8CD > 0:
        drawRect(xCoords[3], 650, 70, 70, opacity=75, align='center')
        drawLabel(app.player.move8CD//60, xCoords[3], 650, fill='white')

# Draws the image for the domain clash if it is triggered
def drawDomainClash(app):
    drawImage(CMUImage(openImage("images/clash.png")), 0, 0)
    # Draws the keys that the user needs to press to win the domain clash
    drawLabel(app.domainClashKeys[0], app.width/2, app.height/2, size=40,
              fill='white')
    if app.domainClashLen > 0:
        # Draws a white rectangle timer to highlight the remaining time
        drawRect(250, 200-31, (app.domainClashLen/(17 * 60)) * 700, 44,
                 fill='white')

# Draws a game over popup if the user's hp fall below 0 inclusively
def drawGameOver(app):
    drawImage(CMUImage(openImage("images/gameover.png")), 0, 0)
    drawImage(app.player.deathImg, app.width/2, app.height/2, align='center')

# Draws a cutscene when the Divine General Mahoraga is summoned
def drawMahoragaCutscene(app):
    # Draws either the version where the special ability is unlocked or locked
    if app.player.specialUnlocked: img = app.mahoragaCutsceneSpecial
    else: img = app.mahoragaCutscene
    drawImage(img[app.mahoragaCutsceneIndex], 0, 0)

############################################################
### APP ###
############################################################

# Sets some important initializations as the app starts
def onAppStart(app):
    app.background = 'black'
    app.cutscene = False
    app.stepsPerSecond = 60
    
    # Sets the keys being held in a set for easy player animation change
    app.heldKeys = set()
    
    # Sets the global sounds that will be used for each menu and domains
    app.mainMenuSound = Sound("sounds/menu.mp3")
    app.charaSelectSound = [Sound("sounds/charaselect/" + str(i) + ".mp3") for\
                            i in range(5)]
    app.domainSounds = [Sound(f"sounds/domain{i}.mp3") for i in range(5)]
    app.shopSound = Sound("sounds/shop.mp3")
    app.battleSounds = [Sound(f"sounds/battle/{i}.mp3") for i in range(4)]
    
    # Initializes an empty enemyList for it to be aliased with Enemy.enemyList
    app.enemyList = []
    
    # Initializes the cutscene for when Divine General Mahoraga is summoned
    app.mahoragaCutscene = [CMUImage(openImage("images/mahocutscene/" +\
                                               f"{i}.png")) for i in range(11)]
    app.mahoragaCutsceneSpecial = [CMUImage(openImage("images/mahocutscene/" +\
                                               f"{i}.png")) for i in range(10)]
    app.mahoragaCutsceneTimer = 60
    app.mahoragaCutsceneIndex = 0
    app.mahoragaCutsceneLen = 0
    
    # Initializes variables for the movesHelp menu
    app.movesHelpImg = [CMUImage(openImage(f"images/moveHelp/{i}" +\
                                           ".png")) for i in range(6)]
    app.movesHelpIndex = 0
    
    # Initializes some map images and domain expansion images
    app.mapImages = [CMUImage(openImage("images/maps/map.png"))]
    app.domainImages = [CMUImage(openImage(f"images/maps/domain{i}.png"))
                        for i in range(5)]
    
    # Resets the global sound to play the mainMenu sound
    app.currentSound = None
    soundReset(app, app.mainMenuSound, False, True)
    
    # Initializes variables for the domain clash event and menu
    app.domainClashInit = False
    app.domainClashLen = 0
    app.domainClashKeys = ""
    
    # Initializes variables regarding the mouse position
    app.mouseAngle = 0
    app.mouseX = 0
    app.mouseY = 0
    
    # Initializes the events when playing the game
    app.paused = False
    app.gameOver = False
    app.deathTimer = -1
    
    # Initializes variables for the character selection menu
    app.charaSelectIndex = 0
    app.charaSelectImgIndex = 0
    app.charactersList = ["Yuta", "Gojo", "Inumaki", "Megumi", "Yuji"]
    app.imagesPath = "images/"
    resetCharaSelection(app)
    
    # Displays the main menu
    menuReset(app)
    app.mainMenu = True
    resetMainMenuButtons(app)

def redrawAll(app):
    # Draws the shop menu interface if user is in the shop
    if app.shopMenu:
        drawShopMenu(app)
    # Draws the credits menu interface if user is in the credits menu
    if app.creditsMenu:
        drawImage(CMUImage(openImage("images/credits.png")), 0, 0)
    # Draws the tutorial menu interface if user is in the tutorial
    if app.tutorialMenu:
        drawImage(f"images/tutorial/{app.tutorialImgIndex % 8}.png", 0, 0,
                  width=app.width, height=app.height)
    # Draws the moves help menu interface if user is in moves help
    if app.movesHelpMenu:
        drawImage(app.movesHelpImg[app.movesHelpIndex], 0, 0)
    # Draws the main menu interface if user is in the main menu
    if app.mainMenu:
        drawMainMenu(app)
    # Draws the character selection interface if user is selecting a character
    if app.charaSelection:
        drawCharacterSelection(app)
    if app.playingGame:
        # Draws the map if there are no domains casted
        if Domains.domains == []:
            drawImage(app.mapImages[0], 0 - app.scrollX, 0 - app.scrollY)
        else:
            Domains.domains[0].drawDomain(app)
        # Draws the move entities casted by the player and enemies
        for moves in PlayerMoves.playerMoves:
            moves.drawMove(app)
        for moves in EnemyMoves.enemyMoves:
            moves.drawMove(app)
        # Draws the ally entities casted by the player
        for entity in PlayerEntities.playerEntities:
            entity.drawEntity(app)
        # Draws the enemy only if they are in frame for efficiency
        for enemy in Enemy.enemyList:
            if -25 <= enemy.x - app.scrollX <= 1175 and\
               -25 <= enemy.y - app.scrollY <= 695: enemy.drawEnemy(app)
        # Draws the player
        app.player.drawPlayer(app)
        # Draws a timer in the middle indicating the death timer in seconds
        if app.deathTimer > 0:
            drawLabel(f"{app.deathTimer//60}", app.width/2, app.height/2,
                      fill='white', size=50)
        # Draws the Hollow Purple Nukes available on the map
        for nuke in HollowNuke.hollowNukes: nuke.drawNuke(app)
        # Draws the cutscene if there are any
        if app.cutscene: drawImage(app.cutsceneImg, 0, 0)
        # Draws the hp bar, energy bar, and awakening bar on the screen's UI
        # while playing the game
        if app.player.hp > 0:
            drawRect(132, 20, (app.player.hp/app.player.maxHp)*250, 30,
                 fill=gradient('green', 'chartreuse', start='left'))
        if app.player.energy > 0:
            drawRect(132, 51, (app.player.energy/app.player.maxEnergy)*250,
                     30, fill=gradient('blue', 'cyan', start='left'))
        # Turns red if the player is awakened
        if app.player.awakeningLen > 0:
            drawRect(470, 15, (app.player.awakeningLen/1800)*252, 25,
                     fill=gradient('maroon', 'red', start='left'))
        elif app.player.awakeningBar > 0:
            drawRect(470, 15,
                 (app.player.awakeningBar/app.player.maxAwakeningBar)*252,
                 25, fill=gradient('hotPink', 'pink', start='left'))
        # Highlights the cost of energy/hp a move will take
        app.player.drawHighlightBar(app)
        # Draws the image UI for the hp bar and awakening bar frames
        drawImage(CMUImage(openImage("images/hpbar.png")), -40, -50)
        drawImage(CMUImage(openImage("images/awakeningbar.png")), 300, -60)
        # Draws boxes on the bottom of the screen to indicate the moves, their
        # cooldowns, and whether or not they are selected
        drawMoveSelectionUI(app)
        drawCooldownBar(app)
        app.player.drawSelectedBox(app)
        drawLabel(f"Wave: {app.currentWave}", app.width/2, 70, size=35)
        drawLabel("Press Esc to pause", 1200, 2, size=20, align='right-top')
        # Draws the Mahoraga cutscene if its duration is above 0
        if app.mahoragaCutsceneLen > 0: drawMahoragaCutscene(app)
        # Draws the domain clash event if the keys are not an empty string
        if app.domainClashKeys != "":
            drawDomainClash(app)
        # Draws a pause menu when paused and a gameOver popup when game is over
        if app.paused:
            drawImage(CMUImage(openImage("images/pause.png")), 0, 0)
        if app.gameOver:
            drawGameOver(app)
    
def onStep(app):
    # Changes the frame of the GIF of a character's splash art in
    # character selection
    if app.charaSelection:
        app.charaSelectImgIndex = (app.charaSelectImgIndex + 1) %\
                                      len(app.charaSelectImages)
    # Reduces cutscene duration
    if app.cutscene:
        app.cutsceneLen -= 1
        if app.cutsceneLen == 0:
            app.cutscene = False
    
    if app.mahoragaCutsceneLen > 0:
        # Empties sound to create suspense
        soundReset(app)
        app.mahoragaCutsceneLen -= 1
        app.mahoragaCutsceneTimer -= 1
        # Changes the image infex of the cutscene every second
        if app.mahoragaCutsceneTimer == 0:
            app.mahoragaCutsceneTimer = 60
            app.mahoragaCutsceneIndex += 1
            # Stops if the index is 10 (the last image) and resets the index
            if app.mahoragaCutsceneIndex == 10:
                # Plays Mahoraga's theme if special ability is unlocked
                if app.player.specialUnlocked:
                    soundReset(app, Sound("sounds/mahotheme.mp3"), True, True)
                else:
                    Sound("sounds/mahohaha.mp3").play(restart=True)
            # Plays a windy sound every even index and a boom every odd index
            elif app.mahoragaCutsceneIndex % 2 == 0:
                Sound("sounds/mahowind.mp3").play(restart=True)
            elif app.mahoragaCutsceneIndex % 2 == 1:
                Sound("sounds/mahoboom.mp3").play(restart=True)
    
    if app.playingGame and not app.gameOver and not app.cutscene and\
       app.mahoragaCutsceneLen == 0 and not app.paused:
        # Increases/decreases the scroll based on the player's positions
        if app.player.y - app.scrollY >= 0.75 * app.height and\
           app.scrollY <= 2000 - 720:
            app.scrollY += 5
        if app.player.y - app.scrollY <= 0.25 * app.height and app.scrollY >= 0:
            app.scrollY -= 5
        if app.player.x - app.scrollX >= 0.75 * app.width and\
           app.scrollX <= 2000 - 1200:
            app.scrollX += 5
        if app.player.x - app.scrollX <= 0.25 * app.width and app.scrollX >= 0:
            app.scrollX -= 5
        
        # Reduces death timer and kills the player if it reaches 0
        if app.deathTimer > 0: app.deathTimer -= 1
        if app.deathTimer == 0: app.player.hp = 0
        
        # Triggers game over if the player's hp is under 0 inclusively
        if app.player.hp <= 0:
            app.gameOver = True
            # Pauses the Domain sounds incase if there are any
            if len(Domains.domains) >= 1:
                Domains.domains[0].sound.pause()
            soundReset(app, Sound("sounds/gameover.mp3"), True, True)
        
        # Makes the player in an idle state if the below keys are not held
        if not('w' in app.heldKeys or 'W' in app.heldKeys or\
               'a' in app.heldKeys or 'A' in app.heldKeys or\
               's' in app.heldKeys or 'S' in app.heldKeys or\
               'd' in app.heldKeys or 'D' in app.heldKeys or\
               'f' in app.heldKeys or 'F' in app.heldKeys):
            app.player.status = 'idle'
            app.player.isBlocking = False
        
        if len(Enemy.enemyList) == 0:
            # Increases the points if there are no enemies left
            app.points += app.currentWave * 3
            # Switches the menu to the shop menu and sound to the shop sound
            menuReset(app)
            app.shopMenu = True
            resetShopButtons(app)
            soundReset(app, app.shopSound, True, True)
            # Switches back to the original character if the death timer is
            # still above 0
            if app.deathTimer > 0:
                if app.charaSelectIndex == 0:
                    app.player = Yuta()
                    app.player.specialUnlocked = True
                if app.charaSelectIndex == 3:
                    app.player = Megumi()
                    app.player.specialUnlocked = True
                app.deathTimer = -1
            # Pauses the domain sound if there is any
            if Domains.domains != []:
                Domains.domains[0].sound.pause()
        
        # Initializes the conditions for a domain clash
        if app.domainClashInit:
            # Pauses both domain's sounds
            Domains.domains[0].sound.pause()
            Domains.domains[1].sound.pause()
            app.domainClashInit = False
            soundReset(app, Sound("sounds/clash.mp3"), True, False)
            # Generates the random keys and 17 seconds to press all keys
            app.domainClashKeys = randomizeClashKeys(app)
            app.domainClashLen = 17 * 60
    
        if app.domainClashLen == 0:
            # Triggers domain clash if there are more than 1 domain
            if len(Domains.domains) > 1: app.domainClashInit = True
            
            # Does the onStep for every domain casted
            for enemyDomain in EnemyDomains.enemyDomains[:]:
                enemyDomain.onStep(app)
            for playerDomain in PlayerDomains.playerDomains[:]:
                playerDomain.onStep(app, Enemy.enemyList)
            
            # Does the onStep for all moves the player casted
            for moves in PlayerMoves.playerMoves:
                moves.imgOnStep()
                # Only reduces the duration if windup is over
                if moves.windup > 0: moves.windup -= 1
                else:
                    moves.duration -= 1
                    # Checks collision on each enemy
                    for enemy in Enemy.enemyList[:]:
                        moves.collision(app.player, enemy, app)
                # Removes from the list of moves if its duration is over
                if moves.duration <= 0:
                    PlayerMoves.playerMoves.remove(moves)
            
            # Does the onStep for every projectiles casted
            for projectile in EnemyProjectiles.enemyProjectiles[:]:
                projectile.onStep(app)
            for projectile in PlayerProjectiles.playerProjectiles[:]:
                projectile.onStep(app)
            
            # Does the onStep for every Hollow Purple Nukes casted
            for nuke in HollowNuke.hollowNukes: nuke.onStep(app)
            
            # Does the onStep and behavior for every enemies
            for enemy in Enemy.enemyList[:]:
                enemy.onStep(app)
                enemy.enemyBehavior(app.player)
                # Removes from the enemyList if hp falls below 0
                if enemy.hp <= 0:
                    Enemy.enemyList.remove(enemy)
            
            # Does the onStep for all moves the player casted
            for moves in EnemyMoves.enemyMoves[:]:
                moves.imgOnStep()
                # Checks collision on the player
                moves.collision(app.player, app)
                # Removes from the list of moves if its duration is over
                if moves.duration == 0:
                    EnemyMoves.enemyMoves.remove(moves)
            
            # Does the onStep for all ally entities the player summoned
            for entity in PlayerEntities.playerEntities[:]:
                entity.autoMove(app, Enemy.enemyList)
                entity.cooldown()
            
            # Automatically moves the player if autoMove duration is up
            if app.player.autoMove > 0:
                app.player.autoMoveMouse(app, app.player.speed,
                                         app.player.movingMove)
            
            # Does the onStep for the player
            app.player.onStep()
        
        # Reduces the duration of domain clash
        elif app.domainClashLen > 0:
            app.domainClashLen -= 1
            # If the keys are empty, the user wins the clash and casts their
            # domain
            if app.domainClashKeys == "":
                Domains.domains.remove(EnemyDomains.enemyDomains.pop())
                app.domainClashLen = 0
                soundReset(app, Domains.domains[0].sound, True, False)
            # Else, they lose and the enemy casts their domain
            elif app.domainClashLen == 0:
                Domains.domains.remove(PlayerDomains.playerDomains.pop())
                app.domainClashKeys = ""
                soundReset(app, Domains.domains[0].sound, True, False)

def onKeyHold(app, keys):
    # Adds the key the user is holding to the heldKeys set
    for key in keys: app.heldKeys.add(key)
    if app.playingGame and not app.gameOver and not app.cutscene:
        # Allows the user to do these commands if the player isn't stunned,
        # performing an autoMove, or there are no domain clashes
        if app.player.stun == 0 and app.domainClashLen == 0 and\
           app.player.autoMove == 0 and not app.paused:
            # Allows the player to do movements if they are not blocking
            if not app.player.isBlocking:
                if 'w' in app.heldKeys or 'W' in app.heldKeys:
                    app.player.y -= 5
                    app.player.status = 'walk'
                if 's' in app.heldKeys or 'S' in app.heldKeys:
                    app.player.y += 5
                    app.player.status = 'walk'
                if 'd' in app.heldKeys or 'D' in app.heldKeys:
                    app.player.x += 5
                    app.player.status = 'walk'
                if 'a' in app.heldKeys or 'A' in app.heldKeys:
                    app.player.x -= 5
                    app.player.status = 'walk'
            # Makes the player block blockable attacks
            if 'f' in app.heldKeys or 'F' in app.heldKeys:
                app.player.isBlocking = True

# Remove a released key from the heldKeys if they are released
def onKeyRelease(app, key):
    if key in app.heldKeys: app.heldKeys.remove(key)

def onKeyPress(app, key):
    if app.creditsMenu:
        if key == 'escape':
            menuReset(app)
            app.mainMenu = True
    if app.movesHelpMenu:
        # Changes the index of the images in movesHelp, adding it by 1 for right
        # and subtracting it by 1 for left
        if key == 'right':
            app.movesHelpIndex = (app.movesHelpIndex + 1) %\
                                 len(app.movesHelpImg)
        if key == 'left':
            app.movesHelpIndex = (app.movesHelpIndex - 1) %\
                                 len(app.movesHelpImg)
        # Brings the user back to playing the game if they hit escape
        if key == 'escape':
            menuReset(app)
            app.playingGame = True
    
    if app.charaSelection:
        # Changes the index of the GIFs in character selection, adding it by 1
        # for right and subtracting it by 1 for left. Resets the sound.
        if key == 'right':
            app.charaSelectIndex = (app.charaSelectIndex + 1) % 5
            soundReset(app, app.charaSelectSound[app.charaSelectIndex], True,
                       True)
            resetCharaSelection(app)
        if key == 'left':
            app.charaSelectIndex = (app.charaSelectIndex + -1) % 5
            soundReset(app, app.charaSelectSound[app.charaSelectIndex], True,
                       True)
            resetCharaSelection(app)
        # Starts the game if the user presses enter
        if key == 'enter':
            startGame(app)
            # Plays a random battle soundtrack
            index = random.randint(0, 3)
            soundReset(app, app.battleSounds[index], True, True)
        # Brings users back to the main menu if they hit escape
        if key == 'escape':
            menuReset(app)
            app.mainMenu = True
            soundReset(app, app.mainMenuSound, True, True)
    
    if app.shopMenu:
        # Starts a new wave after every shop visit if they press enter
        if key == 'enter':
            resetGameState(app)
            generateEnemies(app)
            menuReset(app)
            app.playingGame = True
            index = random.randint(0, 3)
            soundReset(app, app.battleSounds[index], True, True)
        ### A HACK FOR POINTS ###
#         if key in 'pP':
#             app.points += 100
    
    if app.tutorialMenu:
        # Changes the image index in the tutorial menu
        if key == 'right': app.tutorialImgIndex += 1
        if key == 'left': app.tutorialImgIndex -= 1
        # Brings users back to the main menu if they hit escape
        if key == 'escape':
            menuReset(app)
            app.mainMenu = True
    
    if app.playingGame and not app.gameOver and not app.cutscene:
        ### A HACK TO INSTANTLY KILL ENEMIES ###
#         if key == '-':
#             Enemy.enemyList = []
        # Allows users to select a move if the player is not stunned, the game
        # isn't paused, and no domain clashes are triggered
        if app.player.stun == 0 and app.domainClashLen == 0 and not app.paused:
            if '1' in key:
                # Users can take back their choice by pressing the same key
                if app.player.choosingMove == 1 or app.player.choosingMove == 5:
                    app.player.choosingMove = None
                # Users choose move 1 if unlocked and unawakened
                elif app.player.awakeningLen <= 0 and\
                     app.player.move1CD == 0 and 1 in app.unlockedMove:
                    app.player.choosingMove = 1
                # Users choose move 5 if unlocked and awakened
                elif app.player.awakeningLen > 0 and\
                     app.player.move5CD == 0 and 5 in app.unlockedMove:
                    app.player.choosingMove = 5
            if '2' in key:
                # Users can take back their choice by pressing the same key
                if app.player.choosingMove == 2 or app.player.choosingMove == 6:
                    app.player.choosingMove = None
                # Users choose move 2 if unlocked and unawakened
                elif app.player.awakeningLen <= 0 and\
                     app.player.move2CD == 0 and 2 in app.unlockedMove:
                    app.player.choosingMove = 2
                # Users choose move 6 if unlocked and awakened
                elif app.player.awakeningLen > 0 and\
                     app.player.move6CD == 0 and 6 in app.unlockedMove:
                    app.player.choosingMove = 6
            if '3' in key:
                # Users can take back their choice by pressing the same key
                if app.player.choosingMove == 3 or app.player.choosingMove == 7:
                    app.player.choosingMove = None
                # Users choose move 3 if unlocked and unawakened
                elif app.player.awakeningLen <= 0 and\
                     app.player.move3CD == 0 and 3 in app.unlockedMove:
                    app.player.choosingMove = 3
                # Users choose move 7 if unlocked and awakened
                elif app.player.awakeningLen > 0 and\
                     app.player.move7CD == 0 and 7 in app.unlockedMove:
                    app.player.choosingMove = 7
            if '4' in key:
                # Users can take back their choice by pressing the same key
                if app.player.choosingMove == 4 or app.player.choosingMove == 8:
                    app.player.choosingMove = None
                # Users choose move 4 if unlocked and unawakened
                elif app.player.awakeningLen <= 0 and\
                     app.player.move4CD == 0 and 4 in app.unlockedMove:
                    app.player.choosingMove = 4
                # Users choose move 8 if unlocked and awakened
                elif app.player.awakeningLen > 0 and\
                     app.player.move8CD == 0 and 8 in app.unlockedMove:
                    app.player.choosingMove = 8
            # Users can trigger the player's awakening if they press G and the
            # player's awakeningBar is at its max
            if key in 'gG' and 'awakening' in app.unlockedMove and\
               app.player.awakeningBar == app.player.maxAwakeningBar:
                app.player.awaken(app)
            # A HACK FOR GETTING AWAKENING BAR
#             if '=' == key:
#                 app.player.awakeningBar += 5000
        elif app.domainClashKeys != "":
            # If user presses keys corresponding to the zero-th index of domain
            # clash keys, slice the list starting from the first index
            if key.upper() == app.domainClashKeys[0]:
                app.domainClashKeys = app.domainClashKeys[1:]
        # Pauses the game
        if key == 'escape':
            app.paused = not app.paused

def onMousePress(app, mouseX, mouseY):
    if app.mainMenu:
        # Brings them to character selection menu if playButton is selected
        if app.playButton:
            menuReset(app)
            app.charaSelection = True
            app.charaSelectIndex = 0
            resetCharaSelection(app)
            soundReset(app, app.charaSelectSound[0], True, True)
        # Brings them to tutorial menu if playButton is selected
        if app.tutorialButton:
            menuReset(app)
            app.tutorialMenu = True
            app.tutorialImgIndex = 0
        # Brings them to credits menu if playButton is selected
        if app.creditsButton:
            menuReset(app)
            app.creditsMenu = True
    
    if app.shopMenu:
        # Adds a new move to the player if newMoveButton is selected
        if app.newMoveButton and app.points >= 5 and 8 not in app.unlockedMove:
            if random.randint(1, 100) <= 85:
                app.unlockedMove.add(app.nextMove)
                app.nextMove += 1
                Sound("sounds/success.mp3").play(restart=True)
            else:
                Sound("sounds/fail.mp3").play(restart=True)
            app.points -= 5
        # Adds awakening skill to the player if awakeningButton is selected
        if app.awakeningButton and app.points >= 8:
            if 'awakening' in app.unlockedMove:
                print("He stole your money")
                Sound("sounds/mahohaha.mp3").play(restart=True)
            elif random.randint(1, 100) <= 50:
                Sound("sounds/success.mp3").play(restart=True)
                app.unlockedMove.add('awakening')
            else:
                Sound("sounds/fail.mp3").play(restart=True)
            app.points -= 8
        # Adds special ability to the player if specialButton is selected
        if app.specialButton and app.points >= 10:
            if app.player.specialUnlocked:
                print("He stole your money")
                Sound("sounds/mahohaha.mp3").play(restart=True)
            elif random.randint(1, 100) <= 40:
                Sound("sounds/success.mp3").play(restart=True)
                app.player.specialMove()
            else:
                Sound("sounds/fail.mp3").play(restart=True)
            app.points -= 10
    
    # Only triggers when the user is playing the game, the game isn't over, and
    # there's no cutscenes
    if app.playingGame and not app.gameOver and not app.cutscene:
        # Triggers the move corresponding to the user's choice if the user click
        # and the player is not stunned and it is not paused
        if app.player.stun == 0 and not app.paused:
            if app.player.choosingMove == None:
                app.player.mouse1(app)
            if app.player.choosingMove == 1:
                app.player.move1(app)
            if app.player.choosingMove == 2:
                app.player.move2(app)
            if app.player.choosingMove == 3:
                app.player.move3(app)
            if app.player.choosingMove == 4:
                app.player.move4(app)
            if app.player.choosingMove == 5:
                app.player.move5(app)
            if app.player.choosingMove == 6:
                app.player.move6(app)
            if app.player.choosingMove == 7:
                app.player.move7(app)
            if app.player.choosingMove == 8:
                app.player.move8(app)
        if app.paused:
            # If the mouseX and mouseY lie in these coordinates, unpause
            if 600 - (170/2) <= mouseX <= 600 + (170/2) and\
               277 - 30 <= mouseY <= 277 + 30:
                app.paused = False
            # If the mouseX and mouseY lie in these coordinates, brings user to
            # moves help menu
            if 600 - (242/2) <= mouseX <= 600 + (242/2) and\
               406 - (61/2) <= mouseY <= 406 + (61/2):
                menuReset(app)
                app.movesHelpMenu = True
            # If the mouseX and mouseY lie in these coordinates, brings user to
            # main menu
            if 600 - (236/2) <= mouseX <= 600 + (236/2) and\
               536 - (59/2) <= mouseY <= 536 + (59/2):
                menuReset(app)
                app.mainMenu = True
                soundReset(app, app.mainMenuSound, True, True)
                
    if app.gameOver:
        # If the mouseX and mouseY lie in these coordinates, brings user to main
        # menu
        if 393 - (415/2) <= mouseX <= 393 + (415/2) and\
           490 - (161/2) <= mouseY <= 490 + (161/2):
            menuReset(app)
            app.mainMenu = True
            soundReset(app, app.mainMenuSound, True, True)
            app.charaSelectIndex = 0
        # If the mouseX and mouseY lie in these coordinates, restarts the game
        # with the same character
        if 829 - (364/2) <= mouseX <= 829 + (364/2) and\
           493 - (149/2) <= mouseY <= 493 + (149/2):
            startGame(app)
            soundReset(app, app.battleSounds[random.randint(0, 3)], True, True)

def onMouseMove(app, mouseX, mouseY):
    if app.mainMenu:
        # If the mouseX lie in these coordinates,
        if app.width/2 - 200 * 0.8 < mouseX < app.width/2 + 200 * 0.8:
            # If the mouseY lie in these coordinates, highlight playButton
            if 530 * 0.8 - (85 * 0.8 / 2) < mouseY < 530 * 0.8 + (85 * 0.8 / 2):
                resetMainMenuButtons(app)
                app.playButton = True
            # If the mouseY lie in these coordinates, highlight tutorialButton
            elif 665 * 0.8 - (85 * 0.8 / 2) < mouseY < 665 * 0.8 + (85 * 0.8/2):
                resetMainMenuButtons(app)
                app.tutorialButton = True
            # If the mouseY lie in these coordinates, highlight creditsButton
            elif 805 * 0.8 - (85 * 0.8 / 2) < mouseY < 805 * 0.8 + (85 * 0.8/2):
                resetMainMenuButtons(app)
                app.creditsButton = True
            # Else, unhighlight all buttons
            else:
                resetMainMenuButtons(app)
        else:
            resetMainMenuButtons(app)
    
    if app.shopMenu:
        # If the mouseY lie in these coordinates, highlight newMoveButton
        if app.width/2 - 175 * 0.8 < mouseX < app.width/2 + 175 * 0.8 and\
           445 * 0.8 - (85 * 0.8 / 2) < mouseY < 445 * 0.8 + (85 * 0.8 / 2):
            resetShopButtons(app)
            app.newMoveButton = True
        # If the mouseY lie in these coordinates, highlight awakeningButton
        elif app.width/2 - 180 * 0.8 < mouseX < app.width/2 + 180 * 0.8 and\
             560 * 0.8 - (85 * 0.8 / 2) < mouseY < 560 * 0.8 + (85 * 0.8 / 2):
            resetShopButtons(app)
            app.awakeningButton = True
        # If the mouseY lie in these coordinates, highlight specialButton
        elif app.width/2 - 325 * 0.8 < mouseX < app.width/2 + 325 * 0.8 and\
             680 * 0.8 - (85 * 0.8 / 2) < mouseY < 680 * 0.8 + (85 * 0.8 / 2):
            resetShopButtons(app)
            app.specialButton = True
        # Else, unhighlight all buttons
        else:
            resetShopButtons(app)
    
    if app.playingGame and not app.cutscene and not app.gameOver:
        # Changes the player's facing according to the mouse's direction
        if app.mouseX >= app.player.x - app.scrollX:
            app.player.facing, app.player.facingIndex = 'right', 1
        else:
            app.player.facing, app.player.facingIndex = 'left', 0
        # Notes the coordinates and angle of the mouse with respect to player
        app.mouseX = mouseX
        app.mouseY = mouseY
        xDist = mouseX - app.player.x
        yDist = mouseY - app.player.y
        app.mouseAngle = (math.atan2(yDist, xDist) * (-180 / math.pi)) % 360

runApp(width=1200, height=720)