import datetime
import json
import sqlite3
import time

from telebot import types
from enum import Enum
import LinkedList
import database
import telebot as tgbot
from Task.Task import TASK
import threading

_token = json.load(open('Files/config.json', 'r'))["token"]
bot = tgbot.TeleBot(_token)


statuses = {
    "student": 0,
    "teacher": 1,
    "super_user": 2
}


key_word = "8pJSSMgH7B"  # KeyWord for admin


banned_users = set()
"""Blocked users"""


"""
Admin login will be initialized with a hiden command - /adminLog key_word
"""

_help = "Список доступных команд:\n\n" \
        "help - просмотр списка команд\n" \
        "report <текст обращения> - сообщить об ошибке\n" \
        "send <номер задачи> - отправить решение на проверку\n" \
        "status - получить информацию о своих текущих баллах за задачи"
"""
List of commands for teacher which will be in his own "special" help
"""
_help_for_admin = "Список команд для учителя\n\n" \
                  "addTask id visible\invisible - добавить задачку\n" \
                  "deleteTask (parameters) - удалить задачку\n" \
                  "addGroup - добавить группу\n" \
                  "deleteGroup - удалить группу\n" \
                  "getTask - получить номер\n" \
                  "exit - смена статуса на ученика\n" \
 \
"""
Some description for Super User commands
Commands like 'add/deleteTask' don't need to be explained
'add\deleteGroup' needs for cases like: User enters group, which doesn't exist and we throw error\exception
'getTask' is for correct the fields of chosen task ( SuperUser find out that, for example, field answer is wrong and has
                                                                                        to be corrected
"""

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
    connection = sqlite3.connect("Files/database.sql")
    connections[thread_id] = connection
    return connection


class User:
    _cmd_status = None

    """
    Needed in order to enter the wording of the task itself into the Task class as a separate message
    After adding the wording to the class, it is "pushed" to the database and again becomes None
    """

    cur_Task = None

    def __init__(self, id: int, name='', status: str = "student",
                 study_group=None):
        """Initializing constructor"""
        self.id = id
        self.name = name
        self.status = status
        self.study_group = study_group

    def txt_handler(self, txt: str):
        """
        Text messages handler for each user.
        :param txt: message text
        """
        if self.id in banned_users:
            bot.send_message(self.id, 'Вы заблокированы.')
            return
        if self._cmd_status == "register_r_name":
            while True:
                if len(txt.split(" ")) != 2:
                    bot.send_message(self.id, 'Некорректный формат Фамилии Имя')
                    return
                else:
                    self.name = txt
                    break
            bot.send_message(self.id, 'Введите учебную группу: ')
            self._cmd_status = "register_r_study_g"
            return
        if self._cmd_status == "register_r_study_g":
            self.study_group = txt
            bot.send_message(self.id, f'Регистрация успешно завершена. Добро пожаловать, {self.name}!')
            self._cmd_status = None
            return

        if self._cmd_status == "admin_pulling_task":
            field_text = txt
            self.cur_Task.setStatement(field_text)
            """
            Adding the number sending time is necessary 
            for the possible implementation of the deadline system in the future
            """
            connection = get_connection(threading.current_thread().native_id)
            if database.get_problem(self.cur_Task.id, connection) is not None:
                bot.send_message(self.id, "Задача уже добавлена ранее")
                return
            database.add_problem(self.cur_Task, connection)
            bot.send_message(self.id, "Отправляю на сервер")
            current = database.get_problem(self.cur_Task.id, connection)
            bot.send_message(self.id, "Получаю с сервера")  # |
            bot.send_message(self.id, str(current.id))  # |
            bot.send_message(self.id, current.id_of_user)  # | Just for testing
            bot.send_message(self.id, current.statement)  # |
            bot.send_message(self.id, str(current.time_of))  # |
            bot.send_message(self.id, str(current.visable))  # |
            #  There should be a function where we "push" the task into the database
            self._cmd_status = None
            self.cur_Task = None
            return

    def super_user_cmd(self, cmd: str):
        """
        Super user commands handler
        :param cmd: command
        """

        cmd = cmd.split()
        if cmd[0] == 'changeStatus':
            user_id = int(cmd[1])
            new_status = cmd[2]
            if new_status not in statuses.keys():
                bot.send_message(self.id, 'Неизвестный статус пользователя.')
                return
            if user_id in cache.keys():
                cache[user_id].data[1].status = new_status
                bot.send_message(self.id, f'Статус пользователя {user_id} успешно изменён на {new_status}')
            else:
                update_cache(user_id, get_connection(threading.current_thread().native_id))
                cache[user_id].data[1].status = new_status
            return
        if cmd[0] == 'ban':
            if len(cmd) > 2:
                bot.send_message(self.id, 'Некорректный формат команды.')
                return
            try:
                user_id = int(cmd[1])
            except ...:
                bot.send_message(self.id, 'Некорректный формат команды.')
                return
            banned_users.add(user_id)
            bot.send_message(self.id, 'Пользователь успешно заблокирован.')
            return
        if cmd[0] == 'unban':
            if len(cmd) > 2:
                bot.send_message(self.id, 'Некорректный формат команды.')
                return
            try:
                user_id = int(cmd[1])
            except ...:
                bot.send_message(self.id, 'Некорректный формат команды.')
                return
            if user_id not in banned_users:
                bot.send_message(self.id, 'Пользователь не заблокирован.')
                return
            banned_users.remove(user_id)
            bot.send_message(self.id, 'Пользователь успешно разблокирован.')
            return

    def cmd_handler(self, cmd: str):
        """
        Command handler for each user
        :param cmd: command
        """
        if self.id in banned_users:
            bot.send_message(self.id, 'Вы заблокированы.')
            return
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton(text="/help"), types.KeyboardButton(text="/status"))
        if cmd[:3] == 'su ':
            if self.status != 'super_user':
                bot.send_message(self.id, "Ошибка доступа.", reply_markup=kb)
                return
            self.super_user_cmd(cmd[3:])
            return
        if cmd == 'start':
            if self.name != '':
                bot.send_message(self.id, "Вы уже зарегистрированы.", reply_markup=kb)
                return
            bot.send_message(self.id, 'Введите Фамилию Имя:')
            self._cmd_status = "register_r_name"
            return
        if self.name == '':
            bot.send_message(self.id, 'Вы не завершили регистрацию.')
            return
        if cmd == 'help':
            bot.send_message(self.id, _help)
            return
        if cmd == "adminHelp" and statuses[self.status] >= 1:  # Output a special keyboard for the teacher
            bot.send_message(self.id, _help_for_admin)
            return
        if cmd[:4] == 'send':
            bot.send_message(self.id, "Отправка", reply_markup=kb)
            return
        if cmd[:8] == "adminLog":  # Login as admin
            if str(cmd[9:]) != "" and str(cmd[9:]) == key_word:  # !!! The key_word has to be right !!!
                kb1 = kb.add(types.KeyboardButton(text="/adminHelp"))
                bot.send_message(self.id, f"Добро пожаловать, {self.name}!",
                                 reply_markup=kb1)  # Special keyboard for admin
                self.status = "super_user"
            else:
                bot.send_message(self.id, str(cmd[9:]))  # Exception
                bot.send_message(self.id, "Ошибка доступа.")
            return
        if cmd == 'status':
            ...

        if self.status == "teacher" or self.status == "super_user":
            if cmd == "exit":  # Change status for teacher or
                bot.send_message(self.id, "Ваш статус был изменен", reply_markup=kb)  # super user to student
                self.status = "student"
                return
            if cmd[:7] == "addTask":
                coonection = get_connection(threading.current_thread().native_id)
                while True:
                    visibility_status = str(cmd.split(" ")[2])
                    if visibility_status not in ["visible", "invisible"]:
                        bot.send_message(self.id, "Некорректный формат статуса")
                        bot.send_message(self.id, visibility_status)
                        return
                    else:
                        break
                id_of = int(str(cmd.split(" ")[1]))
                if database.get_problem(id_of, coonection) is not None:
                    bot.send_message(self.id, "Задача уже добавлена ранее")
                    return
                bot.send_message(self.id, "Добавляем")
                self._cmd_status = "admin_pulling_task"
                if visibility_status == "visible":
                    visibility_status = 1
                else:
                    visibility_status = 0
                new_one = TASK(id_of, visibility_status)
                now = datetime.datetime.now()
                timestamp = int(datetime.datetime.timestamp(now))
                new_one.time_of = timestamp
                new_one.id_of_user = self.id
                self.cur_Task = new_one
                return


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
    connection = sqlite3.connect("Files/database.sql")
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
