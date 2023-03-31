import sqlite3
import users


def add_user(user: users.User):
    """Adds user into database"""
    con = sqlite3.Connection("user_info.sql")
    cur = con.cursor()
    cur.execute(f"INSERT INTO users(id, name, status, study_group) "
                f"values({user.id}, \"{user.name}\", \"{user.status}\", \"{user.study_group}\");")
    con.commit()
    cur.close()
    con.close()


def update_user_info(user: users.User):
    """Updates info about user in database"""
    con = sqlite3.Connection("user_info.sql")
    cur = con.cursor()
    cur.execute(f"UPDATE users "
                f"set name = \"{user.name}\","
                f"status = \"{user.status}\","
                f"study_group = \"{user.study_group}\""
                f"where id = {user.id};")
    con.commit()
    cur.close()
    con.close()


def get_user(id: int):
    """Find info about user in database and returns it."""
    con = sqlite3.Connection("user_info.sql")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM users where id = {id};")
    res = cur.fetchall()
    cur.close()
    con.close()
    if len(res) == 0:
        return None
    result = users.User(res[0][0], res[0][1], res[0][2], res[0][3])
    return result


def del_user(user: users.User):
    """Deletes information about user from database"""
    con = sqlite3.Connection("user_info.sql")
    cur = con.cursor()
    cur.execute(f"DELETE * from users"
                f"where id = {user.id};")
    cur.close()
    con.commit()
    con.close()
