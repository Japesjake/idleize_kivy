import socket, json, threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout

host = 'localhost'
port = 1235

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

def handle_connection(app_instance):
    while True:
        data = recv_json()
        print(data)
    sock.close()



# msg = {'type': 'login', 'username': 'JpJab', 'password': 'class'}
# send_json(msg)

class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root_anchor = AnchorLayout(anchor_x='center', anchor_y='center')

        # 2. Inner BoxLayout holds the widgets with a fixed height so it won't stretch vertically
        card = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint=(0.5, None),  # 50% screen width
            height=220,  # Fixed total height prevents vertical stretching
        )

        title_label = Label(
            text='Welcome to Idleize \n Please login below',
            halign='center',
            size_hint_y=None,
            height=60,
        )

        self.username_input = TextInput(
            hint_text='username',
            multiline=False,
            size_hint_y=None,
            height=40,
        )

        self.password_input = TextInput(
            hint_text='password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40,
        )
        button_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40
        )
        submit_button = Button(text='Submit',
                               height=40,
                               on_release=self.submit)
        create_button = Button(text='Create New User',
                                height=40,
                                on_release=self.create_new)
        button_box.add_widget(create_button)
        button_box.add_widget(submit_button)

        card.add_widget(title_label)
        card.add_widget(self.username_input)
        card.add_widget(self.password_input)
        card.add_widget(button_box)

        root_anchor.add_widget(card)
        self.add_widget(root_anchor)
    def submit(self, instance):
        send_json({'type': 'login', 'username': self.username_input.text, 'password': self.password_input.text})
    def create_new(self, instance):
        send_json({'type': 'new','username': self.username_input.text, 'password': self.password_input.text})
class Main(Screen):
    pass

class Idleize(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(Main(name='main'))
        return sm
    def on_start(self):
        listening_thread = threading.Thread(target=handle_connection,args=(app,), daemon=True)
        listening_thread.start()


app = Idleize()
app.run()