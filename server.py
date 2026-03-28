import sqlite3, socket

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

# cursor.execute("INSERT INTO Player (name) VALUES ('JpJab');")
# connection.commit()
# connection.close()

# cursor.execute("INSERT INTO PlayerItem (player_id, item_id) VALUES (0,0);")
# connection.commit()
# connection.close()

import socket

def main():
    host, port = '127.0.0.1', 1234
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")
    while True:
        conn, address = server_socket.accept()
        print("Connection from: " + str(address))
    # conn.close()

if __name__ == '__main__': main()
