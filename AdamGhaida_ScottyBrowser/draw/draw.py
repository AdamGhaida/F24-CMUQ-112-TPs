from backend import *
from cmu_graphics import *
import threading
import queue
import os 
from PIL import Image
from . import drawUtils
    
def onAppStart(app):
    # easter egg stuff
    scottyPhoto = Image.open("draw/asset/scottyEasterEgg.jpg").resize((150,150))
    app.scottyEasterEggImage = CMUImage(scottyPhoto)
    app.barkSound = Sound("asset/scottyBark.mp3")


    # colors! 
    app.cmuRed = rgb(196,18,48)
    app.cmuDarkGrey = rgb(109, 110, 113)
    app.cmuSkiboRed = rgb(149, 17, 32)
    app.cmuGreen = rgb(31, 76, 76)

    # we want to speed up CMU_graphics a bit since we're going to 
    # be pushing it to it's limits
    app.stepCounter=0
    app.stepsPerSecond = 60

    #properties for the selenium render on CMU-graphics
    app.webPageXStart = (300/1710)*app.width
    app.webPageYStart = 10

    # Web interaction daemon
    app.webDaemon = webClass(app.width-app.webPageXStart-10,app.height-20)
    app.webDaemon.updateWindowSize(app.width-app.webPageXStart-10,
                                   app.height-20)

    # Tab manager daemon
    app.tabDaemon = tabsClass()

    # -1 is the index stored if and only if there is no currently focused tab.
    #   i.e. the user is on the home page
    app.focusedTabIndex = -1

    # nice home page i found
    app.homePage = "chrome://extensions"
    app.webPage = app.homePage
    app.loadedTabs = app.tabDaemon.parseTabs()


    #Waits until the page is done loading
    app.webDaemon.initPage(app.webPage)

    app.currentImage = CMUImage(app.webDaemon.updatePage())

    app.previousWidth = app.width
    app.previousHeight = app.height

    app.screenshotQueue = queue.Queue()
    
    app.isScreenshotReady = False
    app.previousScreenshotPath = "./backend/screenshots/previousWebPage.png"

    # Various properties and variables made for the new-tab button 
    app.textBoxWord = ""  
    app.textBoxInFocus = False 
    app.textBoxX = 100  
    app.textBoxY = 150  
    app.textBoxWidth = 300  
    app.textBoxHeight = 40  
    app.cursorPosition = len(app.textBoxWord) 
    app.cursorBlink = True

    # for tab closure functionality
    app.hoveredTab = None

    # just to modularize our code and clean up the code base, we have 
    #   an external class storing all of the complicated drawing.
    app.drawUtils = drawUtils.drawUtils()

    # A nice software boot sound i sourced from copyright-free sources
    app.bootSound = Sound('asset/bootSound.mp3')
    app.bootSound.play(restart=True, loop=False)

def redrawAll(app):
    drawRect(0,0,app.width,app.height,fill=app.cmuRed)
    drawLabel("ScottyBrowser",app.webPageXStart/2,20,size=14)
    
    drawImage(app.currentImage, app.webPageXStart, app.webPageYStart)

    app.drawUtils.drawBrowserNavButtons(color=app.cmuSkiboRed)
    
    app.drawUtils.drawRoundedRect(10,80,app.webPageXStart-20,30,
                                  10,app.cmuSkiboRed)
    drawLabel("New Tab +",((app.webPageXStart)/2),95)

    drawLine(10,120,148,120, fill=app.cmuDarkGrey)

    count = 0

    for tabGroup in app.loadedTabs['tabs']:
        tabName = tabGroup['name']
        if len(tabName)>19:
            tabName = tabName[:15]+"..."

        app.drawUtils.drawRoundedRect(10,count*50+130,app.webPageXStart-20,
                                      30,10,app.cmuGreen)
        drawLabel(tabName,((app.webPageXStart)/2),count*50+145)
        
        
        if count == app.hoveredTab:
            drawCircle(10+app.webPageXStart-20, count*50+130,5,fill='white')
            drawLabel("x",10+app.webPageXStart-20, count*50+130,size=14)
        
        count+=1

    if app.textBoxInFocus:
        drawImage(app.scottyEasterEggImage, 0,app.height-150,rotateAngle=45)

        drawRect(0,0,app.width,app.height,fill="black",opacity=50)

        app.drawUtils.drawRoundedRect(app.width/9,app.height/5,7*(app.width)/9,
                                      app.height/5,
                        app.height/15,app.cmuRed)

        app.drawUtils.drawRoundedRect(app.width/9+10,app.height/5+10,
                                      7*(app.width)/9-20,
                        app.height/5-20,app.height/22,"white")
        
        # Search or Internet Buttons:

        drawCircle(8/9 * app.width, app.height/5,10,fill='white')

        drawLabel("x",8/9 * app.width, app.height/5,size=16)

        
        drawCircle(14/18 * app.width, (3/2)*app.height/5,
                   min(app.height,app.width)/25,fill='silver')

        drawLabel("G",14/18 * app.width, (3/2)*app.height/5,size=16)
        
        drawCircle(15/18 * app.width, (3/2)*app.height/5,
                   min(app.height,app.width)/25,fill='silver')

        drawLabel("WWW",15/18 * app.width, (3/2)*app.height/5,size=12)


        
        
        # in some circumstances when the text exceeds the available space, 
        #   we need to account for that by adding ellipses to the front
        maxVisibleLength = int((13/18*app.width-(app.width/9+20))//12)-3 

        if app.width/9+20+12*len(app.textBoxWord)>13/18*app.width:
             
            visibleSegment = app.textBoxWord[-maxVisibleLength:]  
            drawLabel("..." + visibleSegment, app.width / 9 + 20,
                    (2 * (app.height / 5 + 10) + app.height / 5 - 20) / 2,
                    size=20, font='monospace', align='left')
        else:
            drawLabel(app.textBoxWord, app.width/9+20, 
                (2*(app.height/5+10)+app.height/5-20)/2, size=20, 
                font='monospace', align='left')

        # also, we also want to draw the blinking cursor, 
        #   which is controlled inside of onStep(). also, we make 
        #   sure that it does not overflow from the text box.
        if app.cursorBlink:  
            if app.width/9+20 + 12*len(app.textBoxWord) < 13/18 * app.width:
                cursorX = app.width/9+20 + 12*len(app.textBoxWord)
            else:
                cursorX = app.width/9+20 + 12*(maxVisibleLength+3)
            
            cursorY = (2*(app.height/5+10)+app.height/5-20)/2
            drawLine(cursorX, cursorY-10, cursorX, cursorY + 10, lineWidth=2)
        
    
def onMouseMove(app, mouseX, mouseY):
    # reset the hovered tab so we don't need to turn it 
    #   off if the mouse leaves the tab
    app.hoveredTab = None  

    # loop through all tabs and check if the mouse is inside that tab bar
    count = 0
    for tabIndex in range(len(app.loadedTabs['tabs'])):
        x = 10
        y = count * 50 + 130
        width = app.webPageXStart - 10
        height = 30
        if x <= mouseX <= x + width and y-10 <= mouseY <= y + height:
            app.hoveredTab = tabIndex
            break
        count += 1

def onResize(app):

    app.webDaemon.updateWindowSize(app.width-app.webPageXStart-10,
                                   app.height-20)
    # Update previous dimensions
    app.previousWidth = app.width
    app.previousHeight = app.height

def onStep(app):
    loadedTabs = app.loadedTabs['tabs']

    if app.focusedTabIndex != -1 and \
        app.webDaemon.currentPageDifferent(loadedTabs[app.focusedTabIndex]):
        
        app.tabDaemon.updateTab(app.focusedTabIndex, 
                                app.webDaemon.getPageInfo())
        
        app.loadedTabs = app.tabDaemon.parseTabs()
        

    if not app.textBoxInFocus:
        app.currentImage = CMUImage(app.webDaemon.updatePage())
    

    if app.stepCounter % (app.stepsPerSecond // 2) == 0:
        
        app.cursorBlink = not app.cursorBlink
    
    app.stepCounter+=1
        
def onKeyPress(app, key):
    if not app.textBoxInFocus:
        app.webDaemon.typeInSearchField(key)
        return 
    
    
    if key == 'backspace':  # Handle backspace
        app.textBoxWord = app.textBoxWord[:-1]
        app.cursorPosition = len(app.textBoxWord)  

    elif key == "space":
        app.textBoxWord += " "
        app.cursorPosition = len(app.textBoxWord)  

    elif key == 'enter': 
        query = app.textBoxWord.replace(" ","+")
        app.webDaemon.initPage(f"https://www.google.com/search?q={query}")
        
        pageInfo = app.webDaemon.getPageInfo()
        app.tabDaemon.addTab(pageInfo)
        app.loadedTabs = app.tabDaemon.parseTabs()
        app.textBoxInFocus = False
        app.focusedTabIndex = len(app.loadedTabs)-1

    else:
        app.textBoxWord += key  
        app.cursorPosition = len(app.textBoxWord)  

        
def onMousePress(app,x,y):
    # selenium click. Since it's really intensive to process, we dont 
    #   process anything afterwards.
    if not app.textBoxInFocus and app.webPageXStart<x<app.width-10 \
        and 0<y<app.height-10:
        app.webDaemon.click(x-app.webPageXStart,y-10)
        return
    
    # Browser Nav (These are all constants since the browser's left 
    #   bar is always a fixed length)
    if 10<=x<=40 and 15<=y<=65:
        app.webDaemon.tabBackward()
    elif 64<=x<=94 and 15<=y<=65:
        app.webDaemon.tabForward()
    elif 118<=x<=148 and 15<=y<=65:
        app.webDaemon.refresh()


    count = 0
    for index, tabGroup in enumerate(app.loadedTabs['tabs']):

        boxX = 10
        boxY = count * 50 + 125
        width = app.webPageXStart - 20
        height = 30
        
        # check if the mouse click is within the bounds of a tab
        if boxX <= x <= boxX + width and boxY <= y <= boxY + height:
            app.webPage = tabGroup['url']
            app.webDaemon.initPage(app.webPage)

            app.focusedTabIndex = index
            return
        
        count += 1
    
    # New tab button logic
    if 10 <= x <= app.webPageXStart-20 and 80 <= y <= 110:
        #
        app.textBoxWord = ""
        app.textBoxInFocus = True
    
    # we need to be able to remove tabs as well, and that's done here
    if app.hoveredTab!=None and \
          5+app.webPageXStart-20<=x<=15+app.webPageXStart-20 and \
          app.hoveredTab*50+125<=y<=app.hoveredTab*50+135:
        
        app.tabDaemon.removeTab(app.hoveredTab)
        app.loadedTabs = app.tabDaemon.parseTabs()

        if app.hoveredTab == app.focusedTabIndex:
            app.focusedTabIndex = -1
            app.webDaemon.initPage(app.homePage)

        elif app.focusedTabIndex > app.hoveredTab:
            app.focusedTabIndex-=1
        
        return
    
    # All the functionality for the new tab interface
    if app.textBoxInFocus:
        # closing the new tab incase the user changes their mind.
        if app.drawUtils.circularDistance((x,y),
                                          (8/9 * app.width,app.height/5)) <= 10:
            app.textBoxInFocus = False 
            return
        
        # this is variable and resizable
        searchCircleRad = min(app.height,app.width)/25

        # if it's inside of the google search icon, then we click search (obv)
        if app.drawUtils.circularDistance((x,y),(14/18 * app.width, 
                                   (3/2)*app.height/5)) <= searchCircleRad:
            query=app.textBoxWord.replace(" ","+")
            app.webDaemon.initPage(f"https://www.google.com/search?q={query}")
            pageInfo = app.webDaemon.getPageInfo()
            app.tabDaemon.addTab(pageInfo)
            app.loadedTabs = app.tabDaemon.parseTabs()
            app.textBoxInFocus = False
            app.focusedTabIndex = len(app.loadedTabs)-1
            return

        # if it's inside of the web search icon, then we click search (obv)
        if app.drawUtils.circularDistance((x,y),(15/18 * app.width, 
                                   (3/2)*app.height/5)) <= searchCircleRad:
            # We want to make sure that the web page exists and has 
            #   details instead of crashing
            try:
                app.webDaemon.initPage(f"https://{app.textBoxWord}")
                pageInfo = app.webDaemon.getPageInfo()
                app.tabDaemon.addTab(pageInfo)
                app.loadedTabs = app.tabDaemon.parseTabs()
                app.textBoxInFocus = False
            except:
                errorDict = {
                    "name": "404! here's scotty instead",
                    "url": "https://www.cmu.edu/brand/",

                }
                
                app.tabDaemon.addTab(errorDict)
                app.loadedTabs = app.tabDaemon.parseTabs()
                app.textBoxInFocus = False
            
            app.focusedTabIndex = len(app.loadedTabs)-1
            return
        
        if 50<=x<=150 and app.height-150<=y:
            app.barkSound.play(restart=False,loop=False)






runApp(width=900,height=485)