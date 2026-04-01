import sqlite3, socket, threading, time, queue

class Connection():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.client_thread = None
        self.msg = 'default message'
        self.msg_queue = queue.Queue()
    def client_thread(self, conn, addr, q):
        with conn:
            while True:
                self.msg = conn.recv(1024).decode('utf-8')
                print(f"Received from {addr}: {self.msg}")
                q.put(self.msg)
    def start_client_thread(self):
        self.client_thread = threading.Thread(target=self.client_thread, args=(self.conn, self.addr, self.msg_queue))
        self.client_thread.start()
    def get_msg(self):
        return self.msg_queue
    def idle(self):
        while True:
            print(self.msg_queue)
    def start_idle_thread(self):
        pass
class Server():
    def __init__(self):
        self.connections = []
        self.idle_threads = []
        self.idling = True
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

            
if True:
    def send(msg):
        conn.sendall(msg.encode('utf-8'))

    def idle():
        while True:
            global idling
            if idling:
                time.sleep(1)
                response = process(message)
                send(response)


def process(message):
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