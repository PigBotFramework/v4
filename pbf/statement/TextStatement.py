from . import Statement
from ..utils import Utils

class TextStatement(Statement):
    cqtype: str = 'text'
    text: str = ''
    insertStrFlag: bool = False

    def __init__(self, text: str, enterFlag = False, insertStrFlag=False) -> None:
        self.text =text
        if enterFlag:
            self.text += '\n'
        self.insertStrFlag = insertStrFlag
        if insertStrFlag:
            self.process()
    
    def process(self):
        # 插入字符
        if self.insertStrFlag == True:
            self.text = Utils().insertStr(self.text)
        return self.text
    
    def __str__(self):
        return self.text

if __name__ == '__main__':
    stat = TextStatement('azzz')
    print(stat.get())