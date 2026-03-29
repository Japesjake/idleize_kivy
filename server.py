import sqlite3, socket, threading, time

try:
    with sqlite3.connect('data.db') as connection:
        cursor = connection.cursor()
except sqlite3.Error: print('error connecting to database')

def create_db():
    with open("create_db.sql", "r") as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)
    connection.commit()
    connection.close()
# create_db()

# cursor.execute("INSERT INTO Item (item_name) VALUES ('copper ore');")
# connection.commit()
# connection.close()

# cursor.execute("INSERT INTO Player (name) VALUES ('DC');")
# connection.commit()
# connection.close()

# cursor.execute("INSERT INTO PlayerItem (player_id, item_id, count) VALUES (2,1,0);")
# connection.commit()
# connection.close()

cursor.execute("SELECT P.name, I.item_name FROM PlayerItem PI JOIN Player P ON P.player_id = PI.player_id JOIN Item I ON I.item_id = PI.item_id WHERE p.name = 'JpJab';")
# cursor.execute("SELECT * FROM item")
print(cursor.fetchall())
interval = 1
def handle_client(conn, addr):
    with conn:
        while True:
            message = conn.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received from {addr}: {message}")
            response = message
            time.sleep(interval)
            conn.sendall(response.encode('utf-8'))
    print(f"Connection with {addr} closed")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host, port = '127.0.0.1', 1234
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
    
    host, port = '127.0.0.1', 1234
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")
    while True:
        conn, address = server_socket.accept()
        print(f"Connection from: {address}")
    server_socket.close()

if __name__ == '__main__': start_server()
