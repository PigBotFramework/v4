from . import ModelBase

class GroupSettingsModel(ModelBase):
    db_table = "group_settings"
    map = ['uuid', 'qn']
    format_createTable = ["PRIMARY KEY (`id`)"]

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT'
    def uuid(self):
        return 'varchar(255) NOT NULL'
    def qn(self):
        return 'bigint(20) NOT NULL'
    def power(self):
        return 'int(2) NOT NULL DEFAULT \'1\''
    def only_for_uid(self):
        return 'varchar(255) NOT NULL DEFAULT \' \''