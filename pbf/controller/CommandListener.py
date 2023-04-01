from .PbfStruct import Struct
import time
from ..utils import Utils

class CommandListener:
    data: Struct = None
    rclOb: dict = None
    
    def __init__(self, struct):
        self.data = struct

    def set(self, func=None, args=None, step=1, sendTime=time.time()):
        num = Utils().findObject("uid", self.data.se.get('user_id'), commandListenerList).get('num')
        if num == -1:
            if step == None:
                step = 1
            commandListenerList.append({
                "func": func,
                "step": step,
                "args": args,
                "time": sendTime,
                "uid": self.data.se.get('user_id'),
                "gid": self.data.se.get('group_id')
            })
        else:
            if func != None:
                commandListenerList[num]['func'] = func
            if args != None:
                commandListenerList[num]['args'] = args
            if step != None and step != 1 and step != '1':
                commandListenerList[num]['step'] = step
            else:
                commandListenerList[num]['step'] = int(commandListenerList[num]['step']) + 1
            commandListenerList[num]['time'] = sendTime

    def get(self):
        if self.rclOb == None:
            return Utils().findObject("uid", self.data.se.get('user_id'), commandListenerList).get('object')
        else:
            return self.rclOb

    def remove(self):
        num = Utils().findObject("uid", self.data.se.get('user_id'), commandListenerList).get('num')
        if num == -1:
            return False
        else:
            commandListenerList.pop(num)
            return True

commandListenerList = []