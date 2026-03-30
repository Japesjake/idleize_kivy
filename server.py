import sqlite3, socket, threading, time

# try:
#     with sqlite3.connect('data.db') as connection:
#         cursor = connection.cursor()
# except sqlite3.Error: print('error connecting to database')

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
interval = 1
idling = False
start = False
msg = 'copper ore'
def send(msg, conn):
    conn.sendall(msg.encode('utf-8'))

def handle_client(conn, addr):
    with conn:
        while True:
            global msg
            msg = conn.recv(1024).decode('utf-8')
            if not msg:
                break
            print(f"Received from {addr}: {msg}")
            global idling
            if not idling:
                idling = True
            else: idling = False

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host, port = '0.0.0.0', 1234
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        while True:
            global conn
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
            idling_thread = threading.Thread(target=idle)
            idling_thread.start()

def idle():
    while True:
        if idling:
            time.sleep(1)
            process(msg)

def process(msg):
    try:
        with sqlite3.connect('data.db') as connection:
            cursor = connection.cursor()
    except sqlite3.Error: print('error connecting to database')
    time.sleep(1)
    player_name = 'JpJab'
    sql_get_player_id = "SELECT player_id FROM Player WHERE name = ?"
    cursor.execute(sql_get_player_id, (player_name,))
    player_id = cursor.fetchall()[0][0]

    cursor.execute("SELECT item_id FROM item WHERE item_name = ?",(msg,))
    item_id = cursor.fetchall()[0][0]

    sql_update = "UPDATE PlayerItem SET count = count + 1 WHERE player_id = ? AND item_id = ?"
    cursor.execute(sql_update, (player_id,item_id))

    # send(msg, conn) #### uncomment this when communicating with client

    # just prints the results
    sql_select = "SELECT P.name, I.item_name, PI.count FROM PlayerItem PI JOIN Player P ON P.player_id = PI.player_id JOIN Item I ON I.item_id = PI.item_id WHERE p.name = 'JpJab' AND i.item_name = ?;"
    cursor.execute(sql_select, (msg,))
    print(cursor.fetchall())

    connection.commit()
    connection.close()
    return True

if __name__ == '__main__': start_server()

# while True:
#     message = 'copper ore'
#     response = process(msg)
#     time.sleep(1)
