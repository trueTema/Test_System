class Package:

    def __init__(self, points: float, id_user=None, id_task=None, answer = '', date=None,):
        self.id_user = id_user
        self.id_task = id_task
        self.answer = answer
        self.points = points
        self.date = date

    def setPoints(self,point:float):
        self.points = point
    def setId_task(self,id_for_task):
        self.id_task = id_for_task
    def setId_user(self,id_for_user):
        self.id_user = id_for_user
    def setAnswer(self,text):
        self.answer = text
    def setDate(self,time):
        self.date = time