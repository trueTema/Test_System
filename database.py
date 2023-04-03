import sqlite3
import users


def add_user(user: users.User, connection: sqlite3.Connection):
    """
    Adds user into database
    :param user: user object
    :param connection: connection to database
    """
    cur = connection.cursor()
    cur.execute(f"INSERT INTO users(id, name, status, study_group) "
                f"values({user.id}, \"{user.name}\", \"{user.status}\", \"{user.study_group}\");")
    connection.commit()
    cur.close()


def update_user_info(user: users.User, connection: sqlite3.Connection):
    """
    Updates info about user in database
    :param user: user object
    :param connection: connection to database
    """
    cur = connection.cursor()
    cur.execute(f"UPDATE users "
                f"set name = \"{user.name}\","
                f"status = \"{user.status}\","
                f"study_group = \"{user.study_group}\""
                f"where id = {user.id};")
    connection.commit()
    cur.close()


def get_user(id: int, connection: sqlite3.Connection) -> users.User or None:
    """
    Find info about user in database and returns it.
    :param id: user id
    :param connection: connection to database
    :return: user object or None if there is not user with such id
    """
    cur = connection.cursor()
    cur.execute(f"SELECT * FROM users where id = {id};")
    res = cur.fetchall()
    cur.close()
    if len(res) == 0:
        return None
    result = users.User(res[0][0], res[0][1], res[0][2], res[0][3])
    return result


def del_user(user: users.User, connection: sqlite3.Connection):
    """
    Deletes information about user from database
    :param user: user object
    :param connection: connection to database
    """
    cur = connection.cursor()
    cur.execute(f"DELETE * from users"
                f"where id = {user.id};")
    cur.close()
    connection.commit()
