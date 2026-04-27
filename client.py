from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import DictProperty
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
import socket, pickle, json, time, threading
from pathlib import Path
from kivy.animation import Animation
from kivy.clock import Clock
HOST = 'localhost'
PORT = 1235

files = Path('amounts.p')
if not files.is_file():
    with open('amounts.p', 'wb') as file:
        pickle.dump({'copper ingot':1,'iron ingot':1,'copper armor':5,'iron armor':5}, file)

files = Path('relationships.p')
if not files.is_file():
    with open('relationships.p', 'wb') as file:
        pickle.dump({'copper ore': None,'iron ore': None,'copper ingot': 'copper ore', 'iron ingot': 'iron ore', 'copper armor': 'copper ingot', 'iron armor': 'iron ingot'}, file)

files = Path('data.p')
if not files.is_file():
    with open('data.p', 'wb') as file:
        pickle.dump({'copper ore': 0,'iron ore': 0,'copper ingot': 0, 'iron ingot': 0, 'copper armor': 0, 'iron armor': 0}, file)

files = Path('xps.p')
if not files.is_file():
    with open('xps.p', 'wb') as file:
        pickle.dump({'mining': 0, 'smelting': 0, 'crafting': 0}, file)

files = Path('groups.p')
if not files.is_file():
    with open('groups.p','wb') as file:
        pickle.dump({'mining': ('copper ore', 'iron ore'),'smelting': ('copper ingot', 'iron ingot'),'crafting': ('copper armor', 'iron armor')}, file)

files = Path('xp_values.p')
if not files.is_file():
    with open('xp_values.p','wb') as file:
        pickle.dump({'copper ore': 1, 'iron ore': 2, 'copper ingot': 1, 'iron ingot': 2, 'copper armor': 1, 'iron armor': 2}, file)

files = Path('difficulties.p')
if not files.is_file():
    with open ('difficulties.p','wb') as file:
        pickle.dump({'copper ore': 1, 'iron ore': 500, 'copper ingot': 1, 'iron ingot': 500, 'copper armor': 1, 'iron Armor': 500}, file)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

Builder.load_file('main.kv')
class LoginScreen(Screen):
    def verify(self):
        # username = self.ids.username.text
        # password = self.ids.password.text
        username = 'JpJab'
        password = 'password'
        App.get_running_app().verify_credentials(username, password)
        self.manager.current = 'main'
class ThickProgressBar(ProgressBar):
    pass
class MainLayout(Screen):
    def animate(self, duration):
        self.ids.pb.value = 0
        anim = Animation(value=100, duration=duration)
        anim.start(self.ids.pb)
class WindowManager(ScreenManager):
    pass



class Idleize(App):
    with open('data.p', 'rb') as file:
        data = DictProperty(pickle.load(file))
    with open('relationships.p', 'rb') as file:
        relationships = pickle.load(file)
    with open('amounts.p', 'rb') as file:
        amounts = pickle.load(file)
    with open('xps.p', 'rb') as file:
        xps = DictProperty(pickle.load(file))
    with open('groups.p', 'rb') as file:
        groups = pickle.load(file)
    with open('xp_values.p', 'rb') as file:
        xp_values = pickle.load(file)
    with open('difficulties.p', 'rb') as file:
        difficulties = pickle.load(file)
    player_name = 'JpJab'
    item = 'copper ore'
    idling = False
    def build(self):
        self.main = WindowManager()
        client.connect((HOST, PORT))
        return self.main
    def idle_thread(self):
        while True:
            while self.idling:
                item = self.item
                for key, value in self.groups.items():
                    if item in value:
                        xp_group = key
                        break                    
                duration = self.get_duration(xp_group, item)
                child_item = self.relationships.get(item)
                required = self.amounts.get(item, 0)
                has_mats = not child_item or (self.data.get(child_item, 0) >= required)
                if has_mats:
                    Clock.schedule_once(lambda dt: self.root.get_screen('main').animate(duration))
                    time.sleep(duration)
                    if self.idling and item == self.item:
                        def update(dt):
                            new_data = dict(self.data)
                            new_data[item] += 1
                            if child_item:
                                new_data[child_item] -= required
                            self.data = new_data
                            
                            new_xp = dict(self.xps)
                            new_xp[xp_group] += self.xp_values.get(item, 0)
                            self.xps = new_xp
                            print(f'{item}: {self.data.get(item)}')
                            print(f'XP added to {xp_group} total amount {self.xps.get(xp_group)}')
                        Clock.schedule_once(update)
                else:
                    print('Missing materials!')
                    self.idling = False
    def start_idle_thread(self):
        thread = threading.Thread(target=self.idle_thread, daemon=True)
        print(f'thread started.')
        thread.start()
        return thread
    def send(self, item):
        client.sendall(json.dumps((item)).encode('utf-8'))
        if self.item != item:
            self.idling = False
            self.item = item
            self.idling = True
            main_screen = self.root.get_screen('main')
            Animation.stop_all(main_screen.ids.pb)
            main_screen.ids.pb.value = 0
        else:
            self.idling = not self.idling
    def sync(self):
        client.sendall(json.dumps(['sync']).encode('utf-8'))
        response = json.loads(client.recv(1024).decode('utf-8'))
        print(f'Data received from server {response}')
        if response:
            for row in response:
                new = dict(self.data).copy()
                new[row[0]] = row[1]
                self.data = new
    def verify_credentials(self, username, password):
        print('credentials sent')
        client.sendall(json.dumps((username, password)).encode('utf-8'))
        response = json.loads(client.recv(1024).decode('utf-8'))
        print(f'response after credentials sent: {response}')
        client.sendall(json.dumps(['aknowledged']).encode('utf-8'))
        
        
        ### Receives Data concerning idling process on server ###
        response = json.loads(client.recv(1024).decode('utf-8'))
        print(f'Received from Server after aknowledged sent: {response} as type: {type(response)}')
        if response == 'false':
            self.idling = False
        else:
            new = dict(self.data).copy()
            self.item = response[0]
            self.count = response[1]
            new[self.item] = self.count
            self.data = new
            print(f'data on local client after receiving data: {self.data}')
            self.idling = True
        self.start_idle_thread()

        #### saves sync data. Creates a new data.p file if no data on server ###
        response = json.loads(client.recv(1024).decode('utf-8'))
        print(f'Save data received from Server: {response}')
        if response:
            for row in response:
                new = dict(self.data).copy()
                new[row[0]] = row[1]
                self.data = new
                print(f'dictionary saved: {App.get_running_app().data}')
        else:
            with open('data.p', 'wb') as file:
                pickle.dump({'copper ore': 0,'iron ore': 0,'copper ingot': 0, 'iron ingot': 0, 'copper armor': 0, 'iron armor': 0}, file)
            with open('xps.p', 'wb') as file:
                pickle.dump({'mining': 0, 'smelting': 0, 'crafting': 0}, file)

    def get_duration(self, group, item):
        duration = self.difficulties[item] / (self.xps[group] + 1)
        if duration <= 1:
            duration = 1
        return duration
    def on_stop(self):
        with open('data.p', "wb") as file:
            pickle.dump(dict(self.data), file)
        with open('xps.p', "wb") as file:
            pickle.dump(dict(self.xps), file)


if __name__ == "__main__":
    idle = Idleize()
    idle.run()