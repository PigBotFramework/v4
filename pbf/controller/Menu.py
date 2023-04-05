from .PbfStruct import Struct
from .Client import Client
from . import Cache
from ..statement.FaceStatement import FaceStatement
from ..statement.TextStatement import TextStatement
from ..model.BotPluginsModel import BotPluginsModel

class Menu:
    data: Struct = None
    client: Client = None

    def __init__(self, data: Struct):
        self.data = data
        self.client = Client(data)
    
    def getModedMenu(self):
        pluginsList = Cache.get('commandPluginsList')
        botPluginsList = BotPluginsModel(uuid=self.data.uuid)._get('data')
        botPluginsList = botPluginsList if botPluginsList is not None else []
        commandModedList = []

        for i in botPluginsList:
            cmds = pluginsList.get(i.get('path'))
            if cmds == None:
                continue
            for cmd in cmds:
                if cmd.mode not in commandModedList:
                    commandModedList.append(cmd.mode)
        
        return commandModedList

    def sendModedMenu(self):
        menuList = self.getModedMenu()
        messageList = [
            FaceStatement(151),
            TextStatement(f'{self.data.botSettings.get("name")}-菜单', 1)
        ]
        myIter = 0

        for i in menuList:
            if myIter == 0:
                messageList.append(FaceStatement(54))
                messageList.append(TextStatement(i))
                myIter += 1
            else:
                messageList.append(TextStatement(f'  {i}'))
                messageList.append(FaceStatement(54))
                messageList.append(TextStatement(' ', 1))
                myIter = 0
        
        messageList.append(TextStatement(' ', 1))
        if myIter == 1:
            messageList.append(TextStatement(' ', 1))
        messageList.append(TextStatement('[ {0} Powered By PigBotFramework ]'.format(self.data.botSettings.get('name'))))
        
        msg = self.client.msg(messageList)
        # msg.debug()
        msg.send()
    
    def sendSingleMenu(self, mode: str):
        commandList = Cache.get('commandModedList').get(mode)
        if commandList == None:
            raise Exception('Mode name not found')
        
        messageList = [
            FaceStatement(151),
            TextStatement(f'{self.data.botSettings.get("name")}-菜单：{mode}', 1)
        ]

        for i in commandList:
            if i.hidden == 0:
                messageList.append(FaceStatement(54))
                messageList.append(TextStatement(f'{i.name}', 1))
                messageList.append(TextStatement(f'用法：{i.usage}', 1))
                messageList.append(TextStatement(f'解释：{i.description}', 1))
                
                if i.permission == 'admin' or i.permission == 'ao':
                    permission = '管理员'
                elif i.permission == 'owner':
                    permission = '我的主人'
                elif i.permission == 'anyone':
                    permission = '任何人'
                elif i.permission == 'ro':
                    permission = '真正的主人'
                messageList.append(TextStatement(f'权限：{permission}', 1))
            elif i.hidden == 2:
                messageList.append(FaceStatement(54))
                messageList.append(TextStatement(f'{i.usage}', 1))
            
        messageList.append(TextStatement(' ', 1))
        messageList.append(TextStatement('解锁更多功能请机器人主人安装其他插件', 1))
        messageList.append(TextStatement('[ {0} Powered By PigBotFramework ]'.format(self.data.botSettings.get('name'))))

        msg = self.client.msg(messageList)
        # msg.debug()
        msg.send()