from . import DictModel

class ConnectQGModel(DictModel):
    db_table = 'connect_qq_group'
    map = ['uuid', 'uid', 'gid']

    def id(self):
        return 'int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT'
    def uid(self):
        return 'bigint(20) NOT NULL'
    def uuid(self):
        return 'varchar(255) NOT NULL'
    def gid(self):
        return 'bigint(20) NOT NULL'