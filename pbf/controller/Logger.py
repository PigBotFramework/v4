import datetime
import os

import pytz

from .PbfStruct import Struct


class Logger:
    data: Struct = None

    def __init__(self, data: Struct) -> None:
        if not os.path.exists("./logs"):
            os.mkdir("./logs")
        self.data = data

    def setData(self, data: Struct) -> None:
        self.data = data

    def log(self, level, message, *args):
        if self.data == None:
            raise Exception("data is None")

        now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        ctime = now.strftime("%Y-%m-%d %H:%M:%S")

        argsString = ""
        for i in args:
            argsString += f" [{i}]"

        str = f"[{ctime}] [{self.data.runningProgram}] [{self.data.uuid}/{self.data.se.get('user_id')}/{self.data.se.get('group_id')}] [{level}]{argsString} {message}\n"
        print(str)

        fileName = now.strftime("./logs/%Y-%m-%d.log")
        with open(fileName, "a") as f:
            f.write(str)

    def error(self, message: str, *args) -> None:
        self.log("ERROR", message, *args)

    def warn(self, message: str, *args) -> None:
        self.log("WARN", message, *args)

    def warning(self, message: str, *args) -> None:
        self.log("WARNING", message, *args)

    def info(self, message: str, *args) -> None:
        self.log("INFO", message, *args)

    def debug(self, message: str, *args) -> None:
        self.log("DEBUG", message, *args)
