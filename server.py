import socket
import threading, queue, time, sqlite3, json

q = queue.Queue()
host = '0.0.0.0'
port = 1234

idle_threads = []
connections = []

sql_conn = sqlite3.connect('data.db')
cursor = sql_conn.cursor()
cursor.execute("SELECT item_name FROM Item")
items = cursor.fetchall()
items = [item[0] for item in items]
print(items)
class Server():
    def __init__(self):
        pass
    def handle_client(self, conn, addr, username):
        """Function to handle individual client communication."""
        print(f"[NEW CONNECTION] {addr} connected.")
        try:
            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"[{addr}] says: {data}")
                if data in items:
                    conflict = False
                    for connection in connections:
                        for idle_thread in idle_threads:
                            if connection.username == idle_thread.username and idle_thread.idling:
                                print('There is a conflict. Ending loop.')
                                conflict = True
                                idle_thread.idling = False
                                print(f'There are {len(idle_threads)} idle threads active.')
                    if not conflict:
                        print('No conflict. Adding idle_thread...')
                        idle_thread = Idle_thread(username, data)
                        idle_threads.append(idle_thread)
                        idle_thread.thread.start()
                    
        except ConnectionResetError:
            pass
        finally:
            conn.close()
            print(f"[DISCONNECTED] {addr} closed.")
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        print(f"[LISTENING] Server is listening on localhost: {port}")
        while True:
            # Wait for a new connection (blocking call)
            conn, addr = server.accept()
            username = conn.recv(1024).decode('utf-8')
            print(f'username received: {username}')
            ## checks for relevant running threads then send info to client ##
            if idle_threads:
                for idle_thread in idle_threads:
                    if idle_thread.username == username:
                        conn.sendall(json.dumps((idle_thread.item,idle_thread.count)).encode('utf-8'))
                        print(f'Threading info sent to client: ({idle_thread.item},{idle_thread.count})')
            else: 
                conn.sendall(json.dumps('false').encode('utf-8'))
            ## Starts a new connection thread ##
            thread = threading.Thread(target=self.handle_client, args=(conn, addr, username))
            connection = Connection(conn, addr, username, thread)
            connections.append(connection)
            connection.thread.start()
            print(f"[ACTIVE THREADS] {threading.active_count() - 1}")

class Idle_thread():
    def __init__(self, username, item):
        self.idling = True
        self.username = username
        self.item = item
        self.count = 15
        self.thread = threading.Thread(target=self.idle_loop)
    def idle_loop(self):
        sql_conn = sqlite3.connect('data.db')
        cursor = sql_conn.cursor()    
        print('idling...')
        while self.idling:
            time.sleep(1)
            sql = "UPDATE PlayerItem SET count = count + 1 FROM Item, Player WHERE PlayerItem.item_id = Item.item_id AND PlayerItem.player_id = Player.player_id AND Item.item_name = ? AND Player.name = ?;"
            cursor.execute(sql,(self.item,self.username))
            sql_conn.commit()
            sql = "SELECT count FROM PlayerItem JOIN Player ON PlayerItem.player_id = Player.player_id JOIN Item ON PlayerItem.item_id = Item.item_id WHERE Player.name = ? AND Item.item_name = ?"
            cursor.execute(sql,(self.username, self.item))
            self.count = cursor.fetchall()[0][0]
            print(f'{self.item}, {self.count}')

class Connection():
    def __init__(self, conn, addr, username, thread):
        self.conn = conn
        self.addr = addr
        self.username = username
        self.thread = thread

if __name__ == "__main__":
    server = Server()
    server.start_server()
