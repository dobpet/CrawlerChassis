import json

class param:
    dictionary = {
        
        "Network":
        [
            {"SSID": "Fofr", "pass": "12345"},
            {"SSID": "Fofr2", "pass": "56479"}
        ],
        
        
        "AP_SSID": "RP-AP",
        "AP_Pass": "RaspberryWifi2023"
    }
    SettingsFile = "settings.json"
    
    def __init__(self, settingsFile = "settings.json"):
        self.SettingsFile = settingsFile
        try:
            with open(self.SettingsFile) as file:
                #print('File exist')
                self.dictionary = json.load(file)
                #print(data)
            
        except OSError:
            self.SaveSettings()
                
    def SaveSettings(self):
        with open(self.SettingsFile, 'w') as file:
            json.dump(self.dictionary, file)
                
        

    

