import socket
import pyodbc
import threading

import pickle

import os
from io import BytesIO

import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *

from PIL import Image
from time import sleep

# ------------ Socket ------------ #

SERVER_IP     = '0.0.0.0'
SERVER_PORT   = 27603
FORMAT        = "utf8"

# ---------- DB protocol --------- #

FIND_BY_ID    = "find_by_id"
SAVE_ALL_IMGS = "save_all_imgs"
FETCH_DATA    = "fetch_data"
CHECK         = "check"
DISCONNECT    = "disconnect"

FAIL          = "fail"
GOOD          = "good"
SUCCESS       = "success"
CHECKIN       = "checkin"

# ------------ DB info ----------- #

TABLE_NAME    = "Phonebook"
ID            = "ID"
AVATAR        = "Avatar"
FULLNAME      = "FullName"
PHONENUMBER   = "Phonenumber"
EMAIL         = "Email"

# ---- SQL, Login credentials ---- #

# Azure SQL DB
# SERVER        = "socket-skrt.database.windows.net"
# DATABASE      = "SocketProject"
# UID           = "nthquan"
# PWD           = "socket123#"

# # Local DB
# SERVER        = "Laptop"
# DATABASE      = "SOCKET_ACCOUNT"
# UID           = "hquan"
# PWD           = "26102002"

# --------- Count client --------- #

countTotalClient = 0
countLiveClient  = 0

# -------------------------------- #

def fetch_data(conn: socket, cursor):
    # execute query
    cursor.execute(
        'select * from Phonebook'
    )
    data = cursor.fetchall()
    sleep(0.001)
    # data = selectall()
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
        # sleep(0.001)
        # conn.recv(1024) # receive response 3

        status = conn.recv(1024).decode(FORMAT) # receive response 3
        if (status == FAIL):
            break
        else:
            pass

        index += 1

def save_all_images(conn: socket, cursor):
    # execute query
    try:
        cursor.execute(
            "select\
            Avatar,\
            FULLNAME from Phonebook"
        )
        data = cursor.fetchall()
    
    except Exception as e:
        print("Error: unable to fetch data -> ", e)

        return

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

def find_by_id(conn: socket, cursor):
    # receive ID
    id_to_search = conn.recv(1024).decode(FORMAT)
    conn.send(id_to_search.encode(FORMAT)) # response 1
    
    # database exec

    try:
        cursor.execute(
            "select * from\
            Phonebook where\
            ID = ?",

            id_to_search
        )
        data = cursor.fetchone()

    except:
        msg = FAIL
        # send fail message
        conn.send(msg.encode(FORMAT))
        conn.recv(1024) # receive response

        return
    
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

def check_valid_phone_number(conn: socket, cursor):
    phone_number = conn.recv(1024).decode(FORMAT)
    conn.send(phone_number) # response 1

    try:
        cursor.execute (
            "select \
            ID from \
            Phonebook where\
            Phonenumber=?",

            phone_number
        )
        
        data = cursor.fetchone()
        
    except:
        msg = FAIL
        # send fail message
        conn.send(msg.encode(FORMAT))
        conn.recv(1024)

        return

    if (data == None):
        msg = GOOD
    else:
        msg = FAIL
    
    conn.sendall(msg.encode(FORMAT))

def serverStatus():
    print("# ------------------------------------------------------------ #")
    print("- Server:", SERVER_IP, "| Port:", SERVER_PORT)
    print("- Total Client handled:", countTotalClient)
    print("- Client live:", countLiveClient)
    print("# ------------------------------------------------------------ #")

def serverClose():
    print("\n# ------------------------------------------------------------ #")
    print("- [SERVER CLOSED]")
    print("- Server:", SERVER_IP, SERVER_PORT)
    print("- Client:", countTotalClient)
    print("# ------------------------------------------------------------ #")

def handleClient(conn: socket, addr: tuple, cursor):
    global countLiveClient
    global countTotalClient

    print("|> [CLIENT_CONNECT] ", addr, "has connected to the server!")
    
    serverStatus()
    
    request = None

    while True:
        request = conn.recv(1024).decode(FORMAT)
        print("-  Client ", addr, "request", request)
        
        if (request == CHECK):
            conn.sendall(request.encode(FORMAT))
            check_valid_phone_number(conn, cursor)
        
        if (request == FIND_BY_ID):
            conn.sendall(request.encode(FORMAT))
            find_by_id(conn, cursor)

        if (request == FETCH_DATA):
            conn.sendall(request.encode(FORMAT))
            fetch_data(conn, cursor)

        if (request == SAVE_ALL_IMGS):
            conn.sendall(request.encode(FORMAT))
            save_all_images(conn, cursor)

        if (request == CHECKIN):
            countLiveClient -= 1
            countTotalClient -= 1

            conn.sendall(request.encode(FORMAT))

            conn.close()

            return

        if (request == DISCONNECT):
            countLiveClient -= 1
            conn.sendall(request.encode(FORMAT))

            break
    
    print("Client" , addr, "finished")
    print("\n|> [CLIENT_DISCONNECT]", addr, "has disconnected !")

    serverStatus()
    conn.close()

def runServer(cursor):
    global countTotalClient
    global countLiveClient

    # create socket
    try:
        server = socket.socket (
            socket.AddressFamily.AF_INET,
            socket.SocketKind.SOCK_STREAM
        )
        server.bind ((
            SERVER_IP,
            SERVER_PORT
        ))

        server.listen(5)
    except Exception as connect_error:
        messagebox.showerror(
            "Error",
            connect_error
        )

        return
        
    print("[SERVER SIDE - LOGs]")
    print("- Server:", SERVER_IP, SERVER_PORT)
    print("> Server Ready")
    print("> Waiting for Client...\n")

    try:
        while True:
            conn, addr   = server.accept()
            
            clientThread = threading.Thread (
                target   = handleClient,
                args     = (conn, addr, cursor)
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

class ServerConfiguration(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args, **kwargs)
        
        self.title("Server configuration")
        self.iconbitmap('app_icon.ico')
        self.geometry("500x500")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(0,0)

        label_title = tk.Label(
            self,
            text   = "\nSERVER CONFIG",
            font   = ("Arial", 20)
        ).grid (
            row    = 0,
            column = 1
        )

        label_ip_address = tk.Label(
            self,
            text   = "\tIP Address\n",
            font   = 'verdana 10 bold'
        ).grid (
            row    = 1,
            column = 0)

        label_server_port = tk.Label(
            self,
            text   = "\tPORT ",
            font   = 'verdana 10 bold'
        ).grid (
            row    = 2,
            column = 0
        )

        label_server_DB = tk.Label(
            self,
            text   = "\tDB Server ",
            font   = 'verdana 10 bold'
        ).grid (
            row = 3,
            column = 0
        )
        label_name_DB = tk.Label(
            self,
            text   = "\tDatabase: ",
            font   = 'verdana 10 bold'
        ).grid (
            row = 4,
            column = 0
        )
        label_uid_DB = tk.Label(
            self,
            text   = "\tUsername: ",
            font   = 'verdana 10 bold'
        ).grid (
            row = 5,
            column = 0
        )
        label_pwd_DB = tk.Label(
            self,
            text   = "\tPassword: ",
            font   = 'verdana 10 bold'
        ).grid (
            row = 6,
            column = 0
        )

        label_confirm_DB = tk.Label(
            self,
            text   = "\tChoose DB: ",
            font   = 'verdana 10 bold'
        ).grid (
            row = 7,
            column = 0
        )

        self.entry_ip_address = tk.Entry(
            self,
            width = 30
        )
        self.entry_server_port = tk.Entry(
            self,
            width = 30
        )

        self.entry_server = tk.Entry(
            self,
            width = 30
        )
        self.entry_server.insert(tk.END, "Laptop")
        
        self.entry_db = tk.Entry(
            self,
            width = 30
        )
        self.entry_db.insert(tk.END, "SOCKET_ACCOUNT")
        
        self.entry_user = tk.Entry(
            self,
            width = 30
        )
        self.entry_user.insert(tk.END, "hquan")

        self.entry_pwd = tk.Entry(
            self,
            width = 30
        )
        self.entry_pwd.insert(tk.END, "26102002")

        # BUTTON RUN SERVER
        
        button_run_server = tk.Button(
            self,
            text    = "RUN",
            command = lambda: self.click_btn_run_server()
        )
        # IP AUTO FILL BUTTONS

        button_ip_default = tk.Button(
            self,
            text    = "Default IP",
            command = lambda: self.set_ip_default()
        )

        button_ip_loopback = tk.Button(
            self,
            text    = "Loopback IP",
            command = lambda: self.set_ip_loopback()
        )
        button_PC_IP = tk.Button(
            self,
            text    = "Your IP",
            command = lambda: self.set_ip_this()
        )
        button_local_DB = tk.Button(
            self,
            text    = "Local DB",
            command = lambda: self.set_DB_local()
        )
        button_Azure_DB = tk.Button(
            self,
            text    = "Azure DB",
            command = lambda: self.set_DB_Azure()
        )

        # buttons configs
        button_width = 20
        button_order = 7

        button_local_DB.grid(
            row    = button_order + 0,
            column = 1
        )
        button_local_DB.configure(
            width  = button_width
        )

        button_Azure_DB.grid(
            row    = button_order + 1,
            column = 1,
            pady = 10
        )
        button_Azure_DB.configure(
            width  = button_width
        )

        button_ip_default.grid(
            row    = button_order + 2,
            column = 1
        )
        button_ip_default.configure(
            width  = button_width
        )

        button_ip_loopback.grid(
            row    = button_order + 3,
            column = 1
        )
        button_ip_loopback.configure(
            width  = button_width
        )

        button_PC_IP.grid(
            row    = button_order + 4,
            column = 1
        )
        button_PC_IP.configure(
            width  = button_width
        )

        button_run_server.grid(
            row    = button_order + 5,
            column = 1
        )
        button_run_server.configure(
            width  = button_width
        )

        self.entry_ip_address.grid(
            row    = 1,
            column = 1
        )
        self.entry_server_port.grid(
            row    = 2,
            column = 1,
            pady = 20
        )

        self.entry_server.grid(
            row = 3,
            column = 1,
            pady = 5
        )
        self.entry_db.grid(
            row = 4,
            column = 1,
            pady = 5
        )
        self.entry_user.grid(
            row = 5,
            column = 1,
            pady = 5
        )
        self.entry_pwd.grid(
            row = 6,
            column = 1,
            pady = 5
        )

        messagebox.showinfo(
            "Friendly reminder !",
            "You must confirm your DB credentials"
        )

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def set_DB_Azure(self):
        global SERVER
        global DATABASE
        global UID
        global PWD

        SERVER        = "socket-skrt.database.windows.net"
        DATABASE      = "SocketProject"
        UID           = "nthquan"
        PWD           = "socket123#"

        global con_DB
        global cursor

        try:
            con_DB = pyodbc.connect ('\
                DRIVER={ODBC Driver 17 for SQL Server};\
                SERVER='+SERVER+';\
                DATABASE='+DATABASE+';\
                UID='+UID+';\
                PWD='+PWD+';'
            )
            cursor = con_DB.cursor()
        except:
            messagebox.showerror(
                "Error",
                "Can't connect to DB!"
            )
            return

        messagebox.showinfo(
            "Success",
            "Connected to Azure DB!"
        )

        print("- Using DB:")
        print(SERVER)
        print(DATABASE)
        print(UID)
        print(PWD)
        print("\n")



    def set_DB_local (self):
        global SERVER
        global DATABASE
        global UID
        global PWD

        _server = self.entry_server.get()
        _database = self.entry_db.get()
        _uid = self.entry_user.get()
        _pwd = self.entry_pwd.get()

        if(_server == "" or _database == "" or _uid == "" or _pwd == ""):
            messagebox.showerror(
                "Error",
                "Please fill all the entry!"
            )

            return

        else:
            SERVER      = _server
            DATABASE    = _database
            UID         = _uid 
            PWD         = _pwd

        global con_DB
        global cursor

        try:
            con_DB = pyodbc.connect ('\
                DRIVER={ODBC Driver 17 for SQL Server};\
                SERVER='+SERVER+';\
                DATABASE='+DATABASE+';\
                UID='+UID+';\
                PWD='+PWD+';'
            )
            cursor = con_DB.cursor()
        except:
            messagebox.showerror(
                "Error",
                "Can't connect to DB, please check your input!"
            )
            return
        
        messagebox.showinfo(
            "Success",
            "Connected to local DB!"
        )

        print("- Using DB:")
        print(SERVER)
        print(DATABASE)
        print(UID)
        print(PWD)
        print("\n")
        
    def set_ip_default(self):
        ip_default = "0.0.0.0"
        default_port = "27603"

        self.entry_ip_address.delete(
            0,
            tk.END
        )
        self.entry_ip_address.insert(
            0,
            ip_default
        )

        self.entry_server_port.delete(
            0,
            tk.END
        )
        self.entry_server_port.insert(
            0,
            default_port
        )

    def set_ip_loopback(self):
        ip_loopback = "127.0.0.1"
        default_port = "27603"

        self.entry_ip_address.delete(
            0,
            tk.END
        )
        self.entry_ip_address.insert(
            0,
            ip_loopback
        )

        
        self.entry_server_port.delete(
            0,
            tk.END
        )
        self.entry_server_port.insert(
            0,
            default_port
        )

    def set_ip_this(self):
        ip_this = socket.gethostbyname(socket.gethostname())
        default_port = "27603"

        self.entry_ip_address.delete(
            0,
            tk.END
        )
        self.entry_ip_address.insert(
            0,
            ip_this
        )

        self.entry_server_port.delete(
            0,
            tk.END
        )
        self.entry_server_port.insert(
            0,
            default_port
        )

    def click_btn_run_server(self):
        global SERVER_IP
        global SERVER_PORT

        ip_entry = self.entry_ip_address.get()
        port_entry = self.entry_server_port.get()

        global SERVER
        global DATABASE
        global UID
        global PWD

        try:
            if(SERVER == "" or DATABASE == "" or UID == "" or PWD == ""):
                messagebox.showerror(
                    "Database missing",
                    "Please choose a DB !"
                )

                return
        except:
            messagebox.showerror(
                "Database missing",
                "Please choose or confirm a DB !"
            )

            return

        if (ip_entry == "" or port_entry == ""):
            messagebox.showerror(
                "Error",
                "Please fill IP Address and Port"
            )
            return

        SERVER_IP = ip_entry
        SERVER_PORT = int(port_entry)

        
        server = socket.socket (
            socket.AddressFamily.AF_INET,
            socket.SocketKind.SOCK_STREAM
        )

        try:
            server.bind ((
                SERVER_IP,
                SERVER_PORT
            ))
            server.close()

            messagebox.showinfo (
                "Success",
                "Server is running"
            )
        

        except Exception as connection_error:

            messagebox.showerror(
                "Error",
                connection_error
            )

            return

        self.destroy()
        runServer(cursor)

def main():
    app = ServerConfiguration()
    app.mainloop()

if __name__ == "__main__":
    main()