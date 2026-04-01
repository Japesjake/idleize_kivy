import sqlite3, socket, threading, time, queue

class Connection():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.msg = 'default message'
        self.msg_queue = queue.Queue()
        self.idling = False
        self.client_thread = self.start_client_thread()
        self.idle_thread = self.start_idle_thread()
        self.addr_concat = self.addr[0] + ":" + str(self.addr[1])
        self.player_id = self.get_player_id('JpJab')
    def client_thread_func(self, conn, addr, q):
        with conn:
            while True:
                self.msg = conn.recv(1024).decode('utf-8')
                if self.msg:
                    print(f"Received from {addr}: {self.msg}")
                    q.put(self.msg)
                    if not self.idling: self.idling = True
                    else: self.idling = False
    def start_client_thread(self):
        client_thread = threading.Thread(target=self.client_thread_func, args=(self.conn, self.addr, self.msg_queue))
        # self.set_address('JpJab')
        client_thread.start()
        return client_thread
    def idle_thread_func(self):
        while True:
            msg = self.msg_queue.get()
            while self.idling:
                time.sleep(1)
                print('idling...')
                ###########
                self.process(msg) #############
                ############
    def start_idle_thread(self):
        idle_thread = threading.Thread(target=self.idle_thread_func)
        idle_thread.start()
        return idle_thread
    def set_address(self, player_name):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('UPDATE Player SET address = ? WHERE name = ?;', (self.addr_concat,player_name))
            db_connection.commit()
    def get_player_id(self, player_name):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('SELECT player_id FROM Player WHERE name = ?;',(player_name,))
            self.player_id = cursor.fetchall()[0][0]
            return self.player_id
    def get_item_id(self, msg):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('SELECT item_id FROM item WHERE item_name = ?',(msg,))
            item_id = cursor.fetchall()[0][0]
            return item_id
    def process(self,msg):
        with sqlite3.connect('data.db') as db_connection:
            item_id = self.get_item_id(msg)
            cursor = db_connection.cursor()
            cursor.execute('UPDATE PlayerItem SET count = count + 1 WHERE player_id = ? AND item_id = ?;',(self.player_id, item_id))
            db_connection.commit()
            cursor.execute('SELECT count FROM PlayerItem')
            counts = cursor.fetchall()
            print('counts: ', counts)

class Server():
    def __init__(self):
        self.connections = []
        self.idle_threads = []
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host, port = ('0.0.0.0', 1235)
            s.bind((host, port))
            s.listen()
            print(f"Server listening on {host}:{port}")
            while True:
                self.conn, self.addr = s.accept()
                print("connection from: ", self.addr)
                self.addr_concat = self.addr[0] + ":" + str(self.addr[1])
                connection = Connection(self.conn, self.addr)
                self.connections.append(connection)


server = Server()
if __name__ == '__main__': server.run()