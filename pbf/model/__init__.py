from ..controller import Cache, Mysql

class ModelBase:
    sql_update: str = "UPDATE `{}` SET {} WHERE {}"
    sql_insert: str = "INSERT INTO `{}` ({}) VALUES {}"
    sql_delete: str = "DELETE FROM `{}` WHERE {}"
    sql_createTable: str = "CREATE TABLE IF NOT EXISTS `{}`({})"
    sql_dropTable: str = "DROP TABLE IF EXISTS `{}`"
    sql_select: str = "SELECT * FROM `{}`"
    sql_whereCase: str = ""
    sql_whereList: list = []
    
    db_table: str = None
    db_perfix: str = "bot_"
    
    col: list = []
    cache: dict = []
    map: list = []
    args: list = []
    exists: bool = True
    delFlag: bool = False
    
    format_insert: list = []
    format_update: list = []
    format_delete: bool = False
    format_createTable: list = []

    def __str__(self):
        return f'<pbf.model.ModelBase {self.db_table}>'

    def _getIndexStr(self, i):
        strr: str = f"['{self._c()}']"
        listt: list = self.map
        dictOb = Cache.cacheList
        for l in listt:
            ob = i.get(l)
            strr += f"[\"{ob}\"]" if isinstance(ob, str) else f"[{eval('i.get(l)')}]"
            dictOb = dictOb.get(str(i.get(l)))
            if dictOb == None:
                exec(f"Cache.cacheList{strr} = {'{}'}")
                dictOb = {}
            
        return strr
    
    def _getTableName(self):
        return self.db_perfix + self.db_table
        
    def _c(self):
        return "db_" + self._getTableName()
    
    def _getCol(self):
        self.col = []
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
                "default": f"`{name}` {default}",
                "type": _type
            })
    
    def __init__(self, **kwargs):
        # Init class vars.
        for i in dir(self):
            if i[0:1] == "_" or callable(getattr(self, i)):
                continue
            varType = type(getattr(self, i))
            setattr(self, i, varType(getattr(self, i)))

        self.args = kwargs
        
        # 初始化数据
        self._getCol()
        self._refresh(insertFlag=True, kwargs=kwargs)
        self._refreshWhereCase()
    
    def __del__(self):
        if not self.delFlag:
            self._sync()
    
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
    
    def _createTable(self):
        strr: str = ""
        flag: bool = False
        listt: list = self.col + self.format_createTable

        for i in listt:
            if flag:
                strr += ", "
            else:
                flag = True
            if isinstance(i, dict):
                strr += i.get("default")
            elif isinstance(i, str):
                strr += i
        sql = self.sql_createTable.format(self._getTableName(), strr)
        Mysql.commonx(sql)

        self.cache = {}
        Cache.set(self._c(), {})
        
        sql = self.sql_select.format(self._getTableName())
        data = Mysql.selectx(sql)
        for i in data:
            strr = self._getIndexStr(i)
            exec(f"Cache.cacheList{strr} = {eval(str(i))}")
        
        return self
    
    def _dropTable(self):
        Mysql.commonx(self.sql_dropTable.format(self._getTableName()))
        self.delFlag = True
        del self
        return None

    def _get(self, key: str, default=None, *args, **kwargs):
        return self.cache.get(key, default=default, *args, **kwargs)
    
    def _insert(self, **kwargs):
        # 在缓存中新增
        strr = self._getIndexStr(kwargs)
        exec(f"Cache.cacheList{strr} = {eval(str(kwargs))}")
        
        self.exists = True
        self.delFlag = False
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
        # 缓存删除
        strr = self._getIndexStr(self.args)
        exec(f"del Cache.cacheList{strr}")
        
        self.format_delete = True
        
        return self
    
    def __delete(self):
        # 数据库删除
        if self.format_delete:
            Mysql.commonx(self.sql_delete.format(self._getTableName(), self.sql_whereCase), tuple(self.sql_whereList))
            self.format_delete = False
        else:
            return False
    
    def _set(self, **kwargs):
        for k, v in kwargs.items():
            self.format_update.append({
                "key": k,
                "value": v
            })
            
            # 修改缓存
            '''
            _cache = Cache.cacheList
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
            
            Cache.cacheList = _cache
            '''
            
            self.cache[k] = v
            
            strr: str = ""
            for i in self.map:
                ob = self.args.get(i)
                strr += f"[\"{ob}\"]" if isinstance(ob, str) else f"[{eval('self.args.get(i)')}]"
            exec(f"Cache.cacheList{strr} = {eval(str(self.cache))}")
        return self
    
    def __insert(self):
        if not self.format_insert:
            return False

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
            for _ in i:
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
        
        Mysql.commonx(self.sql_insert.format(self._getTableName(), colname, vs), tuple(vsl))
        
    def __update(self):
        if not self.format_update:
            return False
        
        strr: str = ""
        vList: list = []
        flag: bool = False
        for i in self.format_update:
            if flag:
                strr += ", "
            else:
                flag = True
            k, v = i.get("key"), i.get("value")
            strr += f"`{k}` = %s"
            vList.append(v)
        sql = self.sql_update.format(self._getTableName(), strr, self.sql_whereCase)
        Mysql.commonx(sql, tuple(vList+self.sql_whereList))
    
    def _sync(self):
        self.__insert()
        self.__update()
        self.__delete()
        
    def _refresh(self, insertFlag: bool = False, kwargs: dict = {}):
        self.cache = Cache.get(self._c())
        
        # 初始化数据表
        if self.cache == None:
            self._createTable()
            self.cache = Cache.get(self._c())
            
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
