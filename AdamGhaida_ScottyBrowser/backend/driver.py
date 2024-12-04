import os
from selenium import webdriver
from PIL import Image
import io 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class webClass:

    def __init__(self,width,height):
        self.width = width
        self.height = height
        
        # When selenium runs chrome in headless mode, 
        #   139 pixels of window size are the top bar 
        self.chromeTopBarHeight = 139

        self.seleniumOptionsInit()
        
        # Kept here for redundancy 
        self.screenshotDirectory = "./backend/screenshots/"
        self.screenshotName = "webPage.png"

        self.previousScreenshotName = "previousWebPage.png"
        self.screenshotPath = os.path.join(self.screenshotDirectory, 
                                           self.screenshotName)
        self.previousScreenshotPath = os.path.join(self.screenshotDirectory, 
                                                   self.previousScreenshotName)


    def seleniumOptionsInit(self):
        # Various options set up for the emulation of a browser
        chromeOptions = Options()
        chromeOptions.add_argument("--headless")
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument("--disable-dev-shm-usage")
        chromeOptions.add_argument("--force-device-scale-factor=1")
        
        # Various audio configs
        chromeOptions.add_argument("--autoplay-policy=no-user-gesture-required")  
        chromeOptions.add_argument("--use-fake-ui-for-media-stream")
        
        # there's some
        effectiveWidth = self.width
        effectiveHeight = self.height+self.chromeTopBarHeight

        chromeOptions.add_argument(f"window-size={effectiveWidth},{
            effectiveHeight}")
        
        self.driver = webdriver.Chrome(options=chromeOptions)
        self.actions = ActionChains(self.driver)


    # This function is for resizing
    def updateWindowSize(self, width, height):
        self.driver.set_window_size(width,height+self.chromeTopBarHeight)

    # Unused, again this is just kept for redundancy
    def getScreenshot(self):
        return self.screenshotPath

    # Renders a new Page
    def initPage(self,url):
        self.driver.get(url)
        self.focusedURL = url

    # sends page title and url
    def getPageInfo(self):
        name = self.driver.title
        url = self.driver.current_url
        return {
            'name':name,
            'url': url
        }

    # Function to check if the image is valid
    def is_valid_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                img.verify()  # Check if the image is valid (PIL function)
            return True
        except (IOError, SyntaxError) as e:
            print(f"Invalid image: {file_path}")
            return False

    # Update the page and put the screenshot into RAM
    def updatePage(self):
        temp = io.BytesIO(self.driver.get_screenshot_as_png())

        currentImage = Image.open(temp)

        return currentImage

    # Selenium interactions, the logic is handled elsewhere
    def click(self,x,y):
        #move by x,y and back after the click
        self.actions.move_by_offset(x,y).click().perform()
        self.actions.move_by_offset(-x,-y).perform()

    # Checks if the page is different from the current one.
    def currentPageDifferent(self, pageInfo):
        return pageInfo['url']!=self.driver.current_url


    # This is madness, but the web is so broken that we need it.
    def findInputField(self,name=None, id=None, class_name=None, 
                       placeholder=None):
        if name:
            try:
                return self.driver.find_element(By.NAME, name)
            except:
                pass
        
        if id:
            try:
                return self.driver.find_element(By.ID, id)
            except:
                pass
        
        if class_name:
            try:
                return self.driver.find_element(By.CLASS_NAME, class_name)
            except:
                pass
        
        if placeholder:
            try:
                return self.driver.find_element(By.XPATH, f"//input[@placeholder='{placeholder}']")
            except:
                pass
        
        try:
            return self.driver.switch_to.active_element
        except:
            pass

        return None  # If no search field is found

    #Typing function, logic is sent here.
    def typeInSearchField(self, text):
        
        # Find the search input field (e.g., Google's search bar)
        field = self.findInputField(name="q", id="search-box", 
                                    class_name="search-input")
        
        # Error checking
        if field == None:
            return 
        
        match text:
            case "space":
                field.send_keys(Keys.SPACE)
            case "enter":
                field.send_keys(Keys.ENTER)
            case "tab":
                field.send_keys(Keys.TAB)
            case "backspace":
                field.send_keys(Keys.BACK_SPACE)
            case _:
                if len(text)==1:
                    field.send_keys(text)
    
    # Browser Nav
    def tabForward(self):
        self.driver.execute_script("window.history.go(1)")

    def tabBackward(self):
        self.driver.execute_script("window.history.go(-1)")

    def refresh(self):
        self.driver.refresh()
