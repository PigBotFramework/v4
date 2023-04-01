from typing import List

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

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        return f'<RegCmd name: {self.name} mode: {self.mode} function: {self.function}>'