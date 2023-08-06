from . import DictModel

class BiliDynamicModel(DictModel):
    db_table = 'bili_dynamic'
    map = ['uid']

    def id(self):
        return 'int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT'
    def uid(self):
        return 'bigint(20) NOT NULL'
    def offset(self):
        return 'varchar(255)'
