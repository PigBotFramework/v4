from .Client import Client
from .PbfStruct import Struct
from ..utils import Utils
import requests
from . import Cache

class BanWords:
    data: Struct = None
    utils: Utils = None

    def __init__(self, data: Struct):
        self.data = data
        self.utils = Utils(self.data)

    def find(self, message):
        for l in Cache.get("botWeijin"):
            i = l.get('content')
            if i in message and i != '' and (l.get("qn") == 0 or l.get("qn") == self.data.se.get("group_id")):
                return i
        return False
    
    def check(self, weijinFlag=True):
        se = self.data.se
        gid = se.get('group_id')
        message = self.data.message
        
        if message == None:
            return False
        
        messageReplace = message.replace(' ','').strip()
        i = self.find(messageReplace)
        if i != False:
            client = Client(self.data)

            if weijinFlag == True and gid != None and self.data.se.get("sender").get("role") == "member":
                client.msg().raw('[CQ:face,id=151] [CQ:at,qq={2}] {0}不喜欢您使用（{1}）这种词语哦，请换一种表达方式吧！'.format(self.data.botSettings.get('name'), i, self.data.se.get("user_id")))
                self.utils.coin.remove()
                client.CallApi('delete_msg', {'message_id':self.data.se.get('message_id')})
                
            # 如果辱骂机器人则骂回去
            if ('[CQ:at,qq='+str(self.data.botSettings.get('myselfqn'))+']' in messageReplace) or (self.data.botSettings.get('name') in messageReplace) or ('猪比' in messageReplace) or ('猪逼' in messageReplace) or ('猪鼻' in messageReplace) or ('机器人' in messageReplace) or (gid == None):
                repeatnum = self.data.botSettings.get('yiyan')
                while repeatnum > 0:
                    self.utils.coin.remove()
                    dataa = requests.get(url=self.data.botSettings.get('duiapi'))
                    dataa.enconding = "utf-8"
                    if repeatnum == self.data.botSettings.get('yiyan'):
                        replymsg = '[CQ:reply,id='+str(se.get('message_id'))+'] 你骂我？好啊\n'+str(dataa.text)
                    else:
                        replymsg = dataa.text
                    client.msg().raw(replymsg)
                    repeatnum -= 1
        
            # break 
            return True