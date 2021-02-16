# Chat Bot!

![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

##Overview
This is a chat client and server written for the wire protocols assignment in the spring 2021 instantiation of CS262: Introduction to Distributed Systems.
It is written in Python, with an application-specific wire protocol for passing messages and commands between client and server.
It is designed to track users and messages only so long as the chat server is running, though multiple clients may connect and disconnect using the same or different accounts.


## Getting Up and Running
We'll need Python 3.7.

An easy way to manage dependencies is to maintain a virtual environment for all machines which will be running the client or the server.
For this purpose we recommend [installing conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

Once `conda` is installed, it can be used to create an environment <!--from `environment.yml` by calling

```python
conda env create -f environment.yml
```
 -->
 by running
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

## Basic Usage
TODO
