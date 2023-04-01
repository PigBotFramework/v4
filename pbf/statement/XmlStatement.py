from . import Statement

class XmlStatement(Statement):
    cqtype = 'xml'
    data: str = None

    def __init__(self, data: str):
        self.data = data