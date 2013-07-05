from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import XMPPError
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label


class ConnectionModal(ModalView):
    def __init__(self, jabber_id, password):
        super(ConnectionModal, self).__init__(auto_dismiss=False,
            anchor_y="bottom")
        self.label = Label(text="Connecting to %s..." % jabber_id)
        self.add_widget(self.label)
        self.jabber_id = jabber_id
        self.password = password


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
        jabber_id = self.username_box.text + "@" + self.server_box.text
        modal = ConnectionModal(jabber_id, self.password_box.text)
        modal.open()


class Orkiv(App):

    def connect_to_jabber(self, jabber_id, password):
        self.xmpp = ClientXMPP(jabber_id, password)
        self.xmpp.reconnect_max_attempts = 1
        connected = self.xmpp.connect()
        if not connected:
            raise XMPPError("unable to connect")
        self.xmpp.process()
        self.xmpp.send_presence()
        self.xmpp.get_roster()

Orkiv().run()
