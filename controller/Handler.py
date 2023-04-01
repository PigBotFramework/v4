import asyncio, traceback, yaml, time, random, importlib, requests, sys, hmac, os, json, math, datetime, pytz, urllib
from controller import PBF, Mysql, Cache
from controller.Client import Client
from controller.PbfStruct import yamldata, Struct, noMap, mapDict, mapDictToList, mapDoubleDict
from utils import Utils, CQCode, Coin
from inspect import getmembers, isclass
from statement import Statement
from statement.TextStatement import TextStatement
from statement.ImageStatement import ImageStatement
from statement.FaceStatement import FaceStatement
from statement.AtStatement import AtStatement
from controller.Banwords import BanWords
from controller.CommandListener import CommandListener
from controller.Regex import Regex
from controller.Logger import Logger
from controller.Menu import Menu

def reloadPlugins(port: int, flag=False):
    noticeListenerList = []
    requestListenerList = []
    metaListenerList = []
    messageListenerList = []
    ChatterBotListener = [] # 已弃用 ChatterBot监听
    commandListenerList = [] # 后续的菜单都是遍历该数组生成
    pluginsData = []
    commandPluginsList = {} # 后续的指令下发都是遍历该数组
    commandModedList = {} # 分类为索引，获取到某分类下的指令
    pluginsList = getPluginsList()
    pluginsMappedByName = {}
    
    # 引入
    for i in pluginsList:
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
            pluginsData.append(clist)
            pluginsMappedByName[i] = clist
            
            
            with getattr(module, i)(None) as v:
                for cmd in v:
                    # p(f'Plugin: {i} Cmds: {cmd.name} Type: {cmd.type}')
                    if cmd.type == 'command':
                        if commandPluginsList.get(i) == None:
                            commandPluginsList[i] = []
                        commandPluginsList[i].append(cmd)

                        if commandModedList.get(cmd.mode) == None:
                            commandModedList[cmd.mode] = []
                        commandModedList[cmd.mode].append(cmd)

                        commandListenerList.append(cmd)
                    elif cmd.type == 'meta':
                        metaListenerList.append(cmd)
                    elif cmd.type == 'notice':
                        noticeListenerList.append(cmd)
                    elif cmd.type == 'request':
                        requestListenerList.append(cmd)
                    elif cmd.type == 'message':
                        messageListenerList.append(cmd)
        except Exception:
            p(f'An error was made by loading plugins: {i}\n{traceback.format_exc()}')
            pluginsList.remove(i)
    
    
    Cache.connectSql('keywordList', 'SELECT * FROM `botKeyword` WHERE `state` = 0', mapDictToList, 'uuid')
    Cache.connectSql('botBotconfig', 'SELECT * FROM `botBotconfig`', mapDict, 'uuid')
    Cache.connectSql('botWeijin', "SELECT * FROM `botWeijin` WHERE `state`=0 or `state`=3;", noMap)
    Cache.connectSql('botReplace', "SELECT * FROM `botReplace`", noMap)
    Cache.connectSql('settingName', "SELECT * FROM `botSettingName`", noMap)
    Cache.connectSql('groupSettings', 'SELECT * FROM `botSettings`', mapDoubleDict, 'qn uuid')
    Cache.connectSql('userCoin', "SELECT * FROM `botCoin`", mapDict, 'qn')
    Cache.connectSql('botPluginsList', 'SELECT * FROM `botPlugins`', mapDictToList, 'uuid')
    Cache.connectSql('globalBanned', "SELECT * FROM `botQuanping`", mapDict, 'qn')
    loadCache(
        commandModedList = commandModedList,
        commandPluginsList = commandPluginsList,
        commandListenerList = commandListenerList,
        messageListenerList = messageListenerList, 
        metaListenerList = metaListenerList,
        requestListenerList = requestListenerList,
        noticeListenerList = noticeListenerList,
        pluginsList = pluginsList,
        ChatterBotListener = ChatterBotListener,
        pluginsData = pluginsData,
        pluginsMappedByName = pluginsMappedByName
    )
    
    return {"code":200}

def getPluginsList():
    pluginsList = os.listdir('plugins')
    for dbtype in pluginsList[::]:
        if os.path.isfile(os.path.join('plugins',dbtype)) or dbtype.startswith('__'):
            pluginsList.remove(dbtype)
    return pluginsList

def openFile(path):
    with open(path, 'r') as f:
        return f.read()

def CallApi(api, parms, uuid=None, httpurl=None, access_token=None, ob=None, timeout=10):
    if ob != None:
        httpurl = ob.get("httpurl")
        access_token = ob.get("secret")
    elif httpurl != None and access_token != None:
        pass
    elif uuid != None:
        ob = Mysql.selectx('SELECT * FROM `botBotconfig` WHERE `uuid`="{0}";'.format(uuid))[0]
        httpurl = ob.get("httpurl")
        access_token = ob.get("secret")
    
    data = requests.post(url='{0}/{1}?access_token={2}'.format(httpurl, api, access_token), json=parms, timeout=timeout)
    return data.json()

def send(uuid, uid, content, gid=None):
    if gid == None:
        dataa = CallApi('send_msg', {'user_id':uid,'message':content}, uuid)
    else:
        dataa = CallApi('send_msg', {'group_id':gid,'message':content}, uuid)
    if dataa.get('status') != 'failed':
        mid = dataa.get('data').get('message_id')
    else:
        mid = None
    return mid


# ======上报处理逻辑======
def requestInit(se: dict, uuid: str, port: int):
    message = se.get('message')
    if se.get('meta_event_type') == 'heartbeat':
        p('Pass heartbeat event.')
        return None
    
    # 初始化各项
    args = se.get("message").split() if se.get('message') else None # 初始化参数
    messageType = 'cid' if se.get('channel_id') else 'qn' # 消息来源（频道或群组）
    botSettings = Cache.get('botBotconfig', {}).get(uuid) # 机器人实例设置
    groupSettings = None if se.get('group_id') == None else Cache.get('groupSettings', {}).get(se.get('group_id'), {}).get(uuid) # 加载群聊设置
    if se.get('user_id'):
        userInfo = Cache.get('userCoin', {}).get(se.get('user_id'))
        userCoin = -1 if userInfo == None else userInfo.get('value')
        isGlobalBanned = Cache.get('globalBanned', {}).get(se.get('user_id'))
    else:
        userInfo = None
        userCoin = -1
        isGlobalBanned = None
    
    pluginsList = Cache.get('botPluginsList', {}).get(uuid)
    
    struct = Struct(
        args = args,
        messageType = messageType,
        botSettings = botSettings,
        groupSettings = groupSettings,
        userCoin = userCoin,
        isGlobalBanned = isGlobalBanned,
        userInfo = userInfo,
        pluginsList = pluginsList,
        port = port,
        se = se,
        uuid = uuid,
        message = message,
    )
    p(f'Struct was created.')
    
    pbf = PBF(struct)
    logger = Logger(struct)
    regex = Regex(struct)
    client = Client(struct)
    banwords = BanWords(struct)
    menu = Menu(struct)
    p('Inited all vars.')
    
    if not groupSettings and se.get("group_id") != None: # 初始化群聊设置
        pbf.groupInit()
        return 

    if isGlobalBanned == None and se.get('group_id') != None:
        if not groupSettings.get("power", True):
            if message == '开机':
                if se.get('sender').get('role') != 'member' or se.get('user_id') == botSettings.get('owner') or se.get('user_id') == botSettings.get('second_owner'):
                    groupSettings['power'] = 1
                    Cache.set('groupSettings', groupSettings)
                    client.msg(
                        TextStatement(f'{botSettings.get("name")}开机成功！')
                    ).send()
                else:
                    client.msg(
                        FaceStatement(151),
                        TextStatement('就你？先拿到管理员再说吧！')
                    ).send()
            elif message:
                if (f'[CQ:at,qq={botSettings.get("myselfqn")}]' in message) or (botSettings.get('name') in message) or ('机器人' in message):
                    client.msg(
                        TextStatement(f'{botSettings.get("name")}还没有开机哦~', 1),
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

    gid = se.get('group_id')
    cid = se.get('channel_id')
    uid = se.get('user_id')
    settings = groupSettings

    if se.get('post_type') == 'notice':
        # 群通知
        for i in Cache.get('noticeListenerList', []):
            pbf.checkPromiseAndRun(i)
        return 
        
    elif se.get('post_type') == 'request':
        # 请求
        for i in Cache.get('requestListenerList', []):
            pbf.checkPromiseAndRun(i)
        return 
    
    elif se.get('post_type') == 'meta_event':
        for i in Cache.get('metaListenerList', []):
            pbf.checkPromiseAndRun(i)
        return 
    
    else:
        for i in Cache.get('messageListenerList', []):
            pbf.checkPromiseAndRun(i)
        
        if se.get('channel_id') == None and gid != None:
            # 防刷屏 TODO 该内容最好移动到查建中
            messagelist = Cache.get('messagelist', [])
            mlob = utils.findObject('qn', gid, messagelist)
            mlo = mlob.get('object')
            if mlo == 404:
                messagelist.append({'qn':gid, 'uid':uid, 'times':1})
            else:
                arrnum = mlob.get('num')
                if mlo.get('uid') == uid:
                    if mlo.get('times') >= int(settings.get('AntiswipeScreen')):
                        messagelist[arrnum]['times'] = 1
                        if se.get('sender').get('role') == "member":
                            datajson = client.CallApi('set_group_ban', {"group_id":gid,"user_id":uid,"duration":600})
                            if datajson['status'] != 'ok':
                                client.msg(
                                    FaceStatement(151),
                                    TextStatement('检测到刷屏，但禁言失败！')
                                ).send()
                            else:
                                client.msg(
                                    FaceStatement(54),
                                    TextStatement('检测到刷屏，已禁言！')
                                ).send()
                    else:
                        messagelist[arrnum]['times'] += 1
                    # 禁言警告
                    if mlo.get('times') == int(settings.get('AntiswipeScreen'))-1 and se.get('sender').get('role') == "member":
                        client.msg(
                            TextStatement('刷屏禁言警告', 1),
                            TextStatement('请不要连续发送消息超过设定数量！')
                        ).send()
                else:
                    messagelist[arrnum]['times'] = 1
                    messagelist[arrnum]['uid'] = uid
            Cache.set('messagelist', messagelist)
        
        commandPluginsList = Cache.get('commandPluginsList')
        
        p('Handle events finished.')
        # 跟班模式
        only_for_uid = True
        if se.get("group_id"):
            if botSettings.get("only_for_uid") and botSettings.get("only_for_uid") == uid:
                only_for_uid = False
            if len(settings.get("only_for_uid")) != 0 and str(uid) in settings.get("only_for_uid").split():
                only_for_uid = False
            if (not botSettings.get("only_for_uid")) and (len(settings.get("only_for_uid")) == 0):
                only_for_uid = False
            if uid == yamldata.get("chat").get("owner"):
                only_for_uid = False
        else:
            only_for_uid = False
        
        if uid != botSettings.get('owner') and se.get('channel_id') == None and gid == None and botSettings.get("reportPrivate"):
            client.msg(
                FaceStatement(151),
                TextStatement('主人，有人跟我说话话~', 1),
                TextStatement(f'内容为：{message}', 1),
                TextStatement(f'回复请对我说：回复|{se.get("user_id")}|{se.get("message_id")}|<回复内容>')
            ).custom(botSettings.get('owner'))
            if uid != botSettings.get('second_owner'):
                client.msg(
                    FaceStatement(151),
                    TextStatement('副主人，有人跟我说话话~', 1),
                    TextStatement(f'内容为：{message}', 1),
                    TextStatement(f'回复请对我说：回复|{se.get("user_id")}|{se.get("message_id")}|<回复内容>')
                ).custom(botSettings.get('second_owner'))
        
        if '[CQ:at,qq='+str(botSettings.get('owner'))+']' in message and botSettings.get("reportAt"):
            client.msg(
                FaceStatement(151),
                TextStatement('主人，有人艾特你~', 1),
                TextStatement(f'消息内容：{message}', 1),
                TextStatement(f'来自群：{gid}', 1),
                TextStatement(f'来自用户：{uid}')
            ).custom(botSettings.get('owner'))
            
        if '[CQ:at,qq='+str(botSettings.get('second_owner'))+']' in message and botSettings.get("reportAt"):
            client.msg(
                FaceStatement(151),
                TextStatement('副主人，有人艾特你~', 1),
                TextStatement(f'消息内容：{message}', 1),
                TextStatement(f'来自群：{gid}', 1),
                TextStatement(f'来自用户：{uid}')
            ).custom(botSettings.get('second_owner'))
        
        if (f'[CQ:at,qq={botSettings.get("myselfqn")}]' in message) and (userCoin == -1) and not only_for_uid:
            client.msg(
                Statement('reply', id=se.get('message_id')),
                TextStatement(f'{botSettings.get("name")}想起来你还没有注册哦~',1),
                TextStatement('发送“注册”可以让机器人认识你啦QAQ')
            ).send()
        
        try:
            cq = CQCode(message).get('file', type='image')
            if len(cq) <= 0:
                dataa = client.CallApi('ocr_image', {'image':cq[0]})
                message = ''
                datajson = dataa.get('data').get('texts')
                for i in datajson:
                    message += i.get('text')
        except Exception:
            pass
        
        try:
            if gid != None:
                if settings.get('increase_verify') != 0:
                    if pbf.execPlugin('basic.getVerifyStatus()') == True and '人机验证 ' not in message:
                        client.CallApi('delete_msg', {'message_id':se.get('message_id')})
        except Exception:
            pass
        
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
        
        atStr = '[CQ:at,qq='+str(botSettings.get('myselfqn'))+'] '
        if message[0:len(atStr)] == atStr:
            message = message.replace(atStr, '', 1)
        
        if settings.get("v_command"):
            v_command_list = settings.get("v_command").split()
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
        
        if message[0:10] == '[CQ:reply,' and '撤回' in message:
            if uid == botSettings.get('owner') or uid == botSettings.get('second_owner') or se.get('sender').get('role') != 'member':
                reply_id = CQCode(message).get('id', type='reply')
                client.CallApi('delete_msg', {'message_id':reply_id})
                client.CallApi('delete_msg', {'message_id':se.get('message_id')})
                return 
            else:
                client.msg(TextStatement('[CQ:face,id=151] 就你？先拿到管理员再说吧！')).send()
        
        # 违禁词检查
        if settings != None:
            weijinFlag = 1 if settings.get('weijinCheck') else 0
        else:
            weijinFlag = 1
        if banwords.check(weijinFlag) == True and not only_for_uid:
            return 'OK.'
        
        try:
            # 关键词回复
            if settings != None:
                kwFlag = 1 if settings.get('keywordReply') else 0
            else:
                kwFlag = 1
            if kwFlag and not only_for_uid:
                keywordlist = Cache.get('keywordList').get(uuid, [])
                for i in keywordlist:
                    replyFlag = False
                    if userCoin >= i.get('coin') and (i.get("qn") == 0 or gid == i.get("qn")):
                        replyFlag = True
                    if replyFlag == True:
                        replyKey = regex.replace(i.get('key'))
                        if regex.pair(replyKey, message):
                            regex.send(i.get('value'))
        except Exception:
            logger.warn(f'{traceback.format_exc()}')
        
        # 分类菜单
        for i in menu.getModedMenu():
            menuStr = i.replace(' ', '')
            if message[0:len(menuStr)] == menuStr:
                p(f'Send SingleMenu: {i}')
                menu.sendSingleMenu(i)
        
        # 回复
        if not only_for_uid:
            if gid != None or cid != None:
                if gid != None:
                    randnum = settings.get('replyPercent')
                elif cid != None:
                    randnum = 100
                rand = random.randint(1, randnum)
                if (rand == 1) or ('[CQ:at,qq='+str(botSettings.get('myselfqn'))+']' in message):
                    pbf.data.message = pbf.data.se['message'] = pbf.data.message.replace('[CQ:at,qq='+str(botSettings.get('myselfqn'))+']', "")
                    pbf.reply()
            else:
                pbf.reply()

def loadCache(**kwargs):
    '''在对应键不存在的时候设置缓存'''
    for key, value in kwargs.items():
        if (Cache.get(key) == None):
            Cache.set(key, value)

utils = Utils()

def p(string: str):
    print(f'PBF Server: {string}')