#!/usr/bin/env python3
# Importing the socket and threading library to be used in our server
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import select
import pickle


def new_connections():
    # Accepting new connections from client
    while True:
        client, client_address = SERVER.accept()
        print("{} has connected.".format(client_address))
        addresses[client] = client_address
        handle_thread = Thread(target=handle_client, args=(client, client_address))
        handle_thread.start()
        print(client)
        print(client_address)
        print(addresses)


def handle_client(client, client_address):  # Takes client socket as argument.
    """Handles a single client connection."""
    server = ChatServer()
    chat_server = []
    chat_server.append(server)
    print(chat_server)
    name = client.recv(BUFSIZ).decode("utf8")
    connected.append(name)
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    client.send(bytes(str(connected), "utf8"))
    broadcast(bytes(str(connected), "utf8"))
    broadcast(bytes(str(server.list_rooms()), "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
            # broadcast(msg, name+": ")
            chat_server[0].handle_msg(name, msg, client)
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast(msg, prefix=""):  # prefix is for nickname identification.
    # Broadcast the message to all connected clients

    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


class ChatServer:
    def __init__(self):
        self.rooms = {}  # {room_name: Room}
        self.room_player_map = {}  # {playerName: roomName}

    def list_rooms(self):

        if len(self.rooms) == 0:
            msg = 'Oops, no active rooms currently. Create your own!\n' \
                  + 'Use [<join> room_name] to create a room.\n'
            broadcast(bytes(msg, "utf-8"))
            print(self.rooms)

        else:
            data = pickle.dumps(self.room_player_map)
            print(self.rooms)
            print(self.room_player_map)
            print(data)
            for sock in clients:
                sock.send(data)

    def handle_msg(self, player, msg, client):
        instructions = 'Instructions:\n[<list>] to list all rooms\n [<join> room_name] to join/create/switch to a room\n [<manual>] to show instructions\n [<quit>] to quit\n Otherwise start typing and enjoy!\n'
        msg = msg.decode("utf8")

        print(player + " says: " + msg)
        if "name:" in msg:
            # name = msg.split()[1]
            # print("New connection from:", player[1])
            player.send(bytes(instructions, "utf8"))

        elif "<join>" in msg:
            same_room = False
            if len(msg.split()) >= 2:  # error check
                room_name = msg.split()[1]
                if player in self.room_player_map:  # switching?
                    if self.room_player_map[player] == room_name:
                        already = 'You are already in room: %s' % room_name
                        client.send(bytes(already, "utf8"))
                        same_room = True
                    else:  # switch
                        old_room = self.room_player_map[player]
                        self.rooms[old_room].remove_player(player)
                if not same_room:
                    if room_name not in self.rooms:  # new room:
                        print(room_name)
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].players.append(client)
                    # self.rooms[room_name].welcome_new(player)
                    self.room_player_map[player] = room_name
                    # print(self.rooms)
                    # print(self.room_player_map)
                else:
                    print('You are not in room')

            else:
                client.send(bytes(instructions, "utf8"))

        elif "<list>" in msg:
            self.list_rooms()

        elif "<manual>" in msg:
            client.send(instructions.encode('utf8'))

        elif "<quit>" in msg:
            # player.socket.sendall(QUIT_STRING.encode())
            self.remove_player(player)

        else:
            # broadcast(msg.encode('utf8'), str(player) + ': ')
            # check if in a room or not first
            if player in self.room_player_map:
                # room = Room(self.room_player_map)
                self.rooms[self.room_player_map[player]].broadcast(player, msg)

            else:
                msg = 'You are currently not in any room! \n' \
                      + 'Use [<list>] to see available rooms! \n' \
                      + 'Use [<join> room_name] to join a room! \n'
                client.send(bytes(msg, "utf8"))

    def remove_player(self, player):
        if player.name in self.room_player_map:
            self.rooms[self.room_player_map[player.name]].remove_player(player)
            del self.room_player_map[player.name]
        print("Player: " + player.name + " has left\n")


class Room:
    def __init__(self, name):
        self.players = []  # a list of sockets
        self.name = name

    def welcome_new(self, from_player):
        msg = self.name + " welcomes: " + from_player.name + '\n'
        # self.players.append(client)
        for player in self.players:
            player.socket.sendall(msg.encode())

    def broadcast(self, player, msg):
        msg2 = player + ": " + msg
        for player in self.players:
            # player.socket.sendall(msg)
            # player.send(msg)
            print(self.players)
            player.send(bytes(msg2, "utf8"))

    def remove_player(self, player):
        # self.players.remove(player)
        leave_msg = player.name.encode() + b"has left the room\n"
        self.broadcast(player, leave_msg)
# Identifying variables, Clients list and server start


clients = {}
addresses = {}
connected = []

HOST = ''
PORT = 33333
BUFSIZ = 4096
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

# Starting the application and threads
if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=new_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
