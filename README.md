# Chat Bot!

![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview
This is a chat client and server written for the wire protocols assignment in the spring 2021 instantiation of CS262: Introduction to Distributed Systems.
It is written in Python, with an application-specific wire protocol for passing messages and commands between client and server.
It is designed to track users and messages only so long as the chat server is running, though multiple clients may connect and disconnect using the same or different accounts.


## Getting Up and Running
We'll need Python 3.7.

An easy way to manage dependencies is to maintain a virtual environment for all machines which will be running the client or the server.
Although it's perhaps overkill, for this purpose we recommend [installing conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

Once `conda` is installed, it can be used to create an environment by running
 ```bash
 conda create --name chatenv python=3.7
 ```
 followed by
 ```bash
 conda activate chatenv
 ```
(to exit simply type `conda deactivate`).

Once dependencies are in order, the first thing to do is check the configuration parameters in `config.py`---in particular, those for the server address. If you are hosting both client and server on your local machine, then the default `HOST` and `PORT` should suffice; otherwise set them to the server address of your choosing, and ensure that this config file server address is the same for all client and server environments which you would like to have communicate with one another.


To begin chatting, first run
```bash
python3 server.py
```
to start the server (on the server machine), followed by
```bash
python3 client.py
```
to start each client (on each client machine).

Once you're done, client processes will terminate after receiving `logout` or `delete account` commands. The server process will run until it is terminated manually.

## Wire Protocol

The wire protocol is made up of two components: the actual protocol for the distribution of bits over the wire and the protocol for understanding the format of the data.

### Bits on the wire

Each message is a command, consisting of the following components:

`VERSION_LEN` bytes (1)
- version number, messages must match the current version

`COMMAND_LEN` bytes (1)
- indicates the command, defined in `CMD`

`DATALENGTH_LEN` bytes (40)
- length of the following data, in bytes, interpreted as an int

`data_len` bytes (variable)
- ascii string containing the data


Integer components (version, command, data length) are interpreted in the big endian format

### Commands

The wire protocol supports the following commands:

`CREATE` - Create an account. Data: username

`LIST` - Lists existing accounts. Data: (optional) filter, can include wildcard *

`SEND` - Send a message. Data: sender username, recipient username, message

`DELIVER` - Deliver undelivered messages. Data: None

`DELETE` - Delete the current account (and logout). Data: None

`LOGIN` - Login to an existing account. Data: username

`RESPONSE` - Response from server. Data: (optional) error message

`LISTRESPONSE` - Response to `LIST`. Data: list of usernames


### Data format

Data is understood to be a list a ascii strings. Only ascii characters are allowed. Data is optional, some commands like DELIVER take no data and some commands like LIST take an optional argument. Other commands take multiple arguments. The number of strings can range from 0 to arbitrarily large. The entire encoded data must have a length which can be represented in 40 bytes, thus it is capped at 256^40, which should be sufficient.

The list items are delimited by a string, currently "|||"


## Basic Usage
The client's interface consists of two main modes: a login mode, in which the user either logs in, creates an account, or exits; and a 'main loop' within which the user receives any incoming messages and has the ability to list users, compose a message, receive stored messages, delete their account, or logout.

As an example, here is a conversation between users Alicia and Bobert. They each log in and write back and forth. Partway through the conversation Bobert logs out, logs in, and checks his messages.

### Alicia's screen:
Login loop:
```bash
(chatenv) aliciacomp chatbot % python3 client.py                      
Commands: login, create_account, quit
login
Username: Alicia
Username not recognized.
Commands: login, create_account, quit
create_account
Username: Alicia
Logged in as: Alicia
```
Main loop:
```bash
Commands: help (h), compose (c), list users (l), get messages (g), delete account (d), logout (q)
l
Search pattern (optional): *
Accounts:
	Bobert
	Alicia
c
Recipient: Bobert
Message: Salutations, Bobert. Is it snowy where you are?
Send? (y/n): y
Sent to Bobert:
Salutations, Bobert. Is it snowy where you are?

New message from Bobert:
Hey Alicia, yes it is very snowy. I am worried I may lose power.

c
Recipient: Bobert
Message: Dont worry, ERCOT is a very reliable.     
Send? (y/n): y
Sent to Bobert:
Dont worry, ERCOT is a very reliable.

c
Recipient: Bobert
Message: Are you still there?
Send? (y/n): y
Sent to Bobert:
Are you still there?

q
(chatenv) aliciacomp chatbot %
```
### Bob's screen:
Startup and account creation:
```bash
(chatenv) bobertcomp chatbot % python3 client.py
Commands: login, create_account, quit
create_account  
Username: Bobert
Logged in as: Bobert
```
Main loop:
```bash
Commands: help (h), compose (c), list users (l), get messages (g), delete account (d), logout (q)
New message from Alicia:
Salutations, Bobert. Is it snowy where you are?

c
Recipient: Alicia
Message: Hey Alicia, yes it is very snowy. I am worried I may lose power.    
Send? (y/n): y
Sent to Alicia:
Hey Alicia, yes it is very snowy. I am worried I may lose power.

q
```
Restart and login:
```bash
(chatenv) bobertcomp chatbot % python3 client.py
Commands: login, create_account, quit
login
Username: Bobert
Logged in as: Bobert
```
Main loop:
```bash
Commands: help (h), compose (c), list users (l), get messages (g), delete account (d), logout (q)
g
New message from Alicia:
Dont worry, ERCOT is a very reliable.

New message from Alicia:
Are you still there?

c
Recipient: Alicia
Message: Sorry, power went out. Back online now!
Send? (y/n): y
Sent to Alicia:
Sorry, power went out. Back online now!

c
Recipient: Alicia
Message: Hello?
Send? (y/n): y
Sent to Alicia:
Hello?

q
(chatenv) bobertcomp chatbot %
```
Since Alicia logged out before Bobert logged back in, Bobert's last two messages will be waiting for her when she next logs in.

## Notebook

### High level design

Much of the design ended up being focused around delivering undelivered messages. In general chat applications can take many different forms (e.g. FB Messenger, Slack, text messages, phone conversations), but we wanted to match the specification including a notion of there being "logged in". At first we were thinking about a polling solution in which clients periodically polled the server for any messages, which was elegant because clients can go off or on without the server knowing or caring, but didn't match the specification of a notion of being "logged in."

Finally, early on it was clear that all communication would have to go through the server, instead of clients talking directly with each other. The latter would require much greater complexity and would be much less robust.

### Server

We found that a more natural way that led to a notion of users being logged in or out was to keep sockets open for logged in users. When a socket closes that means the user has logged out. This required us to separately store information about the list of users the server knows about, logged in or not, and the list of currently open connections. To facilite conversation, these had to be linked through the `User.connection` field.

One of the main design choices was how to handle multiple client conenctions. We decided to go with `select` over multiprocessing because it seemed like `select` did all of the heavy lifting for us, and avoided ugly problems that could arise from multiprocessing. It also naturally fit with out idea of a `Connection` object, as `select` maintains uuids which are associated with `Connection`s. This way, anything that needs to be written can be written to a buffer on the `Connection`, and when the given socket is ready to send it can flush out of that buffer.

These choices fully determined the structure of `Server`, implementing the control flow was just a matter of implementing the logic for each of the commands. Also, given these choices, it was natural for the user object to own the list of undelivered messages, and therefore it made sense that when the user object was deleted because the account was delete these undelivered messages were discarded.

### Client

The main challenge we faced with the client was how to handle both listening for messages from the server and listening for keyboard input, as these are both functions that typically block. Specifically, it was really hard to figure out how to print incoming messages to the terminal while expecting user input and composition. After trying out a few ideas we settled on a model where the user types a key followed by enter to send a command to the server. This enters a compose mode where server messages are held in a queue and not printed to the screen until the compose mode is closed.

The other main design choice was to have both the sender and receiver receive the message sent from the sender. The message includes sender and receiver metadata, so the client can figure out if the message from the server is one it sent or received. Having the sender wait to print the message until it receives it back from the server greatly simplifies the logic, and ensures that all parties agree on the order of messages.


### Wire Protocol

We wanted to abstract away as much of the detail of the wire protocol as possible from the rest of the application. Given that we were using both blocking and non-blocking sockets, however, we found that the highest level of abstraction we could reach was a class that was responsible for ingesting potentially partial messages and keeping track of how much of an expected message it had parsed.

It was natural for the `WireProtocol` class to also perform the reverse operation, converting structured data into a byte string, and for it to further parse the data into a list of string arguments.

As far as the design of the protocol itself, it represents what we believe to be the minimum requirements for the application. Unlike a more general protocol like JSON, for the chat application all communication between the client and the server comes in the form of commands. There are only a handful of commands so it made sense to encode the command in a single byte. The message, on the other hand, could potentialy be quite large, so we opted for a variable length representation. Technically this leads to a upper limit on the message size, but given that we have 40 bytes to encode the message length one would have to be sending petabytes over the wire for this to be a problem.
