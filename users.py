import json
import sqlite3
import time

from telebot import types

import LinkedList
from debugpy.common.json import enum
import database
import telebot as tgbot
from Task.Task import TASK

_token = json.load(open('Files/config.json', 'r'))["token"]
bot = tgbot.TeleBot(_token)

statuses = enum("student", "teacher", "super_user")
key_word = "8pJSSMgH7B" # KeyWord for admin

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
                      "addTask (parameters) - добавить задачку\n" \
                      "deleteTask (parameters) - удалить задачку\n" \
                      "addGroup - добавить группу\n" \
                      "deleteGroup - удалить группу\n" \
                      "getTask - получить номер\n" \
                      "exit - смена статуса на ученика"


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

    def __init__(self, id: int, name='', status: statuses = "student",
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
            self._cmd_status = None
            return

        if self._cmd_status == "admin_pulling_task":
            field_text = txt
            self.cur_Task.setStatement(field_text)
            self.cur_Task.setTime(time.asctime())
            bot.send_message(self.id, self.cur_Task.getId())       #|
            bot.send_message(self.id, self.cur_Task.getUserId())   #|> Added just to check if it works.
            bot.send_message(self.id, self.cur_Task.getStatement())#|
            bot.send_message(self.id, self.cur_Task.getTime())     #|
            """
            Adding the number sending time is necessary 
            for the possible implementation of the deadline system in the future
            """
            #  There should be a function where we "push" the task into the database
            self._cmd_status = None
            self.cur_Task = None
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
        if cmd == "adminHelp" and self.status == "teacher": #Output a special keyboard for the teacher
            bot.send_message(self.id, _help_for_admin)
            return
        if self.status == "teacher" or self.status == "super_user":
            if cmd == "exit": #Change status for teacher or
                bot.send_message(self.id,"Ваш статус был изменен", reply_markup=kb)          # super user to student
                self.status = "student"
                return
            if cmd[:7] == "addTask":
                id_of = int(str(cmd.split(" ")[1]))
                self._cmd_status = "admin_pulling_task"
                new_one = TASK(id_of)
                new_one.setUserId(self.id)
                self.cur_Task = new_one
                return

        if cmd[:4] == 'send':
            bot.send_message(self.id, "Отправка", reply_markup=kb)
            return
        if cmd[:8] == "adminLog":  # Login as admin
            if str(cmd[9:]) != "" and str(cmd[9:]) == key_word:  # !!! The key_word has to be right !!!
                kb1 = kb.add(types.KeyboardButton(text="/adminHelp"))
                bot.send_message(self.id, f"Здравствуйте, {self.name}!",reply_markup=kb1)  # Special keyboard for admin
                self.status = "teacher"
            else:
                bot.send_message(self.id, str(cmd[9:])) #Exception
                bot.send_message(self.id, "У вас нет доступа к данному статусу")
            return
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
