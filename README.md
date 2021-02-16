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
 ```python
 conda create --name chatenv python=3.7
 ```
 followed by
 ```python
 conda activate chatenv
 ```
(to exit simply type `conda deactivate`).

Once dependencies are in order, the first thing to do is check the configuration parameters in `config.py`---in particular, those for the server address. If you are hosting both client and server on your local machine, then the default `HOST` and `PORT` should suffice; otherwise set them to the server address of your choosing, and ensure that this config file server address is the same for all client and server environments which you would like to have communicate with one another.


To begin chatting, first run
```python
python3 server.py
```
to start the server (on the server machine), followed by
```python
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
TODO
