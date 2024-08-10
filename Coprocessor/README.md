# Coprocessor
This directory contains everything that will be run on your coprocessor of choice.

## Installation
To install all dependencies for the coprocessor, clone this repository on the coprocessor, then run the following command in this directory on the coprocessor:
```pip install -r requirements.txt```


## Overview
The ----vision processing software---- has two ends, a server, usually the coprocessor, and a client, usually the driver 
station. The server is responsible for processing the image and sending the results to the client. The client is 
responsible for interacting with the server in a UI. The server and client communicate over an ethernet connection. 
The server is started by running the `main.py` script in the `Coprocessor` directory. The client is started by running 
the `main.py` script in the `Client` directory. The server hosts a websocket server for each camera connected to it,
starting with port 50000. Each camera has its own process and handles requests independently. There is no main socket
to send general commands to. The client will connect to the server and send bash-style commands to the server. The 
server will then reply with either a bytes object or a json string.
