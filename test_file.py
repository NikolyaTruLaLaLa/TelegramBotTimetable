import sqlite3

with sqlite3.connect('data/timetable') as con:
    a = con.execute('''SELECT * FROM users_st''').fetchall()
    for x in a:
        print(x)

    print(con.execute('''SELECT * FROM les_1''').fetchall()[0])

    #for x in con.execute(f'''SELECT * FROM les_1''').fetchall():
        #print(x)
