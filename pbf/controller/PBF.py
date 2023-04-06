from .PbfStruct import Struct
from .Client import Client
from .CommandListener import CommandListener
from ..utils import Utils
from .Logger import Logger
from .Banwords import BanWords
from inspect import getmembers, isclass
from ..statement import Statement
from ..statement.FaceStatement import FaceStatement
from ..statement.TextStatement import TextStatement
import sys, random, threading, importlib, traceback
from .PbfStruct import yamldata
from .Regex import Regex
from . import Mysql, Cache
sys.path.append('..')


class PBF:
    weijin = None
    rclOb = None
    kwrlist = None
    settingName = None
    commandmode = []
    ChatterBot = None
    ListTrainer = None
    pluginsList: list = []

    commandListener: CommandListener = None
    client: Client = None
    utils: Utils = None
    cache: Cache = Cache
    mysql: Mysql = Mysql
    logger: Logger = None
    banwords: BanWords = None
    regex: Regex = None
    
    name: str = 'PBF Plugin'
    description: str = 'PBF插件'
    cost: float = 0.0
    introduction: str = '# PBF插件'
    author: str = 'xzyStudio'
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def __enter__(self):
        return []

    def __init__(self, data):
        self.data = data
        self.commandListener = CommandListener(data)
        self.client = Client(self.data)
        self.utils = Utils(self.data)
        self.logger = Logger(self.data)
        self.regex = Regex(self.data)
    
    def __str__(self):
        return f'<PBF Program:{self.data.runningProgram} Uuid:{self.data.uuid}>'

    def send(self, message):
        return self.client.msg().raw(message)

    def changeRunningProgram(self, runningProgram: str):
        self.data.runningProgram = runningProgram
        self.logger.setData(self.data)

    def groupInit(self):
        gid = self.data.se.get('group_id')
        if gid == None:
            return 
        Mysql.commonx('INSERT INTO `botSettings` (`qn`, `uuid`, `power`, `connectQQ`) VALUES (%s, %s, %s, %s);', (gid, self.data.uuid, self.data.botSettings.get('defaultPower'), self.data.se.get("user_id")))
        if self.data.botSettings.get('defaultPower'):
            self.client.msg(
                FaceStatement(189),
                TextStatement('机器人已初始化，发送“菜单”可以查看全部指令', 1),
                TextStatement('发送“群聊设置”可以查看本群的初始设置', 1),
                TextStatement('如果不会使用机器人请发送“新手教程”查看教程！')
            ).send()
        else:
            self.client.msg(
                FaceStatement(189),
                TextStatement('机器人已初始化，当前已关机，发送“开机”可以开启机器人'),
                TextStatement('开机后，发送“菜单”可以查看指令！')
            ).send()
        Cache.refreshFromSql('groupSettings')
    
    def reply(self):
        pass

    def execPluginThread(self, func):
        # return self.execPlugin(func)
        threading.Thread(target=self.execPlugin,args=(func,)).start()
    
    def execPlugin(self, func):
        try:
            print(f'PBF Server: {func}')
            className, methodName = func.split('@')
            
            module = importlib.import_module(f'plugins.{className}')
            instance = getattr(module, className)(self.data)
            return getattr(instance, methodName)()
        except Exception:
            self.logger.error(traceback.format_exc())
    
    def getUidOnly(self):
        # 跟班模式
        settings = self.data.groupSettings
        botSettings = self.data.botSettings
        se = self.data.se
        uid = se.get('user_id')
        only_for_uid = True
        if se.get("group_id"):
            if settings._get('only_for_uid') is None:
                settings._set(only_for_uid=' ')
            if botSettings._get("only_for_uid") and botSettings._get("only_for_uid") == uid:
                only_for_uid = False
            if len(settings._get("only_for_uid").split()) != 0 and str(uid) in settings._get("only_for_uid").split():
                only_for_uid = False
            if (not botSettings._get("only_for_uid")) and (len(settings._get("only_for_uid")) == 0):
                only_for_uid = False
            if uid == yamldata.get("chat").get("owner"):
                only_for_uid = False
        else:
            only_for_uid = False
        return only_for_uid
        
    def checkPromiseAndRun(self, i, echoFlag=False, senderFlag=False, content=None):
        uid = self.data.se.get('user_id')
        # gid = self.data.se.get('group_id')
        se = self.data.se
        botSettings = self.data.botSettings
        evalFunc = i.function
        content = content if content else i.name
        promise = i.permission
        
        if promise == 'anyone':
            return self.execPluginThread(evalFunc)
        elif promise == 'owner':
            if uid == botSettings.get('owner') or uid == botSettings.get('second_owner'):
                return self.execPluginThread(evalFunc)
            elif echoFlag == True:
                self.client.msg(
                    FaceStatement(151),
                    TextStatement('你不是我的主人，哼ꉂ(ˊᗜˋ*)')
                ).send()
        elif promise == 'ro':
            if uid == botSettings.get('owner'):
                return self.execPluginThread(evalFunc)
            elif echoFlag == True:
                self.client.msg(
                    FaceStatement(151),
                    TextStatement('你不是我真正的主人，哼ꉂ(ˊᗜˋ*)')
                ).send()
        elif promise == 'xzy':
            if uid == yamldata.get('chat').get('owner') and self.data.uuid == yamldata.get('self').get('defaultUuid'):
                return self.execPluginThread(evalFunc)
            elif echoFlag == True:
                self.client.msg(
                    FaceStatement(151),
                    TextStatement('该指令只有最高管理员可以使用！并且实例必须为官方默认实例')
                ).send()
        
        if senderFlag == True:
            if promise == 'admin':
                if se.get('sender').get('role') != 'member':
                    return self.execPluginThread(evalFunc)
                elif echoFlag == True:
                    self.client.msg(
                        FaceStatement(151),
                        TextStatement('就你？先拿到管理员再说吧！')
                    ).send()
            elif promise == 'ao':
                if se.get('sender').get('role') != 'member' or uid == botSettings.get('owner') or uid == botSettings.get('second_owner'):
                    return self.execPluginThread(evalFunc)
                elif echoFlag == True:
                    self.client.msg(
                        FaceStatement(151),
                        TextStatement('就你？先拿到管理员再说吧！')
                    ).send()
    
if __name__ == '__main__':
    pbf = PBF(Struct(se={'user_id':123}))
    print(pbf)
    pbf.commandListener.set("test")
    print(pbf.commandListener.get())
    
    pbf2 = PBF(Struct(se={'user_id':123}))
    print(pbf2)
    print(pbf2.commandListener.get())