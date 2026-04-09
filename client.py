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
    item = 'item'
    idling = False
    def build(self):
        self.main = MainLayout()
        self.client.connect(('localhost', 1235))
        self.client.sendall(self.player_name.encode('utf-8'))
        print(f'Sent to server: {self.player_name}')
        response = json.loads(self.client.recv(1024).decode('utf-8'))
        print(f'Received from Server: {response} as type: {type(response)}')
        if response != 'false':
            new = dict(self.data).copy()
            self.item = response[0]
            self.count = response[1]
            new[self.item] = self.count
            self.data = new
            print(f'data on local client after receiving data: {self.data}')
            self.idling = True
        else: 
            print('self.idling == False')
            self.idling = False
        self.start_idle_thread()
        return self.main
    def idle_thread(self):
        while True:
            if self.item != 'item':
                print('idling...')
                new = dict(self.data).copy()
                new[self.item] += 1
                self.data = new
                time.sleep(1)
    def start_idle_thread(self):
        thread = threading.Thread(target=self.idle_thread)
        print(f'thread started.')
        thread.start()
        return thread
    def send(self, item):
        self.client.sendall(item.encode('utf-8'))
        if self.idling: self.idling = False
        else: self.idling = True
        print(f'self.idling = {self.idling}')

    def on_stop(self):
        with open('data.p', "wb") as file:
            pickle.dump(dict(self.data), file)


if __name__ == "__main__":
    idle = Idleize()
    idle.run()