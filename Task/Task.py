from debugpy.common.json import enum


class Task:
    def __init__(self, id: int, cost : float = 0,
                time_of = None, id_of_user = None):
        self.id = id
        self.cost = cost
        self.time_of = time_of
        self.id_of_user = id_of_user

    def setId(self,id):
        self.id = id
    def setUserId(self,setId):
        self.id_of_user=setId
    def setCost(self,cost):
        self.cost = cost
    def setTime(self,time):
        self.time_of=time
    def getId(self):
        return self.id
    def getUserId(self):
        return self.id_of_user
    def getCost(self):
        return self.cost
    def getTime(self):
        return self.time_of