import socket
import threading 
import pyodbc
import pickle

import os,io
from io import BytesIO

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog, messagebox, Frame

from PIL import Image, ImageTk

HOST = "127.0.0.1" 
SERVER_PORT = 65432
FORMAT = "utf8"

LOGIN = "login"
SIGNUP = "signup"

FAIL = "fail"
GOOD = "good"
SUCCESS = "success"

# ---------- DB request ---------#

FIND_BY_ID = "find_by_id"
SAVE_ALL_IMGS = "save_all_imgs"
INSERT = "insert"
FETCH_DATA = "fetch_data"
CHECK = "check"
DISCONNECT = "disconnect"
HALT = "halt"

# --- SQL, Login credentials --- #

SERVER = "WINDOWS\SQL19"
DATABASE = "SOCKET_ACCOUNT"
UID = "hquan"
PWD = "26102002"

# ------------------------------ #
def fetch_data(conn):
    # execute query
    cursor.execute("select * from Phonebook")
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
        index += 1

def save_all_images(conn):
    # execute query
    try:
        cursor.execute("select Avatar, FullName from Phonebook")
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

            index += 1
    except Exception as e:
        messagebox.showinfo("Error: unable to fetch data", e)

def find_by_id(conn):
    # receive ID
    id_to_search = conn.recv(1024).decode(FORMAT)
    conn.send(id_to_search.encode(FORMAT)) # response 1
    
    # database exec
    cursor.execute("select * from PHONEBOOK where ID = ?", id_to_search)
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

def check_valid_phone_number(conn):
    phone_number = conn.recv(1024).decode(FORMAT)
    cursor.execute("select id from PHONEBOOK where PHONENUMBER = ?", phone_number)
    
    data = cursor.fetchone()
    if (data == None):
        msg = "valid"
    else:
        msg = "invalid"
    
    conn.sendall(msg.encode(FORMAT))

def handleClient(conn: socket, addr):
    
    print("* [CLIENT_CONNECT]: ",conn.getsockname())
    
    request = None
    while True:
        request = conn.recv(1024).decode(FORMAT)
        print("client ",addr, "request", request)
        
        if (request == CHECK):
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
            conn.sendall(request.encode(FORMAT))
            break
    
    print("Client" , addr, "finished")
    print("*** [CLIENT_DISCONNECT]",conn.getsockname(), "closed !")
    conn.close()

# ----- MAIN ----- #

con_DB = pyodbc.connect('\
    DRIVER={ODBC Driver 17 for SQL Server};\
    SERVER='+SERVER+';\
    DATABASE='+DATABASE+';\
    UID='+UID+';\
    PWD='+PWD+';'
)
cursor = con_DB.cursor()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

s.bind((HOST, SERVER_PORT))
s.listen()

print("SERVER SIDE")
print("server:", HOST, SERVER_PORT)
print("Waiting for Client")

countClient = 0

while TRUE:
    try:
        conn, addr = s.accept()
        thr = threading.Thread(target=handleClient, args=(conn,addr))
        thr.daemon = False
        thr.start()

    except:
        print("Error")

    countClient += 1

print("End")

s.close()
con_DB.close()