from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty
import socket, threading

Builder.load_file('main.kv')
class MainLayout(BoxLayout):
    copper = 0

        
class Idleize(App):
    def send(self,msg):
        client_socket.send(msg.encode('utf-8'))
    def process(self, msg):
        return msg
    def handle_server(self):
        while True:
            data = client_socket.recv(1024).decode()
            print(f"Received From Server {data}")
            self.process(data)
    def connect(self):
        ## 172.238.207.140
        host, port = ('127.0.0.1', 1234)
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        socket_thread = threading.Thread(target=self.handle_server, daemon=True)
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