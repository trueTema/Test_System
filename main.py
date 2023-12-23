import datetime
import json
import signal
from AntiSpamSystem import AntiSpam as AS
import database
import users
import threading


def save_data():
    with open('Files/banned.json', 'w') as file:
        json.dump(list(users.banned_users), file)
        file.close()
    cur = users.activity.head
    connection = users.get_connection(threading.current_thread().native_id)
    while cur is not None:
        database.update_user_info(cur.data[1], connection)
        cur = cur.next


def signal_handler(_signal, _frame):
    """Saves data when the program is going to be closed"""
    save_data()
    exit(0)


min_message_time_interval = 5
"""Minimum time interval between messages"""

max_requests_per_minute_count = 20
"""Maximum requests count need not to be banned per minute"""


def init():
    """Initializing variables"""
    try:
        with open('Files/config.json', 'r') as file:
            data = json.load(file)
            users.max_cache_size = data["max_cache_size"]
            users.max_afk_time = data["max_afk_time"]
            users.time_between_checks = data["time_between_checks"]
            main.min_message_time_interval = data["min_time_interval"]
            main.max_requests_per_minute_count = data["max_request_per_minute_count"]
            file.close()
        with open('Files/banned.json', 'r') as file:
            users.banned_users = set(list(json.load(file)))
            file.close()
    except Exception as e:
        print(f'While starting system {e} has occured.')


def main():
    """Main function of app"""
    cmd_list = [
                'help', 'start', 'report', 'send', 'profile', 'su', "adminLog", "adminHelp", "exit",
                "addTask", "addScript", "deleteTask", "updateTask", "getTask", "status", "stats", "deleteParcel",
                "getLog", "getUserList"
                ]

    #  starting cleaning cache
    th = threading.Thread(target=users.cycle_check)
    th.daemon = True
    th.start()

    last_activity = {}
    """Anti-spam system element"""

    antispam = AS(60, main.max_requests_per_minute_count)

    #  handlers
    @users.bot.message_handler(commands=cmd_list)
    def receive_cmds(message):
        user_id = message.from_user.id
        if user_id in users.banned_users:
            users.bot.send_message(user_id, 'Вы заблокированы. Обратитесь к администратору')
            return
        #  ban all users with too much requests per minute
        antispam.request(user_id, float(datetime.datetime.timestamp(datetime.datetime.now())))
        ban_list = antispam.user_id_list()
        for _user_id in ban_list:
            users.banned_users.add(_user_id)
            users.bot.send_message(user_id, 'Вы заблокированы Анти-Спам системой. Обратитесь к администратору.')
            return

        if user_id not in last_activity.keys():
            last_activity[user_id] = datetime.datetime.timestamp(datetime.datetime.now())
        else:
            now = datetime.datetime.timestamp(datetime.datetime.now())
            if (now - last_activity[user_id]) < main.min_message_time_interval:
                users.bot.send_message(user_id, 'Слишком частые запросы.')
                last_activity[user_id] = now
                return
            last_activity[user_id] = now
        cmd = message.text[1:]

        try:
            connection = users.get_connection(threading.current_thread().native_id)
            users.update_cache(user_id, connection)
        except Exception as e:
            print(f'Cache error: {e}')
        try:
            users.cache[user_id].data[1].cmd_handler(cmd)
        except Exception as e:
            print(f'Command handler error: {e}')

    @users.bot.message_handler(content_types=['text'])
    def receive_txt(message):
        user_id = message.from_user.id
        if user_id in users.banned_users:
            users.bot.send_message(user_id, 'Вы заблокированы. Обратитесь к администратору')
            return
        #  ban all users with too much requests per minute
        antispam.request(user_id, int(datetime.datetime.timestamp(datetime.datetime.now())))
        ban_list = antispam.user_id_list()
        for _user_id in ban_list:
            users.banned_users.add(_user_id)
            users.bot.send_message(user_id, 'Вы заблокированы Анти-Спам системой. Обратитесь к администратору.')
            return

        if user_id not in last_activity.keys():
            last_activity[user_id] = datetime.datetime.timestamp(datetime.datetime.now())
        else:
            now = datetime.datetime.timestamp(datetime.datetime.now())
            if (now - last_activity[user_id]) < main.min_message_time_interval:
                users.bot.send_message(user_id, 'Слишком частые запросы.')
                last_activity[user_id] = now
                return
            last_activity[user_id] = now
        txt = message.text
        if txt[0] == '/':  # Checking that the given text is not an attempt to enter a command
            users.bot.reply_to(message, "Неизвестная команда")
        else:

            try:
                connection = users.get_connection(threading.current_thread().native_id)
                users.update_cache(user_id, connection)
            except Exception as e:
                print(f'Cache error: {e}')
            try:
                users.cache[user_id].data[1].txt_handler(txt)
            except Exception as e:
                print(f'Text handler error: {e}')

    @users.bot.message_handler(content_types=['document'])
    def receive_doc(message):
        user_id = message.from_user.id
        if user_id in users.banned_users:
            users.bot.send_message(user_id, 'Вы заблокированы. Обратитесь к администратору')
            return
        #  ban all users with too much requests per minute
        antispam.request(user_id, int(datetime.datetime.timestamp(datetime.datetime.now())))
        ban_list = antispam.user_id_list()
        for _user_id in ban_list:
            users.banned_users.add(_user_id)
            users.bot.send_message(user_id, 'Вы заблокированы Анти-Спам системой. Обратитесь к администратору.')
            return

        if user_id not in last_activity.keys():
            last_activity[user_id] = datetime.datetime.timestamp(datetime.datetime.now())
        else:
            now = datetime.datetime.timestamp(datetime.datetime.now())
            if (now - last_activity[user_id]) < main.min_message_time_interval:
                users.bot.send_message(user_id, 'Слишком частые запросы.')
                last_activity[user_id] = now
                return
            last_activity[user_id] = now
        """
        Checking and downloading a file
        """
        file_info = users.bot.get_file(message.document.file_id)
        type_of_file = None
        if message.document.file_name[-2:] == "py":
            type_of_file = message.document.file_name[-2:]
            #  This file from Teacher
        elif message.document.file_name[-3:] == "txt":
            type_of_file = message.document.file_name[-3:]
        if type_of_file is None:
            users.bot.reply_to(message, "Некорректный формат данных")
            return
        download = users.bot.download_file(file_info.file_path)
        try:
            connection = users.get_connection(threading.current_thread().native_id)
            users.update_cache(user_id, connection)
        except Exception as e:
            print(f'Cache error: {e}')
        try:
            users.cache[user_id].data[1].doc_handler(download, type_of_file)
        except Exception as e:
            print(f'Document handler error: {e}')
        return

    users.bot.polling(non_stop=True)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    init()
    try:
        main()
    except Exception as e:
        save_data()
        print(f'[Fatal system error]: {e}')
        exit(0)
