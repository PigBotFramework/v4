from . import DictModel

class MCModel(DictModel):
    db_table = "mc"
    map = ['qn']

    def id(self):
        return 'int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT'
    def qn(self):
        return 'bigint(20) NOT NULL'
    def name(self):
        return 'varchar(255)'
    def backpack(self):
        return 'longtext'
    def life(self):
        return 'int(11)', 20
    def hungry(self):
        return 'int(11)', 20
    def achievement(self):
        return 'longtext'
    def xp(self):
        return 'int(11)'
    def doing(self):
        return 'varchar(255)'
    def doingutill(self):
        return 'int(11)'