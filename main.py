from kivy.app import App
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from kivy.uix.actionbar import ActionBar
from kivy.uix.popup import Popup
from bidi.algorithm import get_display
from kivy.properties import NumericProperty
from kivy.uix.colorpicker import ColorPicker
import socket
import pickle


def esc_markup(msg):
    return (msg.replace('&', '&amp;')
            .replace('[', '&bl;')
            .replace(']', '&br;'))


class MyOwnActionBar(ActionBar):
    pass


class AboutPopup(Popup):
    pass


class ChatApp(App):

    def __init__(self, *args, **kwargs):
        super(ChatApp, self).__init__(*args, **kwargs)
        receive_thread = Thread(target=self.on_message)
        receive_thread.start()
    first_size = NumericProperty('20')
    font_color = NumericProperty('1, 1, 1')
    # font_color.register_type('colorpicker', SettingColorPicker)


    def build_config(self, config):
        config.setdefaults('section1', {
            'key1': '20',
            'key2': '25'
        })

    def build_settings(self, settings):
        jsondata = """[
                        { "type": "options",
                          "title": "Text Size",
                          "desc": "Change Text Size Here",
                          "section": "section1",
                          "key": "key1",
                          "options": ["10", "20", "30"] },

                        { "type": "numeric",
                          "title": "Font Color",
                          "desc": "Change Font Color Here",
                          "section": "section1",
                          "key": "key2" }
                    ]"""
        settings.add_json_panel('Python Chat Server Settings',
                                self.config, data=jsondata)

    def display_settings(self, settings):
        try:
            p = self.settings_popup
        except AttributeError:
            self.settings_popup = Popup(content=settings,
                                        title='Settings',
                                        size_hint=(0.8, 0.8))
            p = self.settings_popup
        if p.content is not settings:
            p.content = settings
        p.open()

    def close_settings(self, *args):
        try:
            p = self.settings_popup
            p.dismiss()
        except AttributeError:
            pass  # Settings popup doesn't exist

    def on_config_change(self, config, section, key, value):
        self.first_size = config.getint('section1', 'key1')
        self.second_size = config.getint('section1', 'key1')

    def connect(self):
        host = self.root.ids.server.text
        self.nick = self.root.ids.nickname.text
        print('-- connecting to ' + host)

        self.send(self.nick)
        self.on_connect()

    def disconnect(self):
        print('-- disconnecting')
        self.send('{quit}')
        self.root.current = 'login'
        self.root.ids.chat_logs.text = ''

    def send(self, msg, event=None):  # event is passed by binders.
        """Handles sending of messages."""
        client_socket.send(bytes(msg, "utf8"))
        if msg == "{quit}":
            self.send(msg)
            client_socket.close()

    def send_msg(self, event=None):
        msg = self.root.ids.message.text
        # self.root.ids.chat_logs.text += ('\t[b][color=2980b9]{}:[/color][/b] {}\n'.format(self.nick, esc_markup(msg)))
        self.send(msg)
        self.root.ids.message.text = ''
        if msg == "{quit}":
            self.send(msg)
            self.root.current = 'login'

    def on_connect(self):

        print('-- connected')
        self.root.current = 'chatroom'

    def on_message(self):
        """Handles receiving of messages."""
        client_socket.connect(ADDR)
        while True:
            msg = client_socket.recv(4096)
            try:

                if msg != UnicodeDecodeError:
                    ms = msg.decode('utf8')
                    print(ms)
                    s = '[\''
                    if s not in ms:

                        text = get_display(ms)
                        self.root.ids.chat_logs.text += text + '\n'

                    else:
                        text = get_display(ms)
                        con = eval(text)
                        self.root.ids.chat_clients.text = ''
                        for p in con:
                            self.root.ids.chat_clients.text += p + '\n'
                else:
                    print(msg)
            except UnicodeDecodeError:
                text = pickle.loads(msg)
                print(text)
                self.root.ids.chat_rooms.text = ''
                for p in text:
                    print(p)
                    self.root.ids.chat_rooms.text += p + '\n'

            except OSError:  # Possibly client has left the chat.
                break

    def show_popup(self):
        p = AboutPopup()
        p.open()


host = '127.0.0.1'
PORT = 33333
ADDR = (host, PORT)

client_socket = socket.socket(AF_INET, SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


if __name__ == '__main__':
    ChatApp().run()
