class JSONParser:
    def __init__(self):
        # we want to track the cursor position 
        self.index = 0  

    def parse(self, jsonString):
        self.jsonString = jsonString.strip()
        self.index = 0
        return self.parseUnknownValue()

    #Parsing a new file
    def parseUnknownValue(self):
        char = self.jsonString[self.index]
        if char == '"':
            return self.parseString()
        elif char == '{':
            return self.parseObject()
        elif char == '[':
            return self.parseArray()
        elif self.jsonString.startswith("true", self.index):
            self.index += 4
            return True
        elif self.jsonString.startswith("false", self.index):
            self.index += 5
            return False
        elif self.jsonString.startswith("null", self.index):
            self.index += 4
            return None
        else:
            raise ValueError(f"Unexpected character at index {self.index}: {char}")

    def parseString(self):
        end_index = self.jsonString.find('"', self.index + 1)
        if end_index == -1:
            raise ValueError("Unterminated string")
        result = self.jsonString[self.index + 1:end_index]
        self.index = end_index + 1
        return result

    def parseObject(self):
        obj = {}
        self.index += 1  # Skip '{'
        while self.jsonString[self.index] != '}':
            self.eatWhiteSpace()
            key = self.parseString()
            self.eatWhiteSpace()
            if self.jsonString[self.index] != ':':
                raise ValueError(f"Expected ':' at index {self.index}")
            self.index += 1  # Skip ':'
            self.eatWhiteSpace()
            value = self.parseUnknownValue()
            obj[key] = value
            self.eatWhiteSpace()
            if self.jsonString[self.index] == '}':
                break
            if self.jsonString[self.index] != ',':
                raise ValueError(f"Expected ',' at index {self.index}")
            self.index += 1  # Skip ','
        self.index += 1  # Skip '}'
        return obj

    def parseArray(self):
        array = []
        self.index += 1  # Skip '['
        while self.jsonString[self.index] != ']':
            self.eatWhiteSpace()
            value = self.parseUnknownValue()
            array.append(value)
            self.eatWhiteSpace()
            if self.jsonString[self.index] == ']':
                break
            if self.jsonString[self.index] != ',':
                raise ValueError(f"Expected ',' at index {self.index}")
            self.index += 1  # Skip ','
        self.index += 1  # Skip ']'
        return array

    # nom nom nom
    def eatWhiteSpace(self):
        while self.index < len(self.jsonString) and self.jsonString[self.index].isspace():
            self.index += 1

    # This method converts a dictionary back into a JSON string
    def dictToJSONString(self, data):
        json_str = "{\n"
        for key, value in data.items():
            json_str += f'  "{key}": {self.KVPToJson(value)},\n'
        json_str = json_str.rstrip(",\n") + "\n}"
        return json_str

    # key-value-pair to JSON
    def KVPToJson(self, value):
        # JSON's formatting isnt exactly like a dictionary in python
        #   so for cross-compat, i'm cleaning it up. Also, for 
        #   runtime efficiency, I'm checking the most popular JSON 
        #   types first. 
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return "null"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            return "[" + ", ".join([self.KVPToJson(v) for v in value]) + "]"
        elif isinstance(value, dict):
            return self.dictToJSONString(value)
        return str(value)
    