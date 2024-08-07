import json

from . import Cache
from .Client import Client
from .PbfStruct import Struct
from ..model.BotPluginsModel import BotPluginsModel
from ..statement.FaceStatement import FaceStatement
from ..statement.TextStatement import TextStatement
from ..utils import Utils


class Menu:
    data: Struct = None
    client: Client = None

    def __init__(self, data: Struct):
        self.data = data
        self.client = Client(data)

    def getModedMenu(self):
        pluginsList = Cache.get('commandPluginsList')
        botPluginsList = BotPluginsModel()._get(uuid=self.data.uuid)
        botPluginsList = botPluginsList if botPluginsList is not None else []
        commandModedList = []

        for i in botPluginsList:
            cmds = pluginsList.get(i.get('path'))
            if cmds == None:
                continue
            for cmd in cmds:
                if cmd.mode not in commandModedList and cmd.hidden != 1:
                    commandModedList.append(cmd.mode)

        return commandModedList

    def sendModedMenu(self):
        menuList = self.getModedMenu()
        # Header
        messageList = [
            FaceStatement(46),
            TextStatement(f'{self.data.botSettings._get("name")}-菜单', 1)
        ]
        # Body
        myIter = 0

        for i in menuList:
            if myIter == 0:
                messageList.append(FaceStatement(147))
                messageList.append(TextStatement(i, transFlag=False))
                myIter += 1
            else:
                messageList.append(TextStatement(f'  {i}', transFlag=False))
                messageList.append(FaceStatement(147))
                messageList.append(TextStatement(' ', 1))
                myIter = 0

        messageList.append(TextStatement(' ', 1))
        if myIter == 1:
            messageList.append(TextStatement(' ', 1))

        # Footer
        messageList += Utils(self.data).hitokoto()
        messageList.append(
            TextStatement('[ {0} Powered By PigBotFramework ]'.format(self.data.botSettings._get('name')), transFlag=False))

        msg = self.client.msg(messageList)
        # msg.debug()
        msg.send()

    def sendSingleMenu(self, mode: str):
        commandList = Cache.get('commandModedList').get(mode)
        if commandList == None:
            raise Exception('Mode name not found')

        # Header
        messageList = [
            FaceStatement(46),
            TextStatement(f'{self.data.botSettings._get("name")}-菜单：{mode}', 1)
        ]

        # Body
        for i in commandList:
            if i.hidden == 0:
                messageList.append(FaceStatement(147))
                messageList.append(TextStatement(f'{i.name}', 1, transFlag=False))
                messageList.append(TextStatement(f'用法：{i.usage}', 1))
                messageList.append(TextStatement(f'解释：{i.description}', 1))

                permission = str()
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
                messageList.append(FaceStatement(147))
                messageList.append(TextStatement(f'{i.usage}', 1))

        # Footer
        messageList.append(TextStatement(' ', 1))
        messageList += Utils(self.data).hitokoto()
        messageList.append(TextStatement('解锁更多功能请机器人主人安装其他插件', 1))
        messageList.append(
            TextStatement('[ {0} Powered By PigBotFramework ]'.format(self.data.botSettings._get('name')), transFlag=False))

        msg = self.client.msg(messageList)
        # msg.debug()
        msg.send()
