from .PbfStruct import Struct
from ..statement.ImageStatement import ImageStatement
from ..statement.AtStatement import AtStatement
from ..statement.TextStatement import TextStatement
import random, math, requests, re
from . import Mysql, Cache
from urllib.request import urlopen
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from ..utils import Utils
from ..utils.pillow.build_image import BuildImage, Text2Image
from ..model.BotSettingsModel import BotSettingsModel

class Client:
    data: Struct = None
    utils: Utils = None

    def __init__(self, struct: Struct) -> None:
        self.data = struct
        self.utils = Utils(self.data)
    
    def CallApi(self, api, parms={}, timeout=10):
        botSettings = self.data.botSettings
        if not botSettings:
            botSettings = BotSettingsModel(uuid=self.data.uuid)
            self.data.botSettings = botSettings
        return requests.post(url='{0}/{1}?access_token={2}'.format(botSettings._get('httpurl'), api, botSettings._get('secret')), json=parms, timeout=timeout).json()
    
    def msg(self, *args, coinFlag=True, insertStrFlag=False, retryFlag=True, translateFlag=True):
        return Msg(self.data, *args, coinFlag=coinFlag, insertStrFlag=insertStrFlag, retryFlag=retryFlag, translateFlag=translateFlag)

class Msg(Client):
    content: list = None
    coinFlag: bool = True
    insertStrFlag: bool = False
    retryFlag:bool = True
    translateFlag:bool = True

    def __init__(self, data: Struct, *args, coinFlag=True, insertStrFlag=False, retryFlag=True, translateFlag=True):
        self.data = data
        self.content = list(args)
        try:
            if isinstance(self.content[0], list):
                self.content = self.content[0]
        except Exception:
            pass

    def getParams(self, content: list = None) -> list:
        content: list = content if content != None else self.content
        
        arr: list = []
        for i in content:
            try:
                if type(i) == str:
                    i = TextStatement(i)
                arr.append(i.get())
            except Exception:
                pass
        return arr
    
    def raw(self, content: str, retryFlag=True):
        if 'face54' in content:
            content = content.replace('face54', '[CQ:face,id=54]')
        
        dataa = self.custom(self.data.se.get('user_id'), self.data.se.get('group_id'), content)
        
        if dataa.get('status') == 'failed' and self.data.se.get('post_type') == 'message':
            if retryFlag:
                self.raw('消息发送失败，尝试转图片发送...', retryFlag=False)
                self.data.message = content
                self.data.se['user_id'] = self.data.botSettings.get('myselfqn')
                self.data.se['sender']['nickname'] = self.data.botSettings.get('name')
                return self.image()
        else:
            return dataa.get('data').get('message_id')
    
    def channel(self):
        data = self.CallApi('send_guild_channel_msg', {'guild_id':self.data.se.get('guild_id'),'channel_id':self.data.se.get('channel_id'),'message':self.getParams()})
        return data
    
    def sendMsg(self, *content):
        return self.custom(self.data.se.get('user_id'), self.data.se.get('group_id'), self.getParams(), content)
    
    def custom(self, uid, gid=None, params=None, *content):
        if len(content) != 0:
            self.content += content
        
        if gid == None:
            dataa = self.CallApi('send_msg', {'user_id':uid,'message':params})
        else:
            dataa = self.CallApi('send_msg', {'group_id':gid,'message':params})
        
        if dataa.get('status') == 'failed':
            print(f'PBF Server: Failed to send message')
            print(f'PBF Server: |- Wording: {dataa.get("wording")}')
            print(f'PBF Server: |- UID:{uid} GID:{gid}')
        
        return dataa

    # 注意！本函数需要使用 imageutils
    def image(self):
        userid = self.data.se.get('user_id')
        name = self.data.se.get('sender').get('nickname')
        texts = self.data.message
        texts = re.sub(r"\[CQ:(.*),([^\]]*)?\]", "", texts)
        
        def load_image(path: str):
            return BuildImage.open("./resources/images/" + path).convert("RGBA")
        
        # 获取头像
        url = "http://q1.qlogo.cn/g?b=qq&nk="+str(userid)+"&s=640"
        image_bytes = urlopen(url).read()
        # internal data file
        data_stream = BytesIO(image_bytes)
        # open as a PIL image object
        #以一个PIL图像对象打开
        img = BuildImage.open(data_stream).convert("RGBA").square().circle().resize((100, 100))
    
        name_img = Text2Image.from_text(name, 25, fill="#868894").to_image()
        name_w, name_h = name_img.size
        if name_w >= 700:
            raise ValueError("User name too long!")
    
        corner1 = load_image("my_friend/corner1.png")
        corner2 = load_image("my_friend/corner2.png")
        corner3 = load_image("my_friend/corner3.png")
        corner4 = load_image("my_friend/corner4.png")
        label = load_image("my_friend/label.png")
    
        def make_dialog(text: str) -> BuildImage:
            text_img = Text2Image.from_text(text, 40).wrap(700).to_image()
            text_w, text_h = text_img.size
            box_w = max(text_w, name_w + 15) + 140
            box_h = max(text_h + 103, 150)
            box = BuildImage.new("RGBA", (box_w, box_h))
            box.paste(corner1, (0, 0))
            box.paste(corner2, (0, box_h - 75))
            box.paste(corner3, (text_w + 70, 0))
            box.paste(corner4, (text_w + 70, box_h - 75))
            box.paste(BuildImage.new("RGBA", (text_w, box_h - 40), "white"), (70, 20))
            box.paste(BuildImage.new("RGBA", (text_w + 88, box_h - 150), "white"), (27, 75))
            box.paste(text_img, (70, 16 + (box_h - 40 - text_h) // 2), alpha=True)
        
            dialog = BuildImage.new("RGBA", (box.width + 130, box.height + 60), "#eaedf4")
            dialog.paste(img, (20, 20), alpha=True)
            dialog.paste(box, (130, 60), alpha=True)
            dialog.paste(label, (160, 25))
            dialog.paste(name_img, (260, 22 + (35 - name_h) // 2), alpha=True)
            return dialog
        dialogs = [make_dialog(texts)]
        frame_w = max((dialog.width for dialog in dialogs))
        frame_h = sum((dialog.height for dialog in dialogs))
        frame = BuildImage.new("RGBA", (frame_w, frame_h), "#eaedf4")
        current_h = 0
        for dialog in dialogs:
            frame.paste(dialog, (0, current_h))
            current_h += dialog.height
        
        jpgname = frame.save_jpg()
        self.content = [ImageStatement(file='https://pbfresources.xzynb.top/createimg/{0}'.format(jpgname))]
        self.custom(self.data.se.get('user_id'), self.data.se.get('group_id'), self.getParams())
    
    def randomCoin(self, content: str = None):
        botSettings = self.data.botSettings
        # 随机好感度
        try:
            if random.randint(1, botSettings.get('coinPercent')) == 1 and self.coinFlag:
                userCoin = self.utils.coin.add()
                if userCoin != False:
                    return TextStatement('\n\n『谢谢陪我聊天，好感度加{0}』'.format(userCoin))
        except Exception:
            pass
    
    def debug(self):
        strList = []
        for i in self.content:
            strList.append(str(i))
        print(strList)
        return strList
    
    def getRawText(self):
        msg = ''
        for i in self.content:
            if isinstance(i, TextStatement):
                msg += str(i)
            elif isinstance(i, AtStatement):
                msg += f'@{i.qq}'
            else:
                msg += ' '
        return msg

    def send(self):
        botSettings = self.data.botSettings
        
        self.content.append(self.randomCoin())
        
        # 频道消息
        if self.data.se.get('channel_id') != None:
            return self.channel()
        
        dataa = self.sendMsg()
        try:
            if dataa.get('status') == 'failed' and self.data.se.get('post_type') == 'message':
                if self.retryFlag:
                    self.raw('消息发送失败，尝试转图片发送...', retryFlag=False)
                    self.data.message = self.getRawText()
                    self.data.se['user_id'] = botSettings.get('myselfqn')
                    self.data.se['sender']['nickname'] = botSettings.get('name')
                    return self.image()
            else:
                return dataa.get('data').get('message_id')
        except Exception:
            pass
