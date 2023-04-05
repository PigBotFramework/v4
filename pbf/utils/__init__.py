import hmac, random, math
from .Coin import Coin
from .CQCode import CQCode
from ..controller import Mysql
from ..controller.PbfStruct import Struct
from ..model.BotSettingsModel import BotSettingsModel
from googletrans import Translator as googleTranslator

googleTranslatorIns = googleTranslator()

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

class Utils:
    coin: Coin = None
    data: Struct = None

    def __init__(self, data: Struct = None):
        if data != None:
            self.data = data
            self.coin = Coin(data)

    def insertStr(self, content):
        sendStr = 'abcdefghijklmnopqrstuvwxyz'
        if '[CQ:' not in content:
            for _ in range(math.floor(len(content)/15)):
                pos = random.randint(0, len(content))
                content = content[:pos] + sendStr[random.randint(0, 25)] + content[pos:]
            self.content = content
        return content

    def generateCode(self, num: int):
        '''generate_code方法主要用于生成指定长度的验证码'''
        #定义字符串
        str1 = "23456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        #循环num次生成num长度的字符串
        code =''
        for _ in range(num):
            index = random.randint(0,len(str1)-1)
            code += str1[index]
        return code
    
    def openFile(self, path: str):
        with open(path, 'r') as f:
            return f.read()
        
    def writeFile(self, path: str, content: str):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def cqcode(self, cqcode: str) -> str:
        return CQCode(cqcode)

    def translator(self, text, from_lang="zh-cn", to_lang="en"):
        if from_lang == to_lang or not text.lstrip().rstrip():
            return text
        try:
            return googleTranslatorIns.translate(text, dest=to_lang).text
        except Exception:
            return text

    def findObject(self, key, value, ob):
        '''
        查找键值对并返回对象
        '''
        num = 0
        for i in ob:
            if str(i.get(str(key))) == str(value):
                return {"num":num,"object":i}
            num += 1
        return {"num":-1,"object":404}

    def getPswd(self, uuid):
        '''
        根据UUID获取实例通信密钥
        '''
        if not uuid:
            raise ValueError('Please give a non-empty string as a uuid.')
        botOb = BotSettingsModel(uuid=uuid)
        print(botOb._get('secret'))
        if botOb.exists == False:
            botOb._delete()
            del botOb
            raise ValueError('Cannot find the right secret. Is the uuid right?')
        else:
            return botOb._get('secret')

    def encryption(self, data, secret, encode='utf-8', digestmod='sha1'):
        '''
        HMAC加密
        '''
        key = secret.encode(encode)
        obj = hmac.new(key, msg=data, digestmod=digestmod)
        return obj.hexdigest()
