import json
import signal

import database
import users
import threading


def save_data(_signal, _frame):
    """Saves data when the program is going to be closed"""
    with open('Files/banned.json', 'w') as file:
        json.dump(list(users.banned_users), file)
    cur = users.activity.head
    connection = users.get_connection(threading.current_thread().native_id)
    while cur is not None:
        database.update_user_info(cur.data[1], connection)
        cur = cur.next
    exit(0)


def init():
    """Initializing variables"""
    try:
        with open('Files/config.json', 'r') as file:
            data = json.load(file)
            users.max_cache_size = data["max_cache_size"]
            users.max_afk_time = data["max_afk_time"]
            users.time_between_checks = data["time_between_checks"]
            file.close()
        with open('Files/banned.json', 'r') as file:
            users.banned_users = set(list(json.load(file)))
            file.close()
    except Exception as e:
        print(f'While starting system {e} has occured.')


def main():
    """Main function of app"""
    cmd_list = ['help', 'start', 'report', 'send', 'profile', 'su', "adminLog", "adminHelp", "exit",
                "addTask", "addScript", "deleteTask", "updateTask", "getTask", "status"
                ]

    #  starting cleaning cache
    th = threading.Thread(target=users.cycle_check)
    th.daemon = True
    th.start()

    #  handlers
    @users.bot.message_handler(commands=cmd_list)
    def receive_cmds(message):
        user_id = message.from_user.id
        if user_id in users.banned_users:
            users.bot.send_message(user_id, 'Вы заблокированы.')
            return
        cmd = message.text[1:]

        connection = users.get_connection(threading.current_thread().native_id)
        users.update_cache(user_id, connection)
        users.cache[user_id].data[1].cmd_handler(cmd)

    @users.bot.message_handler(content_types=['text'])
    def receive_txt(message):
        user_id = message.from_user.id
        if user_id in users.banned_users:
            users.bot.send_message(user_id, 'Вы заблокированы.')
            return
        txt = message.text
        if txt[0] == '/':  # Checking that the given text is not an attempt to enter a command
            users.bot.reply_to(message, "Неизвестная команда")
        else:
            connection = users.get_connection(threading.current_thread().native_id)
            users.update_cache(user_id, connection)
            users.cache[user_id].data[1].txt_handler(txt)

    @users.bot.message_handler(content_types=['document'])
    def receive_doc(message):
        file_info = users.bot.get_file(message.document.file_id)
        user_id = message.from_user.id
        """
        Checking and downloading a file
        """
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
        users.cache[user_id].data[1].doc_handler(download, type_of_file)
        return

    users.bot.polling(non_stop=True)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, save_data)
    signal.signal(signal.SIGTERM, save_data)
    init()
    try:
        main()
    except Exception as e:
        print(f'[Fatal system error]: {e}')
