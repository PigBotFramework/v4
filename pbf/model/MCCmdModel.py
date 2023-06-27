from . import ListModel

class MCCmdModel(ListModel):
    db_table = "mc_cmd"

    def id(self):
        return 'int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT'
    def name(self):
        return 'varchar(255) NOT NULL'
    def cmd(self):
        return 'varchar(255) NOT NULL'
    def qn(self):
        return 'bigint(20) NOT NULL'