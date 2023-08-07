from . import Statement
from ..utils import Utils


class TextStatement(Statement):
    cqtype: str = 'text'
    text: str = ''
    insertStrFlag: bool = False
    transFlag: bool = True
    enterFlag: bool = False

    def __init__(self, text: str, enterFlag=False, insertStrFlag=False, transFlag=True) -> None:
        self.text = text
        if enterFlag:
            self.text += '\n'
            self.enterFlag = True
        self.insertStrFlag = insertStrFlag
        self.transFlag = transFlag
        if insertStrFlag:
            self.process()

    def process(self):
        # 插入字符
        if self.insertStrFlag == True:
            self.text = Utils().insertStr(self.text)
        return self.text
    
    def trans(self, lang):
         if self.transFlag:
             self.text = Utils().translator(self.text, to_lang=lang)
             if self.enterFlag and self.text.strip() != '':
                 self.text += '\n'

    def __str__(self):
        return self.text


if __name__ == '__main__':
    stat = TextStatement('azzz')
    print(stat.get())
