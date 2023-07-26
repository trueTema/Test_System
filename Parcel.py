import datetime


class Parcel:

    def __init__(self, points: float, id_user: int, id_task: int, date: int, id: int, answer: str = ''):
        self.id_user = id_user
        self.id_task = id_task
        self.answer = answer
        self.points = points
        self.date = date
        self.id = id
