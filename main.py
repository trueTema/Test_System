import json
import database
import users
from users import User, max_afk_time, max_cache_size, time_between_checks, check_cache, update_cache, cache, bot
import threading

import atexit


#  saving data when process is terminating
def save_data():
    try:
        cur = users.activity.head
        while cur is not None:
            database.update_user_info(cur.data[1])
    except KeyboardInterrupt:
        pass


atexit.register(save_data)

cmd_list = ['help', 'start', 'report', 'send', 'status', 'su']

#  initializing variables:
try:
    with open('config.json', 'r') as file:
        data = json.load(file)
        max_cache_size = data["max_cache_size"]
        max_afk_time = data["max_afk_time"]
        time_between_checks = data["time_between_checks"]
        file.close()
except ...:
    print('While starting system it was unable to read config.json file')

#  starting script of cleaning cache
th = threading.Thread(target=check_cache)
th.daemon = True
th.start()


#  message handlers
@bot.message_handler(commands=cmd_list)
def receive_cmds(message):
    user_id = message.from_user.id
    cmd = message.text[1:]
    update_cache(user_id)
    cache[user_id].data[1].cmd_handler(cmd)


@bot.message_handler(content_types=['text'])
def receive_txt(message):
    user_id = message.from_user.id
    txt = message.text
    update_cache(user_id)
    cache[user_id].data[1].txt_handler(txt)


@bot.message_handler(content_types=['document'])
def receive_doc(message):
    ...


bot.polling(non_stop=True)
