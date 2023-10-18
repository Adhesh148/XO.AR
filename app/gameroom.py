import socket
import threading
import time
import sys

# Let us define constant parameters
MAX_LEN = 64
PORT = 9001
SERVER = "127.0.0.1"
ADDR = (SERVER,PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "!END"

# Global variables
client_list = []
client_names = []
player_info = []

# Create server socket
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(ADDR)

# handle client
def handle_client(conn,addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    # receive username
    username = conn.recv(1024).decode(FORMAT)
    print(username)
    indx = client_list.index(conn)
    client_names[indx] = username

    # send wlcm message
    broadcast_wlcm(conn)

    connected = 1
    while connected:
        # receive message from client
        msg = conn.recv(4096).decode(FORMAT)
        print(msg)
        if(msg == DISCONNECT_MSG):
            closeConnection(conn)
            sys.exit()
        else:
            broadcast(msg,conn)

def closeConnection(conn):
    indx = client_list.index(conn)
    sender = client_names[indx]
    msg = "************ " + sender + " has left the Game Room. **************"
    for clients in client_list:
        if(clients != conn):
            clients.send(msg.encode(FORMAT))
    client_list.pop(indx)
    client_names.pop(indx)
    conn.close()

def broadcast_wlcm(conn):
    sender = client_names[client_list.index(conn)]
    conn_msg = "************* You have joined the Tic Tac Toe Game Room *****************"
    rest_msg = "************ " + sender + " has joined the Tic Tac Toe Game Room. **************"
    for clients in client_list:
        if(clients == conn):
            clients.send(conn_msg.encode(FORMAT))
        else:
            clients.send(rest_msg.encode(FORMAT))

def broadcast(message,conn):
    # Send msg to other client
    for client in client_list:
    	if client != conn:
        	client.send(message.encode(FORMAT))

# start server
def init_server():
    # start listening
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while len(client_list)!=2:
        conn,addr = server.accept()         
        client_list.append(conn)
        client_names.append("player")
        thread = threading.Thread(target=handle_client,args=(conn,addr))
        thread.start()

    # Setup the Game for the two clients - Send Game Info
    time.sleep(0.5)
    
    # First Player: Player: 'X'; Turn: 1 (Plays First)
    msg = 'player: x'
    client_list[0].send(msg.encode(FORMAT))

    # Second Player: Player: 'O'; Turn: 0 (Moves Second)
    msg = 'player: o'
    client_list[1].send(msg.encode(FORMAT))

    while len(client_list) == 2:
    	continue

    server.close()

init_server()