from . import ModelBase

class BlackListModel(ModelBase):
    db_table = 'black_list'
    map = ['qn']
    format_createTable = ["PRIMARY KEY (`id`)"]

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT'
    def qn(self):
        return 'bigint(20) NOT NULL'
    def reason(self):
        return 'varchar(255) NOT NULL'
    def time(self):
        return 'int(11) NOT NULL'
    def uuid(self):
        return 'varchar(255) NOT NULL'