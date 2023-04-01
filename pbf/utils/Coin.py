import sys, random
from ..controller import Cache, Mysql
from ..controller.PbfStruct import Struct

class Coin:
    data: Struct = None

    def __init__(self, data: Struct) -> None:
        self.data = data

    def check(self):
        for i in Cache.get("coinlist"):
            if str(self.data.se.get('user_id')) == str(i.get(self.data.messageType)):
                return i.get('value')
        return -1

    def add(self, value=None):
        if value == None:
            value=random.randint(self.data.botSettings.get('lowRandomCoin'), self.data.botSettings.get('highRandomCoin'))
        
        uid = self.data.se.get('user_id')
        
        if self.data.userCoin == -1:
            return 0
        if self.data.userCoin == False:
            return False

        Mysql.commonx('UPDATE `botCoin` SET `value`=%s WHERE `qn`=%s', (int(self.data.userCoin)+int(value), uid))
        return value
        
    def remove(self, value=None):
        if value == None:
            value = random.randint(self.data.botSettings.get('lowRandomCoin'), self.data.botSettings.get('highRandomCoin'))
        
        uid = self.data.se.get('user_id')
        
        if self.data.userCoin == -1:
            return 0
        if self.data.userCoin == False:
            return False
        
        Mysql.commonx('UPDATE `botCoin` SET `value`=%s WHERE `qn`=%s', (int(self.data.userCoin)-int(value), uid))
        return value