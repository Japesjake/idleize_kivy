from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import DictProperty
import socket, pickle, json

Builder.load_file('main.kv')
class MainLayout(BoxLayout):
    pass

class Idleize(App):
    with open('data.p', 'rb') as file:
        data = DictProperty(pickle.load(file))
        player_name = 'JpJab'
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def build(self):
        self.main = MainLayout()

        self.client.connect(('localhost', 1236))
        self.client.sendall(self.player_name.encode('utf-8'))
        print(f'Sent to server: {self.player_name}')
        response = json.loads(self.client.recv(1024).decode('utf-8'))
        print(f'Received from Server: {response}')
        if response != 'false':
            new = dict(self.data).copy()
            new[response[0]] = response[1]
            print(type(response))
            print(response)
            self.data = new
            print(self.data)
        return self.main
    def send(self, msg):
        self.client.sendall(msg.encode('utf-8'))

if __name__ == "__main__":
    idle = Idleize()
    idle.run()