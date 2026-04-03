from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty
import socket, threading, json, queue

# host, port = ('172.238.207.140', 1234)
host, port = ('127.0.0.1', 1234)
data = []
Builder.load_file('main.kv')
class MainLayout(BoxLayout):
    # copper_ore = NumericProperty(0)
    pass

##### msg = ["copper ore", "JpJab", true, count]
#message sent to client:  [[["JpJab", "iron ore", 0], ["JpJab", "copper ore", 72060]], "initial"]
q = queue.Queue()
def get_count(item_name, msg):
    for row in data:
        if row[1] == item_name:
            return row[2]
            

class Idleize(App):
    player_name = 'JpJab'
    idling = False
    initial = True
    copper_ore = NumericProperty(0)
    def send(self,msg):
        if self.idling == False: self.idling = True
        else: self.idling = False
        msg = (msg, self.player_name, self.idling)
        msg = json.dumps(msg)
        self.client_socket.sendall(msg.encode('utf-8'))
        print('sent message to server: ', msg)
    def process(self):
        msg = q.get()
        if msg[1] == 'initial':
            data = msg[0]
            # get_count()
        else:
            if msg[2] == 'True': self.idling = True
            elif msg[2] == 'False': self.idling = False
        # self.copper_ore = msg[3][0][0]
        # self.initial = False


    def receiver(self):
        while True:
            msg = json.loads(self.client_socket.recv(1024).decode())
            print(f"Received From Server {msg}")
            q.put(msg)
            self.process()
    def connect(self):
        ## 172.238.207.140
        # host, port = ('172.238.207.140', 1234)
        # host, port = ('127.0.0.1', 1234)
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