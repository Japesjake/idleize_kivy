import socket

def run_server():
    # 1. Create a socket and bind it to an address
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Allow immediate reuse of the port after disconnect
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind(('127.0.0.1', 1234))
    server_socket.listen(1)
    print("Server is listening for connections...")

    try:
        # OUTER LOOP: Keeps the server running indefinitely
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected by {addr}")

            try:
                # INNER LOOP: Keeps receiving data from the connected client
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        # Client disconnected (sent empty bytes)
                        print(f"Client {addr} disconnected.")
                        break
                    
                    print(f"Received: {data.decode()}")
                    client_socket.sendall(b"Message received!")
            
            except (ConnectionResetError, BrokenPipeError):
                print(f"Client {addr} forcibly closed the connection.")
            finally:
                # Clean up the client-specific socket
                client_socket.close()
                print("Waiting for next connection...")

    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_server()
