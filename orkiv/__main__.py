from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import XMPPError
from sleekxmpp.jid import InvalidJID
from kivy.uix.textinput import TextInput


class AccountDetailsTextInput(TextInput):
    next = ObjectProperty()

    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] == 9:  # 9 is the keycode for <tab>
            self.next.focus = True
        elif keycode[0] == 13:  # 13 is the keycode for <enter>
            self.parent.parent.parent.login()  # this is not future friendly
        else:
            super(AccountDetailsTextInput, self)._keyboard_on_key_down(
                    window, keycode, text, modifiers)


class AccountDetailsForm(AnchorLayout):
    server_box = ObjectProperty()
    username_box = ObjectProperty()
    password_box = ObjectProperty()

    def login(self):
        try:
            jabber_id = self.username_box.text + "@" + self.server_box.text
            password = self.password_box.text

            app = Orkiv.get_running_app()
            app.connect_to_jabber(jabber_id, password)
            print(app.xmpp.client_roster.keys())
        except (XMPPError, InvalidJID):
            print("Sorry, couldn't connect, check your credentials")
        finally:
            if app.xmpp:
                app.xmpp.disconnect()


class Orkiv(App):

    def __init__(self):
        super(Orkiv, self).__init__()
        self.xmpp = None

    def connect_to_jabber(self, jabber_id, password):
        self.xmpp = ClientXMPP(jabber_id, password)
        self.xmpp.reconnect_max_attempts = 1
        connected = self.xmpp.connect()
        if not connected:
            raise XMPPError()
        self.xmpp.process()
        self.xmpp.send_presence()
        self.xmpp.get_roster()

Orkiv().run()
