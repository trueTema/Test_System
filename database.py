import sqlite3
import time

import users
import Task
from Task import TASK
from Parcel import Parcel


max_timeout = 5
"""Maximum time of waiting of request answer in seconds"""
database_usage = False
"""Indicator that shows if the database is used by any request"""


def retry(function):
    """
    Retry decorator for requests to database
    :param function: request to database
    :return: decorator
    """
    def _wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        global database_usage
        while True:
            cur_time = time.perf_counter()
            if cur_time - start_time >= max_timeout:
                raise Exception(f'Timeout {max_timeout} seconds error')
            if not database_usage:
                database_usage = True
                result = function(*args, **kwargs)
                database_usage = False
                return result
    return _wrapper


@retry
def add_parcel(parcel: Parcel, connection: sqlite3.Connection):
    """
    Adds parcel to the database
    :param parcel: parcel object (Parcel class object)
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute("insert into parcels(problem_ID, student_ID, points, answer, sending_time, ID) "
                    f"values({parcel.id_task}, {parcel.id_user}, {parcel.points}, \"{parcel.answer}\", {parcel.date}, "
                    f"{parcel.id});")
        cur.close()
        connection.commit()
    except Exception as e:
        print(f'[Error] While adding a new parcel to database {e} has occurred.')
    finally:
        cur.close()


@retry
def delete_parcel(parcel_id: int, connection: sqlite3.Connection):
    """
    Deletes parcel from database
    :param parcel_id: parcel's id that we need to delete
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute(f"delete from parcels "
                    f"where ID = {parcel_id};")
        cur.close()
        connection.commit()
    except Exception as e:
        print(f'[Error] While deleting a parcel from database {e} has occurred.')
    finally:
        cur.close()


@retry
def get_parcel_by_id(id: int, connection: sqlite3.Connection):
    """
    Finds the parcel by its id
    :param id: parcel id we need to get
    :param connection: connection to database
    :return: parcel or None if the parcels doesn't exist
    """
    cur = connection.cursor()
    try:
        cur.execute(f"SELECT * from parcels where ID = {id};")
        res = cur.fetchall()
        cur.close()
        if len(res) == 0:
            return None
        res = res[0]
        result = Parcel(id_task=res[0], id_user=res[1], points=res[2], answer=res[3], date=res[4], id=res[5])
        return result
    except Exception as e:
        print(f'[Error] While adding a new problem {e} has occurred.')
    finally:
        cur.close()


@retry
def add_problem(problem: TASK, connection: sqlite3.Connection):
    """
    Adds problem into database
    :param problem: problem object (Task class object)
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute("INSERT INTO problems(problem_ID, teacher_ID, problem_situation, is_visible, users_group, "
                    "deadline, best_or_last) "
                    f"values({problem.id}, {problem.id_of_user}, \"{problem.statement}\", {problem.visible}, "
                    f"\"{problem.group}\", \"{problem.deadline}\", \"{problem.best_or_last}\");")
        cur.close()
        connection.commit()
    except Exception as e:
        print(f'[Error] While adding a new problem {e} has occurred.')
    finally:
        cur.close()


@retry
def get_problem(id: int, connection: sqlite3.Connection) -> Task.TASK or None:
    """
    Returns TASK by ID of problem
    :param id: ID of problem
    :param connection: connection to database
    :return: TASK object or None if it doesn't exist
    """
    cur = connection.cursor()
    try:
        cur.execute(f"select * from problems where problem_ID = {id};")
        res = cur.fetchall()
        cur.close()
        if len(res) == 0:
            return None
        res_task = TASK(id=res[0][0], visible=res[0][3], id_of_user=res[0][1], statement=res[0][2], group=res[0][6],
                        deadline=res[0][5] if res[0][5] != 'None' else users.inf, best_or_last=res[0][4])
        return res_task
    except Exception as e:
        print(f'[Error] While getting a problem from database {e} has occurred.')
    finally:
        cur.close()


@retry
def update_problem(problem: TASK, connection: sqlite3.Connection):
    """
    Updates info about problem in database
    :param problem: problem you need to update
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute(f"update problems "
                    f"set problem_situation = \"{problem.statement}\", "
                    f"is_visible = {problem.visible}, "
                    f"users_group = \"{problem.group}\", "
                    f"deadline = \"{problem.deadline}\", "
                    f"best_or_last = {problem.best_or_last} "
                    f"where problem_ID = {problem.id};")
        cur.close()
        connection.commit()
    except Exception as e:
        print(f'[Error] While updating a problem in database {e} has occurred.')
    finally:
        cur.close()


@retry
def delete_problem(problem_id: int, connection: sqlite3.Connection):
    """
    Deletes problem from database
    :param problem_id: id of problem you need to delete
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute(f"DELETE from problems "
                    f"where problem_ID = {problem_id};")
        cur.execute(f"delete from parcels "
                    f"where problem_ID = {problem_id}")
        cur.close()
        connection.commit()
    except Exception as e:
        print(f'[Error] While deleting an user from database {e} has occurred.')
    finally:
        cur.close()


@retry
def add_user(user: users.User, connection: sqlite3.Connection):
    """
    Adds user into database
    :param user: user object
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute(f"INSERT INTO users(id, name, status, study_group) "
                    f"values({user.id}, \"{user.name}\", \"{user.status}\", \"{user.study_group}\");")
        cur.close()
        connection.commit()
    except Exception as e:
        print(f'[Error] While adding a new parcel to database {e} has occurred.')
    finally:
        cur.close()


@retry
def update_user_info(user: users.User, connection: sqlite3.Connection):
    """
    Updates info about user in database
    :param user: user object
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute(f"UPDATE users "
                    f"set name = \"{user.name}\","
                    f"status = \"{user.status}\","
                    f"study_group = \"{user.study_group}\""
                    f"where id = {user.id};")
        cur.close()
        connection.commit()
    except Exception as e:
        print(f'[Error] While adding a new parcel to database {e} has occurred.')
    finally:
        cur.close()


@retry
def get_user(id: int, connection: sqlite3.Connection) -> users.User or None:
    """
    Find info about user in database and returns it.
    :param id: user id
    :param connection: connection to database
    :return: user object or None if there isn't user with such id
    """
    cur = connection.cursor()
    try:
        cur.execute(f"SELECT * FROM users where id = {id};")
        res = cur.fetchall()
        cur.close()
        if len(res) == 0:
            return None
        result = users.User(id=res[0][0], name=res[0][1], status=res[0][2], study_group=res[0][3])
        return result
    except Exception as e:
        print(f'[Error] While getting an user from database {e} has occurred.')
    finally:
        cur.close()


@retry
def del_user(user: users.User, connection: sqlite3.Connection):
    """
    Deletes information about user from database
    :param user: user object
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute(f"DELETE * from users"
                    f"where id = {user.id};")
        cur.close()
        connection.commit()
    except Exception as e:
        print(f'[Error] While deleting an user from database {e} has occurred.')
    finally:
        cur.close()


@retry
def get_user_list(connection: sqlite3.Connection) -> list[users.User]:
    """
    Returns a full list of registered users
    :param connection: connection to database
    :return: list of users
    """
    cur = connection.cursor()
    try:
        cur.execute(f"select * from users;")
        result = cur.fetchall()
        cur.close()
        if len(result) == 0:
            return result
        result = list(map(lambda sql_obj: users.User(id=int(sql_obj[0]), name=sql_obj[1], status=sql_obj[2],
                                                     study_group=sql_obj[3]), result))
        return result
    except Exception as e:
        print(f'[Error] While searching for user list in database {e} has occurred.')
    finally:
        cur.close()


#  special functions
@retry
def get_user_parcels(user_id: int, connection: sqlite3.Connection) -> list:
    """
    Returns a list of parcels that have been sent by this user.
    :param user_id: id of user
    :param connection: connection to database
    :return: list of user's parcels
    """
    cur = connection.cursor()
    try:
        cur.execute(f"select * from parcels "
                    f"where student_ID = {user_id};")
        res = cur.fetchall()
        cur.close()
        if len(res) == 0:
            return res
        res = list(map(lambda x: Parcel(id_user=x[1], id_task=x[0], points=x[2], answer=x[3], date=x[4], id=x[5]), res))
        return res
    except Exception as e:
        print(f'[Error] While searching for user\'s parcels in database {e} has occurred.')
    finally:
        cur.close()


@retry
def get_user_problem_parcels(user_id: int, problem_id: int, connection: sqlite3.Connection) -> list:
    """
    Returns a list of parcels that have been sent by this user.
    :rtype: object
    :param problem_id: problem's ID
    :param user_id: iof user
    :param connection: connection to database
    :return: list of user's parcels
    """
    cur = connection.cursor()
    try:
        cur.execute(f"select * from parcels "
                    f"where student_ID = {user_id} and problem_ID = {problem_id};")
        res = cur.fetchall()
        cur.close()
        if len(res) == 0:
            return res
        res = list(map(lambda x: Parcel(id_user=x[1], id_task=x[0], points=x[2], answer=x[3], date=x[4], id=x[5]), res))
        return res
    except Exception as e:
        print(f'[Error] While searching for user\'s parcels in database {e} has occurred.')
    finally:
        cur.close()


@retry
def get_problem_parcels(problem_id: int, connection: sqlite3.Connection) -> list:
    """
    Returns a list of parcels that have been sent for this problem.
    :param problem_id: problem's id
    :param connection: connection to database
    :return: list of problem's parcels
    """
    cur = connection.cursor()
    try:
        cur.execute(f"select * from parcels "
                    f"where problem_ID = {problem_id};")
        res = cur.fetchall()
        cur.close()
        if len(res) == 0:
            return res
        res = list(map(lambda x: Parcel(id_user=x[1], id_task=x[0], points=x[2], answer=x[3], date=x[4], id=x[5]), res))
        return res
    except Exception as e:
        print(f'[Error] While searching for problem\'s parcels in database {e} has occurred.')
    finally:
        cur.close()
