import socket, json, threading, time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout

host = 'localhost'
port = 1235

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

def send_json(data):
    app = App.get_running_app()
    if getattr(app, 'session_token',None):
        data = {**data, 'session': app.session_token}
    payload = json.dumps(data) + '\n'
    sock.sendall(payload.encode('utf-8'))
    print('sent: ')
    print(data)
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

class ResourceTab(Screen):
    def __init__(self,items,category_name,**kw):
        super().__init__(**kw)
        parent_layout = BoxLayout(orientation='vertical')
        parent_layout.add_widget(Label(text=category_name.title(),size_hint_y=0.2))
        resources_layout = GridLayout(cols=2)
        for item in items:
            btn = Button(text=item.title())
            btn.bind(on_release=lambda x, current_item=item: send_json({'type': 'toggle idling','item':current_item, 'session': App.get_running_app().session_token}))
            resources_layout.add_widget(btn)

        parent_layout.add_widget(resources_layout)
        self.add_widget(parent_layout)


class Main(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
    def create_ui(self):
        main_layout = BoxLayout(orientation='horizontal')
        sidebar = BoxLayout(
            orientation='vertical',
            size_hint_x=0.25,
            spacing=10
        )

        resource_categories = App.get_running_app().resource_categories
        buttons = [Button(text=category.title()) for category in resource_categories]
        for button in buttons:
            button.bind(on_press=lambda instance, t=button.text: self.switch_tab(t))
            sidebar.add_widget(button)

        self.tab_manager = ScreenManager(transition=FadeTransition(duration=0.15))
        for category_name in resource_categories:
            self.tab_manager.add_widget(ResourceTab(items=resource_categories.get(category_name), category_name=category_name, name=category_name)) 

        main_layout.add_widget(sidebar)
        main_layout.add_widget(self.tab_manager)
        self.add_widget(main_layout)
    def switch_tab(self, tab_name):
        self.tab_manager.current = tab_name.lower()

          
class Idleize(App):
    session_token = None
    resource_categories = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.main = Main(name='main')
        self.sm.add_widget(self.main)
        return self.sm
    def on_start(self):
        listening_thread = threading.Thread(target=handle_connection,args=(app,), daemon=True)
        listening_thread.start()
        with open("client_data.json", "r") as file:
            data = json.load(file)
            version = data.get('version')
        ### remove line under here to reactivate login credential query ###
        send_json({'type':'version check','version': version})
        time.sleep(0.1)
        send_json({'type': 'login', 'username': '', 'password': ''})
    def on_server_message(self, data):
        data_type = data.get('type')
        message = data.get('message')
        if data_type == 'login' and message == 'good':
            self.session_token = data['session']
            #### populates ui after category_data is assigned ###
            self.main.create_ui()
            self.sm.current = 'main'
            #### sets default starting tab ###
            Clock.schedule_once(lambda dt: self.set_default_tab(), 0)
        elif data_type == 'version' and message == 'version mismatch':
            self.resource_categories = data.get('categories')
            self.version = data.get('version')
            with open("client_data.json", "w") as f:
                json.dump({'version': self.version, 'categories':self.resource_categories}, f)
            
        elif data_type == 'version':
            if message == 'good':
                with open("client_data.json", 'r') as f:
                    self.resource_categories = json.load(f).get('categories')
        print('received: ')
        print(data)
    def set_default_tab(self):
        self.main.tab_manager.current = "mining"
app = Idleize()
app.run()