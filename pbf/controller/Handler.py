import importlib
import json
import os
import traceback
import copy
import requests

from . import Cache
from .Banwords import BanWords
from .Client import Client
from .CommandListener import CommandListener
from .Menu import Menu
from .PBF import PBF
from .PbfStruct import Struct
from .. import plugins_path, plugins_path_name
from ..model.BlackListModel import BlackListModel
from ..model.BotPluginsModel import BotPluginsModel
from ..model.BotSettingsModel import BotSettingsModel
from ..model.GroupSettingsModel import GroupSettingsModel
from ..model.UserInfoModel import UserInfoModel
from ..statement.FaceStatement import FaceStatement
from ..statement.TextStatement import TextStatement
from ..utils import Utils, CQCode


def getPluginsList(path: str = "./plugins", folderName: str = None):
    if folderName is None:
        folderName = path.split("/")[-1]
    if not os.path.exists(path):
        os.mkdir(path)
    pluginsList = os.listdir(path)
    for dbtype in pluginsList[::]:
        if os.path.isfile(os.path.join(folderName, dbtype)) or dbtype.startswith('__'):
            pluginsList.remove(dbtype)
    return pluginsList


noticeListenerList: list = []
requestListenerList: list = []
metaListenerList: list = []
messageListenerList: list = []
commandListenerList: list = []  # 后续的菜单都是遍历该数组生成
pluginsData: list = []
commandPluginsList: dict = {}  # 后续的指令下发都是遍历该数组
commandModedList: dict = {}  # 分类为索引，获取到某分类下的指令
pluginsList: list = getPluginsList(plugins_path, plugins_path_name)
pluginsMappedByName: dict = {}
pluginsLoading: bool = False
pluginsPath: str = None
methodName: str = None


def _(key: str, *args, **kwargs) -> object:
    return globals()[key]


def reloadPlugins(flag: bool = False):
    # 清空已有缓存
    Cache.cacheList = {}
    Cache.sqlStr = {}
    globals()['noticeListenerList'] = []
    globals()['requestListenerList'] = []
    globals()['metaListenerList'] = []
    globals()['messageListenerList'] = []
    globals()['commandListenerList'] = []  # 后续的菜单都是遍历该数组生成
    globals()['pluginsData'] = []
    globals()['commandPluginsList'] = {}  # 后续的指令下发都是遍历该数组
    globals()['commandModedList'] = {}  # 分类为索引，获取到某分类下的指令
    globals()['pluginsList'] = getPluginsList(plugins_path, plugins_path_name)
    globals()['pluginsMappedByName'] = {}
    globals()['pluginsLoading'] = False
    globals()['pluginsPath'] = None
    globals()['methodName'] = None

    # Load Plugins
    globals()['pluginsLoading'] = True

    for i in _('pluginsList'):
        p('Load Plugin:', i)
        try:
            module = importlib.import_module(f'plugins.{i}')

            clist = {
                'name': getattr(module, '_name', '插件名'),
                'version': getattr(module, '_version', '1.0.0'),
                'description': getattr(module, '_description', '插件'),
                'author': getattr(module, '_author', '插件作者'),
                'cost': getattr(module, '_cost', 0.00),
                'cwd': i
            }
            _('pluginsData').append(clist)
            _('pluginsMappedByName')[i] = clist

            p('Loading', i, '...')
            module = getattr(module, i)
            globals()['pluginsPath'] = i

            with module(Struct()):
                pass

            for l in dir(module):
                if l.startswith('_') or not callable(getattr(module, l)):
                    continue
                try:
                    globals()['methodName'] = l
                    getattr(module, l).__call__()
                except Exception:
                    pass
        except Exception:
            p(f'An error was made by loading plugins: {i}\n{traceback.format_exc()}')
            _('pluginsList').remove(i)

    # Load Caches
    loadCache(
        commandModedList=_('commandModedList'),
        commandPluginsList=_('commandPluginsList'),
        commandListenerList=_('commandListenerList'),
        messageListenerList=_('messageListenerList'),
        metaListenerList=_('metaListenerList'),
        requestListenerList=_('requestListenerList'),
        noticeListenerList=_('noticeListenerList'),
        pluginsList=_('pluginsList'),
        pluginsData=_('pluginsData'),
        pluginsMappedByName=_('pluginsMappedByName')
    )

    globals()['pluginsLoading'] = False
    return {"code": 200}


def openFile(path):
    ret = str()
    with open(path, 'r') as f:
        ret = f.read()
    return ret


def CallApi(api, parms, uuid=None, httpurl=None, access_token=None, ob=None, timeout=10):
    if ob != None:
        if isinstance(ob, dict):
            httpurl = ob.get("httpurl")
            access_token = ob.get("secret")
        elif isinstance(ob, BotSettingsModel):
            httpurl = ob._get("httpurl")
            access_token = ob._get("secret")
    elif httpurl != None and access_token != None:
        pass
    elif uuid != None:
        ob = BotSettingsModel(uuid=uuid)
        httpurl = ob._get("httpurl")
        access_token = ob._get("secret")
    
    data = requests.post(url='{0}/{1}?access_token={2}'.format(httpurl, api, access_token), json=parms, timeout=timeout)
    return data.json()


def send(uuid, uid, content, gid=None):
    if gid == None:
        dataa = CallApi('send_msg', {'user_id': uid, 'message': content}, uuid)
    else:
        dataa = CallApi('send_msg', {'group_id': gid, 'message': content}, uuid)
    if dataa.get('status') != 'failed':
        mid = dataa.get('data').get('message_id')
    else:
        mid = None
    return mid


# ======上报处理逻辑======
def requestInit(se: dict, uuid: str):
    message = se.get('message')
    if se.get('meta_event_type') == 'heartbeat':
        p('Pass heartbeat event.')
        return None

    # 初始化各项
    args = se.get("message").split() if se.get('message') else None  # 初始化参数
    messageType = 'cid' if se.get('channel_id') else 'qn'  # 消息来源（频道或群组）
    botSettings = BotSettingsModel(uuid=uuid)  # 机器人实例设置
    groupSettings = GroupSettingsModel(uuid=uuid, qn=se.get('group_id'), connectQQ=se.get('user_id'))
    if se.get('user_id'):
        userInfo = UserInfoModel(qn=se.get('user_id'), uuid=uuid, value=0)
        userCoin = userInfo._get('value', -1)
        isGlobalBanned = BlackListModel(uuid=uuid, qn=se.get('user_id'), reason='Debug', time=114514)
        if isGlobalBanned.exists == False:
            isGlobalBanned._delete()
            del isGlobalBanned
            isGlobalBanned = None
    else:
        userInfo = None
        userCoin = -1
        isGlobalBanned = None

    pluginsList = BotPluginsModel()._get(uuid=uuid)

    struct = Struct(
        args=args,
        messageType=messageType,
        botSettings=botSettings,
        userCoin=userCoin,
        isGlobalBanned=isGlobalBanned,
        groupSettings=groupSettings,
        userInfo=userInfo,
        pluginsList=pluginsList,
        se=se,
        uuid=uuid,
        message=message,
    )
    p(f'Struct was created.')

    pbf = PBF(struct)
    client = Client(struct)
    banwords = BanWords(struct)
    menu = Menu(struct)
    p('Inited all vars.')

    if isGlobalBanned == None and se.get('group_id') != None:
        if not groupSettings._get("power", True):
            if message == '开机':
                if se.get('sender').get('role') != 'member' or se.get('user_id') == botSettings._get('owner') or se.get(
                        'user_id') == botSettings._get('second_owner'):
                    groupSettings._set(power=1)
                    client.msg(
                        TextStatement(f'{botSettings._get("name")}开机成功！')
                    ).send()
                else:
                    client.msg(
                        FaceStatement(151),
                        TextStatement('就你？先拿到管理员再说吧！')
                    ).send()
            elif message:
                if (f'[CQ:at,qq={botSettings._get("myselfqn")}]' in message) or (
                        botSettings._get('name') in message) or ('机器人' in message):
                    client.msg(
                        TextStatement(f'{botSettings._get("name")}还没有开机哦~', 1),
                        TextStatement('发送 开机 可以开启机器人！')
                    ).send()
            banwords.check(False)
            p('Bot is shutdowned.')
            return
    elif isGlobalBanned != None:
        banwords.check(True)
        p(f"User: {se.get('user_id')} is banned")
        return
    p('Passed banned check')

    settings = groupSettings

    if se.get('post_type') == 'notice':
        # 群通知
        for i in Cache.get('noticeListenerList', []):
            copy.deepcopy(pbf).checkPromiseAndRun(i)
        return

    elif se.get('post_type') == 'request':
        # 请求
        for i in Cache.get('requestListenerList', []):
            copy.deepcopy(pbf).checkPromiseAndRun(i)
        return

    elif se.get('post_type') == 'meta_event':
        for i in Cache.get('metaListenerList', []):
            copy.deepcopy(pbf).checkPromiseAndRun(i)
        return

    else:
        for i in Cache.get('messageListenerList', []):
            copy.deepcopy(pbf).checkPromiseAndRun(i)

        commandPluginsList = Cache.get('commandPluginsList')

        p('Handle events finished.')
        only_for_uid = pbf.getUidOnly()

        try:
            cq = CQCode(message).get('file', type='image')
            if len(cq) <= 0:
                dataa = client.CallApi('ocr_image', {'image': cq[0]})
                message = ''
                datajson = dataa.get('data').get('texts')
                for i in datajson:
                    message += i.get('text')
        except Exception as e:
            pbf.logger.warn(e, 'ocr_image')

        # 指令监听器
        commandListener = CommandListener(struct)
        if commandListener.get() != 404:
            if message == '退出':
                commandListener.remove()
                client.msg(TextStatement('退出！')).send()
                return True
            else:
                pbf.execPlugin(commandListener.get().get('func'))
                return True

        # 指令
        noticeFlag = False

        def runCommand(i, content, message):
            lengthmx = len(content)
            if message[0:lengthmx] == content:
                # 提示<>
                for arg in args:
                    if '>' in arg or '<' in arg:
                        client.msg(TextStatement('温馨提示，指令列表中的<>符号请忽略！')).send()
                        break
                message = message.replace(content, '', 1).replace('  ', ' ').lstrip().rstrip()
                # ocrImage = message
                se['message'] = message
                struct.se = se
                struct.message = message
                PBF(struct).checkPromiseAndRun(i, True, True, content)
                return True

            # 检测
            lengthmx = len(content.lstrip().rstrip())
            if message[0:lengthmx] == content.lstrip().rstrip():
                global noticeFlag
                noticeFlag = True
            return False

        atStr = '[CQ:at,qq=' + str(botSettings._get('myselfqn')) + '] '
        if message[0:len(atStr)] == atStr:
            message = message.replace(atStr, '', 1)

        if settings._get("v_command"):
            v_command_list = settings._get("v_command").split()
        else:
            v_command_list = []

        if (not only_for_uid) or (v_command_list):
            for l in pluginsList:
                if commandPluginsList.get(l.get('path')) == None:
                    continue
                for i in commandPluginsList.get(l.get('path')):
                    # 识别指令
                    if (not only_for_uid) or (i.get("content").strip() in v_command_list):
                        if runCommand(i, i.name, message):
                            return
                    for alia in i.alias:
                        if (not only_for_uid) or (alia.strip() in v_command_list):
                            if runCommand(i, alia, message):
                                return

        if noticeFlag and not only_for_uid:
            client.msg(TextStatement("请注意指令每一部分之间有一个空格！！！")).send()

        # 分类菜单
        for i in menu.getModedMenu():
            menuStr = i.replace(' ', '')
            if message[0:len(menuStr)] == menuStr:
                p(f'Send SingleMenu: {i}')
                menu.sendSingleMenu(i)


def loadCache(**kwargs):
    '''在对应键不存在的时候设置缓存'''
    for key, value in kwargs.items():
        if (Cache.get(key) == None):
            Cache.set(key, value)


utils = Utils()


def p(*str):
    print('PBF Server:', *str)
