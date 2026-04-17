from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import DictProperty
from kivy.uix.screenmanager import ScreenManager, Screen
import socket, pickle, json, time, threading
from pathlib import Path
HOST = 'localhost'
PORT = 1235

files = Path('relationships.p')
if not files.is_file():
    with open('relationships.p', 'wb') as file:
        pickle.dump({'copper ore': None,'iron ore': None,'copper ingot': 'copper ore', 'iron ingot': 'iron ore'}, file)

files = Path('data.p')
if not files.is_file():
    with open('data.p', 'wb') as file:
        pickle.dump({'copper ore': 0,'iron ore': 0,'copper ingot': 0, 'iron ingot': 0}, file)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

Builder.load_file('main.kv')
class LoginScreen(Screen):
    def verify_credentials(self):
        print('credentials sent')
        global username
        global password
        username = self.ids.username.text
        password = self.ids.password.text
        client.sendall(json.dumps((username, password)).encode('utf-8'))
        response = json.loads(client.recv(1024).decode('utf-8'))
        print(f'response: {response}')
        client.sendall(json.dumps(['aknowledged']).encode('utf-8'))
        # if 'good' in response:
        #     print('good')
        # response = response.strip('good')
        response = json.loads(client.recv(1024).decode('utf-8'))
        print(f'response from server {type(response)} as {response}')
        for row in response:
            new = dict(App.get_running_app().data).copy()
            new[row[0]] = row[1]
            App.get_running_app().data = new
        self.manager.current = 'main'

class MainLayout(Screen):
    pass
class WindowManager(ScreenManager):
    pass



class Idleize(App):
    with open('data.p', 'rb') as file:
        data = DictProperty(pickle.load(file))
    with open('relationships.p', 'rb') as file:
        relationships = DictProperty(pickle.load(file))
    player_name = 'JpJab'
    item = 'item'
    idling = False
    def build(self):
        self.main = WindowManager()
        client.connect((HOST, PORT))
        # client.sendall(self.player_name.encode('utf-8'))
        # print(f'Sent to server: {self.player_name}')
        response = json.loads(client.recv(1024).decode('utf-8'))
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
            self.idling = False
        self.start_idle_thread()
        return self.main
    def idle_thread(self):
        while True:
            while self.idling:
                time.sleep(1)
                print(self.item)
                child_item = self.relationships[self.item]
                if not child_item or self.data[child_item] > 0:
                    print('idling...')
                    new = dict(self.data).copy()
                    new[self.item] += 1
                    self.data = new
                if child_item and self.data[child_item] > 0:
                    print(f'subtracting 1 from {child_item}')
                    print(f'child item count: {self.data[child_item]}')
                    new = dict(self.data).copy()
                    new[child_item] -= 1
                    self.data = new
    def start_idle_thread(self):
        thread = threading.Thread(target=self.idle_thread, daemon=True)
        print(f'thread started.')
        thread.start()
        return thread
    def send(self, item):
        client.sendall(json.dumps((item)).encode('utf-8'))
        if self.idling: self.idling = False
        else: self.idling = True
        print(f'self.idling = {self.idling}')
        self.item = item
        if self.item not in self.data.keys():
            new = dict(self.data).copy()
            new[self.item] = 0
            self.data = new
    def sync(self):
        client.sendall(json.dumps(['sync']).encode('utf-8'))
        response = json.loads(client.recv(1024).decode('utf-8'))
        print(f'Data received from server {response}')
        if response:
            for row in response:
                new = dict(self.data).copy()
                new[row[0]] = row[1]
                self.data = new
    def on_stop(self):
        with open('data.p', "wb") as file:
            pickle.dump(dict(self.data), file)


if __name__ == "__main__":
    idle = Idleize()
    idle.run()