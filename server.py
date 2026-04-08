import socket
import threading, queue, time

q = queue.Queue()
host = '0.0.0.0'
port = 1235
idle_threads = []
connections = []
class Server():
    def __init__(self):
        pass
    def handle_client(self, conn, addr, username):
        """Function to handle individual client communication."""
        print(f"[NEW CONNECTION] {addr} connected.")
        try:
            while True:
                # Receive data (blocking call)
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break  # Client disconnected
                


                q.put(data)
                
                print(f"[{addr}] says: {data}")
                
                # Echo back to client
                conn.send(f"Server received: {data}".encode('utf-8'))
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
            ####
            # username = conn.recv(1024).decode('uft-8')
            username = 'JpJab'
            ####
            thread = threading.Thread(target=self.handle_client, args=(conn, addr, username))
            connection = Connection(conn, addr, username, thread)
            connections.append(connection)
            connection.thread.start()

            conflict = False
            print(connections)
            print(idle_threads)
            for connection in connections:
                print(connection.username)
                for idle_thread in idle_threads:
                    print(idle_thread.username)
                    if connection.username == idle_thread.username:
                        conflict = True
                        print('conflict !!!!!')
            if not conflict:
                idle_thread = Idle_thread(username)
                idle_threads.append(idle_thread)
                idle_thread.start_idler()
                print(f"[ACTIVE THREADS] {threading.active_count() - 1}")

class Connection():
    def __init__(self, conn, addr, username, thread):
        self.conn = conn
        self.addr = addr
        self.username = username
        self.thread = thread


class Idle_thread():
    def __init__(self, username):
        self.idling = False
        self.username = username
    def idle_loop(self, username):
        # if not q.empty():
        #     msg = q.get()
        #     self.idling = msg[2]
        while True:
            print('idling...')
            print('.')
            time.sleep(1)
            if not q.empty():
                msg = q.get()
                self.idling = msg[2]
                if self.idling == False:
                    break
    def start_idler(self):
        idle_thread = threading.Thread(target=self.idle_loop, args=(self.username,))
        idle_thread.start()
        print(f"idle thread created.")

if __name__ == "__main__":
    server = Server()
    server.start_server()
