from . import ListModel
import time

class BanWordsModel(ListModel):
    db_table = 'banwords'

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY'
    def content(self):
        return 'varchar(255) NOT NULL'
    def time(self):
        return 'int(11) NOT NULL', time.time()
    def state(self):
        return 'int(11) NOT NULL DEFAULT "0"'
    def qn(self):
        return 'bigint(20) DEFAULT "0"'
    def uuid(self):
        return 'varchar(255) NOT NULL'