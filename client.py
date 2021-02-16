import sys
import socket
import threading
import multiprocessing as mp

from wireprotocol import WireProtocol, CMD
from getch import getch


def listen_for_messages(q, socket, buffer_size):
    # sets up
    wp = WireProtocol()

    while True:
        # indicates that the socket has been closed from the main process
        if socket.fileno() == -1:
            break

        data = socket.recv(buffer_size)
        if not data:
            q.put(None) # None indicates server cut connection (uncontrolled failure mode)
            break

        # if parse_incoming_bytes is True, an entire message has been received
        while wp.parse_incoming_bytes(data):
            print('received full message, command: %d, args: %s' % (wp.command, str(wp.parse_data())))
            q.put([wp.command, wp.parse_data()])
            data = wp.tmp_buffer # Save any leftover bytes
            wp.reset_buffers()


def _username_bad_char_checker(inputstring, alsoallowed=''):
    allowed = 'abcdefghijklmnopqrstuvwxyz0123456789' + alsoallowed
    for c in inputstring:
        if c.lower() not in allowed:
            print(f"Illegal username character: '{c}'")
            return True
    return False


class Client:
    def __init__(self, host, port, buffer_size=64):
        # import server address (HOST, PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        self.username = None

        # queue for detecting keyboard input
        self.kblistenq = mp.Queue()

        # starts process which listens on the socket and puts received messages on the queue
        self.socketq = mp.Queue()
        self.socketprocess = mp.Process(target=listen_for_messages, args=[self.socketq, self.socket, buffer_size])
        self.socketprocess.daemon = True
        self.socketprocess.start()

        # starting loop to either login, create account, or quit, sets self.username
        quitflag = self.starting_loop()
        if quitflag:
            sys.exit()
        if self.username is None:
            raise Exception("Username should be set but is not.")
        
        # start waiting for keyboard input
        self.start_kb_listening()

        # enter main loop to send and receive messages, delete acct, log out, etc.
        self.main_loop()


    def start_kb_listening(self):
        # starts a thread which listens for a keyboard interaction
        def _listen_for_keystroke(q):
            # process listens for (and enqueues) a single char, then exits
            ch = getch()
            q.put(ch)

        self.keyboardprocess = threading.Thread(target=_listen_for_keystroke, args=[self.kblistenq])
        #self.keyboardprocess.daemon = True
        self.keyboardprocess.start()

    def send_to_server(self, command, *args):
        msg = WireProtocol.data_to_bytes(command, *args)
        i = 0
        while i < len(msg):
            sent = self.socket.send(msg[i:])
            i += sent

    def starting_loop(self):
        # blocks while logging in--which is fine, shouldn't be receiving messages anyway
        quitflag = False

        print("Commands: login, create_account, quit")
        # loop to receive user input for login/create account
        while True:  # keep looping until successful login or quit
            userinput = input(">>> ")
            if userinput == "login":
                successflag = self.enter_login_mode()
                if successflag:
                    break
            elif userinput == "create_account":
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

    # this method and enter_create_acct_mode() are nearly identical
    def enter_login_mode(self):
        """
            sets self.username if succeeds
            returns successflag to indicate whether this action was performed
        """
        while True: # loop to receive user input for name/abort
            username = input("Username: ")
            if _username_bad_char_checker(username):
                continue
            # client sends chosen username to Server
            self.send_to_server(CMD.LOGIN, username)
            # blocks waiting for login respnose message from server
            cmd, data = self.socketq.get()
            if not cmd == CMD.RESPONSE:
                raise Exception("Unexpected communication type from server.")

            success = not data # no error message indicates success
            if success:
                self.username = username
                print(f'Logged in as: {self.username}')
                return True
            else:
                print('Username not recognized.')
                continue

    def enter_create_acct_mode(self):
        """
            sets self.username if succeeds
            returns successflag to indicate whether this action was performed
        """
        while True: # loop to receive user input for name/abort
            username = input("Username: ")
            if _username_bad_char_checker(username):
                continue
            # client sends chosen username to Server
            self.send_to_server(CMD.CREATE, username)
            # blocks waiting for create acct respnose message from server
            cmd, data = self.socketq.get()
            if not cmd == CMD.RESPONSE:
                raise Exception("Unexpected communication type from server.")

            success = not data # no error message indicates success
            if success:
                self.username = username
                print(f'Logged in as: {self.username}')
                return True
            else:
                print('Username is taken.')
                continue

    def logout(self):
        self.socket.close()  # server handles it from here
        sys.exit()

    def list_accounts(self):
        # TODO: elicit search string, check it for bad chars
        print("Optional wildcard search (supports '*' and '?')")

        # loop to elicit valid wildcard string
        search_string = input("Search string: ")
        while _username_bad_char_checker(search_string, '*?'):
            search_string = input("Search string: ")
        if search_string == '':
            search_string = '*'
        # client sends username search to Server
        self.send_to_server(CMD.LIST, search_string)
        # listen_for_messages will handle receiving and printing of returned user list

    def check_for_messages(self):
        self.send_to_server(CMD.DELIVER)

    def enter_command_mode(self, inputchar):
        if inputchar == 'h':
            print("Commands: help (h), compose (c), list users (l), get messages (g), delete account (d), logout (q)")

        elif inputchar == 'c':
            self.enter_compose_mode()

        elif inputchar == 'l':
            self.list_accounts()

        elif inputchar == 'g':
            self.check_for_messages()

        elif inputchar == 'd':
            self.enter_delete_mode()

        elif inputchar == 'q':
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

            if CMD.DELIM.decode('ascii') in inputstring:
                print(f'Illegal character sequence: "{CMD.DELIM}"')
                return True

            return False

        # prompt for recipient
        recipient = input("Recipient: ")
        # prompt for message

        bad_chars = True
        while bad_chars:  # loop while message is illegal
            message = input("Message: ")
            bad_chars = _message_bad_char_checker(message)

        #prompt send y/n
        bail = False
        while True:  # loop to confirm sending
            sendit = input("Send? (y/n): ")
            if sendit == "y":
                bail = False
                break
            elif sendit == "n":
                bail = True

        if not bail:
            self.send_to_server(CMD.SEND, self.username, recipient, message)

    def enter_delete_mode(self):
        # this deletes the account without preserving server-stored messages

        really_delete = False
        while True:  # loop to prompt user for confirmation
            send = input("Confirm account deletion? (y/n): ")
            if send == "y":
                really_delete = True
                break
            elif send == "n":
                really_delete = False
                break

        if really_delete:
            self.send_to_server(CMD.DELETE)

    def display_message(self, parsed_message):
        # parsed message of the form [wp.command, wp.parse_data()]
        cmd, parsed_data = parsed_message
        if cmd == CMD.SEND:
            sender, message_body = parsed_data
            print(f"New message from {sender}: \n{message_body}\n")
        elif cmd == CMD.LISTRESPONSE:
            acct_list = parsed_data
            print(acct_list)
            print("Other accounts:\n" + "\n".join(acct_list))
        else:
            raise Exception("Cannot display a non-message command")


    def main_loop(self):
        print("Commands: help (h), compose (c), list users (l), get messages (g), delete account (d), logout (q)")
        while True:
            # receive any incoming messages
            if not self.socketq.empty():
                parsed_message = self.socketq.get()  # of the form [wp.command, wp.parse_data()]
                self.display_message(parsed_message)

            # if keyboard interrupts, elicit and handle user commands
            if not self.kblistenq.empty():
                inputchar = self.kblistenq.get()
                self.enter_command_mode(inputchar)
                self.start_kb_listening() # start new thread to continue listening for commands

if __name__ == '__main__':
    client = Client('localhost', 9000, 64)
