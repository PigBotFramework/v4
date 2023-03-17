import mysql, cache

class ModelBase:
    sql_update: str = "UPDATE `{}` SET {} WHERE {}"
    sql_insert: str = "INSERT INTO `{}` ({}) VALUES {}"
    sql_delete: str = "DELETE FROM `{}` WHERE {}"
    sql_whereCase: str = ""
    sql_whereList: list = []
    
    db_table: str = None
    db_perfix: str = "bot_"
    
    col: list = []
    cache = None
    map: list = []
    args: list = []
    exists: bool = True
    
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
        self._refresh(insertFlag=True, kwargs=kwargs)
        self._refreshWhereCase()
    
    def _refreshWhereCase(self):
        # 生成where子句
        self.sql_whereCase = ""
        self.sql_whereList = []
        
        flag: bool = False
        for i in self.map:
            if flag:
                self.sql_whereCase += ", "
            else:
                flag = True
            self.sql_whereCase += "`{}` = %s".format(i)
            self.sql_whereList.append(self.args.get(i))
    
    def _initTable(self):
        return self
    
    def _get(self, key: str, *args, **kwargs):
        return self.cache.get(key, *args, **kwargs)
    
    def _insert(self, **kwargs):
        # 在缓存中新增
        strr: str = ""
        for i in self.map:
            if kwargs.get(i) == None:
                raise Exception("Key Not Found.")
            strr += f"[{eval(str(kwargs.get(i)))}]"
        exec(f"cache.cacheList{strr} = {eval(str(kwargs))}")
        
        self.cache = kwargs
        self.args = kwargs
        self._refreshWhereCase()
        
        # 更新到同步列表
        insertList: list = []
        for i in self.col:
            insertList.append(kwargs.get(i.get('name')))
        self.format_insert.append(insertList)
        return self
    
    def _delete(self):
        # 数据库删除
        mysql.commonx(self.sql_delete.format(self._c(), self.sql_whereCase), tuple(self.sql_whereList))
        
        # 缓存删除
        strr: str = ""
        for i in self.map:
            strr += f"[{eval(str(self.args.get(i)))}]"
        exec(f"del cache.cacheList{strr}")
        
        return self
    
    def _set(self, **kwargs):
        for k, v in kwargs.items():
            self.format_update.append({
                "key": k,
                "value": v
            })
            
            # 修改缓存
            '''
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
            '''
            
            self.cache[k] = v
            
            strr: str = ""
            for i in self.map:
                strr += f"[{eval(str(self.args.get(i)))}]"
            exec(f"cache.cacheList{strr} = {eval(str(self.cache))}")
        return self
    
    def __insert(self):
        colname: str = ""
        flag: bool = False
        for i in self.col:
            name = i.get('name')
            if flag:
                colname += ", "
            else:
                flag = True
            colname += f"`{name}`"
        
        vs: str = ""
        vsl: list = []
        fflag: bool = False
        for i in self.format_insert:
            strr: str = ""
            flag: bool = False
            for l in i:
                if flag:
                    strr += ", "
                else:
                    flag = True
                strr += "%s"
            if fflag:
                vs += ", "
            else:
                fflag = True
            
            vs += f"({strr})"
            vsl += i
        
        mysql.commonx(self.sql_insert.format(self._c(), colname, vs), tuple(vsl))
        
    def __update(self):
        pass
    
    def _sync(self):
        self.__insert()
        self.__update()
        
    def _refresh(self, insertFlag: bool = False, kwargs: dict = {}):
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
                if insertFlag:
                    self._insert(**kwargs)
                    self.exists = False
                else:
                    raise Exception("Key Not Found.")
            iter += 1

class TestModel(ModelBase):
    db_table = "bot402ModReport"
    map = ["qn"]
    
    def qn(self):
        return "test"
    
    def au(self):
        return None
    
    def time(self):
        pass
    
    def nickname(self):
        pass

def mapDict(ob, key: str):
    obDict = {}
    for i in ob:
        obDict[i.get(key)] = i
    
    return obDict

if __name__ == "__main__":
    cache.connectSql('bot402ModReport', 'SELECT * FROM `bot402ModReport`', mapDict, 'qn')
    
    print(cache.cacheList)
    
    model = TestModel(qn=int(input("Please input UID > ")))
    print(model.cache)
    print(model._get("nickname"))
    model._set(nickname="123456")
    print(model._get("nickname"))
    
    model._insert(nickname="test", qn=int(input("> ")), au="az", time="time")
    
    print(cache.cacheList)
    
    model._insert(nickname="test", qn=int(input("> ")), au="az", time="time")._sync()
    
    print(cache.cacheList)
    
    model._delete()
    
    print(cache.cacheList)