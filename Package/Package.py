import datetime


class Package:

    def __init__(self, points: float, id_user: int, id_task: int, answer: str, date: datetime.datetime):
        self.id_user = id_user
        self.id_task = id_task
        self.answer = answer
        self.points = points
        self.date = date

    def setPoints(self, point: float):
        self.points = point
    def setId_task(self, id_for_task: int):
        self.id_task = id_for_task
    def setId_user(self, id_for_user: int):
        self.id_user = id_for_user
    def setAnswer(self, text: str):
        self.answer = text
    def setDate(self, time: datetime.datetime):
        self.date = time