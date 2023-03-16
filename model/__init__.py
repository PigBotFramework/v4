import mysql, cache

class ModelBase:
    sql_update: str = "UPDATE `{}` _set {} WHERE {}"
    sql_insert: str = "INSERT INTO `{}` ({}) VALUES {}"
    sql_delete: str = "DELETE * FROM `{}` WHERE {}"
    sql_whereCase: str = ""
    sql_whereList: list = []
    
    db_table: str = None
    db_perfix: str = "bot_"
    
    col: list = []
    cache = None
    map: list = []
    args: list = []
    
    format_insert: list = []
    format_update: list = []
    
    def _getTableName(self):
        return self.db_perfix + self.db_table
        
    def _c(self):
        # TODO 测试时这里返回特殊字符串，生产使用请注释
        return self.db_table.replace(self.db_perfix, "")
        return "db_" + self._getTableName()
    
    def _getCol(self):
        for i in dir(self):
            if i[0:1] == "_" or not callable(getattr(self, i)):
                continue
            name = i
            i = getattr(self, i)
            desc = i.__doc__
            default = i()
            _type = type(name)
            self.col.append({
                "desc": desc,
                "name": name,
                "default": default,
                "type": _type
            })
    
    def __init__(self, **kwargs):
        self.args = kwargs
        self.db_table = self.db_perfix + self.db_table
        
        # 初始化数据
        self._getCol()
        self._refresh()
        
        # 生成where子句
        for i in self.map:
            self.sql_whereCase += "`{}` = %s".format(i)
            self.sql_whereList.append(self.args.get(i))
    
    def _initTable(self):
        return self
    
    def _get(self, key: str, *args, **kwargs):
        return self.cache.get(key, *args, **kwargs)
    
    def _insert(self, **kwargs):
        insertList: list = []
        for i in self.col:
            insertList.append(kwargs.get(i))
        self.format_insert.append(insertList)
        return self
    
    def _delete(self):
        mysql.commonx(self.sql_delete.format(self.db_table, self.sql_whereCase), tuple(self.sql_whereList))
        return self
    
    def _set(self, **kwargs):
        for k, v in kwargs.items():
            self.format_update.append({
                "key": k,
                "value": v
            })
            
            # 修改缓存
            _cache = cache.cacheList
            cacheList: list = []
            map: list = ["_db_table"]
            self.args["_db_table"] = self._c()
            map += self.map
            for i in map:
                cacheList.append(_cache)
                _cache = _cache.get(self.args.get(i))
                if _cache == None:
                    raise Exception("Key Not Found.")
            
            _cache[k] = v
            
            listLength = len(cacheList) - 1
            while listLength >= 0:
                _temp = cacheList[-listLength]
                _temp[map[-listLength]] = _cache
                _cache = _temp
                listLength -= 1
            
            cache.cacheList = _cache
            self.cache[k] = v
        return self
    
    def __insert(self):
        pass
        
    def __update(self):
        pass
    
    def _sync(self):
        self._insert()
        self._update()
        
    def _refresh(self):
        self.cache = cache.get(self._c())
        
        # 初始化数据表
        if self.cache == None:
            self._initTable()
            
        # 获取具体cache
        iter = 0
        for i in self.map:
            _cache = self.cache
            self.cache = self.cache.get(self.args.get(i))
            if self.cache == None:
                raise Exception("Key Not Found.")
            iter += 1

class TestModel(ModelBase):
    db_table = "botBotconfig"
    map = ["uuid"]
    
    def name(self):
        """
        Test
        """
        return "test"
    
    def httpurl(self):
        """
        HttpUrl
        """
        return None

def mapDict(ob, key: str):
    obDict = {}
    for i in ob:
        obDict[i.get(key)] = i
    
    return obDict

if __name__ == "__main__":
    cache.connectSql('botBotconfig', 'SELECT * FROM `botBotconfig`', mapDict, 'uuid')
    
    model = TestModel(uuid="123456789")
    print(model._get("name"))
    model._set(name="123456")
    print(model._get("name"))
    model._set(secret="xxx")
    print("\ncacheListb ", model.cache)