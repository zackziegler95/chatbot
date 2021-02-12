# All Zack

class WireProtocal:
    def __init__(self, uuid):
        self.incoming_msg_len = -1
        self.msg_buffer = io.BytesIO(b'')

    def add_to_buffer(self, msg_bytes):
        # add to msg_buffer
        # error if msg_len is not set

    def set_waiting_msglen(self, length):
        self.incoming_msg_len = length

    def _finalize_message(self):
        # gets bytes from msg_buffer
        # flushes msg_buffer
        # resets incoming_msg_len
        # converts bytes to json
        # returns json

    def 

class BlockingClientSocket:
    def __init__(self, socket):
        self.socket = socket
        self.wire_protocal = WireProtocal()
    
    def send(self, msg):
        # msg is arbitrary json
        # loops until msg is fully sent
        # self.wire_protocal.add_to_buffer(data)

    def recv(self):
        # msg is arbitrary json
        # loops until msg is fully received

