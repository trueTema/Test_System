from debugpy.common.json import enum

statuses_of_task = enum("right", "wrong")#Status of task chanching on conclusion of check-script

class Task:
    def __init__(self, id: int, status_of_task : statuses_of_task = "wrong",
                time_of = None, id_of_user = None):
        self.id = id
        self.status_of_task = status_of_task
        self.time_of = time_of
        self.id_of_user = id_of_user

    def setId(self,id):
        self.id = id
    def setUserId(self,setId):
        self.id_of_user=setId
    def getId(self):
        return self.id
    def getUserId(self):
        return self.id_of_user