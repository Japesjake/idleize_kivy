import sqlite3, socket, threading, time, queue, json

##### msg = ["copper ore", "JpJab", true, count]

msg_queue = queue.Queue()
connections = []
idle_threads = []
host, port = ('0.0.0.0', 1234)
def get_all_items(player_id):
    with sqlite3.connect('data.db') as db_connection:
        cursor = db_connection.cursor()
    cursor.execute('SELECT Player.name, Item.item_name, PlayerItem.count FROM PlayerItem JOIN Player ON PlayerItem.player_id = Player.player_id JOIN Item ON PlayerItem.item_id = Item.item_id WHERE Player.player_id = ?',(player_id,))
    data = cursor.fetchall()
    return data
def get_player_id(player_name):
    with sqlite3.connect('data.db') as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('SELECT player_id FROM Player WHERE name = ?;',(player_name,))
        player_id = cursor.fetchall()[0][0]
        return player_id

def get_item_count(item_id):
    with sqlite3.connect('data.db') as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('SELECT count FROM PlayerItem WHERE item_id = ?;',(item_id,))
        item_count = cursor.fetchall()[0][0]
        return item_count
    
def send_message(idle_thread, connection, initial_data = False):
    if initial_data:
        msg = json.dumps((initial_data, 'initial'))
    else:
        msg = json.dumps((idle_thread.item_name, connection.player_name, str(idle_thread.idling), idle_thread.item_count))
    connection.conn.sendall(msg.encode('utf-8'))
    print('message sent to client: ', msg)

class Connection():
    def __init__(self, conn, addr, s):
        self.conn = conn
        self.addr = addr
        self.msg = 'default message'
        self.idling = False
        self.client_thread = self.start_client_thread()
        self.addr_concat = self.addr[0] + ":" + str(self.addr[1])
        self.player_name = 'JpJab'
        self.player_id = get_player_id(self.player_name)
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
        pass
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # host, port = ('0.0.0.0', 1234)
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

                ##### initial message #####
                for idle_thread in idle_threads:
                    for connection in connections:
                        if idle_thread.player_id == connection.player_id:
                            all_items = get_all_items(idle_thread.player_id)
                            data = {}
                            for row in all_items:
                                data[row[1]] = row[2]
                            send_message(idle_thread, connection)
                            send_message(idle_thread, connection, data)

            ### might need to comment out this part to fix connection refused error
            for connection in connections:
                if not connection.conn:
                    s.close()
    def create_idle_thread(self):
        idle_thread = Idle_thread()
        idle_threads.append(idle_thread)
        idle_thread.start()
        print('thread created')
class Idle_thread():
    def __init__(self):
        self.player_id = get_player_id('JpJab')
        self.idling = False
        self.item_id = 'item_id'
        self.item_name = 'item_name'
        self.item_count = 'item_count'
    def idle_loop(self):
        while True:
            msg = msg_queue.get()
            self.idling = msg[2]
            while True:
                print('idling...')
                time.sleep(1)
                if not msg_queue.empty():
                    msg = msg_queue.get()
                    self.idling = msg[2]
                if self.idling == False:
                    break
                ###########
                self.process(msg)
                ############
                
    def start(self):
        idle_thread = threading.Thread(target=self.idle_loop)
        idle_thread.start()
        return idle_thread
    def process(self,msg):
        with sqlite3.connect('data.db') as db_connection:
            self.item_name = msg[0]
            self.item_id = self.get_item_id(self.item_name)
            self.item_count = get_item_count(self.item_id)
            cursor = db_connection.cursor()
            cursor.execute('UPDATE PlayerItem SET count = count + 1 WHERE player_id = ? AND item_id = ?;',(self.player_id, self.item_id))
            db_connection.commit()
            cursor.execute('SELECT count FROM PlayerItem WHERE item_id = ?;',(self.item_id,))
            self.item_count = cursor.fetchall()
            print(self.item_count)
            ######
            for connection in connections:
                if connection.conn.fileno() != -1:
                    if connection.player_id == self.player_id:
                        send_message(self, connection)

    def get_item_id(self, name):
        with sqlite3.connect('data.db') as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('SELECT item_id FROM item WHERE item_name = ?',(name,))     
            item_id = cursor.fetchall()[0][0]
            return item_id
    
server = Server()
if __name__ == '__main__': server.run()