from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty


class AccountDetailsForm(AnchorLayout):
    server_box = ObjectProperty()
    username_box = ObjectProperty()
    password_box = ObjectProperty()

    def login(self):
        print("Click the goddamn button")


class Orkiv(App):
    pass

Orkiv().run()
