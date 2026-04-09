import sqlite3

try:
    with sqlite3.connect('data.db') as connection:
        cursor = connection.cursor()
except sqlite3.Error: print('error connecting to database')

# def create_db():
#     with open("create_db.sql", "r") as sql_file:
#         sql_script = sql_file.read()
#     cursor.executescript(sql_script)
#     connection.commit()
#     connection.close()
# create_db()

# cursor.execute("INSERT INTO Item (item_name) VALUES ('copper ore');")
# connection.commit()
# connection.close()

# cursor.execute("INSERT INTO Player (name) VALUES ('DC');")
# connection.commit()
# connection.close()

# cursor.execute("INSERT INTO PlayerItem (player_id, item_id, count) VALUES (1,2,0);")
# connection.commit()
# connection.close()

# cursor.execute("SELECT P.name, I.item_name FROM PlayerItem PI JOIN Player P ON P.player_id = PI.player_id JOIN Item I ON I.item_id = PI.item_id WHERE p.name = 'JpJab';")
# cursor.execute("SELECT * FROM item")
# print(cursor.fetchall())
# connection.close()

cursor.execute('ALTER TABLE PlayerItem ADD COLUMN count INTEGER')
connection.commit()
connection.close()

with sqlite3.connect('data.db') as db_connection:
    cursor = db_connection.cursor()
    cursor.execute('SELECT player_id FROM Player WHERE name = ?;',('JpJab',))
    print(cursor.fetchall()[0][0])