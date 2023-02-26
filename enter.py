from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
import uvicorn, asyncio, traceback, yaml, time, random, importlib, requests, sys, hmac, os, json, math, datetime, pytz, urllib
import utils as uts
from urllib.request import urlopen
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from pbf import PBF
import mysql, cache
from client import Client
from PbfStruct import yamldata, Struct, noMap, mapDict, mapDictToList, mapDoubleDict
from utils import Utils, CQCode, Coin
from inspect import getmembers, isclass
from statement import Statement
from statement.TextStatement import TextStatement
from statement.ImageStatement import ImageStatement
from statement.FaceStatement import FaceStatement
from statement.AtStatement import AtStatement
from banwords import BanWords
from commandListener import CommandListener
from regex import Regex
from menu import Menu

requests.adapters.DEFAULT_RETRIES = 5

description = '''
> PigBotFramework is built on FastApi, all APIs are listed below and provide query parameters  
**Notice: 以下接口默认使用1000处理器，其他处理器用法相同**
'''
tags_metadata = [
    {
        "name": "上报接口",
        "description": "OneBot(v11)标准上报接口",
        "externalDocs": {
            "description": "OneBot Docs",
            "url": "https://onebot.dev/",
        },
    },
    {
        "name": "GOCQ接口",
        "description": "GOCQ操作接口",
        "externalDocs": {
            "description": "Go-CQHttp Docs",
            "url": "https://docs.go-cqhttp.org/",
        },
    },
    {
        "name": "其他接口",
        "description": "其他接口",
    },
]
app = FastAPI(
    title="PigBotFramework API",
    description=description,
    openapi_tags=tags_metadata,
    version="4.1.0",
    contact={
        "name": "xzyStudio",
        "url": "https://xzynb.top",
        "email": "gingmzmzx@gmail.com",
    },
)

# 初始化 slowapi，注册进 fastapi
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
port = str(sys.argv[1])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)

@app.post("/{}".format(port), tags=['上报接口'])
async def post_data(request: Request, X_Signature: Union[str, None] = Header(default=None)):
    """
    描述：**机器人事件POST上报接口**  
    身份验证：可通过`GET`参数`pswd`验证，或**通过header中的`X_Signature`验证身份**（OneBot标准）  
    上报数据：在Request请求体中以json格式  
    """
    try:
        # sha1校验防伪上报
        params = request.query_params
        botPswd = utils.getPswd(params.get("uuid"))
        if botPswd == params.get("pswd"):
            sig = botPswd
            received_sig = botPswd
        else:
            sig = utils.encryption(await request.body(), botPswd)
            received_sig = X_Signature[len('sha1='):] if X_Signature else False
        if sig == received_sig:
            se = await request.json()
            p(f'Recv: {se}')
            # botIns.CrashReport(se, params.get("uuid"))
            requestInit(se, params.get("uuid"), port)
        else:
            return {"code":403}
    except Exception as e:
        p(f'Crashed: {e}\n{traceback.format_exc()}')

@app.get("/{}/get".format(port), tags=['上报接口'])
async def get_data(uuid:str, pswd:str, params:str):
    """
    描述：**机器人事件GET上报接口**  
    身份验证：需提供`UUID`和`pswd`，**不可通过`X_Signature`验证身份**（不是OneBot规定的上报接口，可用于其他情况的上报）  
    上报数据：**`params`参数为`json_encode()`且`urlencode()`后的上报数据**  
    """
    if utils.getPswd(uuid) == pswd:
        requestInit(json.loads(params), uuid, port)
        return json.loads(params)
    else:
        return {"code":403}

@app.post("/{}/testSpeed".format(port), tags=['其他接口'])
@app.get("/{}/testSpeed".format(port), tags=['其他接口'])
@limiter.limit("12/minute")
async def webtestSpeed(request: Request, X_Forwarded_For: Union[str, None] = Header(default=None)):
    """
    描述：测试指令执行速度和延迟  
    频率限制：**12次/分钟**  
    测试方法：模拟执行`菜单`指令  
    """
    timeStart = time.time()
    message = "菜单 noreply"
    requestInit({'post_type': 'message', 'message_type': 'group', 'self_id': 3558267090, 'sub_type': 'normal', 'group_id': 763432519, 'message': message, 'sender': {'age': 0, 'area': '', 'card': '', 'level': '', 'nickname': '', 'role': 'owner', 'sex': 'unknown', 'title': '', 'user_id': 66600000}, 'user_id': 66600000, 'font': 0, 'raw_message': message}, "123456789", port)
    timeEnd = time.time()
    report = {"code":200,"port":int(port)%1000,"startTime":timeStart,"endTime":timeEnd,"cost":timeEnd-timeStart}
    return report

@app.post("/{}/status".format(port), tags=['其他接口'])
@app.get("/{}/status".format(port), tags=['其他接口'])
async def webstatus():
    """
    描述：获取处理器状态  
    返回值：`{"code":200}`  
    """
    return json.dumps({"code":200}, ensure_ascii=False)

@app.post("/{}/webhook".format(port), tags=['其他接口'])
async def webhook(request: Request, X_Hub_Signature: Union[str, None] = Header(default=None)):
    """
    描述：WebHooks接口  
    身份验证：header中的`X_Hub_Signature`  
    用途：用于自动pull插件  
    """
    # github加密是将post提交的data和WebHooks的secret通过hmac的sha1加密，放到HTTP headers的X-Hub-Signature参数中
    body = await request.json()
    token = utils.encryption(body, '123456')
    # 认证签名是否有效
    signature = X_Hub_Signature.split('=')[-1]
    if signature != token:
        return "token认证无效", 401
    data = json.loads(str(body, encoding = "utf8"))
    # 运行shell脚本，更新代码
    os.system('./pull.sh {0} {1} {2}'.format(data.get('repository').get('name'), data.get('repository').get('url'), data.get('repository').get('full_name')))
    return {"status": 200}

@app.get("/{}/overview".format(port), tags=['GOCQ接口'])
@app.post("/{}/overview".format(port), tags=['GOCQ接口'])
async def weboverview(uuid:str):
    """
    描述：获取机器人GOCQ数据概览  
    参数：`UUID` 机器人实例uuid  
    返回值：data[] 具体内容可以请求后查看  
    """
    try:
        botSettings = mysql.selectx('SELECT * FROM `botBotconfig` WHERE `uuid`="{0}";'.format(uuid))[0]
        
        # 尝试请求gocq获取gocq信息
        try:
            gocq = CallApi("get_version_info", {}, ob=botSettings, timeout=5).get("data")
            if gocq.get('app_name') != "go-cqhttp":
                return {'code':502}
        except Exception as e:
            print(e)
            return {'code':502}
        
        data = {'code':200,'go-cqhttp':gocq,'time':time.time()}
        # 获取各项数据
        # 1. 群聊列表
        groupList = CallApi('get_group_list', {}, ob=botSettings).get('data')
        data['groupCount'] = len(groupList)
        # 2. 好友列表
        friendList = CallApi('get_friend_list', {}, ob=botSettings).get('data')
        data['friendCount'] = len(friendList)
        # 3. 网络信息
        network = CallApi('get_status', {}, ob=botSettings).get('data')
        data['network'] = network.get('stat')
        
        return data
    except Exception as e:
        return traceback.format_exc()
    
@app.get("/{}/getFriendAndGroupList".format(port), tags=['GOCQ接口'])
async def webgetFriendAndGroupList(pswd:str, uuid:str):
    """
    描述：获取机器人好友和群聊列表  
    参数：`pswd:str` 密钥    `uuid:str` 实例uuid  
    返回值：`{"friendList":..., "groupList":...}`  
    """
    try:
        if pswd == utils.getPswd(uuid):
            groupList = CallApi('get_group_list', {}, uuid).get('data')
            friendList = CallApi('get_friend_list', {}, uuid).get('data')
            return {'friendList':friendList,'groupList':groupList}
        else:
            return 'Password error.'
    except Exception as e:
        return traceback.format_exc()

@app.get("/{}/getFriendList".format(port), tags=['GOCQ接口'])
async def webgetFriendList(pswd:str, uuid:str):
    """获取机器人好友列表"""
    if pswd == utils.getPswd(uuid):
        return CallApi('get_friend_list', {}, uuid).get('data')
    else:
        return 'Password error.'

@app.get("/{}/kickUser".format(port), tags=['GOCQ接口'])
async def webkickUser(pswd:str, uuid:str, gid:int, uid:int):
    """踢出某人"""
    if pswd == utils.getPswd(uuid):
        data = CallApi('set_group_kick', {'group_id':gid,'user_id':uid}, uuid)
        if data['status'] == 'ok':
            return 'OK.'
        else:
            return 'failed.'
    else:
        return 'Password error.'

@app.get("/{}/banUser".format(port), tags=['GOCQ接口'])
async def webBanUser(pswd:str, uuid:str, uid:int, gid:int, duration:int):
    """禁言某人"""
    if pswd == utils.getPswd(uuid):
        CallApi('set_group_ban', {'group_id':gid,'user_id':uid,'duration':duration}, uuid)
        return 'OK.'
    else:
        return 'Password error.'

@app.get("/{}/delete_msg".format(port), tags=['GOCQ接口'])
async def webDeleteMsg(pswd:str, uuid:str, message_id:str):
    """撤回消息"""
    if pswd == utils.getPswd(uuid):
        CallApi('delete_msg', {'message_id':message_id}, uuid)
        # commonx('DELETE FROM `botChat` WHERE `mid`="{0}"'.format(mid))
        return 'OK.'
    else:
        return 'Password error.'

@app.get("/{}/getMessage".format(port), tags=['GOCQ接口'])
async def webGetMessage(uuid:str, message_id:int):
    """获取消息"""
    try:
        return CallApi('get_msg', {'message_id':message_id}, uuid)
    except Exception as e:
        return traceback.format_exc()

@app.get("/{}/getForwardMessage".format(port), tags=['GOCQ接口'])
async def webGetForwardMessage(uuid:str, message_id:str):
    """获取合并转发消息"""
    try:
        return CallApi('get_forward_msg', {'message_id':message_id}, uuid)
    except Exception as e:
        return traceback.format_exc()

@app.get("/{}/getGroupHistory".format(port), tags=['GOCQ接口'])
async def webGetGroupHistory(uuid:str, group_id:int, message_seq:int=0):
    """获取群聊聊天记录"""
    try:
        if message_seq == 0:
            return CallApi('get_group_msg_history', {'group_id':group_id}, uuid)
        else:
            return CallApi('get_group_msg_history', {'group_id':group_id, "message_seq":message_seq}, uuid)
    except Exception as e:
        return traceback.format_exc()

@app.get("/{}/sendMessage".format(port), tags=['GOCQ接口'])
@app.post("/{}/sendMessage".format(port), tags=['GOCQ接口'])
async def webSendMessage(pswd:str, uuid:str, uid:int, gid:int, message:str):
    """发送消息"""
    if pswd == utils.getPswd(uuid):
        SendOld(uuid, uid, message, gid)
        return 'OK.'
    else:
        return 'Password error.'
        
@app.get("/{}/callApi".format(port), tags=['GOCQ接口'])
@app.post("/{}/callApi".format(port), tags=['GOCQ接口'])
async def webCallApi(uuid:str, name:str, pswd:str, params={}):
    """发送消息"""
    if pswd == utils.getPswd(uuid):
        return CallApi(name, json.loads(params), uuid)
    else:
        return 'Password error.'

@app.get("/{}/getGroupList".format(port), tags=['GOCQ接口'])
async def getGroupList(uuid:str):
    """获取某机器人群聊列表"""
    return CallApi('get_group_list', {}, uuid)
    
@app.get("/{}/getGroupDe".format(port), tags=['GOCQ接口'])
@limiter.limit("1/minute")
async def webgetGroupDe(uuid:str, request: Request):
    """
    获取某机器人群聊列表加最新一条消息
    频率限制6次每分钟
    """
    try:
        dataList = CallApi('get_group_list', {}, uuid)['data']
        for i in dataList:
            messages = CallApi('get_group_msg_history', {'group_id':i.get("group_id")}, uuid).get("data").get("messages")
            message = messages[-1].get("message")
            i['message'] = message
        return dataList
    except Exception as e:
        return e

@app.get("/{}/MCServer".format(port), tags=['其他接口'])
async def MCServer(msg:str, uuid:str, qn:int):
    """MC服务器消息同步"""
    print('服务器消息：')
    # msg = msg[2:-1]
    
    if msg != '' and '[Server] <' not in msg:
        msg = '[CQ:face,id=151] 服务器消息：'+str(msg)
        if 'logged in with entityid' in msg:
            msg1 = msg[0:msg.find('logged in with entityid')-1]
            msg = msg1 + '进入了游戏'
        
        SendOld(uuid, None, msg, qn)
    
    return '200 OK.'

@app.get('/{}/getPluginsData'.format(port), tags=['其他接口'])
async def webgetPluginsData():
    """刷新插件数据"""
    return cache.get('pluginsData', [])

@app.get('/{}/getPluginByName'.format(port), tags=['其他接口'])
async def webgetPluginByName(name: str):
    """刷新插件数据"""
    cpl = cache.get('commandPluginsList', {}).get(name)
    pmbn = cache.get('pluginsMappedByName', {}).get(name)
    return {'pluginData':pmbn, 'cmds':cpl}

@app.get('/{}/getGroupMemberList'.format(port), tags=['GOCQ接口'])
async def webGetGroupMemberList(uuid:str, gid:int):
    """获取群聊成员列表"""
    return CallApi('get_group_member_list', {'group_id':gid}, uuid)

@app.get('/{}/getGOCQConfig'.format(port), tags=['其他接口', 'GOCQ接口'])
async def webgetGOCQConfig(uin:int, host:str, port:int, uuid:str, secret:str, password:str="null", url:str="https://pbfpost.xzynb.top/1000/?uuid={0}"):
    '''生成GOCQ配置'''
    try:
        gocqConfig = json.loads('{"account": {"uin": 123, "password": null, "encrypt": false, "status": 0, "relogin": {"delay": 3, "interval": 3, "max-times": 0}, "use-sso-address": true, "allow-temp-session": false}, "heartbeat": {"interval": -1}, "message": {"post-format": "string", "ignore-invalid-cqcode": false, "force-fragment": false, "fix-url": false, "proxy-rewrite": "", "report-self-message": false, "remove-reply-at": false, "extra-reply-data": false, "skip-mime-scan": false}, "output": {"log-level": "trace", "log-aging": 1, "log-force-new": true, "log-colorful": false, "debug": false}, "default-middlewares": {"access-token": "", "filter": "", "rate-limit": {"enabled": false, "frequency": 1, "bucket": 1}}, "database": {"leveldb": {"enable": true}, "cache": {"image": "data/image.db", "video": "data/video.db"}}, "servers": [{"http": {"host": "1.1.1.1", "port": 2222, "timeout": 10, "long-polling": {"enabled": false, "max-queue-size": 2000}, "middlewares": {"access-token": "", "filter": "", "rate-limit": {"enabled": false, "frequency": 1, "bucket": 1}}, "post": [{"url": "http://127.0.0.1:8000/", "secret": "123456", "max-retries": 0, "retries-interval": 0}]}}]}')
        gocqConfig['account']['password'] = password
        gocqConfig['account']['uin'] = uin
        gocqConfig['servers'][0]['http']['host'] = host
        gocqConfig['servers'][0]['http']['port'] = port
        gocqConfig['servers'][0]['http']['post'][0]['url'] = url.format(uuid)
        gocqConfig['servers'][0]['http']['post'][0]['secret'] = secret
        gocqConfig['default-middlewares']['access-token'] = secret
        gocqConfig['servers'][0]['http']['middlewares']['access-token'] = secret
        filename = 'config-{0}.yml'.format(uuid)
        file = open("./resources/createimg/{0}".format(filename), 'w+', encoding='utf-8')
        yaml.dump(gocqConfig, file)
        file.close()
        return json.dumps(filename, ensure_ascii=False)
    except Exception as e:
        return e

@app.get("/{}/reloadPlugins".format(port), tags=['其他接口'])
async def webreloadPlugins():
    '''刷新插件及指令列表'''
    return reloadPlugins(port)

"""
@app.get("/{}/sendAll".format(port), tags=['其他接口', 'GOCQ接口'])
async def websendAll(pswd:str):
    '''机器人通知机器人主人'''
    try:
        if pswd == yamldata.get("self").get("pswd"):
            message = '请注意！机器人上报地址有更新，请将gocq的config.yml中的servers中的http中的post中的url改为以下值：\nhttps://pbfpost.xzynb.top/1000/?uuid={}\n如不及时更改会造成机器人无法使用，请注意！\n如有疑问，请联系 2417481092'.format(i.get("uuid"))
            for i in mysql.selectx('SELECT * FROM `botBotconfig`'):
                try:
                    SendOld(i.get('uuid'), i.get('owner'), message)
                except Exception as e:
                    pass
            return "OK"
        else:
            return "pswd error."
    except Exception as e:
        return e
"""

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
        except Exception as e:
            p(f'An error was made by loading plugins: {i}\n{traceback.format_exc()}')
            pluginsList.remove(i)
    
    
    cache.connectSql('keywordList', 'SELECT * FROM `botKeyword` WHERE `state` = 0', mapDictToList, 'uuid')
    cache.connectSql('botBotconfig', 'SELECT * FROM `botBotconfig`', mapDict, 'uuid')
    cache.connectSql('botWeijin', "SELECT * FROM `botWeijin` WHERE `state`=0 or `state`=3;", noMap)
    cache.connectSql('botReplace', "SELECT * FROM `botReplace`", noMap)
    cache.connectSql('settingName', "SELECT * FROM `botSettingName`", noMap)
    cache.connectSql('groupSettings', 'SELECT * FROM `botSettings`', mapDoubleDict, 'qn uuid')
    cache.connectSql('userCoin', "SELECT * FROM `botCoin`", mapDict, 'qn')
    cache.connectSql('botPluginsList', 'SELECT * FROM `botPlugins`', mapDictToList, 'uuid')
    cache.connectSql('globalBanned', "SELECT * FROM `botQuanping`", mapDict, 'qn')
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
        ob = mysql.selectx('SELECT * FROM `botBotconfig` WHERE `uuid`="{0}";'.format(uuid))[0]
        httpurl = ob.get("httpurl")
        access_token = ob.get("secret")
    
    data = requests.post(url='{0}/{1}?access_token={2}'.format(httpurl, api, access_token), json=parms, timeout=timeout)
    return data.json()

def SendOld(uuid, uid, content, gid=None):
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
    weijin = cache.get('botWeijin')
    kwrlist = cache.get('botReplace')
    settingName = cache.get('settingName')
    args = se.get("message").split() if se.get('message') else None # 初始化参数
    messageType = 'cid' if se.get('channel_id') else 'qn' # 消息来源（频道或群组）
    botSettings = cache.get('botBotconfig', {}).get(uuid) # 机器人实例设置
    groupSettings = None if se.get('group_id') == None else cache.get('groupSettings', {}).get(se.get('group_id'), {}).get(uuid) # 加载群聊设置
    if se.get('user_id'):
        userInfo = cache.get('userCoin', {}).get(se.get('user_id'))
        userCoin = -1 if userInfo == None else userInfo.get('value')
        isGlobalBanned = cache.get('globalBanned', {}).get(se.get('user_id'))
    else:
        userInfo = None
        userCoin = -1
        isGlobalBanned = None
    
    pluginsList = cache.get('botPluginsList', {}).get(uuid)
    
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
                    cache.set('groupSettings', groupSettings)
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
        for i in cache.get('noticeListenerList', []):
            pbf.checkPromiseAndRun(i)
        return 
        
    elif se.get('post_type') == 'request':
        # 请求
        for i in cache.get('requestListenerList', []):
            pbf.checkPromiseAndRun(i)
        return 
    
    elif se.get('post_type') == 'meta_event':
        for i in cache.get('metaListenerList', []):
            pbf.checkPromiseAndRun(i)
        return 
    
    else:
        for i in cache.get('messageListenerList', []):
            pbf.checkPromiseAndRun(i)
        
        if se.get('channel_id') == None and gid != None:
            # 防刷屏 TODO 该内容最好移动到查建中
            messagelist = cache.get('messagelist', [])
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
            cache.set('messagelist', messagelist)
        
        commandPluginsList = cache.get('commandPluginsList')
        
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
        except Exception as e:
            pass
        
        try:
            if gid != None:
                if settings.get('increase_verify') != 0:
                    if pbf.execPlugin('basic.getVerifyStatus()') == True and '人机验证 ' not in message:
                        client.CallApi('delete_msg', {'message_id':se.get('message_id')})
        except Exception as e:
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
                ocrImage = message
                se['message'] = message
                struct.se = se
                struct.message = message
                PBF(struct).checkPromiseAndRun(i, True, True, content)
                return True
            
            # 检测
            lengthmx = len(content.lstrip().rstrip())
            if message[0:lengthmx] == content.lstrip().rstrip():
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
        
        # 关键词回复
        if settings != None:
            kwFlag = 1 if settings.get('keywordReply') else 0
        else:
            kwFlag = 1
        if kwFlag and not only_for_uid:
            keywordlist = cache.get('keywordList').get(uuid)
            for i in keywordlist:
                replyFlag = False
                if userCoin >= i.get('coin') and (i.get("qn") == 0 or gid == i.get("qn")):
                    replyFlag = True
                if replyFlag == True:
                    replyKey = regex.replace(i.get('key'))
                    if regex.pair(replyKey, message):
                        regex.send(i.get('value'))
        
        # 分类菜单
        for i in menu.getModedMenu():
            if i.replace(' ', '') in message:
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
        if (cache.get(key) == None):
            cache.set(key, value)

utils = Utils()

def p(string: str):
    print(f'PBF Server: {string}')

def serve(port):
    p('Loading plugins...')
    reloadPlugins(port, True)
    p('Plugins loaded.')
    
    uts.scheduler.start()
    p('Scheduler started.')

    p(f'Running on {port}')
    uvicorn.run(app="enter:app",  host='0.0.0.0', port=int(port), reload=True, debug=True)

reloadPlugins(port)

if __name__ == '__main__':
    serve(port)