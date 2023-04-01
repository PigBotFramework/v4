from . import Statement

class FaceStatement(Statement):
    cqtype: str = 'face'
    id: int = None

    def __init__(self, face: int) -> None:
        self.id = face