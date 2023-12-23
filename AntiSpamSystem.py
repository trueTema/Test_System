from collections import deque
from datetime import datetime


class AntiSpam:
    request_time_storage = {}
    interval = 5
    max_request_count = 20

    def __init__(self, time_interval: float, max_request_count: int):
        self.interval = time_interval
        self.max_request_count = max_request_count

    def __clean_queue(self, user_id: int):
        now = datetime.timestamp(datetime.now())
        while len(self.request_time_storage[user_id]) > 0 and self.request_time_storage[user_id][0] + self.interval < now:
            self.request_time_storage[user_id].popleft()

    def request(self, user_id: int, time: float):
        """
        Registers request
        :param user_id: user_id pulled request
        :param time: request time
        :return:
        """
        if user_id not in self.request_time_storage.keys():
            self.request_time_storage[user_id] = deque()
        self.request_time_storage[user_id].append(time)
        for i in self.request_time_storage.keys():
            self.__clean_queue(i)

    def user_id_list(self) -> list[int]:
        """
        Return ID of users that pulled more requests that max limit
        :return: list of user IDs
        """
        ans = []
        for i in self.request_time_storage.keys():
            self.__clean_queue(i)
            if len(self.request_time_storage[i]) > self.max_request_count:
                ans.append(i)
        return ans
