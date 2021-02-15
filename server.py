import selectors
import socket
import uuid
import types

from wireprotocol import WireProtocol
both_events = selectors.EVENT_READ | selectors.EVENT_WRITE

class Message:
    def __init__(self, sender, recip, msg):
        self.sender = sender
        self.recip = recip
        self.msg = msg

# parts of select code modified from https://realpython.com/python-sockets/#multi-connection-client-and-server
class Server:
    def __init__(self, ip, port, buffer_size):
        self.uuid2wp = {}
        self.username2uuid = {}
        self.uuid2username = {}
        self.username2sendbuffer = {}

        self.select = selectors.DefaultSelector()

        self.buffer_size = buffer_size

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))
        self.serversocket.listen()
        self.serversocket.setblocking(False) # nonblocking socket here, using select
        self.select.register(self.serversocket, selectors.EVENT_READ, data=None)

    
    # Zack
    def accept_connection(self, serversocket):
        clientsocket, addr = serversocket.accept()
        clientsocket.setblocking(False)

        uuid = str(uuid.uuid1())
        data = types.SimpleNamespace(addr=addr, uuid=uuid)
        self.select.register(clientsocket, both_events, data=data)
        self.uuid2wp[uuid] = WireProtocol()

    def logout(self, uuid, clientsocket):
        del self.uuid2wp[uuid]
        
        username = self.uuid2username.get(uuid)
        if username is not None:
            del self.username2uuid[username]
            del self.uuid2username[uuid]
            del self.username2sendbuffer[username]

        self.select.unregister(clientsocket)
        clientsocket.close()

    def receive(self, uuid, command, data):
        if command == CMD.CREATE:
            pass
        elif command == CMD.LIST:
            pass
        elif command == CMD.SEND:
            pass
        elif command == CMD.DELIVER:
            pass
        elif command == CMD.DELETE:
            pass
        elif command == CMD.LOGIN:
            username = data
            self.username2sendbuffer[username] = []
            self.username2uuid[username] = uuid
            self.uuid2username[uuid] = username
        else:
            raise ValueError('unknown command id %d' % command)

    def read_or_write(self, key, mask):
        clientsocket = key.fileobj
        data = key.data
        uuid = data.uuid
        wp = self.uuid2wp[uuid]
        username = self.uuid2username.get(uuid, None)

        # check if we need to recv
        if mask & selectors.EVENT_READ:
            recv_data = clientsocket.recv(self.buffer_size)
            if not recv_data:
                self.logout(uuid, clientsocket)
                return

            while wp.parse_incoming_bytes(recv_data):
                self.receive(uuid, wp.command, wp.parse_data())
                recv_data = wp.tmp_buffer
                wp.reset_buffers()

        # check if we need to send and are ready to send
        if mask & selectors.EVENT_WRITE and username and self.username2sendbuffer.get(username, None):
            ZACK: START HERE


    def receive_client_message(self, msg):
        # msg is arbitrary json from a client
        pass

    # Zack
    def main_loop(self):
        # call select, process any client messages that need to be processed

        events = self.select.select(timeout=None)
        for key, mask in events:
            if key.data is None: # this is a accept call
                self.accept_connection(key.fileobj) # fileobj is the serversocket
            else: # this is a recv call
                self.read_or_write(key, mask)
