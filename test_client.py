import pytest

import client
from wireprotocol import CMD
from client import Client

# Note: even the constructor for Client cannot be tested in isolation
# since its behavior is dependent on what kind of server is listening on
# the specified port.
# Even if a Client object is successfully initialized, its behavior in other
# methods is determined by a combination keyboard input and behavior of the
# server to which it is connected; therefore its control flow cannot be tested
# atomically.

def test_username_bad_char_checker():
    good_usernames = ['johndoe', 'g', 'AdamSandler', 'HBiden420']
    bad_usernames = [CMD.DELIM.decode('ascii'), '', '%andy', "for username in good_usernames:", "Jimmy John", '__main__']
    for username in good_usernames:
        res = client._username_bad_char_checker(username)
        assert not res
    for username in bad_usernames:
        res = client._username_bad_char_checker(username)
        assert res

def test_message_bad_char_checker():
    good_messages = ["Let's play bughouse on chess.com", 'Hello friend, how are you?', ""]
    bad_messages = [CMD.DELIM.decode('ascii'), '"wassap"', "f'hello{world}''"]
    for message in good_messages:
        res = client._message_bad_char_checker(message)
        assert not res
    for message in bad_messages:
        res = client._message_bad_char_checker(message)
        assert res

def test_client_init():
    # tests for correct response if nothing is listening on address below
    CLIENTBUFFERSIZE = 64
    HOST = "127.0.0.1"
    PORT = 9000
    pytest.raises(ConnectionRefusedError, Client, host=HOST, port=PORT, buffer_size=CLIENTBUFFERSIZE)
