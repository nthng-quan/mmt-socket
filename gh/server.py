import socket 
import threading 
import pyodbc

HOST = "127.0.0.1" 
SERVER_PORT = 65432
FORMAT = "utf8"

LOGIN = "login"
SIGNUP = "signup"

# --- SQL, Login credentials --- #

SERVER = "NTHQUAN\SQL19"
DATABASE = "SOCKET_ACCOUNT"
UID = "hquan"
PWD = "26102002"

# ------------------------------ #

def recvList(conn):
    list = []

    item = conn.recv(1024).decode(FORMAT)

    while (item != "end"):
        
        list.append(item)
        # response
        conn.sendall(item.encode(FORMAT))
        item = conn.recv(1024).decode(FORMAT)
    
    return list

def serverLogin(conn):
    # recv account from client
    client_account = recvList(conn)

    # query data: password
    try:
        cursor.execute("select PASSWRD from ACCOUNT where USERNAME = ?", client_account[0])

        password = cursor.fetchone()
        data_password = password[0]
        
        if (client_account[1] == data_password):
            msg = "> Login successfully !"

        else:
            msg = "> Invalid password !"

    except:
        print(client_account[0], client_account[1])
        msg = "> Error: Can't find username !"

    conn.sendall(msg.encode(FORMAT))

def serverSignup(conn):
    # recv account from client
    client_account = recvList(conn)

    # query data: password
    try:
        cursor.execute("select PASSWRD from ACCOUNT where USERNAME = ?", client_account[0])
        msg = "> Username's already existed !"
        print(msg)

    except:
        cursor.execute("insert ACCOUNT values (?, ?)", client_account[0], client_account[1])
        con_DB.commit()

        print(client_account[0], client_account[1])

        msg = "> Signup successfully !"
        print(msg)

    conn.sendall(msg.encode(FORMAT))

def handleClient(conn: socket, addr):
    
    print("conn:",conn.getsockname())
    
    msg = None
    
    while (msg != "x"):
        msg = conn.recv(1024).decode(FORMAT)
        print("client ",addr, "request", msg)

        if (msg == LOGIN):
            #response
            conn.sendall(msg.encode(FORMAT))
            serverLogin(conn)

        if (msg == SIGNUP):
            #response
            conn.sendall(msg.encode(FORMAT))
            serverSignup(conn)
    
    
    print("client" , addr, "finished")
    print(conn.getsockname(), "closed")
    conn.close()

# ----- MAIN ----- #

con_DB = pyodbc.connect(' DRIVER={ODBC Driver 17 for SQL Server};\
                        SERVER='+SERVER+';\
                        DATABASE='+DATABASE+';\
                        UID='+UID+';\
                        PWD='+PWD+';')

cursor = con_DB.cursor()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

s.bind((HOST, SERVER_PORT))
s.listen()

print("SERVER SIDE")
print("server:", HOST, SERVER_PORT)
print("Waiting for Client")

nClient = 0
while (nClient < 2):
    try:
        conn, addr = s.accept()
        
        thr = threading.Thread(target=handleClient, args=(conn,addr))
        thr.daemon = False
        thr.start()

    except:
        print("Error")
    
    nClient += 1


print("End")

s.close()
con_DB.close()