#################################################
# app.py
#
# Your name: Enkhmunkh Enkhbayar
# Your andrew id: eenkhbay
#################################################

#################################################
#                                               #
#               Graphics Functions              #
#                                               #
#################################################

import math
import time
import json
import random as rand

from cmu_graphics import *
from classes import *
from utils import *
from interactions import *


WIDTH, HEIGHT = 800, 800
MAXRES = max(WIDTH, HEIGHT)

# Color of the blocks
colors = [
    "black",
    "darkBlue",
    "darkGreen",
    "darkCyan",
    "darkRed",
    "indigo",
    "goldenrod",
    "lightGray",
    "darkGray",
    "blue",
]

# Notes to show on start screen
notes = [
    "./assets/start_labels/shakeItOff.png",
    "./assets/start_labels/cursedClash.png",
    "./assets/start_labels/notSoSuperMario.png",
    "./assets/start_labels/hue.png",
    "./assets/start_labels/slay.png",
    "./assets/start_labels/balleywag.png",
    "./assets/start_labels/2012memes.png",
    "./assets/start_labels/return42.png",
    "./assets/start_labels/defbob.png",
    "./assets/start_labels/bingqilin.png",
]


def onAppStart(app):
    app.setMaxShapeCount(100000)
    app.RES = app.WIDTH, app.HEIGHT = WIDTH, HEIGHT

    # Menu and Start
    app.mouseX = 0
    app.mouseY = 0
    app.selectedWorld = 0
    app.selectedNote = rand.randint(0, len(notes) - 1)

    # Main Game sounds
    app.deleteSound = Sound("./assets/sounds/break.mp3")
    app.placeSound = Sound("./assets/sounds/place.mp3")
    app.clickSound = Sound("./assets/sounds/click.mp3")
    app.backgroundSound = Sound("./assets/sounds/sweden.mp3")
    app.backgroundSound.play(restart=True, loop=True)


# Main Screen


def start_redrawAll(app):
    drawImage("./assets/main.png", 0, 0)
    drawImage(notes[app.selectedNote], 528.62, 92.45)
    drawButton(app, "Play", 175, 55, WIDTH / 2, 520)


# Following function draws a button when called
def drawButton(app, label, width, height, x, y, size=32):
    drawRect(x, y, width, height, align="center", fill=rgb(204, 204, 204))
    drawRect(x + 1, y + 1, width - 2, height - 2, align="center", fill=rgb(87, 87, 87))
    if checkMouseHoveringButton(app.mouseX, app.mouseY, x, y, width, height):
        drawRect(x, y, width - 2, height - 2, align="center", fill=rgb(87, 87, 87))
    else:
        drawRect(x, y, width - 2, height - 2, align="center", fill=rgb(111, 111, 111))
    drawLabel(label, x, y, size=size, fill="white", font="monospace", bold=True)


# Menu Screen


# Gets worlds that are created from the main.json file
def menu_onScreenActivate(app):
    with open("main.json", "r") as file:
        app.worlds = json.load(file)


# Draws the designs of the menu page with interactive buttons and
# world selection
def menu_redrawAll(app):
    drawImage("./assets/menu.png", 0, 0)
    drawLabel("Worlds:", WIDTH / 2, 100)
    for worldIndex in range(len(app.worlds)):
        offsetY = (
            25 * worldIndex
            + 100 * worldIndex
            - (125 * (app.selectedWorld - 2) if app.selectedWorld > 2 else 0)
        )
        drawRect(
            50,
            250 + offsetY,
            700,
            100,
            border="white" if worldIndex == app.selectedWorld else None,
            borderWidth=2,
            fill=None,
        )
        drawLabel(
            app.worlds[worldIndex]["name"],
            70,
            280 + offsetY,
            fill="white",
            align="left",
            bold=True,
            size=24,
            font="monospace",
        )
        drawLabel(
            "Last saved: " + app.worlds[worldIndex]["updatedAt"],
            70,
            320 + offsetY,
            fill=rgb(184, 182, 181),
            align="left",
            size=24,
            bold=True,
            font="monospace",
        )
    drawImage("./assets/menuTop.png", 0, 0)
    drawImage("./assets/menuBottom.png", 0, 695)
    drawButton(app, "Create New World", 275, 55, 187.5, 747.5, 24)
    drawButton(app, "Delete", 105, 55, 387.5, 747.5, 24)
    drawButton(app, "Play Selected World", 300, 55, 600, 747.5, 24)


# The following initialized the basic game variables that is required
# to run the game
def initializeGame(app):
    app.camera = Camera((0, 0, 0), [], (0, math.pi / 2, 0))
    app.dragStartingPosition = None
    app.world = World()
    app.selectedBlockPosition = None
    app.selectedBlockFace = None

    app.stepsPerSecond = 60
    app.startTime = time.perf_counter()
    app.frameCount = 0
    app.fps = 0

    app.planesToShow = []
    app.planePointsOnScreen = []

    app.colors = colors
    app.selectedColorIndex = 0


# The following function, checks if mouse click is on a button and runs
# the functions accordingly on Menu Screen
def menu_onMousePress(app, mouseX, mouseY, label):
    if 50 < mouseX < 325 and 720 < mouseY < 775:
        app.clickSound.play(restart=True)
        createWorld(app)
    if 335 < mouseX < 440 and 720 < mouseY < 775:
        if len(app.worlds) > app.selectedWorld:
            app.clickSound.play(restart=True)
            deleteWorld(app.worlds[app.selectedWorld]["name"])
    if 450 < mouseX < 750 and 720 < mouseY < 775:
        if len(app.worlds) > app.selectedWorld:
            app.clickSound.play(restart=True)
            initializeGame(app)
            loadWorld(app, app.worlds[app.selectedWorld]["name"])
            setActiveScreen("game")


# Game Screen


# Draws plane when given points and if the plane is selected by user
# it highlights it
def drawPlane(plane, selected, color):
    drawPolygon(
        *plane,
        fill=color,
        border="red" if selected == True else "black",
        borderWidth=2 if selected == True else 0.4,
    )


# Draws inventory in game where user can select any of the blocks
# and start building
def drawInventory(app):
    startingX = (WIDTH - len(colors) * 24) / 2
    startingY = HEIGHT - 24
    for i in range(len(colors)):
        drawRect(
            startingX + i * 24,
            startingY,
            24,
            24,
            fill=colors[i],
            border="white" if app.selectedColorIndex != i else "grey",
        )


# After getting all the plane points on screen, it draws the planes
# And draws the user interface
def game_redrawAll(app):
    for plane in app.planePointsOnScreen:
        drawPlane(plane[0], plane[1], plane[2])

    # Draws center pointer
    drawRect(WIDTH / 2, HEIGHT / 2, 2, 8, align="center", fill="black")
    drawRect(WIDTH / 2, HEIGHT / 2, 8, 2, align="center", fill="black")
    drawLabel(f"{app.fps} FPS", 5, 5, fill="black", align="left-top")

    drawInventory(app)


# Game onStep updates the planes to show, finds the selected block, and
# checks fps
def game_onStep(app):
    updatePlanesToShow(app)
    findSelectedBlockPosition(app)

    # Calculate and display FPS every second
    app.frameCount += 1
    currentTime = time.perf_counter()
    elapsedTime = currentTime - app.startTime
    if elapsedTime > 1.0:
        app.fps = math.ceil(app.frameCount / elapsedTime)
        app.startTime = currentTime
        app.frameCount = 0


def main():
    runAppWithScreens(initialScreen="start", width=WIDTH, height=HEIGHT)


main()
