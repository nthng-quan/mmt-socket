import pickle

import os,io
from io import BytesIO

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog, messagebox, Frame

from PIL import Image, ImageTk

# ---------- SOCKET ----------- #
import socket

HOST = "127.0.0.1"
SERVER_PORT = 65432
FORMAT = "utf8"

LOGIN = "login"
SIGNUP = "signup"

FAIL = "fail"
SUCCESS = "success"
MAX_BUFFER_SIZE = 4096*500

# --- SQL, Login credentials --- #

SERVER = "WINDOWS\SQL19"
DATABASE = "SOCKET_ACCOUNT"
UID = "hquan"
PWD = "26102002"

# ----------- Request ---------- #

INSERT = "insert"
FIND_BY_ID = "find_by_id"
SAVE_ALL = "save_all"
CHECK = "check"
DISCONNECT = "disconnect"
FETCH_DATA = "fetch_data"
SAVE_ALL_IMGS = "save_all_imgs"
GOOD = "good"
HALT = "halt"

# ------------------------------ #

SELECT_FILE_PATH = ""

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, SERVER_PORT))
print("Connected !")

def get_file_path():
    global SELECT_FILE_PATH
    file_path = filedialog.askopenfilename(
        initialdir = "D:\\sql_data\\pics",
        title = "Select image for avatar !",
        filetypes = (
            ("jpeg files","*.jpg"),
            ("png files","*.png"),
            ("all files","*.*")
        )
    )
    SELECT_FILE_PATH = file_path

def popup_information(userid, fullname, phonenumber, email, img):
    win = tk.Toplevel()
    win.geometry("300x280")
    win.resizable(0,0)
    win.wm_title(str(userid) + " - " + str(fullname))

    image = Image.open(io.BytesIO(img))
    image_resized = image.resize((150, 150), Image.ANTIALIAS)
    image_resized = ImageTk.PhotoImage(image_resized)

    label_avatar = tk.Label(
        win,
        image = image_resized
    )

    label_fullName = tk.Label(
        win,
        text = "- FULLNAME: " + fullname
    )

    label_email = tk.Label(
        win,
        text = "- EMAIL: " + email
    )

    label_phone = tk.Label(
        win,
        text = "- PHONE NUMBER: " + phonenumber
    )

    button_download = tk.Button(
        win,
        text="Download fullsize avatar",
        command=lambda: save_avatar(img)
    )

    # LAYER ORDER
    label_avatar.pack(pady=3)
    label_fullName.pack(pady=3)
    label_phone.pack(pady=3)
    label_email.pack(pady=3)
    button_download.pack(pady=3)

    win.mainloop()

def check_phone_number(phone_number):
    cursor.execute("SELECT id FROM PHONEBOOK WHERE PhoneNumber = ?", phone_number)
    row = cursor.fetchone()

    if row is None:
        return TRUE
    else:
        return FALSE

def save_avatar(img):
    image = Image.open(io.BytesIO(img))

    file_path = filedialog.asksaveasfilename(
        defaultextension='.png',
        filetypes=[
                ("PNG file",".png"),
                ("JPEG file", ".jpeg"),
                ("All files", ".*"),
        ]
    )

    if (file_path == ""):
        return

    try:
        image.save(file_path)
        messagebox.showinfo("Success", "Image saved successfully !")

        if messagebox.askyesno("Open image", "Do you want to open the image?"):
            os.startfile(file_path)

    except:
        messagebox.showerror("Error", "Image not saved !")

# ------------------- Skrt skrt ------------------- #
class HomePage(tk.Frame):
    def __init__(self,parent, appController):
        tk.Frame.__init__(self,parent)
        label_title = tk.Label(self, text="HOME PAGE")
        btn_Login = tk.Button(
            self,
            text="Login",
            command=lambda: appController.showPage(Login)
        )

        btn_search = tk.Button(
            self,
            text="search",
            command=lambda: appController.showPage(Search_by_id)
        )

        label_title.pack()
        btn_Login.pack()
        btn_search.pack() 

class ShowPhoneBook(tk.Frame):
    def __init__(self, parent, appController):
        tk.Frame.__init__(self, parent)
        self.SortDir = True

        l_frame = Frame(self)
        l_frame.pack(pady = 10)

        self.label_title = tk.Label(
            l_frame,
            text="Phone Book",
            font=("Arial", 20)
        )
        
        self.dataCols = ('ID', 'Full name', 'Phone number', 'Email')

        self.tree = ttk.Treeview(
            l_frame,
            columns = self.dataCols,
            height = 10,
        )

        style = ttk.Style(parent)
        style.map("TreeView")
        style.configure(
            "Treeview", 
            rowheight = 40,
        )

        self.verscrlbar = tk.Scrollbar(
            l_frame,
            orient = "vertical",
            command = self.tree.yview
        )

        # Configuring treeview
        self.tree.configure(xscrollcommand = self.verscrlbar.set)
        
        # ---- Search button ---- #
        self.label_id = tk.Label(
            self,
            text="Search by ID",
            font=("Arial Bold", 10)
        )

        self.entry_id = tk.Entry(self,font=("Arial",10))

        self.button_confirm_id = tk.Button(
            self,
            text="Confirm",
            command=lambda: self.find_by_id()
        )

        # -- DOWNLOAD -- #
        self.button_download_all_img = tk.Button(
            self,
            text="Download all images",
            command= lambda: self.save_all_image()
        )

        # -- REFRESH -- #
        self.button_refresh_phone_book = tk.Button(
            self,
            text="Refresh",
            command=lambda: self.fetch_data()
        )
        
        # Setup column heading
        self.tree.heading('#0', text='Avatar', anchor='c')
        self.tree.column("#0", minwidth=75, width=75, anchor ='c')

        self.tree.heading('#1', text='ID', anchor='c')
        self.tree.column("#1", minwidth=25, width=25, anchor ='c')

        self.tree.heading('#2', text='Full name', anchor='c')
        self.tree.column("#2", minwidth=100, width=100, anchor ='c')
        
        self.tree.heading('#3', text='Phone number', anchor='c')
        self.tree.column("#3", minwidth=100, width=100, anchor ='c')
        
        self.tree.heading('#4', text='Email', anchor='c')
        self.tree.column("#4", minwidth=100, width=250, anchor ='c')


        self.tree.configure(xscrollcommand = self.verscrlbar.set)

        # LAYER ORDER
        self.fetch_data() # auto refresh
        self.label_title.pack()
        self.tree.pack(side = 'left')
        self.verscrlbar.pack(side = 'right', fill = 'y')

        self.label_id.pack()
        self.entry_id.pack(pady=3)
        self.button_confirm_id.pack(pady=3)
        
        self.button_refresh_phone_book.pack(pady=3)
        self.button_download_all_img.pack(pady=3)

    def fetch_data(self):
        self.tree.delete(*self.tree.get_children())
        
        # send request to server
        option = FETCH_DATA
        client.sendall(option.encode(FORMAT))
        client.recv(1024) # wait for request response

        # receive data
        data = []
        # receive query response
        msg = client.recv(MAX_BUFFER_SIZE).decode(FORMAT)
        client.send(msg.encode(FORMAT)) # client repond 1
        
        # receive max_rows
        max_rows = int(client.recv(1024).decode(FORMAT))
        print(max_rows)
        client.send(GOOD.encode(FORMAT)) # client repond 2

        index = 0
        if (msg == GOOD):
            while index < max_rows:
                data_in_bytes = client.recv(MAX_BUFFER_SIZE)
                unpickle_data = pickle.loads(data_in_bytes)

                # send response 3 to server
                client.send("ok".encode(FORMAT))

                print(unpickle_data[2])

                data.append(unpickle_data)

                index += 1
        
        for row in data:
            self._user_id = row[0]

            self._user_avatar = Image.open(io.BytesIO(row[1]))
            self._user_avatar = self._user_avatar.resize((35, 35), Image.ANTIALIAS)
            self._user_avatar = ImageTk.PhotoImage(self._user_avatar)

            self._user_avatar.image = self._user_avatar
            
            self._user_fullname = row[2]
            self._user_phonenumber = row[3]
            self._user_email = row[4]
        
            self.tree.insert(
                '',self._user_id, self._user_id,
                image = self._user_avatar.image,
                value=(
                self._user_id,
                self._user_fullname,
                self._user_phonenumber,
                self._user_email),
            )

    def find_by_id(self):
        id_to_search = self.entry_id.get()

        if(id_to_search == ""):
            messagebox.showerror("Error", "ID cannot be empty !")
            return
  
        request = FIND_BY_ID # send request to server
        client.send(request.encode(FORMAT))
        client.recv(1024).decode(FORMAT) # request accepted

        # send id to server
        client.send(id_to_search.encode(FORMAT))
        client.recv(1024).decode(FORMAT) # wait response 1

        # receive response msg
        msg = client.recv(1024).decode(FORMAT)
        client.send(msg.encode(FORMAT)) # response
        print(msg)

        if (msg == FAIL):
            messagebox.showerror("Error", "ID not found !")
            client.send(msg.encode(FORMAT)) # response
            return
        else:
            # receive data
            packet = b''
            packet += client.recv(MAX_BUFFER_SIZE)
            client.send(msg.encode(FORMAT)) # response
            data = pickle.loads(packet)

            userid = data[0]
            img = data[1]
            fullname = data[2]
            phonenumber = data[3]
            email = data[4]

            popup_information(userid, fullname, phonenumber, email, img)
        
    def save_all_image(self):
        folder_path = filedialog.askdirectory(
            title = "Select/Create folder to save all the images"
        )

        if folder_path == "":
            return

        # send request to server
        option = SAVE_ALL_IMGS
        client.sendall(option.encode(FORMAT))
        client.recv(1024) # wait for request response

        # receive data
        data = []
        # receive query response
        msg = client.recv(MAX_BUFFER_SIZE).decode(FORMAT)
        client.send(msg.encode(FORMAT)) # client repond 1
        
        # receive max_rows
        str_max_rows = client.recv(1024).decode(FORMAT)

        max_rows = int(str_max_rows)

        client.send(GOOD.encode(FORMAT)) # client reponse 2

        index = 0

        if (msg == GOOD):
            while index < max_rows:
                data_in_bytes = client.recv(MAX_BUFFER_SIZE)
                
                # send response 3 to server
                client.send(GOOD.encode(FORMAT))
                unpickle_data = pickle.loads(data_in_bytes)

                data.append(unpickle_data)

                index += 1

        # try:
        for row in data:
            self._user_avatar = Image.open(io.BytesIO(row[0]))
            self._user_avatar.image = self._user_avatar
            self._user_fullname = row[1]

            self._user_avatar.save(folder_path + "\\" + self._user_fullname + ".png")

        messagebox.showinfo("Success", "All images have been succesfully saved to\n" + folder_path)

        # ask if user want to open folder
        if messagebox.askyesno("Open folder", "Do you want to open the folder?"):
            os.startfile(folder_path)

        # except:
        #     messagebox.showerror("Error", "Something went wrong !")

class Socket_App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        # Title + icon
        self.title("Socket App")
        self.geometry("600x680")

        self.resizable(0,0)
        
        #Handle [X] button
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
      
        container = tk.Frame()
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        frame = ShowPhoneBook(container, self)
        frame.fetch_data()
        frame.grid(row=0, column=0, sticky="nsew")

    def on_closing(self):
        request = DISCONNECT
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            client.sendall(request.encode(FORMAT))
            self.destroy()

if __name__ == "__main__":
    app = Socket_App()
    try:
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error", e)
