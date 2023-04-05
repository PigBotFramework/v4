from .PbfStruct import yamldata
import pymysql

sql_config = "SELECT * FROM `botSettings` WHERE `uuid` = %s and {}"
sql_coinlist = "SELECT * FROM `botCoin` WHERE `uuid` = %s and {}"
sql_quanjing = "SELECT * FROM `botQuanping` WHERE {}"
sql_keywordListSql = "SELECT * FROM `botKeyword` WHERE `uuid` = %s and `state`=0"

def selectx(sqlstr, params=(), host=yamldata.get('database').get('dbhost'), user=yamldata.get('database').get('dbuser'), password=yamldata.get('database').get('dbpassword'), database=yamldata.get('database').get('dbname')):
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sqlstr, params)
    except Exception as e:
        print("selectx execute error\nsql: {}\nparams: {}\nerror: {}".format(sqlstr, params, e))
        raise Exception(e)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def commonx(sqlstr, params=(), host=yamldata.get('database').get('dbhost'), user=yamldata.get('database').get('dbuser'), password=yamldata.get('database').get('dbpassword'), database=yamldata.get('database').get('dbname')):
    connect = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sqlstr, params)
    except Exception as e:
        print("commonx execute error\nsql: {}\nparams: {}\nerror: {}".format(sqlstr, params, e))
        raise Exception(e)
    connect.commit()
    cursor.close()
    connect.close()

def getConfig(uuid, key, value, template, sql=None):
    if sql == None:
        sql = '`{0}`=%s'.format(key)
        template = template.format(sql)
        ob = selectx(template, (uuid, value)) if uuid else selectx(template, (value))
    else:
        template = template.format(sql)
        ob = selectx(template, (uuid)) if uuid else selectx(template)
    
    return None if not ob else ob