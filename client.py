import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('172.238.207.140', 1234))

print(client.recv(1024).decode())
client.send('Hello Server'.encode('utf-8'))