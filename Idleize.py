from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import NoTransition
from kivy.properties import NumericProperty
from kivy.clock import Clock

Builder.load_file('main.kv')

class MainLayout(BoxLayout):
    copper = NumericProperty(0)
    rate = 1
    running = False
    def idle(self):
        if not self.running:
            self.running_clock = Clock.schedule_interval(self.increment,self.rate)
            self.running = True
        else: 
            self.running_clock.cancel()
            self.running = False

    def increment(self, inc, ):
        self.copper += 1
        print(self.copper)
            

class Idleize(App):
    def build(self):
        return MainLayout()

app = Idleize()
app.run()