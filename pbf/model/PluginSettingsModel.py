from . import ModelBase
import time

class PluginSettingsModel(ModelBase):
    db_table = 'plugin_settings'
    map = ['package_name', 'key']
    format_createTable = ["PRIMARY KEY (`id`)"]

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT'
    def package_name(self):
        return 'varchar(255) NOT NULL'
    def key(self):
        return 'varchar(255) NOT NULL'
    def value(self):
        return 'varchar(1000)'
    def time(self):
        return ('int(11)', time.time())