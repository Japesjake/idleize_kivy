from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import DictProperty
import socket, pickle, json, time, threading

Builder.load_file('main.kv')
class MainLayout(BoxLayout):
    pass

# with open('data.p', 'wb') as file:
#     pickle.dump({'copper ore': 4}, file)


class Idleize(App):
    with open('data.p', 'rb') as file:
        data = DictProperty(pickle.load(file))
    player_name = 'JpJab'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    idling = False
    item = 'item'
    thread = 'thread'
    def build(self):
        self.main = MainLayout()

        self.client.connect(('localhost', 1234))
        self.client.sendall(self.player_name.encode('utf-8'))
        print(f'Sent to server: {self.player_name}')
        response = json.loads(self.client.recv(1024).decode('utf-8'))
        print(f'Received from Server: {response}')
        if response != 'false':
            self.idling = True
            new = dict(self.data).copy()
            self.item = response[0]
            self.count = response[1]
            new[self.item] = self.count
            self.data = new
            self.start_idle_thread()
        else: 
            self.idling = False
        return self.main
    def idle_thread(self):
        while self.idling:
            print('idling...')
            time.sleep(1)
            new = dict(self.data).copy()
            new[self.item] += 1
            self.data = new
    def start_idle_thread(self):
        self.thread = threading.Thread(target=self.idle_thread)
        self.thread.start()
    def send(self, item):
        self.client.sendall(item.encode('utf-8'))
    def on_stop(self):
        with open('data.p', "wb") as file:
            pickle.dump(dict(self.data), file)

if __name__ == "__main__":
    idle = Idleize()
    idle.run()