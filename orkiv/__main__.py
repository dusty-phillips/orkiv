## Uses sound from http://www.freesound.org/people/TwistedLemon/sounds/2054/

import datetime
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import XMPPError
from sleekxmpp.jid import InvalidJID
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.listview import ListItemButton
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import escape_markup
from kivy.core.audio import SoundLoader


class EnterTextInput(TextInput):
    def __init__(self, **kwargs):
        self.register_event_type("on_enter_key")
        super(EnterTextInput, self).__init__(**kwargs)

    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] == 13:  # 13 is the keycode for <enter>
            self.dispatch("on_enter_key")
        else:
            super(EnterTextInput, self)._keyboard_on_key_down(
                    window, keycode, text, modifiers)

    def on_enter_key(self):
        pass


class ConnectionModal(ModalView):
    def __init__(self, jabber_id, password):
        super(ConnectionModal, self).__init__(auto_dismiss=False,
            anchor_y="bottom")
        self.label = Label(text="Connecting to %s..." % jabber_id)
        self.add_widget(self.label)
        self.jabber_id = jabber_id
        self.password = password
        self.on_open = self.connect_to_jabber

    def connect_to_jabber(self):
        app = Orkiv.get_running_app()
        try:
            app.connect_to_jabber(self.jabber_id, self.password)
            app.root.show_buddy_list()
            self.dismiss()
        except (XMPPError, InvalidJID):
            self.label.text = "Sorry, couldn't connect, check your credentials"
            button = Button(text="Try Again")
            button.size_hint = (1.0, None)
            button.height = "40dp"
            button.bind(on_press=self.dismiss)
            self.add_widget(button)
            app.disconnect_xmpp()


class AccountDetailsTextInput(EnterTextInput):
    next = ObjectProperty()

    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] == 9:  # 9 is the keycode for <tab>
            self.next.focus = True
        else:
            super(AccountDetailsTextInput, self)._keyboard_on_key_down(
                    window, keycode, text, modifiers)

    def on_enter_key(self):
        self.parent.parent.parent.login()  # this is not future friendly


class AccountDetailsForm(AnchorLayout):
    server_box = ObjectProperty()
    username_box = ObjectProperty()
    password_box = ObjectProperty()

    def login(self):
        jabber_id = self.username_box.text + "@" + self.server_box.text
        modal = ConnectionModal(jabber_id, self.password_box.text)
        modal.open()


class BuddyListItem(BoxLayout, ListItemButton):
    jabberid = StringProperty()
    full_name = StringProperty()
    status_message = StringProperty()
    online_status = StringProperty()


class BuddyList(BoxLayout):
    list_view = ObjectProperty()

    def __init__(self):
        super(BuddyList, self).__init__()
        self.app = Orkiv.get_running_app()
        self.list_view.adapter.data = sorted(self.app.xmpp.client_roster.keys())
        self.new_messages = set()

    def force_list_view_update(self):
        self.list_view.adapter.update_for_new_data()
        self.list_view._trigger_reset_populate()

    def roster_converter(self, index, jabberid):
        result = {
            "jabberid": jabberid,
            "full_name": self.app.xmpp.client_roster[jabberid]['name']
        }

        presence = sorted(
            self.app.xmpp.client_roster.presence(jabberid).values(),
            key=lambda p: p.get("priority", 100), reverse=True)
        if presence:
            result['status_message'] = presence[0].get('status', '')
            show = presence[0].get('show')
            result['online_status'] = show if show else "available"
        else:
            result['status_message'] = ""
            result['online_status'] = "offline"

        if jabberid in self.new_messages:
            result['background_color'] = (0.6, 0.4, 0.6, 1)
        else:
            result['background_color'] = (0, 0, 0, 1)

        if index % 2:
            result['background_color'] = (x + .3 for x in result['background_color'])

        return result


class ChatWindow(BoxLayout):
    jabber_id = StringProperty()
    chat_log_label = ObjectProperty()
    send_chat_textinput = ObjectProperty()

    def send_message(self):
        app = Orkiv.get_running_app()
        app.xmpp.send_message(
            mto=self.jabber_id,
            mbody=self.send_chat_textinput.text)
        self.append_chat_message("Me", self.send_chat_textinput.text, color="aaffbb")
        self.send_chat_textinput.text = ''

    def append_chat_message(self, sender, message, color):
        self.chat_log_label.text += "[b](%s) [color=%s]%s[/color][/b]: %s\n" % (
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                color,
                escape_markup(sender),
                escape_markup(message))
        self.chat_log_label.parent.scroll_y = 0.0


class OrkivRoot(BoxLayout):
    mode = StringProperty("narrow")

    @property
    def chat_visible(self):
        return ChatWindow in {c.__class__ for c in self.children}

    @property
    def buddy_list_visible(self):
        return self.buddy_list in self.children

    def __init__(self):
        super(OrkivRoot, self).__init__()
        self.buddy_list = None
        self.chat_windows = {}
        self.in_sound = SoundLoader.load("orkiv/sounds/in.wav")

    def show_buddy_list(self):
        self.clear_widgets()
        if not self.buddy_list:
            self.buddy_list = BuddyList()
        for buddy_list_item in self.buddy_list.list_view.adapter.selection:
            buddy_list_item.deselect()
        self.add_widget(self.buddy_list)

    def get_chat_window(self, jabber_id):
        if jabber_id not in self.chat_windows:
            self.chat_windows[jabber_id] = ChatWindow(jabber_id=jabber_id)
        return self.chat_windows[jabber_id]

    def show_buddy_chat(self, jabber_id):
        self.remove_widget(self.buddy_list)
        self.add_widget(self.get_chat_window(jabber_id))
        self.buddy_list.new_messages.discard(jabber_id)
        self.buddy_list.force_list_view_update()

    def handle_xmpp_message(self, message):
        if message['type'] not in ['normal', 'chat']:
            return
        jabber_id = message['from'].bare

        chat_window = self.get_chat_window(jabber_id)
        chat_window.append_chat_message(jabber_id, message['body'], color="aaaaff")
        self.in_sound.play()
        if chat_window not in self.children:
            self.buddy_list.new_messages.add(jabber_id)
            self.buddy_list.force_list_view_update()


class Orkiv(App):
    def __init__(self):
        super(Orkiv, self).__init__()
        self.xmpp = None

    def connect_to_jabber(self, jabber_id, password):
        self.xmpp = ClientXMPP(jabber_id, password)
        self.xmpp.reconnect_max_attempts = 1
        connected = self.xmpp.connect()
        if not connected:
            raise XMPPError("unable to connect")
        self.xmpp.process()
        self.xmpp.send_presence()
        self.xmpp.get_roster()
        self.xmpp.add_event_handler('message', self.root.handle_xmpp_message)

    def disconnect_xmpp(self):
        if self.xmpp and self.xmpp.state.ensure("connected"):
            self.xmpp.abort()
        self.xmpp = None

    def on_stop(self):
        self.disconnect_xmpp()


Orkiv().run()
