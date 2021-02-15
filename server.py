import JFormat

class Server:
    def __init__(self, ip, port):
        self.users = {} # mapping from usernames to users?
        self.all_messages = {}

    # Zack
    def login_user(self, username, clientsocket):
        self.logged_in_users[username] = clientsocket

    def receive_client_message(self, formatted_message):
        # msg is arbitrary json from a client

        # check if msg is empty, ie. if Client is disconnecting
        # and should be logged out?

        # parse and handle based on message type
        msg = JFormat(formatted_message)
        msg_type = msg.jtype
        if msg_type == "login_request":
            pass
        elif msg_type == "login_response":
            pass
        elif msg_type == "create_request":
            pass
        elif msg_type == "create_response":
            pass
        elif msg_type == "list_request":
            pass
        elif msg_type == "list_response":
            pass
        elif msg_type == "text_message":
            pass
        elif msg_type == "inbox_check":
            pass
        elif msg_type == "delete_request":
            pass
        else:
            raise Exception("Server received message of unknown type: " + formatted_message)

    # Zack
    def main_loop(self):
        # call select, process any client messages that need to be processed
        pass


class User:
    def __init__(self, socket, username):
        self.socket = socket
        self.username = username
        self.is_logged_in = True
        self.undelivered_text_messages = []
        self.message_queue = []

    def login(self):
        self.is_logged_in = True

    def logout(self):
        self.is_logged_in = False
