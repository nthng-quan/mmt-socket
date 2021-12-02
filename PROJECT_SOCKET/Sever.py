import socket 
import threading 
import pyodbc

HOST = "127.0.0.1" 
SERVER_PORT = 65432
FORMAT = "utf8"

LOGIN = "login"
SIGNUP = "signup"
FAIL = "fail"
OK = "ok"
END = "x"

# --- SQL, Login credentials --- #

SERVER = "DESKTOP-CFB5BC2\SQLEXPRESS"
DATABASE = "Socket_Account"
UID = "ht"
PWD = "123456" 

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

def serverLogin(conn: socket):
    # recv account from client
    user = conn.recv(1024).decode(FORMAT)
    conn.sendall(user.encode(FORMAT))
    pswd = conn.recv(1024).decode(FORMAT)
    conn.sendall(pswd.encode(FORMAT))
    print(user, pswd)

    # query data: password
    
    cursor.execute("select pass from Account where username = ?", user)
    
    password= cursor.fetchone()
    print(password)
    data_password = password[0]


    # verify login
    msg = OK
    if (pswd == data_password):
        msg = OK
        print(msg)

    else:
        msg = FAIL
        print(msg)

 
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
    
    option = conn.recv(1024).decode(FORMAT)
    print(option)
    count = 0
    while (count < 50):

        if (option == LOGIN):
            serverLogin(conn)
            option = "x"
        
        count += 1
    
    
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
s.listen(1)

print("SERVER SIDE")
print("server:", HOST, SERVER_PORT)
print("Waiting for Client")

nClient = 0
while (nClient < 3):
    try:
        conn, addr = s.accept()
        
        thr = threading.Thread(target=handleClient, args=(conn,addr))
        thr.daemon = False
        thr.start()

    except:
        print("Error")
    
    nClient += 1


print("End")

input()
s.close()
con_DB.close()