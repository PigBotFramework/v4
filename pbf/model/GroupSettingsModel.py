from . import DictModel


class GroupSettingsModel(DictModel):
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
        return ('int(2) NOT NULL DEFAULT \'1\'', 1)

    def only_for_uid(self):
        return ('varchar(255) DEFAULT \' \'', '')

    def replyPercent(self):
        return ("int(11) NOT NULL DEFAULT '100'", 100)

    def autoAcceptGroup(self):
        return ("int(11) NOT NULL DEFAULT '1'", 1)

    def recallFlag(self):
        return ("int(11) NOT NULL DEFAULT '1'", 1)

    def admin(self):
        return ("int(11) NOT NULL DEFAULT '1'", 1)

    def decrease(self):
        return ("int(11) NOT NULL DEFAULT '1'", 1)

    def increase(self):
        return ("int(11) NOT NULL DEFAULT '1'", 1)

    def AntiswipeScreen(self):
        return ("int(11) NOT NULL DEFAULT '10'", 10)

    def increase_notice(self):
        return (
        "varchar(255) NOT NULL DEFAULT '欢迎入群！（请管理自定义入群欢迎内容）'", '欢迎入群！（请管理自定义入群欢迎内容）')

    def weijinCheck(self):
        return ("int(11) NOT NULL DEFAULT '0'", 0)

    def keywordReply(self):
        return ("int(11) NOT NULL DEFAULT '1'", 1)

    def bannedCount(self):
        return ("int(11) NOT NULL DEFAULT '0'", 0)

    def MCSMApi(self):
        return "varchar(255)"

    def MCSMUuid(self):
        return "varchar(255)"

    def MCSMRemote(self):
        return "varchar(255)"

    def MCSMKey(self):
        return "varchar(255)"

    def messageSync(self):
        return ("int(11) NOT NULL DEFAULT '0'", 0)

    def dui(self):
        return "int(11)"

    def delete_es(self):
        return ("int(11) NOT NULL DEFAULT '0'", 0)

    def increase_verify(self):
        return ("int(11) NOT NULL DEFAULT '0'", 0)

    def translateLang(self):
        return ("varchar(255) NOT NULL DEFAULT 'zh-cn'", 'zh-cn')

    def MC_random(self):
        return ("int(11) NOT NULL DEFAULT '0'", 0)

    def connectQQ(self):
        return "bigint(20)"

    def decrease_notice_kick(self):
        return ("varchar(255) NOT NULL DEFAULT '成员{user}被{operator}踢出了本群'", '成员{user}被{operator}踢出了本群')

    def decrease_notice_leave(self):
        return ("varchar(255) NOT NULL DEFAULT '成员{user}主动离开了本群'", '成员{user}主动离开了本群')

    def v_command(self):
        return "longtext"

    def client_id(self):
        return "varchar(11)"

    def client_secret(self):
        return "varchar(11)"

    def sche(self):
        return ("int(11) NOT NULL DEFAULT '0'", 0)

    def scheContent(self):
        return "varchar(1000)"
