import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 1234))

print(client.recv(1024).decode())
client.send('Hello Server'.encode('utf-8'))