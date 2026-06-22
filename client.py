from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import DictProperty
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
import socket, pickle, json, time, threading, random
from pathlib import Path
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.factory import Factory
from data import data, xps, groups, recipies, xp_values, difficulties, enemies, hps, player_stats, equipment_stats, equipped, equippables

HOST = 'localhost'
PORT = 1235

Builder.load_file('main.kv')

def create_data():
    with open('data.p', 'wb') as file:
        pickle.dump(data, file)

def create_xps():
    with open('xps.p', 'wb') as file:
        pickle.dump(xps, file)

def create_hps():
    with open('hps.p', 'wb') as file:
        pickle.dump(hps, file)

def create_equipped():
    with open('equipped.p', 'wb') as file:
        pickle.dump(equipped, file)

files = Path('data.p')
if not files.is_file():
    create_data()

files = Path('xps.p')
if not files.is_file():
    create_xps()

files = Path('hps.p')
if not files.is_file():
    create_hps()

files = Path('equipped.p')
if not files.is_file():
    create_equipped()

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
    def on_enter(self):
        App.get_running_app().populate_inventory()
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
    with open('hps.p', 'rb') as file:
        hps = DictProperty(pickle.load(file))
    with open('equipped.p', 'rb') as file:
        equipped = DictProperty(pickle.load(file))
    print(equipped)
    player_name = 'JpJab'
    item = 'copper ore'
    idling = False

    groups = groups
    recipies = recipies
    xp_values = xp_values
    difficulties = difficulties
    enemies = enemies
    player_stats = player_stats
    equipment_stats = equipment_stats
    equippables = equippables
    def equip(self, name):
        new_equipped = dict(self.equipped)
        if 'armor' in name:
            new_equipped['body'] = name
        if 'sword' in name or 'bow' in name:
            new_equipped['right'] = name
        def apply_update(dt):
            self.equipped = new_equipped
        Clock.schedule_once(apply_update)
    def populate_inventory(self):
        container = self.root.get_screen('main').ids.list_container
        for name, amount in self.data.items():
            if name in equippables.keys() and amount > 0:
                btn = Button(
                    text=name,
                    size_hint_y=None,
                    height=40,
                )
                btn.bind(on_press=lambda instance, current_name=name: self.equip(current_name))
                container.add_widget(btn) 
    def build(self):
        self.main = WindowManager()
        client.connect((HOST, PORT))
        return self.main
    def idle_thread(self):
        while True:
            item = self.item
            while self.idling:
                if 'fight' in item:
                    Clock.schedule_once(lambda dt: self.root.get_screen('main').animate(1))
                    time.sleep(1)
                    print('fighting')
                    print(1)
                    enemy = item.removeprefix('fight ')
                    enemy_max_hp = self.enemies.get(enemy).get('hp')
                    enemy_actual_hp = self.hps.get(enemy)
                    enemy_attack = self.enemies.get(enemy).get('attack')
                    enemy_defense = self.enemies.get(enemy).get('defense')
                    player_max_hp = self.player_stats.get('hp')
                    player_actual_hp = self.hps.get('player')
                    player_body = self.equipped.get('body')
                    player_right = self.equipped.get('right')
                    player_armor_type = self.equippables.get(player_body)
                    player_weapon_type = self.equippables.get(player_right)
                    if player_armor_type == 'strength':
                        player_defense = self.equipment_stats.get(player_body)
                    if player_armor_type == 'dexterity':
                        player_defense = self.player_stats.get('dexterity')
                    if player_weapon_type == 'strength':
                        player_attack = self.player_stats.get('strength')
                    if player_weapon_type == 'dexterity':
                        player_attack = self.player_stats.get('dexterity')
                    enemy_hits = (enemy_attack + random.randint(-5, 5)) - (player_defense + random.randint(-5, 5)) > 0
                    player_hits = (player_attack + random.randint(-5, 5)) - (enemy_defense + random.randint(-5,5)) > 0
                    new_hps = dict(self.hps)
                    print('armor' + player_armor_type)
                    print('weapon' + player_weapon_type)
                    if enemy_hits:
                        new_hps['player'] -= enemy_attack
                    if player_hits:
                        new_hps[enemy] -= player_attack

                    if self.hps['player'] <= 0 or self.hps[enemy] <= 0:
                        self.idling = False
                        new_hps['player'] = player_max_hp
                        new_hps[enemy] = enemy_max_hp
                    def apply_hp_update(dt):
                        self.hps = new_hps
                    Clock.schedule_once(apply_hp_update)
                    print(self.hps)
                else:
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
            print('opening popup')
            # create_data()
            # create_xps()
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

        if response and (response.get('inventory') or response.get('experience')):
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
        else:
            # If the server returned blank arrays, initialize the fresh default state locally
            print("No online state found. Generating fresh local database fallback profile profiles...")
            def init_default_profile(dt):
                self.data = {'copper ore': 0,'iron ore': 0,'copper ingot': 0, 'iron ingot': 0, 'copper armor': 0, 'iron armor': 0, 'wood': 0, 'stick': 0, 'copper arrow': 0}
                self.xps = {'mining': 0, 'smelting': 0, 'crafting': 0, 'gathering': 0}
            Clock.schedule_once(init_default_profile)
            
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