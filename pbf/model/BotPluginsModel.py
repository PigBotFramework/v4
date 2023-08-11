from . import ListModel


class BotPluginsModel(ListModel):
    db_table = "bot_plugins"
    map = ['uuid']
    format_createTable = ["PRIMARY KEY (`id`)"]

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT'
    def path(self):
        return 'varchar(255) NOT NULL'
    def uuid(self):
        return 'varchar(255) NOT NULL'
    def time(self):
        return 'int(11) NOT NULL'