from . import Statement


class FaceStatement(Statement):
    cqtype: str = 'face'
    id: str = None

    def __init__(self, face: int) -> None:
        self.id = str(face)
