from debugpy.common.json import enum


class TASK:
    def __init__(self, id: int, visible: int, cost: float = 0, group: str = None,
                time_of=None, deadline=None,id_of_user=None, statement=None):
        self.id = id
        self.cost = cost
        self.time_of = time_of
        self.group = group
        self.id_of_user = id_of_user
        self.statement = statement
        self.visible = visible
        self.deadline = deadline