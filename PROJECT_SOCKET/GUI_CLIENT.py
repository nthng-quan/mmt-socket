from pathlib import Path
import socket
import tkinter as tk
# from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox
from tkinter import *
from tkinter import messagebox

HOST = "127.0.0.1"
SERVER_PORT = 65432
FORMAT = "utf8"

LOGIN = "login"
SIGNUP = "signup"
FAIL = "fail"
OK = "ok"

OUTPUT_PATH = Path(__file__).parent

ASSETS_PATH_SIGN_IN = OUTPUT_PATH / Path("./assets_signin")
ASSETS_PATH_SIGN_UP = OUTPUT_PATH / Path("./assets_signup")

def relative_to_assets_signup(path: str) -> Path:
    return ASSETS_PATH_SIGN_UP / Path(path)

def relative_to_assets_signin(path: str) -> Path:
    return ASSETS_PATH_SIGN_IN / Path(path)

class HomePage(tk.Frame):
    def __init__(self,parent,appController):
        tk.Frame.__init__(self,parent)
        label_title = tk.Label(self, text="HOME PAGE")
        btn_logout = tk.Button(self, text="log out", command=lambda: appController.showPage(Sign_in))

        label_title.pack()
        btn_logout.pack() 


class Sign_in(tk.Frame):
    def __init__(self, parent, appController):
        tk.Frame.__init__(self, parent)
        canvas = tk.Canvas(
            self,
            bg = "#FFFFFF",
            height = 600,
            width = 617,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.place(x = 0, y = 0)
        canvas.create_rectangle(
            0.0,
            0.0,
            617.0,
            600.0,
            fill="#FCF4F4",
            outline="")

        self.entry_image_1 = PhotoImage(
            file=relative_to_assets_signin("entry_1.png"))
        self.entry_bg_1 = canvas.create_image(
            308.0,
            357.0,
            image=self.entry_image_1
        )
        self.entry_1 = tk.Entry(self,
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0
        )
        self.entry_1.place(
            x=153.0,
            y=255.0, 
            width=310.0,
            height=40.0
        )

        canvas.create_text(
            155.0,
            318.0,
            anchor="nw",
            text="Password",
            fill="#352F2F",
            font=("RobotoCondensed BoldItalic", 15 * -1)
        )

        self.entry_image_2 = PhotoImage(
            file=relative_to_assets_signin("entry_2.png"))
        self.entry_bg_2 = canvas.create_image(
            308.0,
            276.0,
            image=self.entry_image_2
        )
        self.entry_2 = tk.Entry(self,
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0
        )
        self.entry_2.place(
            x=153.0,
            y=336.0,
            width=310.0,
            height=40.0
        )
      
        canvas.create_text(
            152.0,
            237.0,
            anchor="nw",
            text="Username",
            fill="#352F2F",
            font=("RobotoCondensed BoldItalic", 15 * -1)
        )
        # -- login
        self.button_image_1 = PhotoImage(
            file=relative_to_assets_signin("button_1.png"))
        
        button_1 = tk.Button(
            self,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: appController.clientLogin(self,client),
            relief="flat"
        )
        button_1.place(
            x=181.0,
            y=410.0,
            width=120.0,
            height=25.0
        )
        # -- signup
        self.button_image_2 = PhotoImage(
            file=relative_to_assets_signin("button_2.png"))
        button_2 = tk.Button(
            self,
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: appController.showPage(Sign_in),
            relief="flat"
        )
        button_2.place(
            x=316.0,
            y=410.0,
            width=120.0,
            height=25.0
        )
        self.label_notice = tk.Label(self,text="",bg="bisque2")
        self.label_notice.place(x=250,y=425)
        canvas.create_text(
            145.0,
            164.0,
            anchor="nw",
            text="Log in",
            fill="#353030",
            font=("Roboto Bold", 50 * -1)
        )

class Socket_App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        # Title + icon
        self.title("Socket App")
        self.geometry("617x600")
        photo = PhotoImage(file=relative_to_assets_signin("app_icon.png"))
        self.iconphoto(False, photo)
        self.resizable(width=False, height=False)
        
        #Handle [X] button
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
      
        container = tk.Frame()
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Sign_in ,HomePage):
            frame = F(container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F] = frame 

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def showPage(self, FrameName_Class):
        self.frames[FrameName_Class].tkraise()
    
    def clientLogin(self,curFrame,sck:socket):
        try:
            
            user = curFrame.entry_1.get()
            pswd = curFrame.entry_2.get()
            if (user == "" or pswd == ""):
                curFrame.label_notice["text"] = "Fields cannot be empty"
                return 
            # send command option
            option = LOGIN
            sck.sendall(option.encode(FORMAT))
            
            # send account info
            sck.sendall(user.encode(FORMAT))
            sck.recv(1024)
            sck.sendall(pswd.encode(FORMAT))
            sck.recv(1024)

             # recv login check
            msg = sck.recv(1024).decode(FORMAT)
            if (msg == FAIL):
                curFrame.label_notice["text"] = "invalid password"
                option=FAIL
                return 
            else:
                self.showPage(HomePage)
        except:
            print("Error: Server is not responding")


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect( (HOST, SERVER_PORT) )

    print("CLIENT SIDE")

    app = Socket_App()
    app.showPage(Sign_in)
    app.mainloop()


