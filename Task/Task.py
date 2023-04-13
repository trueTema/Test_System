from debugpy.common.json import enum


class TASK:
    def __init__(self, id: int, visible: int, cost: float = 0, group: str = None,
                time_of=None, id_of_user = None, statement=None):
        self.id = id
        self.cost = cost
        self.time_of = time_of
        self.group = group
        self.id_of_user = id_of_user
        self.statement = statement
        self.visible = visible

    def setId(self,id):
        self.id = id
    def setStatement(self,text):
        self.statement = text
    def setUserId(self,setId):
        self.id_of_user=setId
    def setCost(self,cost):
        self.cost = cost
    def setTime(self,time):
        self.time_of=time
    def getId(self):
        return self.id
    def getStatement(self):
        return self.statement
    def getUserId(self):
        return self.id_of_user
    def getCost(self):
        return self.cost
    def getTime(self):
        return self.time_of