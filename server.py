import sqlite3, socket, threading, time, queue

class Connection():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.thread = None
        self.msg = 'default message'
        self.msg_queue = queue.Queue()
    def client_thread(self, conn, addr, q):
        with conn:
            while True:
                self.msg = conn.recv(1024).decode('utf-8')
                if self.msg:
                    print(f"Received from {addr}: {self.msg}")
                    q.put(self.msg)
    def start_client_thread(self):
        self.thread = threading.Thread(target=self.client_thread, args=(self.conn, self.addr, self.msg_queue))
        self.set_address('JpJab')
        self.thread.start()
    def set_address(self, player_name):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
        self.concatenated_address = self.addr[0] + ":" + str(self.addr[1])
        print(self.concatenated_address)
        cursor.execute('UPDATE Player SET address = ? WHERE name = ?', (self.concatenated_address,player_name))
        db_connection.commit()
        db_connection.close()
class Server():
    def __init__(self):
        self.connections = []
        self.idle_threads = []
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host, port = ('0.0.0.0', 1234)
            s.bind((host, port))
            s.listen()
            print(f"Server listening on {host}:{port}")
            while True:
                conn, addr = s.accept()
                connection = Connection(conn, addr)
                self.connections.append(connection)
                connection.start_client_thread()

                idle_thread = threading.Thread(target=self.idle_thread)
                self.idle_threads.append(idle_thread)
                idle_thread.start()
    def idle_thread(self):
        while True:
            time.sleep(1)
            for connection in self.connections:
                msg = connection.msg_queue.get()
                if msg:
                    # self.process(msg, addr)
                    pass
    def process(self):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()

def processes(message):
    try:
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
    except sqlite3.Error: print('error connecting to database')
    player_name = 'JpJab'
    sql_get_player_id = "SELECT player_id FROM Player WHERE name = ?"
    cursor.execute(sql_get_player_id, (player_name,))
    player_id = cursor.fetchall()[0][0]
    cursor.execute("SELECT item_id FROM item WHERE item_name = ?",(message,))
    item_id = cursor.fetchall()[0][0]
    # print(item_id)

    sql_update = "UPDATE PlayerItem SET count = count + 1 WHERE player_id = ? AND item_id = ?"
    cursor.execute(sql_update, (player_id,item_id))

    # send(msg, conn) #### uncomment this when communicating with client

    # just prints the results
    sql_select = "SELECT P.name, I.item_name, PI.count FROM PlayerItem PI JOIN Player P ON P.player_id = PI.player_id JOIN Item I ON I.item_id = PI.item_id WHERE p.name = 'JpJab' AND i.item_name = ?;"
    cursor.execute(sql_select, (message,))
    print(cursor.fetchall())

    sql_get_item_count = "SELECT count FROM PlayerItem WHERE item_id = ? AND player_id = ?"
    cursor.execute(sql_get_item_count, (item_id, player_id))
    item_count = cursor.fetchall()[0][0]


    db_connection.commit()
    db_connection.close()
    return str(item_count)


server = Server()
if __name__ == '__main__': server.run()

# while True:
#     message = 'copper ore'
#     response = process(msg)
#     time.sleep(1)

# def handle_client(conn, addr):
#     with conn:
#         while True:
#             global msg
#             msg = conn.recv(1024).decode('utf-8')
#             if msg:
#                 global message
#                 message = msg
#             if not msg:
#                 break
#             print(f"Received from {addr}: {msg}")
#             global idling
#             if not idling:
#                 idling = True
#             else: idling = False


# def start_server():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         host, port = '0.0.0.0', 1235
#         s.bind((host, port))
#         s.listen()
#         print(f"Server listening on {host}:{port}")
#         while True:
#             global conn
#             conn, addr = s.accept()
#             client_thread = threading.Thread(target=handle_client, args=(conn, addr))
#             client_thread.start()
#             if not idling:
#                 idling_thread = threading.Thread(target=idle)
#                 idling_thread.start()