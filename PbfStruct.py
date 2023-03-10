'''
This is the struct of data
'''
import yaml
# 打开yaml文件
fs = open("data.yaml",encoding="UTF-8")
yamldata = yaml.load(fs,Loader=yaml.FullLoader)

def noMap(ob, key: str):
    return ob

def mapDict(ob, key: str):
    obDict = {}
    for i in ob:
        obDict[i.get(key)] = i
    
    return obDict

def mapDoubleDict(ob, key: str):
    first, second = key.split()
    obDict = {}
    for i in ob:
        if (obDict.get(i.get(first)) == None):
            obDict[i.get(first)] = {}
        obDict[i.get(first)][i.get(second)] = i
    return obDict

def mapDictToList(ob, key: str):
    obDict = {}
    for i in ob:
        if (obDict.get(i.get(key)) == None):
            obDict[i.get(key)] = []
        obDict[i.get(key)].append(i)
    
    return obDict


class Struct:
    args: list = []
    messageType: str = 'qn'
    botSettings: dict = {}
    userCoin: int = -1
    userInfo: dict = {}
    pluginsList: list = []
    port: int = 1000
    se: dict = {}
    message: str = ""
    ocrImage: str = ""
    isGlobalBanned: bool = False
    uuid: str = None
    runningProgram: str = "BOT"
    groupSettings: dict = {}

    def set(self, key: str, value):
        setattr(self, key, value)
    
    def get(self, key: str):
        return getattr(self, key, None)

    def __init__(self, **kwargs):
        for i in kwargs:
            exec(f'self.{i} = kwargs.get("{i}")')
    
    def __str__(self):
        return f'<Struct Program:{self.runningProgram} Uuid:{self.uuid}>'

if __name__ == '__main__':
    struct = Struct(runningProgram='az')
    print(str(struct))