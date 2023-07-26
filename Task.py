from debugpy.common.json import enum


class TASK:
    def __init__(self, id: int, visible: int = 1, cost: float = 0, group: str = None,
                deadline=None, id_of_user=None, statement=None, best_or_last=1):
        self.id = id
        self.cost = cost
        self.group = group
        self.id_of_user = id_of_user
        self.statement = statement
        self.visible = visible
        self.deadline = deadline
        self.best_or_last = best_or_last

