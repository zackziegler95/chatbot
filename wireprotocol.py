# All Zack

# version 0
# 1 byte, version
# 1 byte, command
## 0 - create account
### data: ascii username
## 1 - list accounts
### data: (optional) ascii text wildcard
## 2 - send message
### data: ascii recipient username @@@ ascii message
## 3 - deliver undelivered messages
### data: none
## 4 - delete account
### data: none
# 40 bytes, data length
# data length bytes, data

WP_VERSION = 0 # current version is 0
VERSION_LEN = 1
COMMAND_LEN = 1
DATALENGTH_LEN = 40
DELIM = b'|||'

class WireProtocol:
    # The idea here is for the operations of the wire protocol to be independent
    # of the details of the socket
    # This class is responsible for validating data

    def __init__(self, uuid):
        self.reset_buffers()

    def reset_buffers(self):
        self.version = -1 # -1 will indicate we don't have it yet
        self.command = -1
        self.data_len = -1 
        self.tmp_buffer = b'' # empty byte string will indicate we don't have it yet
        self.data_buffer = b''

    def parse_incoming_bytes(self, msg_bytes):
        # msg_bytes is byte string
        # returns True if we've received a full message, otherwise False

        self.tmp_buffer = self.tmp_buffer + msg_bytes

        # first check if version is needed, and if so check if we have it all
        if self.version == -1:
            if len(self.tmp_buffer) < VERSION_LEN:
                return False
            self.version = int.from_bytes(self.tmp_buffer[:VERSION_LEN], "big")
            self.tmp_buffer = self.tmp_buffer[VERSION_LEN:]

        # next check if the command is needed, and if so check if we have it all
        if self.command == -1:
            if len(self.tmp_buffer) < COMMAND_LEN:
                return False
            self.command = int.from_bytes(self.tmp_buffer[:COMMAND_LEN], "big")
            self.tmp_buffer = self.tmp_buffer[COMMAND_LEN:]

        # next check if the length is needed, and if so check if we have it all
        if self.data_len == -1:
            if len(self.tmp_buffer) < DATALENGTH_LEN:
                return False
            self.data_len = int.from_bytes(self.tmp_buffer[:DATALENGTH_LEN], "big")
            self.tmp_buffer = self.tmp_buffer[DATALENGTH_LEN:]

        # finally check if the data_buffer is empty and if so check if we have it all
        # data might not be provided, in which case the length is 0 and we don't need
        # to get data
        if not self.data_buffer and self.data_len > 0:
            if len(self.tmp_buffer) < self.data_len:
                return False
            self.data_buffer = int.from_bytes(self.tmp_buffer[:self.data_len], "big")
            self.tmp_buffer = self.tmp_buffer[self.data_len:]

        return True

    def parse_data(self):
        if self.version != WP_VERSION:
            raise ValueError('version mismatch, current version is %d but received version is %d' % (WP_VERSION, self.version))

        # create account
        if self.command == 0:
            return self.data_buffer.decode('ascii')

        # list account
        if self.command == 1:
            if self.data_buffer:
                return self.data_buffer.decode('ascii')
            else:
                return None

        # send message
        if self.command == 2:
            if DELIM not in text:
                raise ValueError('data delimeter not found in message body')
            text = [arg.decode('ascii') for arg in self.data_buffer.split(DELIM)]
            return text

        # deliver undelivered messages
        if self.command == 3:
            if self.data_buffer:
                raise ValueError('no data expected for deliver undelivered messages command')
            return None

        # delete account
        if self.command == 4:
            if self.data_buffer:
                raise ValueError('no data expected for delete account command')
            return None

        raise ValueError('command id %d unknown' % self.command)
    
    @staticmethod
    def data_to_bytes(command, *args):
        # any args passed are eventually concatenated with the DELIM delimeter
        # args should be a list of (normal) strings
        message = b''

        # version
        if WP_VERSION >= 2**VERSION_LEN:
            raise ValueError('version %d is larger than max version %d' % (WP_VERSION, 2**VERSION_LEN-1))
        message += int.to_bytes(WP_VERSION, VERSION_LEN, 'big')

        # command
        if command >= 2*COMMAND_LEN:
            raise ValueError('command %d is larger than max version %d' % (command, 2**COMMAND_LEN-1))
        message += int.to_bytes(command, COMMAND_LEN, 'big')

        # data length
        if args:
            num_args = len(args)
            args = [arg.encode('ascii') for arg in args]
            data_len = sum(map(len, args))+len(DELIM)*(num_args-1)
        else:
            data_len = 0

        if data_len >= 2*DATALENGTH_LEN:
            raise ValueError('data length %d is larger than max data length %d' % (data_len, 2**DATALENGTH_LEN-1))
        message += int.to_bytes(data_len, DATALENGTH_LEN, 'big')

        # data
        if data_len > 0:
            message += DELIM.join(args)

        return message
        

class BlockingClientSocket:
    def __init__(self, socket):
        self.socket = socket
        self.wire_protocol = WireProtocol()
    
    def send(self, msg):
        # msg is arbitrary json
        # loops until msg is fully sent
        # self.wire_protocol.add_to_buffer(data)

    def recv(self):
        # msg is arbitrary json
        # loops until msg is fully received

