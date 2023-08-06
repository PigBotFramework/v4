from . import ListModel

class BiliDynamicQnModel(ListModel):
    db_table = "bili_dynamic_qn"

    def id(self):
        return 'int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT'
    def qn(self):
        return 'bigint(20) NOT NULL'
    def uuid(self):
        return 'varchar(255) NOT NULL'
    def uid(self):
        return 'varchar(255) NOT NULL'