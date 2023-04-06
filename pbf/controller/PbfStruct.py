from ..model.BotPluginsModel import BotPluginsModel
from ..model.BlackListModel import BlackListModel
from ..model.BotSettingsModel import BotSettingsModel
from ..model.GroupSettingsModel import GroupSettingsModel
from ..model.UserInfoModel import UserInfoModel
import yaml
# 打开yaml文件
fs = open("data.yaml",encoding="UTF-8")
yamldata = yaml.load(fs,Loader=yaml.FullLoader)

'''
from revChatGPT.V1 import Chatbot
try:
    chatbot = Chatbot(config={
        "session_token": "abab"
    })
except Exception:
    chatbot = None
'''

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
    botSettings: BotSettingsModel = None
    userCoin: int = -1
    userInfo: UserInfoModel = None
    pluginsList: list = []
    port: int = 1000
    se: dict = {}
    message: str = ""
    ocrImage: str = ""
    isGlobalBanned: bool = False
    uuid: str = None
    runningProgram: str = "BOT"
    groupSettings: GroupSettingsModel = None

    def set(self, key: str, value):
        setattr(self, key, value)
    
    def get(self, key: str):
        return getattr(self, key, None)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def __str__(self):
        return f'<Struct Program:{self.runningProgram} Uuid:{self.uuid}>'

if __name__ == '__main__':
    struct = Struct(runningProgram='az')
    print(str(struct))