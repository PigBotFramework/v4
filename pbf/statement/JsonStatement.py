from . import Statement
import json

class JsonStatement(Statement):
    cqtype = 'json'
    data: str = None
    
    def __init__(self, jsonStr: dict):
        self.data = json.dumps(jsonStr)