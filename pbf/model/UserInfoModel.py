from . import ModelBase

class UserInfoModel(ModelBase):
    db_table = 'user_info'
    map = ['qn']
    format_createTable = ["PRIMARY KEY (`id`)"]

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT'
    def qn(self):
        return 'bigint(20) NOT NULL'
    def value(self):
        return 'bigint(20) NOT NULL DEFAULT \'0\''
    def toushi(self):
        return 'int(11) DEFAULT \'0\''
    def cid(self):
        return 'varchar(255)'
    def shiye(self):
        return 'int(11)'
    def taohua(self):
        return 'int(11)'
    def cai(self):
        return 'int(11)'
    def zong(self):
        return 'varchar(255)'
    def uuid(self):
        return 'varchar(255) NOT NULL'