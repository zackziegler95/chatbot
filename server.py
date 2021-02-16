import selectors
import socket
import uuid as uuid_module
import types
import fnmatch
import config

from wireprotocol import WireProtocol, CMD
both_events = selectors.EVENT_READ | selectors.EVENT_WRITE

class Message:
    def __init__(self, sender, recip, msg):
        self.sender = sender
        self.recip = recip
        self.msg = msg

# We need a separate connection class to store information about connections separate from
# a notion of users. Before a user is , logged in a connection is still established and
# messages need to be able to be sent back and forth
class Connection:
    def __init__(self, uuid, socket):
        self.uuid = uuid
        self.wp = WireProtocol()
        self.socket = socket
        self.send_buffer = b''

class User:
    def __init__(self, username):
        self.username = username
        self.connection = None
        self.undelivered_messages = []

    def login(self, conn):
        print('logging in %s' % self.username)
        self.connection = conn

    def logout(self):
        print('logging out %s' % self.username)
        self.connection = None

# parts of select code modified from https://realpython.com/python-sockets/#multi-connection-client-and-server
class Server:
    def __init__(self, host=config.HOST, port=config.PORT, buffer_size=config.SERVERBUFFERSIZE):
        self.users = []
        self.connections = []

        self.select = selectors.DefaultSelector()
        self.buffer_size = buffer_size

        print('Initiating server socket')
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversocket.bind((host, port))
        self.serversocket.listen()
        self.serversocket.setblocking(False) # nonblocking socket here, using select
        self.select.register(self.serversocket, selectors.EVENT_READ, data=None)

    def conn2user(self, conn):
        res = [u for u in self.users if u.connection is not None and u.connection.uuid == conn.uuid]
        if res:
            return res[0]
        else:
            return None

    def accept_connection(self, serversocket):
        clientsocket, addr = serversocket.accept()
        clientsocket.setblocking(False)

        # uuid is unique to the connection. The same user connecting multiple times gets
        # a different uuid every time
        uuid = str(uuid_module.uuid1())
        data = types.SimpleNamespace(addr=addr, uuid=uuid)
        conn = Connection(uuid, clientsocket)
        self.connections.append(conn)
        self.select.register(clientsocket, both_events, data=data)

    def logout(self, uuid, clientsocket):
        del self.uuid2wp[uuid]

        username = self.uuid2username.get(uuid)
        if username is not None:
            del self.username2uuid[username]
            del self.uuid2username[uuid]
            del self.username2sendbuffer[username]

    def _process_create(self, conn, data):
        username = data
        error = ''
        if username in [u.username for u in self.users]:
            error = 'username already exists'
        elif CMD.DELIM.decode('ascii') in username:
            error = 'illegal character sequence %s in username' % CMD.DELIM.decode('ascii')
        else:
            user = User(username)
            user.login(conn)
            self.users.append(user)

        # send response with potential error
        conn.send_buffer += WireProtocol.data_to_bytes(CMD.RESPONSE, error)

    def _process_list(self, conn, data):
        # check if we need to filter by anything
        names = [u.username for u in self.users]
        if data is not None:
            names = [n for n in names if fnmatch.fnmatch(n, data)]
        conn.send_buffer += WireProtocol.data_to_bytes(CMD.LISTRESPONSE, *names)

    def _process_send(self, conn, data):
        from_name = data[0]
        to_name = data[1]
        msg = data[2]

        from_user = self.conn2user(conn)
        error = ''
        if from_user is None:
            error = 'attempting to send a message before logging in, for message: from: %s | to: %s | body: %s' % (from_name, to_name, msg)

        elif from_name != from_user.username:
            error = 'specified from name is not the sender. Got username %s, current username is %s, for message: from: %s | to: %s | body: %s' % (from_name, from_user.username, from_name, to_name, msg)

        elif to_name not in [u.username for u in self.users]:
            error = 'specific recipient %s does not exist, for message: from: %s | to: %s | body: %s' % (to_name, from_name, to_name, msg)

        if error:
            conn.send_buffer += WireProtocol.data_to_bytes(CMD.RESPONSE, error)
            return

        to_user = [u for u in self.users if u.username == to_name][0]

        # Send to recipient immediately if they are online
        if to_user.connection is not None:
            to_user.connection.send_buffer += WireProtocol.data_to_bytes(CMD.SEND, *data)
        else:
            # If they're not online, add to undelivered message list
            to_user.undelivered_messages.append(data)

        # In any event, send back to the sender for printing
        from_user.connection.send_buffer += WireProtocol.data_to_bytes(CMD.SEND, *data)

    def _process_deliver(self, conn, data):
        print('conn uuid: %s' % str(conn.uuid))
        for u in self.users:
            print(u.username)
            print(u.connection)
            if u.connection:
                print(u.connection.uuid)

        from_user = self.conn2user(conn)
        error = ''
        if from_user is None:
            error = 'attempting to deliver undelivered messages before logging in'
            conn.send_buffer += WireProtocol.data_to_bytes(CMD.RESPONSE, error)
            return

        for msg in from_user.undelivered_messages:
            conn.send_buffer += WireProtocol.data_to_bytes(CMD.SEND, *msg)
        from_user.undelivered_messages = []

    def _process_delete(self, conn, data):
        # If the user is logged in, log them out
        from_user = self.conn2user(conn)
        if from_user is not None:
            from_user.logout()

        # delete the user
        del self.users[self.users.index(from_user)]

    def _process_login(self, conn, data):
        username = data
        error = ''
        if username not in [u.username for u in self.users]:
            error = 'username does not exist'
        else:
            user = [u for u in self.users if u.username == username][0]

            # check if user is already logged in
            if user.connection is not None:
                error = 'user is already logged in'
            else:
                user.login(conn)
                print('user logged in, username: %s, conn %s' % (user.username, user.connection))

        # send response with potential error
        conn.send_buffer += WireProtocol.data_to_bytes(CMD.RESPONSE, error)

    def receive(self, conn, command, data):
        if command == CMD.CREATE:
            self._process_create(conn, data)
        elif command == CMD.LIST:
            self._process_list(conn, data)
        elif command == CMD.SEND:
            self._process_send(conn, data)
        elif command == CMD.DELIVER:
            self._process_deliver(conn, data)
        elif command == CMD.DELETE:
            self._process_delete(conn, data)
        elif command == CMD.LOGIN:
            self._process_login(conn, data)
        else:
            raise ValueError('unknown command id %d' % command)

    def read_or_write(self, key, mask):
        clientsocket = key.fileobj
        data = key.data
        uuid = data.uuid
        conn = [c for c in self.connections if c.uuid == uuid][0]
        wp = conn.wp
        from_user = self.conn2user(conn)

        # check if we need to recv
        if mask & selectors.EVENT_READ:
            recv_data = clientsocket.recv(self.buffer_size)
            if not recv_data:
                # remove the clientsocket for list of sockets select polls
                self.select.unregister(clientsocket)
                clientsocket.close()

                # remove the connection
                del self.connections[self.connections.index(conn)]

                # logout as well if needed
                if from_user is not None:
                    from_user.logout()
                return

            while wp.parse_incoming_bytes(recv_data):
                self.receive(conn, wp.command, wp.parse_data())
                recv_data = wp.tmp_buffer
                wp.reset_buffers()

        # check if we need to send and are ready to send
        if mask & selectors.EVENT_WRITE and conn.send_buffer:
            sent = clientsocket.send(conn.send_buffer)
            conn.send_buffer = conn.send_buffer[sent:]

    def main_loop(self):
        print('Entering main loop')

        while True:
            # call select, process any client messages that need to be processed
            events = self.select.select(timeout=None)
            for key, mask in events:
                if key.data is None: # this is a accept call
                    self.accept_connection(key.fileobj) # fileobj is the serversocket
                else: # this is ready for send or recv
                    self.read_or_write(key, mask)

if __name__ == '__main__':
    server = Server()
    server.main_loop()
