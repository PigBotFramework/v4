from typing import List
from functools import wraps
from ..controller import Handler
class RegCmd:
    name: str = 'Command name'
    description: str = 'Command description'
    permission: str = 'cmd.permission.cmdname'
    usage: str = 'Command usage'
    alias: List[str] = []
    hidden: bool = False
    enabled: bool = True
    type: str = 'command'
    function: str = '__enter__'
    mode: str = '机器人操作'
    pwd: str = 'foo'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        return f'<RegCmd name: {self.name} mode: {self.mode} function: {self.function}>'

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not Handler.pluginsLoading:
                return func(*args, **kwargs)

            if self.type == 'command':
                pwd = Handler.pluginsPath
                if Handler.commandPluginsList.get(pwd) == None:
                    Handler.commandPluginsList[pwd] = []
                Handler.commandPluginsList[pwd].append(self)

                if Handler.commandModedList.get(self.mode) is None:
                    Handler.commandModedList[self.mode] = []
                Handler.commandModedList[self.mode].append(self)

                Handler.commandListenerList.append(self)
            elif self.type == 'meta':
                Handler.metaListenerList.append(self)
            elif self.type == 'notice':
                Handler.noticeListenerList.append(self)
            elif self.type == 'request':
                Handler.requestListenerList.append(self)
            elif self.type == 'message':
                Handler.messageListenerList.append(self)
        return wrapper