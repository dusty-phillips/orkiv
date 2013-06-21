from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty


class AccountDetailsForm(AnchorLayout):
    server_box = ObjectProperty()
    username_box = ObjectProperty()
    password_box = ObjectProperty()

    def login(self):
        print(self.server_box.text)
        print(self.username_box.text)
        print(self.password_box.text)


class Orkiv(App):
    pass

Orkiv().run()
