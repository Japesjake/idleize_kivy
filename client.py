import socket, json, threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

host = 'localhost'
port = 1235

global sock
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

def send_json(data):
    payload = json.dumps(data) + '\n'
    sock.sendall(payload.encode('utf-8'))

def recv_json():
    data = b""
    while True:
        chunk = sock.recv(1)
        if not chunk:
            return None
        if chunk == b'\n':
            break
        data += chunk
    try:
        return(json.loads(data.decode('utf-8')))
    except json.JSONDecodeError:
        return None

def handle_connection():
    while True:
        data = recv_json()
        print(data)
    sock.close()

listening_thread = threading.Thread(target=handle_connection, daemon=True)
listening_thread.start()



# msg = {'type': 'login', 'username': 'JpJab', 'password': 'class'}
# send_json(msg)

class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Welcome to Idleize \n Please login below'))
        username_input = TextInput(hint_text='username',
                                   size_hint=(0.5,None),
                                   height=40,
                                   pos_hint={'center_x': 0.5})
        password_input = TextInput(hint_text='password',
                                   size_hint=(0.5,None),
                                   height=40,
                                   pos_hint={'center_x': 0.5})
        layout.add_widget(username_input)
        layout.add_widget(password_input) 
        self.add_widget(layout)

class Idleize(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        # sm.add_widget(Main(name='main'))
        return sm

Idleize().run()