from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty
import socket, threading, json

Builder.load_file('main.kv')
class MainLayout(BoxLayout):
    copper = 0

class Idleize(App):
    player_name = 'JpJab'
    idling = False
    def send(self,msg):
        if self.idling == False: self.idling = True
        else: self.idling = False
        msg = (msg, self.player_name, self.idling)
        msg = json.dumps(msg)
        client_socket.send(msg.encode('utf-8'))
    def process(self, msg):
        return msg
    def receiver(self):
        while True:
            data = client_socket.recv(1024).decode()
            print(f"Received From Server {data}")
    def connect(self):
        ## 172.238.207.140
        host, port = ('127.0.0.1', 1235)
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
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