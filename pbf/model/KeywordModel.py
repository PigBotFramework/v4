from . import ListModel

class KeywordModel(ListModel):
    db_table = "keywords"

    def id(self):
        return 'int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT'
    def key(self):
        return 'longtext NOT NULL'
    def value(self):
        return 'longtext NOT NULL'
    def time(self):
        return 'int(11) NOT NULL'
    def state(self):
        return 'int(11) NOT NULL'
    def uid(self):
        return 'bigint(11) NOT NULL'
    def coin(self):
        return 'int(11) NOT NULL'
    def uuid(self):
        return 'varchar(255) NOT NULL'
    def qn(self):
        return 'bigint(20) NOT NULL'