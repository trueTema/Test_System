import signal
import sqlite3
import threading
import time

from telebot import types

import LinkedList
from debugpy.common.json import enum
import database
import telebot as tgbot
from Data import config
from Task import Task
bot = tgbot.TeleBot(config.BOT_TOKEN)

statuses = enum("student", "teacher", "super_user")

_help = "Список доступных команд:\n\n" \
        "help - просмотр списка команд\n" \
        "report <текст обращения> - сообщить об ошибке\n" \
        "send <номер задачи> - отправить решение на проверку\n" \
        "status - получить информацию о своих текущих баллах за задачи"

connections = dict()
"""Hash table that contains connections for threads"""


def get_connection(thread_id: int) -> sqlite3.Connection:
    """
    returns connection to database for any thread
    :param thread_id:
    :return: connection to database
    """
    if thread_id in connections.keys():
        return connections[thread_id]
    connection = sqlite3.connect("user_info.sql")
    connections[thread_id] = connection
    return connection


class User:
    _cmd_status = None

    def __init__(self, id: int, name='', status: statuses = "student",
                 study_group=None, current_number_of_task=None, current_task=Task):
        """Initializing constructor"""
        self.id = id
        self.name = name
        self.status = status
        self.study_group = study_group
        self.current_number_of_task = current_number_of_task

        self.current_task = current_task  # Field of user's task
        self.current_task.Task.setUserId(self.id)

    def txt_handler(self, txt: str):
        """
        Text messages handler for each user.
        :param txt: message text
        """
        if self._cmd_status == "register_r_name":
            while True:
                if len(txt.split(" ")) != 2:
                    bot.send_message(self.id, 'Неправильный формат Фамилии Имя')
                    return
                else:
                    self.name = txt
                    break
            bot.send_message(self.id, 'Введите учебную группу:')
            self._cmd_status = "register_r_study_g"
            return
        if self._cmd_status == "register_r_study_g":
            self.study_group = txt
            bot.send_message(self.id, f'Регистрация успешно завершена. Добро пожаловать, {self.name}!')
            self.current_task.Task.setUserId(self.id)
            self._cmd_status = None
            return

    def super_user_cmd(self, cmd: str):
        """
        Super user commands handler
        :param cmd: command
        """
        ...

    def cmd_handler(self, cmd: str):
        """
        Command handler for each user
        :param cmd: command
        """
        if cmd[:3] == 'su ':
            if self.status != 'super_user':
                bot.send_message(self.id, "Ошибка доступа.")#dsdsds
                return
            self.super_user_cmd(cmd[3:])
            return
        if cmd == 'start':
            if self.name != '':
                bot.send_message(self.id, "Вы уже зарегистрированы.")
                return
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.row(types.KeyboardButton(text="/help"), types.KeyboardButton(text="/status"))
            bot.send_message(self.id, 'Введите Фамилию Имя:')
            self._cmd_status = "register_r_name"
            return
        if self.name == '':
            bot.send_message(self.id, 'Вы не завершили регистрацию.')
            return
        if cmd == 'help':
            bot.send_message(self.id, _help)
            return
        if cmd[:4] == 'send':
            bot.send_message(self.id, "Отправка")
            curr_num = str(cmd[4:]).replace("<", "").replace(">", "")
            self.current_number_of_task = curr_num
            self.current_task.Task.setUserId(curr_num)#Need to add list of id's from DataBase, which will be created by admin
        if cmd == 'status':
            ...


activity = LinkedList.LinkedList()
"""Last recent used cache list"""
cache = dict()
"""Last recent used cache hash table"""

max_cache_size = 3  # size of cache
max_afk_time = 10 * 60  # seconds
time_between_checks = 5 * 60  # time between two checks in check_cache() in seconds


def update_cache(id: int, connection: sqlite3.Connection):
    """
    Updates cache if you need to add User there
    :param connection: connection to sql database
    :param id: id of user that you need to add in cache
    """
    cur_time = time.time()
    if id in cache.keys():
        user = cache[id].data[1]
        activity.delete(cache[id])
    else:
        user = database.get_user(id, connection)
    if user is None:
        user = User(id)
        database.add_user(user, connection)
    activity.push((cur_time, user))
    cache[id] = activity.head
    if activity.size > max_cache_size:
        cur_id = activity.tail.data[1].id
        database.update_user_info(activity.tail.data[1], connection)
        cache.pop(cur_id)
        activity.pop()


def cycle_check():
    """Decorator that makes infinity cycle for function with pause between iterations"""
    connection = sqlite3.connect("user_info.sql")
    """database connection"""
    try:
        while True:
            check_cache(connection)
            #  node = activity.head
            #  while node is not None:
            #      print(node.data[0], node.data[1].id)
            #      node = node.next
            #  print('-' * 20)
            time.sleep(time_between_checks)
    except (KeyboardInterrupt, SystemExit):
        connection.close()
        raise KeyboardInterrupt


def check_cache(connection: sqlite3.Connection):
    """
    Removes elements from cache if they have not been used for a long time
    """
    cur_time = time.time()
    #  print(cur_time)
    while activity.size and cur_time - activity.tail.data[0] > max_afk_time:
        user = activity.tail.data[1]
        database.update_user_info(user, connection)
        cache.pop(user.id)
        activity.pop()
