import json
import multiprocessing
import signal
import time

import telebot.types

import database
import users
import threading


def save_data(_signal, _frame):
    """Saves data when the program is going to be closed"""
    cur = users.activity.head
    while cur is not None:
        database.update_user_info(cur.data[1])
    exit(0)


def main():
    """Main function of app"""
    #  initializing variables:
    try:
        with open('config.json', 'r') as file:
            data = json.load(file)
            users.max_cache_size = data["max_cache_size"]
            users.max_afk_time = data["max_afk_time"]
            users.time_between_checks = data["time_between_checks"]
            file.close()
    except ...:
        print('While starting system it was unable to read config.json file')

    cmd_list = ['help', 'start', 'report', 'send', 'status', 'su']

    #  starting cleaning cache
    th = threading.Thread(target=users.check_cache)
    th.daemon = True
    th.start()

    #  handlers
    @users.bot.message_handler(commands=cmd_list)
    def receive_cmds(message):
        user_id = message.from_user.id
        cmd = message.text[1:]
        users.update_cache(user_id)
        users.cache[user_id].data[1].cmd_handler(cmd)

    @users.bot.message_handler(content_types=['text'])
    def receive_txt(message):
        user_id = message.from_user.id
        txt = message.text
        users.update_cache(user_id)
        users.cache[user_id].data[1].txt_handler(txt)

    @users.bot.message_handler(content_types=['document'])
    def receive_doc(message):
        ...

    users.bot.polling(non_stop=True)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, save_data)
    signal.signal(signal.SIGTERM, save_data)
    try:
        main()
    except Exception as e:
        print(f'[Fatal system error]: {e}')
