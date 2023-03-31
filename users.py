import time
import LinkedList
from debugpy.common.json import enum
import database
import telebot as tgbot

_token = '6003964860:AAHk29MXvsxDCH1BGqOsJbm-W9fMJ64Maxc'
bot = tgbot.TeleBot(_token)

statuses = enum("student", "teacher", "super_user")

_help = "Список доступных команд:\n\n" \
        "help - просмотр списка команд\n" \
        "report <текст обращения> - сообщить об ошибке\n" \
        "send <номер задачи> - отправить решение на проверку\n" \
        "status - получить информацию о своих текущих баллах за задачи"


class User:
    _cmd_status = None

    def __init__(self, id: int, name='', status: statuses = "student", study_group=None):
        self.id = id
        self.name = name
        self.status = status
        self.study_group = study_group

    def txt_handler(self, txt):
        if self._cmd_status == "register_r_name":
            self.name = txt
            bot.send_message(self.id, 'Введите учебную группу:')
            self._cmd_status = "register_r_study_g"
            return
        if self._cmd_status == "register_r_study_g":
            self.study_group = txt
            bot.send_message(self.id, f'Регистрация успешно завершена. Добро пожаловать, {self.name}!')
            self._cmd_status = None
            return

    def super_user_cmd(self, cmd):
        ...

    def cmd_handler(self, cmd):
        if cmd[:3] == 'su ':
            if self.status != 'super_user':
                bot.send_message(self.id, "Ошибка доступа.")
                return
            self.super_user_cmd(cmd[3:])
            return
        if cmd == 'start':
            bot.send_message(self.id, 'Введите Фамилию Имя:')
            self._cmd_status = "register_r_name"
            return
        if self.name == '':
            bot.send_message(self.id, 'Вы не завершили регистрацию.')
            return
        if cmd == 'help':
            bot.send_message(self.id, _help)
            return
        if cmd == 'send':
            ...
        if cmd == 'status':
            ...


activity = LinkedList.LinkedList()
cache = dict()

max_cache_size = 3  # size of cache
max_afk_time = 10 * 60  # seconds
time_between_checks = 5 * 60  # time between two checks in check_cache() in seconds


def update_cache(id: int):
    """
    Updates cache if you need to add User there
    :param id: id of user that you need to add in cache
    """
    cur_time = time.time()
    if id in cache.keys():
        user = cache[id].data[1]
        activity.delete(cache[id])
    else:
        user = database.get_user(id)
    if user is None:
        user = User(id)
    activity.push((cur_time, user))
    cache[id] = activity.head
    if activity.size > max_cache_size:
        cur_id = activity.tail.data[1].id
        cache.pop(cur_id)
        activity.pop()


def test_decor(func):
    def wrapper():
        while True:
            func()
            node = activity.head
            while node is not None:
                print(node.data[0], node.data[1].id)
                node = node.next
            print('-' * 20)
            time.sleep(time_between_checks)
    return wrapper


@test_decor
def check_cache():
    """
    Removes elements from cache if they have not been used for a long time
    """
    cur_time = time.time()
    print(cur_time)
    while activity.size and cur_time - activity.tail.data[0] > max_afk_time:
        id = activity.tail.data[1].id
        cache.pop(id)
        activity.pop()
