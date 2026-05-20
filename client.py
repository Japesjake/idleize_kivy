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
from kivy.factory import Factory

HOST = 'localhost'
PORT = 1235

def create_data():
    with open('data.p', 'wb') as file:
        pickle.dump({'copper ore': 0,'iron ore': 0,'copper ingot': 0, 'iron ingot': 0, 'copper armor': 0, 'iron armor': 0, 'wood': 0, 'stick':0, 'copper arrow': 0}, file)

def create_xps():
    with open('xps.p', 'wb') as file:
        pickle.dump({'mining': 0, 'smelting': 0, 'crafting': 0, 'gathering': 0}, file)

files = Path('data.p')
if not files.is_file():
    create_data()

files = Path('xps.p')
if not files.is_file():
    create_xps()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Utility network functions to avoid packet smashing / JSONDecodeError
def send_json(sock, data):
    payload = json.dumps(data) + '\n'
    sock.sendall(payload.encode('utf-8'))

def recv_json(sock):
    data = b""
    while True:
        chunk = sock.recv(1)
        if not chunk:
            # Connection dropped or closed mid-transmission
            return None 
        if chunk == b'\n':
            break
        data += chunk
        
    # Guard against parsing empty streams
    if not data:
        return None
        
    try:
        return json.loads(data.decode('utf-8'))
    except json.JSONDecodeError:
        return None

Builder.load_file('main.kv')

class LoginScreen(Screen):
    def verify(self):
        username = self.ids.username.text
        password = self.ids.password.text
        
        # FIX: Run network operations inside an async background thread to prevent app hanging
        threading.Thread(
            target=App.get_running_app().verify_credentials, 
            args=(username, password), 
            daemon=True
        ).start()

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
    with open('xps.p', 'rb') as file:
        xps = DictProperty(pickle.load(file))
        
    groups = {'mining': ('copper ore', 'iron ore'),'smelting': ('copper ingot', 'iron ingot'),'crafting': ('copper armor', 'iron armor', 'copper arrow'), 'gathering':('wood', 'stick')}
    recipies = {'copper ingot': {'copper ore': 1}, 'iron ingot': {'iron ore': 1}, 'copper armor': {'copper ingot': 1}, 'iron armor': {'iron ingot': 1}, 'stick': {'wood': 1}, 'copper arrow': {'copper ingot': 1, 'stick': 1}}
    xp_values = {'copper ore': 1, 'iron ore': 2, 'copper ingot': 1, 'iron ingot': 2, 'copper armor': 1, 'iron armor': 2, 'wood':1, 'stick':1, 'copper arrow': 1}
    difficulties = {'copper ore': 1, 'iron ore': 500, 'copper ingot': 1, 'iron ingot': 500, 'copper armor': 1, 'iron armor': 500, 'wood': 1, 'stick': 1, 'copper arrow': 1}
    player_name = 'JpJab'
    item = 'copper ore'
    idling = False

    def build(self):
        self.main = WindowManager()
        client.connect((HOST, PORT))
        return self.main

    def idle_thread(self):
        while True:
            item = self.item
            while self.idling:
                for key, value in self.groups.items():
                    if item in value:
                        xp_group = key
                        break                    
                duration = self.get_duration(xp_group, item)
                child_items = self.recipies.get(item)
                has_mats = True
                if child_items:
                    for child_item, amount in child_items.items():
                        if self.data.get(child_item) - amount < 0:
                            has_mats = False
                if has_mats:
                    Clock.schedule_once(lambda dt: self.root.get_screen('main').animate(duration))
                    start_time = time.time()
                    while time.time() - start_time < duration:
                        if not self.idling or self.item != item:
                            break
                        time.sleep(0.1)
                        
                    if self.idling and item == self.item:
                        def update(dt):
                            new_data = dict(self.data)
                            can_still_afford = True
                            if child_items:
                                for child_item, amount in child_items.items():
                                    if new_data.get(child_item, 0) < amount:
                                        can_still_afford = False
                                        break
                            if not can_still_afford:
                                return
                            new_data[item] += 1
                            if child_items:
                                for child_item, amount in child_items.items():
                                    new_data[child_item] -= amount
                            new_xp = dict(self.xps)
                            new_xp[xp_group] += self.xp_values.get(item, 0)
                            self.xps = new_xp
                            self.data = new_data
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
        send_json(client, item)
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
        threading.Thread(target=self._perform_sync, daemon=True).start()

    def _perform_sync(self):
        send_json(client, ['sync'])
        response = recv_json(client)
        if response:
            def apply_sync(dt):
                new_data = dict(self.data)
                for item_name, count in response.get('inventory', []):
                    new_data[item_name] = count
                self.data = new_data

                new_xps = dict(self.xps)
                for category_name, xp_value in response.get('experience', []):
                    new_xps[category_name] = xp_value
                self.xps = new_xps
            Clock.schedule_once(apply_sync)

    def verify_credentials(self, username, password):
        print('credentials sent')
        send_json(client, (username, password))
        response = recv_json(client)
        print(f'response after credentials sent: {response}')
        
        if response == ['new']:
            print('creating new data and opening popup')
            create_data()
            create_xps()
            # Safely trigger popup rendering on main loop, then drop out of this thread context
            Clock.schedule_once(lambda dt: Factory.CreateProfilePopup().open())
            return
        
        if response == ['good']:
            send_json(client, ['aknowledged'])
            self.continue_login_flow()

    def confirm_new_profile_creation(self):
        """Dispatched asynchronously when user taps 'Yes' inside the popup modal"""
        threading.Thread(target=self._async_profile_confirm, daemon=True).start()

    def _async_profile_confirm(self):
        send_json(client, ['aknowledged'])
        self.continue_login_flow()
        
    def cancel_new_profile_creation(self):
        """Dispatched asynchronously when user taps 'No' inside the popup modal"""
        threading.Thread(target=self._async_profile_cancel, daemon=True).start()

    def _async_profile_cancel(self):
        # Send a cancellation notice instead of an acknowledgment
        send_json(client, ['canceled'])
    def continue_login_flow(self):
        ### Receives Data concerning idling process on server ###
        response = recv_json(client)
        print(f'Received from Server after status checked: {response}')
        
        if response is None:
            print("Server disconnected unexpectedly.")
            return # Safely exit thread context
            
        if response == 'false':
            self.idling = False
        else:
            def set_idle_state(dt):
                new = dict(self.data).copy()
                self.item = response[0]
                self.count = response[1]
                new[self.item] = self.count
                self.data = new
                self.idling = True
            Clock.schedule_once(set_idle_state)
            
        self.start_idle_thread()

        ### saves sync data. Creates a new data.p file if no data on server ###
        response = recv_json(client)
        print(f'Save data received from Server: {response}')
        
        if response is None:
            print("Server disconnected during sync pipeline.")
            return

        if response:
            def final_sync(dt):
                new_data = dict(self.data)
                for item_name, count in response.get('inventory', []):
                    new_data[item_name] = count
                self.data = new_data

                new_xps = dict(self.xps)
                for category_name, xp_value in response.get('experience', []):
                    new_xps[category_name] = xp_value
                self.xps = new_xps
            Clock.schedule_once(final_sync)
            
        Clock.schedule_once(lambda dt: self.switch_to_main_screen())

    def switch_to_main_screen(self):
        self.main.current = 'main'

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
    Idleize().run()