from server import Server, User, Connection
from wireprotocol import WireProtocol, CMD

def setup_server(server):
    server.users = [User('u1'), User('u2'), User('u3')]
    conn1 = Connection('uuid1', None)
    conn2 = Connection('uuid2', None)
    conn3 = Connection('uuid3', None)

    server.users[0].login(conn1)
    server.users[1].login(conn2)
    server.users[2].login(conn3)
    server.connections = [conn1, conn2, conn3]

def test_conn2user():
    server = Server(host=None)
    setup_server(server)
    
    conn = server.connections[1]
    user = server.conn2user(conn)
    assert user.username == 'u2'

def test_conn2user_empty():
    server = Server(host=None)
    conn = Connection('uuid1', None)
    user = server.conn2user(conn)
    assert user is None

def test_conn2user_notpresent():
    server = Server(host=None)
    setup_server(server)

    conn = Connection('asdfasdf', None)
    user = server.conn2user(conn)
    assert user is None

def test_create():
    server = Server(host=None)
    setup_server(server)

    conn = Connection('newconn', None)
    server._process_create(conn, 'newuser')
    assert len(server.users) == 4
    assert server.users[-1].username == 'newuser'

def test_create_failure():
    server = Server(host=None)
    setup_server(server)

    conn = Connection('newconn', None)
    server._process_create(conn, 'u2')
    assert len(server.users) == 3
    assert conn.send_buffer[-len('username already exists'):] == b'username already exists'

def test_list():
    server = Server(host=None)
    setup_server(server)

    conn = Connection('newconn', None)
    server._process_list(conn, None)
    assert conn.send_buffer[-12:] == b'u1|||u2|||u3'

def test_list_wildcard():
    server = Server(host=None)
    setup_server(server)

    conn = Connection('newconn', None)
    server._process_list(conn, '*1')
    assert conn.send_buffer[-2:] == b'u1'

def test_send_immediately():
    server = Server(host=None)
    setup_server(server)

    conn = server.connections[1]
    server._process_send(conn, [server.users[1].username, server.users[2].username, 'test message'])
    assert conn.send_buffer[-22:] == b'u2|||u3|||test message'
    assert server.users[2].connection.send_buffer[-22:] == b'u2|||u3|||test message'

def test_send_notlogged():
    server = Server(host=None)
    setup_server(server)

    conn = Connection('newconn', None)
    server._process_send(conn, [server.users[1].username, server.users[2].username, 'test message'])

    wp = WireProtocol()
    wp.parse_incoming_bytes(conn.send_buffer)
    assert wp.command == CMD.RESPONSE # indicates error

def test_send_imposter():
    server = Server(host=None)
    setup_server(server)

    conn = server.connections[0]
    server._process_send(conn, [server.users[1].username, server.users[2].username, 'test message'])

    wp = WireProtocol()
    wp.parse_incoming_bytes(conn.send_buffer)
    assert wp.command == CMD.RESPONSE # indicates error

def test_send_notexists():
    server = Server(host=None)
    setup_server(server)

    conn = server.connections[1]
    server._process_send(conn, [server.users[1].username, 'asdfasdfadf', 'test message'])

    wp = WireProtocol()
    wp.parse_incoming_bytes(conn.send_buffer)
    assert wp.command == CMD.RESPONSE # indicates error

def test_send_later():
    server = Server(host=None)
    setup_server(server)
    server.users[2].logout()

    conn = server.connections[1]
    server._process_send(conn, [server.users[1].username, server.users[2].username, 'test message'])
    assert conn.send_buffer[-22:] == b'u2|||u3|||test message' # should still send to the sender
    assert len(server.users[2].undelivered_messages) == 1
    assert server.users[2].undelivered_messages[0] == [server.users[1].username, server.users[2].username, 'test message']

def test_deliver_order():
    server = Server(host=None)
    setup_server(server)
    server.users[2].logout()

    # first send from u2 to u3
    conn = server.connections[1]
    server._process_send(conn, [server.users[1].username, server.users[2].username, 'test message!'])
    server._process_send(conn, [server.users[1].username, server.users[2].username, 'another test message'])

    # then login as u3 and get all the messages
    conn = server.connections[2]
    server.users[2].login(conn)

    assert len(server.users[2].undelivered_messages) == 2

    server._process_deliver(conn, None)

    wp = WireProtocol()
    wp.parse_incoming_bytes(conn.send_buffer)
    assert wp.command == CMD.SEND
    assert wp.data_buffer == b'u2|||u3|||test message!'
    
    remaining_bytes = wp.tmp_buffer
    wp.reset_buffers()
    wp.parse_incoming_bytes(remaining_bytes)
    assert wp.command == CMD.SEND
    assert wp.data_buffer == b'u2|||u3|||another test message'

def test_login():
    server = Server(host=None)
    setup_server(server)
    server.users[2].logout()

    conn = Connection('newconn', None)
    server._process_login(conn, server.users[2].username)
    wp = WireProtocol()
    wp.parse_incoming_bytes(conn.send_buffer)
    assert wp.command == CMD.RESPONSE
    assert wp.data_len == 0

def test_login_noaccount():
    server = Server(host=None)
    setup_server(server)
    server.users[2].logout()

    conn = Connection('newconn', None)
    server._process_login(conn, server.users[2].username+'asdfasdf')
    wp = WireProtocol()
    wp.parse_incoming_bytes(conn.send_buffer)
    assert wp.command == CMD.RESPONSE
    assert wp.data_len == len('username does not exist')
    assert wp.data_buffer == b'username does not exist'

def test_login_alreadylogged():
    server = Server(host=None)
    setup_server(server)

    conn = Connection('newconn', None)
    server._process_login(conn, server.users[2].username)
    wp = WireProtocol()
    wp.parse_incoming_bytes(conn.send_buffer)
    assert wp.command == CMD.RESPONSE
    assert wp.data_len == len('user is already logged in')
    assert wp.data_buffer == b'user is already logged in'
