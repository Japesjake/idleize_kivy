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
    player_id = 0
    path = Path("copper.p")
    if path.is_file():
        with open('copper.p', 'rb') as f:
            copper = NumericProperty(pickle.load(f))
    else: copper = NumericProperty(0)
    rate = 1
    running = False
    def idle(self):
        if not self.running:
            self.running_clock = Clock.schedule_interval(self.increment,self.rate)
            self.running = True
        else: 
            self.running_clock.cancel()
            self.running = False
    def increment(self, inc):
        self.copper += 1
        print(self.copper)
    def on_stop(self):
        self.running_clock.cancel()
        with open('copper.p', 'wb') as f: 
            pickle.dump(self.copper, f)

class Idleize(App):
    def communicate(self, client_socket):
        while True:
            pass
    def connect(self):
        HOST = '127.0.0.1'
        PORT = 1234
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        # socket_thread = threading.Thread(target=communicate, args=(client_socket,), daemon=True)
        # socket_thread.start()
    def build(self):
        self.main = MainLayout()
        return self.main
    def on_stop(self):
        with open('copper.p', 'wb') as f:
            pickle.dump(self.main.copper, f)
app = Idleize()
app.connect()
# app.run()