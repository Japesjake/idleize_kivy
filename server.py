import socket
import threading, queue

q = queue.Queue()
host = '0.0.0.0'
port = 1235
class Server():
    def __init__(self):
        self.addr = None
    def handle_client(self, conn, addr):
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
            
            # Start a new thread for each client
            thread = threading.Thread(target=self.handle_client, args=(self.conn, self.addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

class Idle_thread(threading.Thread):
    def __init__(self):
        self.idling = False
    def idle_loop(self):
        if not q.empty():
            msg = q.get()
            self.idling = msg[2]
            while True:
                print('idling...')
                if not q.empty():
                    msg = q.get()
                    self.idling = msg[2]
                    if self.idling == False:
                        break

if __name__ == "__main__":
    server = Server()
    server.start()
