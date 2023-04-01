from . import Mysql

def set(key: str, value):
    '''
    Set or replace the key.
    Returns: void
    '''
    cacheList[key] = value

def get(key: str, default = None):
    '''
    Get the key value.
    Returns: key value or None
    '''
    return cacheList.get(key, default)

def delete(key: str):
    '''
    Delete the key.
    Returns: the deleted value or None`
    '''
    value = cacheList.get(key)
    cacheList.pop(key)
    return value

def check(key: str):
    '''
    Check if the key exists.
    Returns: boolean
    '''
    return key in cacheList

def connectSql(key: str, sql: str, mapFunc, arg: str = None):
    '''
    Connect Sql Select Statement with Cache Item
    '''
    res = mapFunc(Mysql.selectx(sql), arg)
    set(key, res)
    sqlStr[key] = {'sql':sql,'mapFunc':mapFunc,'arg':arg}

def disconnectSql(key: str):
    if sqlStr.get(key) != None:
        del sqlStr[key]

def refreshFromSql(_key: str = None):
    for key, value in sqlStr.items():
        if key == None or key == _key:
            func = value.get('mapFunc')
            print('cache refreshFromSql', key, value.get('sql'), value.get('arg'))
            set(key, func(Mysql.selectx(value.get('sql')), value.get('arg')))
        
def getSql(key: str):
    return sqlStr.get(key, {}).get('sql')


cacheList: dict = {}
sqlStr: dict = {}

if __name__ == '__main__':
    set('test', 'test')
    print(get('test'))
    print(delete('test'))