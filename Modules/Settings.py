from configparser import ConfigParser

from os import makedirs, path

class AppSettings:
    def __init__(self) -> None:
        print("Init App Settings")
        self.configDir = "./Settings"
        self.configFilePath = "./Settings/config.ini"
        self.assurePath(self.configDir)
        if not (path.isfile(self.configFilePath)):
            self.createDefaultIni()
        print("--> AppSettings created")
        return

    def createDefaultIni(self) -> None:
        print("- create Default config.ini")
        config = ConfigParser()
        config['main'] = {'darkTheme':1}
        # with open(path, 'w') --> create the .ini file using the default contents. Closes automatically
        with open(self.configFilePath, 'w') as configfile:
            config.write(configfile)
        return

    def getIntValue(self,section,key) -> int:
        config = ConfigParser()
        config.read(self.configFilePath)
        value = config.get(section, key)
        return value

    def setValue(self, section, key, value) -> None:
        config = ConfigParser()
        config.read(self.configFilePath)
        config.set(section, key, str(value))
        with open(self.configFilePath, 'w') as configfile:
            config.write(configfile)
        return


    def getDarkTheme(self) -> int:
        print("- getDarkTheme")
        value = 0
        try:
            value = int(self.getIntValue("main", "darkTheme"))
        except:
            pass
        return value

        
    def assurePath(self, dirPath):
        print(f"- assurePath: {dirPath}")
        try:
            # exists_ok=True --> succeeds even if directory exists (won't raise FileExistsError)
            makedirs(dirPath, exist_ok=True)
        except OSError as error:
            print("--> OSError: " + str(error))
        return