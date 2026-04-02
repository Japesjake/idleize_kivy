import sqlite3, socket, threading, time, queue, json

msg_queue = queue.Queue()
connections = []
idle_threads = []
def get_player_id(player_name):
    with sqlite3.connect('data.db') as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('SELECT player_id FROM Player WHERE name = ?;',(player_name,))
        player_id = cursor.fetchall()[0][0]
        return player_id

class Connection():
    def __init__(self, conn, addr, s):
        self.conn = conn
        self.addr = addr
        self.msg = 'default message'
        self.idling = False
        self.client_thread = self.start_client_thread()
        self.addr_concat = self.addr[0] + ":" + str(self.addr[1])
        self.player_id = get_player_id('JpJab')
        self.s = s
    def client_thread_func(self, conn, addr, q):
        with conn:
            while True:
                self.msg = conn.recv(1024).decode('utf-8')
                if self.msg:
                    print(f"Received from {addr}: {self.msg}")
                    self.msg = json.loads(self.msg)
                    q.put(self.msg)
    def start_client_thread(self):
        client_thread = threading.Thread(target=self.client_thread_func, args=(self.conn, self.addr, msg_queue))
        client_thread.start()
        return client_thread
    def set_address(self, player_name):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('UPDATE Player SET address = ? WHERE name = ?;', (self.addr_concat,player_name))
            db_connection.commit()
class Server():
    def __init__(self):
        self.conn = None
        self.addr = None 
        
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host, port = ('0.0.0.0', 1234)
            s.bind((host, port))
            s.listen()
            print(f"Server listening on {host}:{port}")
            while True:
                self.conn, self.addr = s.accept()
                print("connection from: ", self.addr)
                connection = Connection(self.conn, self.addr, s)
                connections.append(connection)
                booleans = [idle_thread.player_id == connection.player_id for idle_thread in idle_threads]
                if not any(booleans): self.create_idle_thread()
                for idle_thread in idle_threads:
                    for connection in connections:
                        if idle_thread.player_id == connection.player_id:
                            msg = str(idle_thread.idling).encode('utf-8')
                            self.conn.sendall(msg)
                            print("sent message to client: ", msg)
    def create_idle_thread(self):
        idle_thread = Idle_thread()
        idle_threads.append(idle_thread)
        idle_thread.start()
        print('thread created')
class Idle_thread():
    def __init__(self):
        self.player_id = get_player_id('JpJab')
        self.idling = False
    def idle_loop(self):
        while True:
            msg = msg_queue.get()
            self.idling = msg[2]
            while self.idling:
                print('idling...')
                time.sleep(1)
                ###########
                self.process(msg)
                ############
                if not msg_queue.empty():
                    msg = msg_queue.get()
                    self.idling = msg[2]
                
    def start(self):
        idle_thread = threading.Thread(target=self.idle_loop)
        idle_thread.start()
        return idle_thread
    def process(self,msg):
        with sqlite3.connect('data.db') as db_connection:
            item_id = self.get_item_id(msg)
            cursor = db_connection.cursor()
            cursor.execute('UPDATE PlayerItem SET count = count + 1 WHERE player_id = ? AND item_id = ?;',(self.player_id, item_id))
            db_connection.commit()
            cursor.execute('SELECT count FROM PlayerItem')
            count = cursor.fetchall()
            print(count)
    def get_item_id(self, msg):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('SELECT item_id FROM item WHERE item_name = ?',(msg[0],))     
            item_id = cursor.fetchall()[0][0]
            return item_id
    
server = Server()
if __name__ == '__main__': server.run()