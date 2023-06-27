from . import ListModel

class MemesModel(ListModel):
    db_table = "memes"

    def id(self):
        return 'int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT'
    def keyword(self):
        return 'varchar(255) NOT NULL'
    def url(self):
        return 'varchar(255) NOT NULL'
    def uid(self):
        return 'bigint(20) NOT NULL'
    def time(self):
        return 'int(11) NOT NULL'