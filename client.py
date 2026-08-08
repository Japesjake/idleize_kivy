import socket, json, threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock

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
        Clock.schedule_once(lambda dt: app_instance.on_server_message(data))
    sock.close()
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

class Tab(Screen):
    def __init__(self,tab_type,tabs, **kw):
        super().__init__(**kw)
        self.tab_type = tab_type
        self.add_widget(Label(text=self.name))
        for category, items in tabs.items():
            if category == tab_type:
                for item in items:
                    self.add_widget(Button(text=item))


class Main(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        main_layout = BoxLayout(orientation='horizontal')
        sidebar = BoxLayout(
            orientation='vertical',
            size_hint_x=0.25,
            spacing=10
        )
        tabs = {'Character':('dummy',), 'Combat':('dummy',), 'Mining':('Copper Ore',), 'Smelting':('dummy',), 'Crafting':('dummy',), 'Gathering':('dummy',), 'Cooking':('dummy',)}
        buttons = [Button(text=tab) for tab in tabs.keys()]
        for button in buttons:
            button.bind(on_press=lambda instance, t=button.text: self.switch_tab(t))
            sidebar.add_widget(button)

        self.tab_manager = ScreenManager(transition=FadeTransition(duration=0.15))
        for tab in tabs:
            self.tab_manager.add_widget(Tab(tab_type=tab,tabs=tabs, name=tab)) 

        main_layout.add_widget(sidebar)
        main_layout.add_widget(self.tab_manager)
        self.add_widget(main_layout)
    def switch_tab(self, tab_name):
        self.tab_manager.current = tab_name

          
class Idleize(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(Main(name='main'))
        return self.sm
    def on_start(self):
        listening_thread = threading.Thread(target=handle_connection,args=(app,), daemon=True)
        listening_thread.start()
        ### remove line under here to reactivate login credential query ###
        send_json({'type': 'login', 'username': '', 'password': ''})
    def on_server_message(self, data):
        data_type = data.get('type')
        if data_type == 'login' and data.get('message') == 'good':
            self.sm.current = 'main'
        print(data)

app = Idleize()
app.run()