import datetime


class Package:

    def __init__(self, points: float, id_user: int, id_task: int, date: int, answer: str = ''):
        self.id_user = id_user
        self.id_task = id_task
        self.answer = answer
        self.points = points
        self.date = date
