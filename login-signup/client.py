import socket

HOST = "127.0.0.1"
SERVER_PORT = 65432
FORMAT = "utf8"

LOGIN = "login"
SIGNUP = "signup"

def sendList(client, list):

    for item in list:
        client.sendall(item.encode(FORMAT))
        #wait response
        client.recv(1024)

    msg = "end"
    client.send(msg.encode(FORMAT))

def clientLogin(client):
    account = []
    username = input('-> Username: ')
    password = input('-> Password: ')

    # check username and password validation
    account.append(username)
    account.append(password)
    
    # send account to server
    sendList(client, account)

    # receive response from server (Valid or Invalid)
    validCheck = client.recv(1024).decode(FORMAT)

    print(validCheck)

def clientSignup(client):
    account = []
    username = input('-> Username: ')
    password = input('-> Password: ')

    # check username and password validation
    account.append(username)
    account.append(password)
    
    # send account to server
    sendList(client, account)

    # receive response from server (Valid or Invalid)
    validCheck = client.recv(1024).decode(FORMAT)

    print(validCheck)


# ----- MAIN ----- #

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("CLIENT SIDE")


try:
    client.connect( (HOST, SERVER_PORT) )
    print("client address:",client.getsockname())


    msg = None
    while (msg != "x"):
        msg = input("- talk: ")
        client.sendall(msg.encode(FORMAT))

        # functions called by client
        if (msg == LOGIN): 
            # wait response
            client.recv(1024)
            clientLogin(client)

        if (msg == SIGNUP):
            # wait response
            client.recv(1024)
            clientSignup(client)
            
except:
    print("Error")


client.close()