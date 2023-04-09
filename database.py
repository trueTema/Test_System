import datetime
import sqlite3
import users
from Task import Task
from Task.Task import TASK
from Package.Package import Package


def add_parcel(parcel: Package, connection: sqlite3.Connection):
    """
    Adds parcel to the database
    :param parcel: parcel object (Package class object)
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute("insert into parcels(problem_ID, student_ID, points, any_info, sending_time) "
                    f"values({parcel.id_task}, {parcel.id_user}, {parcel.points}, \"{parcel.answer}\", {parcel.date});")
        connection.commit()
    except Exception as e:
        print(f'[Error] While adding a new parcel to database {e} has occured.')
    finally:
        cur.close()


def update_parcel(parcel: Package, connection: sqlite3.Connection):
    """
    Updates parcel if user with that id has already sent parcel before.
    :param parcel: parcel that we need to update
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute("update parcels "
                    f"set points = {parcel.points}, "
                    f"sending_time = {parcel.date}, "
                    f"any_info = \"{parcel.answer}\" "
                    f"where student_ID = {parcel.id_user} and problem_ID = {parcel.id_task};")
        connection.commit()
    except Exception as e:
        print(f'[Error] While updating a parcel in database {e} has occured.')
    finally:
        cur.close()


def delete_parcel(parcel: Package, connection: sqlite3.Connection):
    """
    Deletes parcel from database
    :param parcel: parcel that we need to delete
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute(f"delete from parcels "
                    f"where problem_ID = {parcel.id_task} and student_ID = {parcel.id_user};")
        connection.commit()
    except Exception as e:
        print(f'[Error] While deleting a parcel from database {e} has occured.')
    finally:
        cur.close()


def add_problem(problem: TASK, connection: sqlite3.Connection):
    """
    Adds problem into database
    :param problem: problem object (Task class object)
    :param connection: connection to database
    """
    cur = connection.cursor()
    try:
        cur.execute("insert into problems(problem_ID, teacher_ID, problem_situation, is_visible)"
                    f"values({problem.id}, {problem.id_of_user}, \"{problem.statement}\", {problem.visible});")
        connection.commit()
    except Exception as e:
        print(f'[Error] While adding a new problem {e} has occured.')
    finally:
        cur.close()


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
        if len(res) == 0:
            return None
        res_task = TASK(id=res[0][0], visible=res[0][3], id_of_user=res[0][1], statement=res[0][2])
        return res_task
    except Exception as e:
        print(f'[Error] While getting a problem from database {e} has occured.')
    finally:
        cur.close()


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
                    f"is_visible = {problem.visible} "
                    f"where problem_ID = {problem.id};")
        connection.commit()
    except Exception as e:
        print(f'[Error] While updating a problem in database {e} has occured.')
    finally:
        cur.close()


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
        connection.commit()
    except Exception as e:
        print(f'[Error] While deleting an user from database {e} has occured.')
    finally:
        cur.close()


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
        connection.commit()
    except Exception as e:
        print(f'[Error] While adding a new parcel to database {e} has occured.')
    finally:
        cur.close()


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
        connection.commit()
    except Exception as e:
        print(f'[Error] While adding a new parcel to database {e} has occured.')
    finally:
        cur.close()


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
        if len(res) == 0:
            return None
        result = users.User(res[0][0], res[0][1], res[0][2], res[0][3])
        return result
    except Exception as e:
        print(f'[Error] While getting an user from database {e} has occured.')
    finally:
        cur.close()


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
        connection.commit()
    except Exception as e:
        print(f'[Error] While deleting an user from database {e} has occured.')
    finally:
        cur.close()


#  special functions
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
        if len(res) == 0:
            return res
        res = list(map(lambda x: Package(id_user=x[0], id_task=x[1], points=x[2], answer=x[3], date=x[4]), res))
        return res
    except Exception as e:
        print(f'[Error] While searching for user\'s parcels in database {e} has occured.')
    finally:
        cur.close()


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
        if len(res) == 0:
            return res
        res = list(map(lambda x: Package(id_user=x[0], id_task=x[1], points=x[2], answer=x[3], date=x[4]), res))
        return res
    except Exception as e:
        print(f'[Error] While searching for problem\'s parcels in database {e} has occured.')
    finally:
        cur.close()
