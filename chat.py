from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


def esc_markup(msg):
    return (msg.replace('&', '&amp;')
            .replace('[', '&bl;')
            .replace(']', '&br;'))


class ShorbagiChat():
    def connect(self):
        host = self.ids.server.text
        self.nick = self.ids.nickname.text
        print('-- connecting to ' + host)
        PORT = 33333
        ADDR = (host, PORT)
        self.client_socket.connect(ADDR)
        self.send(self.nick)
        self.on_connect()

    def disconnect(self):
        print('-- disconnecting')
        self.current = 'login'
        self.ids.chat_logs.text = ''

    def send(self, msg, event=None):  # event is passed by binders.
        """Handles sending of messages."""
        self.client_socket.send(bytes(msg, "utf8"))
        print('send: ' + msg)
        if msg == "{quit}":
            self.client_socket.close()

    def send_msg(self, event=None):
        msg = self.ids.message.text
        self.ids.chat_logs.text += ('\t[b][color=2980b9]{}:[/color][/b] {}\n'.format(self.nick, esc_markup(msg)))
        self.send(msg)
        self.ids.message.text = ''
        if msg == "{quit}":
            self.current = 'login'

    def on_connect(self):
        print('-- connected')
        self.current = 'chatroom'

    def receive(self, msg):
        """Handles receiving of messages."""

        while True:
            try:
                msg = self.client_socket.recv(self.bufsiz).decode("utf8")
                print(msg)
            except OSError:  # Possibly client has left the chat.
                break

    def on_message(self, msg):
        self.ids.chat_logs.text += '\t' + msg + '\n'
        print(msg + 'On_msg')

    bufsiz = 1024
    client_socket = socket(AF_INET, SOCK_STREAM)



receive_thread = Thread(target=ShorbagiChat.receive)
receive_thread.start()


