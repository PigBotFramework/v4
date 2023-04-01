from . import Statement

class AtStatement(Statement):
    cqtype: str = 'at'
    qq: int = None

    def __init__(self, qq: int) -> None:
        self.qq = qq
