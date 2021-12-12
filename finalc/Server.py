import socket
import pyodbc
import threading

import pickle

import os
from io import BytesIO

from PIL import Image
from time import sleep

from config import *

countTotalClient = 0
countLiveClient  = 0

# -------------------------------- #

con_DB = pyodbc.connect ('\
    DRIVER={ODBC Driver 17 for SQL Server};\
    SERVER='+SERVER+';\
    DATABASE='+DATABASE+';\
    UID='+UID+';\
    PWD='+PWD+';'
)
cursor = con_DB.cursor()

server = socket.socket (
    socket.AddressFamily.AF_INET,
    socket.SocketKind.SOCK_STREAM
)
server.bind ((
    HOST,
    SERVER_PORT
))

server.listen()

def fetch_data(conn: socket):
    # execute query
    cursor.execute(
        'select * from Phonebook'
    )
    data = cursor.fetchall()

    # send query respose
    conn.sendall(GOOD.encode(FORMAT))
    conn.recv(1024) # receive response 1

    # initialize data
    max_rows = len(data)
    
    conn.sendall(str(max_rows).encode(FORMAT))
    conn.recv(1024) # receive response 2
   
    index = 0

    while (index < max_rows):
        data_to_bytes = pickle.dumps(data[index], pickle.HIGHEST_PROTOCOL)
        
        conn.sendall(data_to_bytes) # send data in bytes
        conn.recv(1024) # receive response 3
        
        sleep(0.001)

        index += 1

def save_all_images(conn: socket):
    # execute query
    try:
        cursor.execute(
            "select\
            Avatar,\
            FULLNAME from Phonebook"
        )
        data = cursor.fetchall()

        # send query respose
        conn.sendall(GOOD.encode(FORMAT))
        conn.recv(1024) # receive response 1

        # initialize data
        max_rows = len(data)
        conn.sendall(str(max_rows).encode(FORMAT))

        conn.recv(1024) # receive response 2
        index = 0

        while (index < max_rows):
            data_to_bytes = pickle.dumps(data[index], pickle.HIGHEST_PROTOCOL)
            conn.sendall(data_to_bytes) # send data in bytes
            conn.recv(1024) # receive response 3
            
            sleep(0.001)

            index += 1

    except Exception as e:
        print("Error: unable to fetch data -> ", e)

def find_by_id(conn: socket):
    # receive ID
    id_to_search = conn.recv(1024).decode(FORMAT)
    conn.send(id_to_search.encode(FORMAT)) # response 1
    
    # database exec
    cursor.execute(
        "select * from\
        Phonebook where\
        ID = ?",

        id_to_search
    )
    data = cursor.fetchone()
    
    # if cant find data
    if (data == None):
        msg = FAIL
        # send fail message
        conn.send(msg.encode(FORMAT))
        conn.recv(1024) # receive response
        return
    
    # if found data
    msg = SUCCESS
    # send success message
    conn.send(msg.encode(FORMAT))
    conn.recv(1024).decode(FORMAT) # receive response

    data_to_bytes = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
    conn.send(data_to_bytes) # send data in bytes
    
    # receive response
    conn.recv(1024).decode(FORMAT)

def check_valid_phone_number(conn: socket):
    phone_number = conn.recv(1024).decode(FORMAT)
    conn.send(phone_number) # response 1

    cursor.execute (
        "select \
        ID from \
        Phonebook where\
        Phonenumber=?",

        phone_number
    )
    
    data = cursor.fetchone()

    if (data == None):
        msg = GOOD
    else:
        msg = FAIL
    
    conn.sendall(msg.encode(FORMAT))

def serverStatus():
    print("# ------------------------------------------------------------ #")
    print("- Server:", HOST, SERVER_PORT)
    print("- Total Client handled:", countTotalClient)
    print("- Client live:", countLiveClient)
    print("# ------------------------------------------------------------ #")

def serverClose():
    print("\n# ------------------------------------------------------------ #")
    print("- [SERVER CLOSED]")
    print("- Server:", HOST, SERVER_PORT)
    print("- Client:", countTotalClient)
    print("# ------------------------------------------------------------ #")

def handleClient(conn: socket, addr: tuple):
    global countLiveClient

    print("|> [CLIENT_CONNECT] ", addr, "has connected to the server!")
    
    serverStatus()
    
    request = None

    while True:
        request = conn.recv(1024).decode(FORMAT)
        print("-  Client ", addr, "request", request)
        
        if (request == CHECK):
            conn.sendall(request.encode(FORMAT))
            check_valid_phone_number(conn)
        
        if (request == FIND_BY_ID):
            conn.sendall(request.encode(FORMAT))
            find_by_id(conn)

        if (request == FETCH_DATA):
            conn.sendall(request.encode(FORMAT))
            fetch_data(conn)

        if (request == SAVE_ALL_IMGS):
            conn.sendall(request.encode(FORMAT))
            save_all_images(conn)

        if (request == DISCONNECT):
            countLiveClient -= 1
            conn.sendall(request.encode(FORMAT))

            break
    
    print("Client" , addr, "finished")
    print("\n|> [CLIENT_DISCONNECT]", addr, "has disconnected !")

    serverStatus()
    conn.close()

def runServer():
    global countTotalClient
    global countLiveClient

    print("[SERVER SIDE - LOGs]")
    print("- Server:", HOST, SERVER_PORT)
    print("> Server Ready")
    print("> Waiting for Client...\n")

    try:
        while True:
            conn, addr   = server.accept()
            
            clientThread = threading.Thread (
                target   = handleClient,
                args     = (conn, addr)
            )
            
            clientThread.daemon = False
            clientThread.start()
            
            countTotalClient += 1
            countLiveClient  += 1

    except Exception as error:
        print("|> Error ->", error)
        serverClose()

        server.close()
    
    finally:
        serverClose()
        serverStatus()

        server.close()
        
if __name__ == "__main__":
    runServer()