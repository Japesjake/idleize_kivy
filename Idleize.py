from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty
import socket, threading, json, queue

data = {'copper ore':1}

Builder.load_file('main.kv')
class MainLayout(BoxLayout):
    data = data
    print(data)

##### msg = ["copper ore", "JpJab", true, count]

q = queue.Queue()

class Idleize(App):
    player_name = 'JpJab'
    idling = False
    initial = True
    def send(self,msg):
        if self.idling == False: self.idling = True
        else: self.idling = False
        msg = (msg, self.player_name, self.idling)
        msg = json.dumps(msg)
        self.client_socket.sendall(msg.encode('utf-8'))
        print('sent message to server: ', msg, 'of type: ', type(msg))
    def process(self):
        msg = q.get()
        if not self.initial:
            if msg[2] == 'True': self.idling = True
            elif msg[2] == 'False': self.idling = False
        self.initial = False
        print('!!!!!', msg)
        data[msg[0]] = msg[3][0][0]
        print(type(data[msg[0]]))

    def receiver(self):
        while True:
            msg = json.loads(self.client_socket.recv(1024).decode())
            print(f"Received From Server {msg}")
            q.put(msg)
            self.process()
    def connect(self):
        ## 172.238.207.140
        host, port = ('172.238.207.140', 1234)
        # host, port = ('127.0.0.1', 1235)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
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