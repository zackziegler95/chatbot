import sys

from wireprotocol import WireProtocol, CMD

# Greg
# Change control flow to new protocol

# Zack
def listen_for_messages(self, q, socket, buffer_size):
    wp = WireProtocol()

    while True:
        data = socket.recv(buffer_size)
        if not data:
            q.put(None) # None indicates server cut connection
            break
        
        # if parse_incoming_bytes is True, an entire message has been received
        while wp.parse_incoming_bytes(data):
            q.put([wp.command, wp.parse_data()])
            data = wp.tmp_buffer # Save any leftover bytes
            wp.reset_buffers()

def listen_for_keystroke(self, q):
    # do something with pipe
    ch = getch()
    q.put(ch)

class Client:
    def __init__(self, buffer_size=64):
        # import server address (HOST, PORT)
        server_address = (127, 9000)
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect(*server_address)

        quitflag = self.starting_loop()
        if quitflag:
            sys.exit()

        self.username = None

        self.socketq = mp.Queue()
        # starts separate process for the socket which sends messages from the
        # first queue, and puts received messages on the second
        self.socketprocess = mp.Process(target=listen_for_messages, args=[self.q, self.clientsocket, buffer_size])
        self.socketprocess.start()

        self.kblistenq = queue.Queue()
        self.start_kb_listening()

        if self.clientsocket = None:
            raise Exception("Client socket should be set before logging in.")
        # beginning loop to either login, create account, or quit
        # sets self.username if login or create account succeeds.

        if self.username is None:
            raise Exception("Username should be set but is not.")
        # enter main loop to send and receive messages, delete acct, log out
        self.main_loop()
    
    def start_kb_listening(self):
        self.keyboardprocess = threading.Thread(target=listen_for_keypress, args=[self.kblistenq])
        self.keyboardprocess.daemon = True
        self.keyboardprocess.start()

    def send_to_server(self, command, *args):
        msg = WireProtocol.data_to_bytes(command, args)
        i = 0
        while i < len(msg):
            sent += self.socket.send(msg[i:])
            i += sent

    def _username_bad_char_checker(inputstring):
        allowed = 'abcdefghijklmnopqrstuvwxyz0123456789'
        for c in inputstring:
            if c.lower() not in allowed:
                print("pls no use char: " + c)
                return True
        return False

    def starting_loop(self):
        quitflag = False

        print("Commands: login, create account, quit")
        while True: # loop to receive user input for login/create account
            userinput = input(">>> ")
            if userinput == "login":
                successflag = self.enter_login_mode()
                if successflag:
                    break
            elif userinput == "create account":
                successflag = self.enter_create_acct_mode()
                if successflag:
                    break
            elif userinput == "quit":
                quitflag = True
                break
            else:
                print("(invalid command)")
                continue

        return quitflag

    # this method and enter_login_mode() are nearly identical
    def enter_create_acct_mode(self):
        """
            sets self.username if succeeds
            returns successflag to indicate whether this was performed
        """
        print("Commands: enter name, return")
        while True: # loop to receive user input for name/abort
            userinput = input(">>> ")
            if userinput == "enter name":
                username = input("Username: ")
                # Client sends chosen username to Server
                self.send_to_server(JFormat.make_create_request(username=username))
                # set a timeout?
                # TODO: wait for "create_respnose" message from Server, use it to populate
                name_is_good = True
                name_is_good = False
                if name_is_good:
                    self.username = username
                    return True # successfully set self.username
                else:
                    continue

            elif userinput == "return":
                return False # failed to set self.username
            else:
                print("(invalid command)")
                continue

    def enter_login_mode(self):
        """
            sets self.username if succeeds
            returns successflag to indicate whether this was performed
        """
        print("Commands: enter name, return")
        while True: # loop to receive user input for name/abort
            userinput = input(">>> ")
            if userinput == "enter name":
                username = input("Username: ")
                # Client sends chosen username to Server
                self.send_to_server(JFormat.make_login_request(username=username))
                # set a timeout?
                # TODO: wait for "login_respnose" message from Server, use it to populate
                nameisgood = True
                nameisgood = False
                if nameisgood:
                    self.username = username
                    return True # successfully set self.username
                else:
                    continue

            elif userinput == "return":
                return False # failed to set self.username
            else:
                print("(invalid command)")
                continue

    def logout(self):
        pass
        # TODO: this should just close the client's socket

    def list_accounts(self):
        # TODO: support text wildcards (see rubric)?
        print("(requesting user list)")
        # send request to server for users (specify logged in vs out?)
        formatted_list_request = JFormat.make_user_list_request(sender=self.username)
        self.send_to_server(formatted_list_request)
        # listen_for_messages will handle receiving and printing user list

    # unsure about these
    def check_for_messages(self):
        formatted_check = JFormat.make_inbox_check(sender=self.username)
        self.send_to_server(formatted_check)

    def enter_command_mode(self):
        userinput = input(">>> ")

        if userinput == 'help':
            print("Commands: help, compose, list users, get messages, delete account, logout")

        elif userinput == 'compose':
            self.enter_compose_mode()

        elif userinput == 'list users':
            self.list_accounts()

        elif userinput == 'get messages':
            self.check_for_messages()

        elif userinput == 'delete account':
            self.enter_delete_mode()

        elif userinput == 'logout':
            self.logout()

        else:
            print("(invalid command)")


    def enter_compose_mode(self):
        # helper function to disallow chars within message
        def _message_bad_char_checker(inputstring):
            disallowed = ['"', '"""', '{', '}']
            for c in inputstring:
                if c in disallowed:
                    print("pls no use char: " + c)
                    return True

            if CMD.DELIM in inputstring:
                print('Illegal character sequence: %s' % CMD.DELIM)
                return True

            return False

        # prompt for recipient
        recipient = input("Recipient: ")
        # prompt for message

        bad_chars = True
        while bad_chars:
            message = input("Message: ")
            bad_chars = _message_bad_char_checker(message)

        #prompt send y/n
        abort = False
        while True:
            send = input("Send? (y/n): ")
            if send == "y":
                abort = False
            elif send == "n":
                abort = True

        if not abort:
            self.send_to_server(CMD.SEND, [self.username, recipient, message])

    def enter_delete_mode(self):
        # this deletes the account without addressing any stored messages

        #prompt user for confirmation
        really_delete = False
        while True:
            send = input("Confirm account deletion? (y/n): ")
            if send == "y":
                really_delete = True
            elif send == "n":
                really_delete = False

        if really_delete:
            formatted_delete_request = JFormat.make_delete_request(sender=self.username)
            self.send_to_server(formatted_delete_request)

    def main_loop(self):
        print("Commands: help, compose, list users, get messages, delete account, logout")
        while True:
            if not self.socketq.empty():
                # handle receiving and printing
                pass

            if not self.kblistenq.empty():
                self.kblistenq.get()
                self.enter_command_mode()
                self.start_kb_listening()

