from . import Statement

class ImageStatement(Statement):
    cqtype: str = 'image'
    url: str = None
    file: str = None
    type: str = None
    cache: int = 0
    id: int = 40000
    c: int = 2

    def __init__(self, url: str = 'https://pbf.xzynb.top/statics/image/head.jpg', file: str = 'image.image', type: str = None, cache: int = 0, id: int = 40000, c: int = 2) -> None:
        self.url = url
        self.file = file
        self.type = type
        self.cache = cache
        self.id = id
        self.c = c