import json
import signal

from telebot import types

import Package.Package
import Task.Task
import database
import users
import threading


def save_data(_signal, _frame):
    """Saves data when the program is going to be closed"""
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
    except ...:
        print('While starting system it was unable to read config.json file')


def main():
    """Main function of app"""
    cmd_list = ['help', 'start', 'report', 'send', 'status', 'su', "adminLog", "adminHelp", "exit",
                "addTask"
                ]

    #  starting cleaning cache
    th = threading.Thread(target=users.cycle_check)
    th.daemon = True
    th.start()

    #  handlers
    @users.bot.message_handler(commands=cmd_list)
    def receive_cmds(message):
        user_id = message.from_user.id
        cmd = message.text[1:]

        connection = users.get_connection(threading.current_thread().native_id)
        users.update_cache(user_id, connection)
        users.cache[user_id].data[1].cmd_handler(cmd)

    @users.bot.message_handler(content_types=['text'])
    def receive_txt(message):
        user_id = message.from_user.id
        txt = message.text
        if txt[0] == '/':  # Checking that the given text is not an attempt to enter a command
            users.bot.reply_to(message, "Такой команды не существует")
        else:
            connection = users.get_connection(threading.current_thread().native_id)
            users.update_cache(user_id, connection)
            users.cache[user_id].data[1].txt_handler(txt)

    @users.bot.message_handler(content_types=['document'])
    def receive_doc(message):
        file_info = users.bot.get_file(message.document.file_id)
        """
        Checking and downloading a file
        """
        if message.document.file_name[-2:] != "py":
            users.bot.reply_to(message, "Неправильный формат данных")
            return
        download = users.bot.download_file(file_info.file_path)  # This part addes just for testing
        # For testing on your computer - pass ypi own way
        src = message.document.file_name
        with open(src, "wb") as new_file:
            new_file.write(download)
        users.bot.reply_to(message, "Ваш файл был принят")

    users.bot.polling(non_stop=True)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, save_data)
    signal.signal(signal.SIGTERM, save_data)
    init()
    try:
        main()
    except Exception as e:
        print(f'[Fatal system error]: {e}')
