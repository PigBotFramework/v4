from . import ModelBase

class BotSettingsModel(ModelBase):
    db_table = 'bot_settings'
    map = ['uuid']
    format_createTable = ["PRIMARY KEY (`id`)"]

    def id(self):
        return 'int(11) NOT NULL AUTO_INCREMENT'
    def httpurl(self):
        return 'varchar(255) NOT NULL'
    def uuid(self):
        return 'varchar(255) NOT NULL'
    def secret(self):
        return 'varchar(255) NOT NULL'
    def name(self):
        return 'varchar(255) NOT NULL'
    def bannedCount(self):
        return 'int(11) NOT NULL'
    def defaultCoin(self):
        return 'int(11) NOT NULL'
    def coinPercent(self):
        return 'int(11) NOT NULL'
    def lowRandomCoin(self):
        return 'int(11) NOT NULL'
    def highRandomCoin(self):
        return 'int(11) NOT NULL'
    def owner(self):
        return 'bigint(20) NOT NULL'
    def second_owner(self):
        return 'bigint(20) NOT NULL'
    def yiyan(self):
        return 'int(11) NOT NULL'
    def duiapi(self):
        return 'varchar(255) NOT NULL'
    def musicApi(self):
        return 'varchar(255) NOT NULL'
    def musicApiLimit(self):
        return 'int(11) NOT NULL'
    def headImageApi(self):
        return 'varchar(255) NOT NULL'
    def myselfqn(self):
        return 'bigint(20) NOT NULL'
    def autoAcceptGroup(self):
        return 'int(11) NOT NULL'
    def autoAcceptFriend(self):
        return 'int(11) NOT NULL'
    def reportAt(self):
        return 'int(11) NOT NULL'
    def reportPrivate(self):
        return 'int(11) NOT NULL'
    def defaultPower(self):
        return 'int(11) NOT NULL'
    def host(self):
        return 'varchar(255) NOT NULL'
    def port(self):
        return 'int(11) NOT NULL'
    def only_for_uid(self):
        return 'bigint(20) NOT NULL DEFAULT \'0\''
    def chuo(self):
        return 'varchar(1000) NOT NULL DEFAULT \'不要戳我啦 我爱你，别戳了！\''
    def allowPM(self):
        return 'int(11) NOT NULL DEFAULT \'1\''