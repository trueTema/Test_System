import sqlite3

connect = sqlite3.connect("user_info.sql")
cur = connect.cursor()

#  script
#cur.execute(f"insert into users(id, name, status, study_group) values(5, \"a\", \"bb\", \"ccc\");")
cur.execute(f"update users set id = 8 where id = 5")
#cur.execute(f"select * from users;")

cur.close()
connect.commit()
connect.close()
