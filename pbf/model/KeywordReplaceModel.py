from . import ListModel

class KeywordReplaceModel(ListModel):
    db_table = 'keyword_replace'

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY'
    def key(self):
        return 'varchar(255) NOT NULL'
    def value(self):
        return 'varchar(255) NOT NULL'
    def explain(self):
        return 'varchar(255) NOT NULL'