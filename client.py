from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import DictProperty
import socket, threading, json, queue

Builder.load_file('main.kv')
data = DictProperty()

class MainLayout(BoxLayout):
    data = data

class Idleize(App):
    player_name = 'JpJab'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 1235))
    client.sendall(player_name.encode('utf-8'))
    def build(self):
        self.main = MainLayout()
        return self.main
    def send(self, msg):
        self.client.sendall(msg.encode('utf-8'))

if __name__ == "__main__":
    idle = Idleize()
    idle.run()