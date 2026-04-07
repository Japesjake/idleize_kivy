import socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 1234))
    
    while True:
        msg = input("Message (type 'quit' to exit): ")
        if msg.lower() == 'quit':
            break
        client.send(msg.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        print(f"Server says: {response}")

    client.close()

if __name__ == "__main__":
    start_client()