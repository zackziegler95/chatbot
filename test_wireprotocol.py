import pytest

from wireprotocol import WireProtocol, CMD

def test_data_to_bytes_singlearg():
    command = CMD.CREATE
    username = 'testname'
    res = WireProtocol.data_to_bytes(command, username)
    assert res == b'\x00\x00' + b'\x00'*39 + b'\x08' + b'testname'

def test_data_to_bytes_multiarg():
    command = CMD.SEND
    to_str = 'toname' # 6 bytes
    from_str = 'fromname' # 8 bytes
    msg = 'hello world!' # 12 bytes
    res = WireProtocol.data_to_bytes(command, to_str, from_str, msg) # total len is 26 + 3*2 = 32
    assert res == b'\x00\x02' + b'\x00'*39 + b'\x20' + b'toname|||fromname|||hello world!'

def test_parse_bytes_singlearg():
    wp = WireProtocol()
    msg_bytes = b'\x00\x00' + b'\x00'*39 + b'\x08' + b'testname'
    output = wp.parse_incoming_bytes(msg_bytes)
    assert output == True
    assert wp.version == 0
    assert wp.command == 0
    assert wp.data_len == 8
    print(wp.data_buffer)
    assert wp.data_buffer == b'testname'

def test_parse_bytes_multiarg():
    wp = WireProtocol()
    msg_bytes = b'\x00\x02' + b'\x00'*39 + b'\x20' + b'toname|||fromname|||hello world!'
    output = wp.parse_incoming_bytes(msg_bytes)
    assert output == True
    assert wp.version == 0
    assert wp.command == 2
    assert wp.data_len == 32
    assert wp.data_buffer == b'toname|||fromname|||hello world!'

def test_parse_bytes_multiarg_partial():
    wp = WireProtocol()
    msg_bytes = b'\x00\x02' + b'\x00'*39 + b'\x20' + b'toname|||fro'
    output = wp.parse_incoming_bytes(msg_bytes)
    assert output == False
    assert wp.version == 0
    assert wp.command == 2
    assert wp.data_len == 32
    assert wp.data_buffer == b''
    assert wp.tmp_buffer == b'toname|||fro'

def test_msg_data_parse():
    wp = WireProtocol()
    msg_bytes = b'\x00\x02' + b'\x00'*39 + b'\x20' + b'toname|||fromname|||hello world!'
    wp.parse_incoming_bytes(msg_bytes)
    data_out = wp.parse_data()
    assert len(data_out) == 3
    assert data_out[0] == 'toname'
    assert data_out[1] == 'fromname'
    assert data_out[2] == 'hello world!'

def test_malformed():
    wp = WireProtocol()
    msg_bytes = b'this is very wrong!'
    wp.parse_incoming_bytes(msg_bytes)
    with pytest.raises(ValueError):
        data_out = wp.parse_data()
