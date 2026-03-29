from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import NoTransition
from kivy.properties import NumericProperty
from kivy.clock import Clock
import subprocess, sys, pickle, socket, threading
from pathlib import Path

Builder.load_file('main.kv')
class MainLayout(BoxLayout):
    item_count = 0
    def send(self,message):
        client_socket.send(message.encode('utf-8'))
        # Clock.
        # data = client_socket.recv(1024).decode()
        # print('Received from server: ' + data)
class Idleize(App):
    def handle_server(self):
        while True:
            data = client_socket.recv(1024).decode()
            print(f"Received From Server {data}")
    def connect(self):
        HOST, PORT = ('127.0.0.1', 1234)
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
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