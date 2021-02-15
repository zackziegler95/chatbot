from wireprotocol import WireProtocol

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

def listen_for_keystroke(self, pipe):
    # do something with pipe

class Client:
    def __init__(self):
        pass
    
    # Zack
    def send_to_server(self, command, *args):
        msg = WireProtocol.data_to_bytes(command, args)
        i = 0
        while i < len(msg):
            sent += self.socket.send(msg[i:])
            i += sent

    def create_account(self):
        pass

    def login(self):
        pass

    def delete_account(self):
        pass

    def list_accounts(self):
        pass

    # unsure about these
    def check_for_messages(self):
        pass

    def enter_compose_mode(self):
        pass
    
    def main_loop(self):
        pass
