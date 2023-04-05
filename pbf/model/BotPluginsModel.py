from . import ModelBase

class BotPluginsModel(ModelBase):
    db_table = "bot_plugins"
    map = ['uuid']
    format_createTable = ["PRIMARY KEY (`id`)"]

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT'
    def data(self):
        return 'varchar(1000)'
    def uuid(self):
        return 'varchar(255) NOT NULL'