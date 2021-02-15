from wireprotocol import WireProtocol

class Server:
    def __init__(self, ip, port):
        self.logged_in_users = {}
        pass
    
    # Zack
    def login_user(self, username, clientsocket):
        self.logged_in_users[username] = clientsocket

    def receive_client_message(self, msg):
        # msg is arbitrary json from a client
        pass

    # Zack
    def main_loop(self):
        # call select, process any client messages that need to be processed
        pass
