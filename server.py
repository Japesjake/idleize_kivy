import sqlite3, socket, threading, time, queue

class Connection():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.thread = None
        self.msg = 'default message'
        self.msg_queue = queue.Queue()
        self.addr_concat = self.addr[0] + ":" + str(self.addr[1])
        self.player_id = self.get_player_id('JpJab')
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
            cursor.execute('UPDATE Player SET address = ? WHERE name = ?;', (self.addr_concat,player_name))
            db_connection.commit()
    def get_player_id(self, player_name):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('SELECT player_id FROM Player WHERE name = ?;',(player_name,))
            self.player_id = cursor.fetchall()
            print(self.player_id)

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
                self.addr_concat = self.addr[0] + ":" + str(self.addr[1])
                connection = Connection(self.conn, self.addr)
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
                    self.process(msg, connection.addr_concat, connection)
    def get_item_id(self, msg):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('SELECT item_id FROM item WHERE item_name = ?',(msg,))
            item_id = cursor.fetchall()[0][0]
            return item_id
    def process(self, msg, addr_concat, connection):
        with sqlite3.connect('data.db') as db_connection:
            self.item_id = self.get_item_id(msg)
            cursor = db_connection.cursor()
            cursor.execute('UPDATE PlayerItem SET count = count + 1 WHERE player_id = ? AND item_id = ?;',(connection.player_id, self.item_id))
            db_connection.commit()
            cursor.execute('SELECT count FROM PlayerItem')

            print(connection.player_id)

server = Server()
if __name__ == '__main__': server.run()