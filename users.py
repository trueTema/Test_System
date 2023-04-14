import datetime
import json
import os
import sqlite3
import time

from telebot import types
import run_checker
import LinkedList
import database
import telebot as tgbot
from Task import TASK
from Parcel import Parcel
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
                  "deleteTask id - удалить задачку\n" \
                  "updateTask id - обновить задачу\n"\
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
    cur_task_id = None

    def __init__(self, id: int, name='', status: str = "student",
                 study_group=None):
        """Initializing constructor"""
        self.id = id
        self.name = name
        self.status = status
        self.study_group = study_group

    def doc_handler(self, file: bytes, filetype: str):
        if self._cmd_status == 'pushing_checking_script':
            if filetype != 'py':
                bot.send_message(self.id, 'Скрипт должен быть формата .py')
                return
            src = f"Scripts/{str(self.cur_Task.id)}.py"
            with open(src, "wb") as new_file:
                new_file.write(file)
                new_file.close()
            connection = get_connection(threading.current_thread().native_id)
            database.add_problem(self.cur_Task, connection)
            self._cmd_status = None
            self.cur_Task = None
            bot.send_message(self.id, 'Задача успешно добавлена.')
            return
        if self._cmd_status == 'updating_checking_script':
            if filetype != 'py':
                bot.send_message(self.id, 'Скрипт должен быть формата .py')
                return
            os.remove(f'Scripts/{self.cur_Task.id}.py')
            src = f"Scripts/{str(self.cur_Task.id)}.py"
            with open(src, "wb") as new_file:
                new_file.write(file)
                new_file.close()
            connection = get_connection(threading.current_thread().native_id)
            database.update_problem(self.cur_Task, connection)
            bot.send_message(self.id, "Задача была успешно обновлена.")
            self.cur_Task = None
            self._cmd_status = None
            return
        if self._cmd_status == "pushing_parcel":
            if filetype != 'txt':
                bot.send_message(self.id, 'Посылкой может быть только текстовый файл.')
                return
            now = datetime.datetime.now()
            timestamp = int(datetime.datetime.timestamp(now))
            try:
                checker_result = run_checker.get_points(f'Scripts/{self.cur_task_id}.py', run_checker.bytes_to_str(file))
            except Exception as e:
                bot.send_message(self.id, 'Нетестируемый ответ.')
                return
            if len(checker_result["errors"]) != 0:
                bot.send_message(self.id, 'Нетестируемый ответ.')
                return
            if database.get_problem(self.cur_task_id, get_connection(threading.current_thread().native_id)).visible == 1:
                bot.send_message(self.id, f'Набрано баллов: {checker_result["points"]}')
            current_parcell = Parcel(points=checker_result["points"],
                                     date=timestamp, id_user=self.id, id_task=self.cur_task_id,
                                     answer=str(file))
            connection = get_connection(threading.current_thread().native_id)
            database.add_parcel(current_parcell, connection)  # Sending parcell
            self.cur_Task = None
            self._cmd_status = None
            bot.send_message(self.id, "Посылка была отправлена")
            return
        if self._cmd_status == "updating_parcell":
            if filetype != 'txt':
                bot.send_message(self.id, 'Посылкой может быть только текстовый файл.')
                return
            now = datetime.datetime.now()
            timestamp = int(datetime.datetime.timestamp(now))
            try:
                checker_result = run_checker.get_points(f'Scripts/{self.cur_task_id}.py', run_checker.bytes_to_str(file))
            except Exception as e:
                bot.send_message(self.id, 'Нетестируемый ответ.')
                return
            if len(checker_result["errors"]) != 0:
                bot.send_message(self.id, 'Нетестируемый ответ.')
                return
            if database.get_problem(self.cur_task_id, get_connection(threading.current_thread().native_id)).visible == 1:
                bot.send_message(self.id, f'Набрано баллов: {checker_result["points"]}')
            current_parcell = Parcel(points=checker_result["points"], date=timestamp, id_user=self.id, id_task=self.cur_task_id,
                                     answer=str(file))
            connection = get_connection(threading.current_thread().native_id)
            database.update_parcel(current_parcell, connection)  # Updating parcell
            bot.send_message(self.id, "Данная посылка уже существует, а поэтому обновлена")
            self.cur_Task = None
            self._cmd_status = None
            return

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
            self.cur_Task.statement = field_text
            """
            Adding the number sending time is necessary 
            for the possible implementation of the deadline system in the future
            """
            self._cmd_status = 'pushing_checking_script'
            bot.send_message(self.id, 'Отправьте скрипт оценки для этой задачи.')
            return
        if self._cmd_status == "updating_task":
            field_text = txt
            self.cur_Task.statement = field_text
            self._cmd_status = 'updating_checking_script'
            bot.send_message(self.id, 'Отправьте скрипт оценки для этой задачи.')
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
                if cache[user_id].data[1].status == 'super_user' and (self.id != 451938981) and (user_id != self.id):
                    bot.send_message(self.id, 'Невозможно поменять статус суперпользователя.')
                    return
                cache[user_id].data[1].status = new_status
                bot.send_message(self.id, f'Статус пользователя {user_id} успешно изменён на {new_status}')
            else:
                update_cache(user_id, get_connection(threading.current_thread().native_id))
                if cache[user_id].data[1].status == 'super_user' and (self.id != 451938981) and (user_id != self.id):
                    bot.send_message(self.id, 'Невозможно поменять статус суперпользователя.')
                    return
                cache[user_id].data[1].status = new_status
            return
        if cmd[0] == 'changeName':
            user_id = int(cmd[1])
            new_name = ' '.join(cmd[2:])
            if user_id in cache.keys():
                if cache[user_id].data[1].status == 'super_user' and (self.id != 451938981) and (user_id != self.id):
                    bot.send_message(self.id, 'Невозможно поменять имя суперпользователя.')
                    return
                cache[user_id].data[1].name = new_name
                bot.send_message(self.id, f'Имя пользователя {user_id} успешно изменёно на {new_name}')
            else:
                update_cache(user_id, get_connection(threading.current_thread().native_id))
                if cache[user_id].data[1].status == 'super_user' and (self.id != 451938981) and (user_id != self.id):
                    bot.send_message(self.id, 'Невозможно поменять имя суперпользователя.')
                    return
                cache[user_id].data[1].name = new_name
            return
        if cmd[0] == 'changeGroup':
            user_id = int(cmd[1])
            new_group = cmd[2]
            if user_id in cache.keys():
                if cache[user_id].data[1].status == 'super_user' and (self.id != 451938981) and (user_id != self.id):
                    bot.send_message(self.id, 'Невозможно поменять группу суперпользователя.')
                    return
                cache[user_id].data[1].study_group = new_group
                bot.send_message(self.id, f'Группа пользователя {user_id} успешно изменёна на {new_group}')
            else:
                update_cache(user_id, get_connection(threading.current_thread().native_id))
                if cache[user_id].data[1].status == 'super_user' and (self.id != 451938981) and (user_id != self.id):
                    bot.send_message(self.id, 'Невозможно поменять группу суперпользователя.')
                    return
                cache[user_id].data[1].study_group = new_group
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
            if user_id in cache.keys():
                user = cache[user_id].data[1]
            else:
                user = database.get_user(user_id, get_connection(threading.current_thread().native_id))
            if user is not None and user.status == 'super_user' and (self.id != 451938981):
                bot.send_message(self.id, 'Невозможно заблокировать суперпользователя.')
                return
            if user_id == self.id:
                bot.send_message(self.id, 'Невозможно заблокировать себя.')
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
            if len(cmd.split(" ")) != 2:
                bot.send_message(self.id, "Вы не ввели айди номера или сделали это неправильно ")
                return
            id_of_parcell = int(cmd.split(" ")[1])
            coonection = get_connection(threading.current_thread().native_id)
            if database.get_problem(id_of_parcell, coonection) is None:
                bot.send_message(self.id, "Вы пытаетесь отправить решение для несуществующей задачи")
                return
            list_of_parcels = database.get_user_problem_parcels(self.id, id_of_parcell, coonection)
            if len(list_of_parcels) == 0:
                self._cmd_status = "pushing_parcel"
                self.cur_task_id = id_of_parcell
                bot.send_message(self.id, "Отправка", reply_markup=kb)
            else:
                self._cmd_status = "updating_parcell"
                self.cur_task_id = id_of_parcell
                bot.send_message(self.id, "Обновление посылки")
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
        if cmd[:10] == "updateTask":
            if statuses[self.status] == 0:
                bot.send_message(self.id, "У вас нет прав для этой команды")
                return
            else:
                id_of_task = int(cmd.split(" ")[1])
                if len(cmd.split()) < 4:
                    group = "None"
                else:
                    group = cmd.split()[3]
                coonection = get_connection(threading.current_thread().native_id)
                if database.get_problem(id_of_task, coonection) is None:
                    bot.send_message(self.id, "Вы пытаетесь обновить несущеуствующую задачу")
                    return
                if len(cmd.split(" ")) not in (3, 4):
                    bot.send_message(self.id, "Комнда должна быть в виде: /updateTask <ID> <visible/invisible> [group]")
                    return
                while True:
                    visibility_status = str(cmd.split(" ")[2])
                    if visibility_status not in ["visible", "invisible"]:
                        bot.send_message(self.id, "Некорректный формат статуса")
                        return
                    else:
                        if visibility_status == "visible":
                            visibility_status = 1
                        else:
                            visibility_status = 0
                        break
                current_task = database.get_problem(id_of_task, coonection)
                current_task.visible = visibility_status
                current_task.group = group
                now = datetime.datetime.now()
                timestamp = int(datetime.datetime.timestamp(now))
                current_task.time_of = timestamp
                bot.send_message(self.id, "Обновление таска")
                self.cur_Task = current_task
                self._cmd_status = "updating_task"
                return
        if cmd == 'profile':
            bot.send_message(self.id, f'Имя: {self.name}\n'
                                      f'Статус: {self.status}\n'
                                      f'Группа: {self.study_group}'
                                      )
            return
        if cmd == "exit":
            if self.status == "teacher" or self.status == "super_user":
                bot.send_message(self.id, "Ваш статус был изменен", reply_markup=kb)  # super user to student)
                self.status = "student"
                return
            else:
                bot.send_message(self.id, "У вас нет доступа к данной команде")
        if cmd[:10] == "deleteTask":
            if self.status == "teacher" or self.status == "super_user":
                if len(cmd.split(" ")) == 1:
                    bot.send_message(self.id, "Вы не ввели ID задачи")
                    return
                id_of_task = int(cmd.split(" ")[1])
                coonection = get_connection(threading.current_thread().native_id)
                if database.get_problem(id_of_task, coonection) is not None:
                    database.delete_problem(id_of_task, coonection)
                    bot.send_message(self.id, f"Задача под индексом {id_of_task} была удалена")
                    return
                else:
                    bot.send_message(self.id, "Данной команды нет в базе данных")
                    return
            else:
                bot.send_message(self.id, "У вас нет доступа к этой команде")
                return
        if cmd[:6] == 'status':
            cmd = cmd.split()
            if len(cmd) != 2:
                bot.send_message(self.id, 'Некорректный формат.')
                return
            try:
                problem_id = int(cmd[1])
            except Exception as e:
                bot.send_message(self.id, 'Некорректный формат.')
                return
            parcels_list = database.get_user_problem_parcels(self.id, problem_id, get_connection(threading.current_thread().native_id))
            if len(parcels_list) == 0:
                bot.send_message(self.id, "У вас ещё нет посылок.")
                return
            is_visible = True if database.get_problem(problem_id, get_connection(threading.current_thread().native_id)).visible == 1 else False
            parcels_list.sort(key=lambda x: x.date)
            res = 'Ваши посылки:\n\nНомер\Баллы\Время отправки\n'
            for i in range(len(parcels_list)):
                date = datetime.datetime.utcfromtimestamp(parcels_list[i].date).strftime('%Y-%m-%d %H:%M:%S')
                res += f'[{i+1}]' + ' ' + f'{parcels_list[i].points if is_visible else "Баллы скрыты"}' + ' ' + f'{date}\n'
            bot.send_message(self.id, res)

        if cmd[:7] == "addTask":
            if self.status == "teacher" or self.status == "super_user":
                coonection = get_connection(threading.current_thread().native_id)
                if len(cmd.split(" ")) not in (3, 4):
                    bot.send_message(self.id, "Комнда должна быть в виде: /addTask <ID> <visible/visible> [group]")
                    return
                while True:
                    visibility_status = str(cmd.split(" ")[2])
                    if visibility_status not in ["visible", "invisible"]:
                        bot.send_message(self.id, "Некорректный формат статуса")
                        # bot.send_message(self.id, visibility_status)
                        return
                    else:
                        break
                id_of = int(str(cmd.split(" ")[1]))
                if len(cmd.split()) < 4:
                    group = "None"
                else:
                    group = cmd.split()[3]
                if visibility_status == "visible":
                    visibility_status = 1
                else:
                    visibility_status = 0
                cur_task = database.get_problem(id_of, coonection)
                if cur_task is not None:
                    bot.send_message(self.id, 'Данная задача уже существует.')
                    return
                bot.send_message(self.id, "Добавляем")
                self._cmd_status = "admin_pulling_task"
                new_one = TASK(id_of, visibility_status, group=group)
                now = datetime.datetime.now()
                timestamp = int(datetime.datetime.timestamp(now))
                new_one.time_of = timestamp
                new_one.id_of_user = self.id
                self.cur_Task = new_one
                return
            else:
                bot.send_message(self.id, "У вас нет доступа к этой команде")
        if cmd[:7] == 'getTask':
            cmd = cmd.split()[1:]
            try:
                task_id = int(cmd[0])
            except Exception as e:
                bot.send_message(self.id, 'Некорректный формат ввода.')
                return
            cur_task = database.get_problem(task_id, get_connection(threading.current_thread().native_id))
            if cur_task is None:
                bot.send_message(self.id, 'Задача не существует.')
                return
            if (cur_task.id_of_user != self.id and cur_task.group != self.study_group and self.status != 'super_user') and cur_task.group != "None":
                bot.send_message(self.id, 'Отказано в доступе.')
                return
            bot.send_message(self.id, f'ID: {cur_task.id}\nУсловие: {cur_task.statement}'
                                      f'\nГруппа: {"Публичная" if cur_task.group == "None" else cur_task.group}')


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
