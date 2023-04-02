from .Client import Client
from .PbfStruct import Struct
from ..statement.TextStatement import TextStatement
from . import Cache

class Regex:
    client: Client = None
    data: Struct = None
    kwrList: list = None
    

    def __init__(self, data: Struct):
        self.data = data
        self.client = Client(data)
        self.kwrList = Cache.get('botReplace')

    def exceptx(self, replyKey, message):
        if ('$1' in replyKey) and ('$2' in replyKey):
            replyKey = replyKey.split('$1')[1]
            replyKey = replyKey.split('$2')[0]
            if ',' in replyKey:
                replyKey = replyKey.split(',')
                for i in replyKey:
                    if i in message:
                        return 1
            elif replyKey in message:
                return 1
        else:
            return 0
    
    def replace(self, replyContent):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        se = self.data.se
        coin = self.data.userCoin
        _ = f'{uid}{gid}{se}'
        
        if coin == -1:
            coin = '用户未注册！'
        for i in self.kwrList:
            replyContent = replyContent.replace(i.get('key'), str(eval(i.get('value'))))
        return replyContent
    
    def orx(self, replyKey, message):
        if '|' in replyKey:
            splitKey = replyKey.split('|')
            for sk in splitKey:
                if sk in message:
                    return 1
                elif '&amp;' in sk:
                    if self.andx(sk, message):
                        return 1
            return 0
        elif '&amp;' in replyKey:
            return self.andx(replyKey, message)
        else:
            return 0
    
    def andx(self, replyKey, message):
        if '&amp;' in replyKey:
            msgand = replyKey.split('&amp;')
            for msgandi in msgand:
                if msgandi not in message:
                    return 0
            return 1
        else:
            return 0

    def pair(self, replyKey, message):
        if self.exceptx(replyKey, message):
            return False
        if ('$1' in replyKey) and ('$2' in replyKey):
            replyKey = replyKey.split('$1')[0] + replyKey.split('$2')[1]
        if self.orx(replyKey, message) or replyKey in message:
            return True
        return False
    
    def send(self, replyContent):
        replyContent = self.replace(replyContent)
        if ('|' in replyContent) and ('|]' not in replyContent) and ('[|' not in replyContent):
            replyContentList = replyContent.split('|')
            for rcl in replyContentList:
                self.client.msg().raw(rcl)
        else:
            self.client.msg().raw(replyContent)