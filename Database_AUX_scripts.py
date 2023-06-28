import sqlite3

#  just scirpts for test, not program

connect = sqlite3.connect("user_info.sql")
cur = connect.cursor()

#  script
#  cur.execute(f"insert into users(id, name, status, study_group) values(5, \"a\", \"bb\", \"ccc\");")
cur.execute(f"select * from problems;")
#  cur.execute(f"update users set id = 8 where id = 5")
#cur.execute(f"delete from users")
print(cur.fetchall())
cur.close()
connect.commit()
connect.close()
