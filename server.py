import socket
import threading, queue, time

q = queue.Queue()
host = '0.0.0.0'
port = 1234
idle_threads = []
connections = []
class Server():
    def __init__(self):
        self.addr = None
    def handle_client(self, conn, addr, username):
        """Function to handle individual client communication."""
        print(f"[NEW CONNECTION] {self.addr} connected.")
        try:
            while True:
                # Receive data (blocking call)
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break  # Client disconnected
                


                q.put(data)
                
                print(f"[{self.addr}] says: {data}")
                
                # Echo back to client
                conn.send(f"Server received: {data}".encode('utf-8'))
        except ConnectionResetError:
            pass
        finally:
            conn.close()
            print(f"[DISCONNECTED] {self.addr} closed.")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        print(f"[LISTENING] Server is listening on localhost: {port}")
        while True:
            
            # Wait for a new connection (blocking call)
            self.conn, self.addr = server.accept()
            ####
            # username = conn.recv(1024).decode('uft-8')
            username = 'JpJab'
            ####
            
            # Start a new thread for each client

            connection = threading.Thread(target=self.handle_client, args=(self.conn, self.addr, username))
            connections.append(connection)
            connection.start()
            conflict = False
            for connection in connections:
                for idle_thread in idle_threads:
                    if connection.username == idle_thread.username:
                        conflict = True
            if not conflict:
                idle_thread = Idle_thread(username)
                idle_thread.start_idler()
                print(f"[ACTIVE THREADS] {threading.active_count() - 1}")

class Idle_thread(threading.Thread):
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
        # print(f"idle thread.username = {idle_thread.username}")
        idle_threads.append(idle_thread)
        idle_thread.start()
        print(f"idle thread created.")

if __name__ == "__main__":
    server = Server()
    server.start()
