import socket
import threading, queue, time, sqlite3

q = queue.Queue()
host = '0.0.0.0'
port = 1235

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
                    break  # Client disconnected
                # q.put(data)
                print(f"[{addr}] says: {data}")
                # Echo back to client
                conn.send(f"Server received: {data}".encode('utf-8'))
                if data in items:
                    conflict = False
                    for connection in connections:
                        for idle_thread in idle_threads:
                            if connection.username == idle_thread.username:
                                conflict = True
                    if not conflict:
                        idle_thread = Idle_thread(username, data)
                        idle_threads.append(idle_thread)
                        idle_thread.start_idler()
                    
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
            thread = threading.Thread(target=self.handle_client, args=(conn, addr, username))
            connection = Connection(conn, addr, username, thread)
            connections.append(connection)
            connection.thread.start()
            print(f"[ACTIVE THREADS] {threading.active_count() - 1}")

class Connection():
    def __init__(self, conn, addr, username, thread):
        self.conn = conn
        self.addr = addr
        self.username = username
        self.thread = thread


class Idle_thread():
    def __init__(self, username, item):
        self.idling = False
        self.username = username
        self.item = item
    def idle_loop(self):
        # if not q.empty():
        #     msg = q.get()
        #     self.idling = msg[2]
        sql_conn = sqlite3.connect('data.db')
        cursor = sql_conn.cursor()        
        while True:
            print('idling...')
            time.sleep(1)
            sql = "UPDATE PlayerItem SET count = count + 1 FROM Item, Player WHERE PlayerItem.item_id = Item.item_id AND PlayerItem.player_id = Player.player_id AND Item.item_name = ? AND Player.name = ?;"
            cursor.execute(sql,(self.item,self.username))
            sql_conn.commit()
            #######
            # if not q.empty():
            #     msg = q.get()
            #     self.idling = msg[2]
            #     if self.idling == False:
            #         break
    def start_idler(self):
        idle_thread = threading.Thread(target=self.idle_loop)
        idle_thread.start()
        print(f"idle thread created.")

if __name__ == "__main__":
    server = Server()
    server.start_server()
