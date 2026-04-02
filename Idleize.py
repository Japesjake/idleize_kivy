from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty
import socket, threading, json, queue

Builder.load_file('main.kv')
class MainLayout(BoxLayout):
    copper = 0

q = queue.Queue()

class Idleize(App):
    player_name = 'JpJab'
    idling = False
    def send(self,msg):
        if self.idling == False: self.idling = True
        else: self.idling = False
        msg = (msg, self.player_name, self.idling)
        msg = json.dumps(msg)
        self.client_socket.sendall(msg.encode('utf-8'))
        print('sent message to server: ', msg)
    def process(self, msg):
        if msg == 'True': msg = True
        elif msg == 'False': msg = False
        self.idling = msg
        print(type(self.idling))
        print(self.idling)
    def receiver(self):
        while True:
            msg = self.client_socket.recv(1024).decode()
            print(f"Received From Server {msg}")
            # q.put(msg)
            self.process(msg)
    def connect(self):
        ## 172.238.207.140
        host, port = ('127.0.0.1', 1234)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        # client_socket.listen()
        socket_thread = threading.Thread(target=self.receiver, daemon=True)
        socket_thread.start()
    def build(self):
        self.main = MainLayout()
        return self.main
app = Idleize()
app.connect()
try:
    app.run()
except Exception as e:
    print(e)
    client_socket.close()