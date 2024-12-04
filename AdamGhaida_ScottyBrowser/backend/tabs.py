import json 
import os
from .jsonParser import JSONParser

class tabsClass:

    def __init__(self):
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        self.jsonPath = os.path.join(scriptDir, "tabs.json")

        self.JSONInterface = JSONParser()

        self.parsedTabs = self.parseTabs()


    def parseTabs(self):
        return self.JSONInterface.parse(self.readData())
    
    def updateTab(self, index, pageInfo):
        # Ensure the "tabs" key exists in the parsedTabs
        if "tabs" not in self.parsedTabs:
            print("No tabs to update.")
            return
        
        # Validate the index
        if index < 0 or index >= len(self.parsedTabs["tabs"]):
            print(f"Invalid index {index}. Cannot update tab.")
            return
        print(pageInfo)
        # Update the tab with new pageInfo
        for key, value in pageInfo.items():
            if key in self.parsedTabs["tabs"][index]:
                self.parsedTabs["tabs"][index][key] = value
            else:
                print(f"Warning: Key '{key}' not found in the tab structure. Skipping.")
        
        print("\n\n\n PARSED tabs\n",self.parsedTabs)
        # Convert the updated dictionary back to JSON
        newJsonStr = self.JSONInterface.dictToJSONString(self.parsedTabs)
        
        # Write the updated JSON back to the file
        self.writeData(newJsonStr)
        print(f"Tab at index {index} updated successfully.")

    def addTab(self, pageInfo,):        
        # If the "tabs" key doesn't exist, initialize it
        print("pageInfo", pageInfo)
        if "tabs" not in self.parsedTabs:
            self.parsedTabs["tabs"] = []

        # Append the new tab to the list of tabs
        self.parsedTabs["tabs"].append(pageInfo)

        # Convert the dictionary back to JSON string format
        newJsonStr = self.JSONInterface.dictToJSONString(self.parsedTabs)

        # Write the updated JSON back to the file
        
        self.writeData(newJsonStr)


    def removeTab(self, index):
        removedTab = self.parsedTabs["tabs"].pop(index)

        # Convert the updated dictionary back to JSON
        newJsonStr = self.JSONInterface.dictToJSONString(self.parsedTabs)
        self.writeData(newJsonStr)
        

    def readData(self):
        with open(self.jsonPath, 'r') as JSONFile:
            return JSONFile.read()

    def writeData(self,data):
        with open(self.jsonPath, 'w') as JSONFile:
            JSONFile.write(data)

    def uploadData(self, newJsonObject):
        newTab = json.dump(newJsonObject)
        self.tabsFile["tabs"].append(newTab)
