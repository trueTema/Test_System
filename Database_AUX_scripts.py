import sqlite3

#  just scirpts for test, not program

connect = sqlite3.connect("Files/database.sql")
cur = connect.cursor()
cur.execute("drop table if exists parcels")
cur.execute("CREATE TABLE IF NOT EXISTS parcels ("
            "problem_ID int not null, "
            "student_ID int check(student_ID > 0) not null, "
            "points float not null, "
            "answer text not null, "
            "sending_time big_int check(sending_time > 0), "
            "ID int check(ID > 0) unique not null"
            ");")
#  script
#  cur.execute(f"insert into users(id, name, status, study_group) values(5, \"a\", \"bb\", \"ccc\");")
cur.execute(f"select * from parcels;")
#  cur.execute(f"update users set id = 8 where id = 5")
#cur.execute(f"delete from users")
print(cur.fetchall())
cur.close()
connect.commit()
connect.close()
