from ..statement import Statement

class CQCode:
    content: str = None
    
    def __init__(self, content: str) -> None:
        if content == None:
            raise ValueError("Content cannot be None!")
        self.content = content

    def getArr(self) -> list:
        arr: list = []

        left: list = self.content.split("[")
        del left[0]
        for i in left:
            try:
                right: list = i.split("]")[0].split(",")
                cqDict: dict = {"type":"cqcode","data":{}}
                for j in right:
                    if j == right[0]:
                        cqDict["type"] = j.split(":")[1]
                    else:
                        l = j.split("=")
                        cqDict["data"][l[0]] = l[1]
                arr.append(cqDict)
            except Exception:
                raise ValueError("Not a valid CQCode!")
        
        return arr
    
    def get(self, key: str, index: int = None, type: str = None) -> list:
        arr: list = []
        CQArr: list = self.getArr()

        if index != None:
            if len(CQArr) > index:
                return [CQArr[index].get("data").get(key)]
            else:
                # raise IndexError("Index out of range!")
                return [] 
        
        elif type != None:
            for i in CQArr:
                if i.get("type") == type:
                    arr.append(i.get("data").get(key))

        else:
            for i in CQArr:
                if i.get("data").get(key) != None:
                    arr.append(i.get("data").get(key))
        
        return arr
    
    def toStatement(self):
        return Statement('cqcode').set(self.getArr())
                

if __name__ == "__main__":
    cqcode = CQCode("[CQ:face,id=54][CQ:image,url=azazaz,az=abab]")
    print(cqcode.getArr())
    print(cqcode.get("az"))