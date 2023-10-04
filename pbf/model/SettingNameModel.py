from . import ListModel

class SettingNameModel(ListModel):
    db_table = "setting_name"

    def id(self):
        return 'int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT'
    def name(self):
        return 'varchar(255) NOT NULL'
    def description(self):
        return 'varchar(255) NOT NULL'
    def other(self):
        return 'varchar(255)'
    def isHide(self):
        return 'int(11) NOT NULL'
    def type(self):
        return 'varchar(255)'