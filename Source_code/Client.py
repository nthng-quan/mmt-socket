import socket
import pyodbc

import pickle

import os,io
from io import BytesIO

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, Frame

from PIL import Image, ImageTk

# ---------- SOCKET ----------- #

SERVER_IP        = socket.gethostbyname("nthngquan.ddns.net")
SERVER_PORT      = 27603
FORMAT           = "utf8"
STATUS           = True
MAX_BUFFER_SIZE  = 4096*500
# DATA             = []

# ----------- DB protocol ---------- #

FIND_BY_ID       = "find_by_id"
SAVE_ALL_IMGS    = "save_all_imgs"
FETCH_DATA       = "fetch_data"
CHECK            = "check"
DISCONNECT       = "disconnect"

FAIL             = "fail"
GOOD             = "good"
SUCCESS          = "success"
CHECKIN          = "checkin"

# ------------------------------ #

SELECT_FILE_PATH = ""
alldata = []

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

def popup_information ( userid,
                        fullname,
                        phonenumber,
                        email,
                        img ):

    win = tk.Toplevel()
    win.geometry("300x280")
    win.iconbitmap(r'app_icon.ico')
    
    win.resizable(0,0)
    win.wm_title(str(userid) + " - " + str(fullname))

    image         = Image.open(io.BytesIO(img))
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
        text    = "Download fullsize avatar",
        command = lambda: save_avatar(img)
    )

    # LAYER ORDER
    button_dis = 3
    label_avatar.pack(pady = button_dis)
    label_fullName.pack(pady = button_dis)
    label_phone.pack(pady = button_dis)
    label_email.pack(pady = button_dis)
    button_download.pack(pady = button_dis)

    win.mainloop()

def check_phone_number(phone_number):
    global client

    try:
        request = CHECK
        client.send(request.encode(FORMAT))
        client.recv(1024)

    except:
        messagebox.showerror ("Error", "Connection error, Server is down !")

        return
    

        client.send(phone_number.encode(FORMAT))
        client.recv(1024)

        valid_check = client.recv(1024).decode(FORMAT)
        client.recv(1024)

        if valid_check == GOOD:
            return True
        else:
            return False

def save_avatar(img):
    global client

    image     = Image.open(io.BytesIO(img))

    file_path = filedialog.asksaveasfilename (
        defaultextension = '.png',
        filetypes = [ 
            ("PNG file",".png"),
            ("JPEG file", ".jpeg"),
            ("All files", ".*"),
        ]
    )

    if (file_path == ""):
        return

    try:
        image.save(file_path)
        messagebox.showinfo (
            "Success",
            "Image saved successfully !"
        )

        if messagebox.askyesno (
            "Open image",
            "Do you want to open the image?"):

            os.startfile(file_path)

    except:
        messagebox.showerror (
            "Error",
            "Image not saved !"
        )

class ShowPhoneBook(tk.Frame):
    def __init__(self, parent, appController):
        tk.Frame.__init__(self, parent)
        self.SortDir = True

        l_frame = Frame(self)
        l_frame.pack(pady = 10)

        self.label_title = tk.Label(
            l_frame,
            text = "Phone Book",
            font = ("Arial", 20)
        )
        
        self.dataCols = ( # Columns headings
            'ID',
            'Full name',
            'Phone number',
            'Email'
        )

        self.tree = ttk.Treeview(
            l_frame,
            columns = self.dataCols,
            height  = 10,
        )

        style = ttk.Style(parent)
        style.map("TreeView")
        style.configure(
            "Treeview", 
            rowheight = 40,
        )

        self.verscrlbar = tk.Scrollbar(
            l_frame,
            orient   = "vertical",
            command  = self.tree.yview
        )

        # Configuring treeview
        self.tree.configure(xscrollcommand = self.verscrlbar.set)
        
        # ---- Search button ---- #
        self.label_id = tk.Label(
            self,
            text = "Search by ID",
            font = ("Arial Bold", 10)
        )

        self.entry_id = tk.Entry(
            self,
            font = ("Arial", 10)
        )

        button_width = 17

        self.button_confirm_id = tk.Button(
            self,
            text    = "Confirm",
            width   = button_width,
            command = lambda: self.find_by_id()
        )

        # -- DOWNLOAD -- #
        self.button_download_all_img = tk.Button(
            self,
            text    = "Download all images",
            width   = button_width,
            command = lambda: self.save_all_image()
        )

        # -- REFRESH -- #
        self.button_refresh_phone_book = tk.Button(
            self,
            text    = "Refresh",
            width   = button_width,
            command = lambda: self.refresh()
        )
        
        # -- UPDATE -- #
        self.button_update_phone_book = tk.Button(
            self,
            text    = "Update",
            width   = button_width,
            command = lambda: self.fetch_data()
        )
        # Setup column heading
        
        # column 0 - Avatar
        self.tree.heading(
            '#0',
            text   = 'Avatar',
            anchor = 'c'
        )
        self.tree.column(
            '#0',
            minwidth = 75,
            width    = 75,
            anchor   = 'c'
        )

        # column 1 - ID
        self.tree.heading(
            '#1',
            text     = 'ID',
            anchor   = 'c'
        )
        self.tree.column(
            '#1',
            minwidth = 25,
            width    = 25,
            anchor   = 'c'
        )

        # column 2 - Full name
        self.tree.heading(
            '#2',
            text     = 'Full name',
            anchor   = 'c'
        )
        self.tree.column(
            '#2',
            minwidth = 100,
            width    = 100,
            anchor   = 'c')
        
        # column 3 - Phone number
        self.tree.heading(
            '#3',
            text     = 'Phone number',
            anchor   = 'c'
        )
        self.tree.column(
            "#3",
            minwidth = 100,
            width    = 100,
            anchor   = 'c'
        )
        
        # column 4 - Email
        self.tree.heading(
            '#4',
            text     = 'Email',
            anchor   = 'c'
        )
        self.tree.column(
            '#4',
            minwidth = 100,
            width    = 250,
            anchor   = 'c'
        )

        self.tree.configure(xscrollcommand = self.verscrlbar.set)

        # LAYER ORDER
        self.label_title.pack()
        self.tree.pack(
            side = 'left'
        )
        self.verscrlbar.pack(
            side = 'right',
            fill = 'y'
        )

        button_dis = 3
        self.label_id.pack()
        self.entry_id.pack(pady = button_dis)
        self.button_confirm_id.pack(pady = button_dis)
        
        self.button_refresh_phone_book.pack(pady = button_dis)
        self.button_download_all_img.pack(pady = button_dis)
        self.button_update_phone_book.pack(pady = button_dis)

        messagebox.showinfo (
            "Welcome to Phone Book !",
            "Use the update button to update data from server"
        )

    def refresh(self):
        global alldata

        if (len(alldata) == 0):
            messagebox.showinfo (
                "Oops",
                "Looks like you haven't update data from server yet !"
            )

            return

        self.tree.delete(*self.tree.get_children())

        for row in alldata:
            self._user_id           = row[0]

            self._user_avatar       = Image.open(io.BytesIO(row[1]))
            self._user_avatar       = self._user_avatar.resize((35, 35), Image.ANTIALIAS)
            self._user_avatar       = ImageTk.PhotoImage(self._user_avatar)

            self._user_avatar.image = self._user_avatar
            
            self._user_fullname     = row[2]
            self._user_phonenumber  = row[3]
            self._user_email        = row[4]
        
            self.tree.insert (
                '',            # parent
                self._user_id, # index
                self._user_id, # iid
                
                image = self._user_avatar.image,
                value = (
                    self._user_id,
                    self._user_fullname,
                    self._user_phonenumber,
                    self._user_email
                ),
            )

    def fetch_data(self):
        global alldata
        alldata = []

        try:
            # send request to server
            option = FETCH_DATA
            client.sendall(option.encode(FORMAT))
            client.recv(1024) # wait for request response
        
        except:
            messagebox.showerror (
                "Error",
                "Connection error, Server is down !"
            )
            
            return

        self.tree.delete(*self.tree.get_children())
        
        # receive data
        data = []
        # receive query response
        msg = client.recv(1024).decode(FORMAT)
        client.send(msg.encode(FORMAT)) # client repond 1
        
        # receive max_rows
        max_rows = int(client.recv(1024).decode(FORMAT))
        client.send(GOOD.encode(FORMAT)) # client repond 2

        index = 0
        if (msg == GOOD):
            while index < max_rows:
                data_in_bytes = client.recv(MAX_BUFFER_SIZE)
                # unpickle_data
                # self.after(10, data.append(pickle.loads(data_in_bytes)))

                # send response 3 to server
                # client.send(GOOD.encode(FORMAT))
                try:
                    unpickle_data = pickle.loads(data_in_bytes)
                    client.send(GOOD.encode(FORMAT))

                except:
                    client.send(FAIL.encode(FORMAT))
                    messagebox.showinfo(
                        "Error",
                        "Error receiving data from server\
                        \n Please retry !"
                    )

                    return

                data.append(unpickle_data)

                index += 1

        alldata = data
        
        for row in data:
            self._user_id           = row[0]

            self._user_avatar       = Image.open(io.BytesIO(row[1]))
            self._user_avatar       = self._user_avatar.resize((35, 35), Image.ANTIALIAS)
            self._user_avatar       = ImageTk.PhotoImage(self._user_avatar)

            self._user_avatar.image = self._user_avatar
            
            self._user_fullname     = row[2]
            self._user_phonenumber  = row[3]
            self._user_email        = row[4]
        
            self.tree.insert(
                '',            # parent
                self._user_id, # index
                self._user_id, # iid
                
                image = self._user_avatar.image,
                value = (
                    self._user_id,
                    self._user_fullname,
                    self._user_phonenumber,
                    self._user_email
                ),
            )

        self.refresh()

    def find_by_id(self):
        id_to_search = self.entry_id.get()

        if (id_to_search == ""):
            messagebox.showerror (
                "Error",
                "ID cannot be empty !"
            )

            return
            
        try:
            request = FIND_BY_ID # send request to server
            client.send(request.encode(FORMAT))
            client.recv(1024).decode(FORMAT) # request accepted

        except:
            messagebox.showerror (
                "Error",
                "Connection error, Server is down !"
            )

            return

        # send id to server
        client.send(id_to_search.encode(FORMAT))
        client.recv(1024).decode(FORMAT) # wait response 1

        # receive response msg
        msg = client.recv(1024).decode(FORMAT)
        client.send(msg.encode(FORMAT)) # response

        if (msg == FAIL):
            messagebox.showerror (
                "Error",
                "ID not found !"
            )

            return

        else:
            # receive data
            print(msg, request)

            packet       =  b''
            packet      +=  client.recv(MAX_BUFFER_SIZE)
            client.send(msg.encode(FORMAT)) # response
            data         =  pickle.loads(packet)

            userid       =  data[0]
            img          =  data[1]
            fullname     =  data[2]
            phonenumber  =  data[3]
            email        =  data[4]

            popup_information(userid, fullname, phonenumber, email, img)
        
    def save_all_image(self):
        folder_path = filedialog.askdirectory (
            title = "Select/Create folder to save all the images"
        )

        if folder_path == "":
            return

        # send request to server
        try:
            request = SAVE_ALL_IMGS
            client.sendall(request.encode(FORMAT))
            client.recv(1024) # wait for request response
        
        except:
            messagebox.showerror (
                "Error",
                "Connection error, Server is down !"
            )

            return

        # receive data
        data = []

        # receive query response
        msg = client.recv(MAX_BUFFER_SIZE).decode(FORMAT)
        client.send(msg.encode(FORMAT)) # client repond 1
        
        # receive max_rows
        str_max_rows = client.recv(1024).decode(FORMAT)
        max_rows     = int(str_max_rows)

        client.send(GOOD.encode(FORMAT)) # client reponse 2

        currentRow = 0
        
        if (msg == GOOD):
                
            messagebox.showinfo (
                "Downloading",
                "Downloading all images, please wait..."
            )

            while currentRow < max_rows:
                data_in_bytes = client.recv(MAX_BUFFER_SIZE)
                
                # send response 3 to server
                client.send(GOOD.encode(FORMAT))
                unpickle_data = pickle.loads(data_in_bytes)

                data.append(unpickle_data)

                currentRow += 1

        for row in data:
            self._user_avatar        =  Image.open(io.BytesIO(row[0]))
            self._user_avatar.image  =  self._user_avatar

            self._user_fullname      =  row[1]

            self._user_avatar.save (
                folder_path + "\\" + self._user_fullname + ".png"
            )

        messagebox.showinfo (
            "Success",
            "All images have been succesfully saved to\n" + folder_path
        )

        # ask if user want to open folder
        if messagebox.askyesno (
            "Open folder",
            "Do you want to open the folder ?"):

            os.startfile(folder_path)

class ClientConfiguration(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args, **kwargs)
                
        self.title("Client configuration")
        self.iconbitmap('app_icon.ico')
        self.geometry("400x195")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.resizable(width=False, height=False)

        label_title = tk.Label(
            self,
            text   = "CONNECT TO SERVER",
            font   = ("Arial", 15, "bold"),
            pady   = 5
        ).grid (
            row    = 0,
            column = 1
        )

        label_ip_address = tk.Label(
            self,
            text   = "   Server's IP Address",
            font   = ("Arial", 10, "bold"),
        ).grid (
            row    = 1,
            column = 0,
        )

        label_server_port = tk.Label(
            self,
            text   = "   Port: ",
            font   = ("Arial", 10, "bold"),
        ).grid (
            row    = 2,
            column = 0
        )

        self.entry_ip_address = tk.Entry(
            self,
            width   = 30,
            justify = "center"
        )
        self.entry_server_port = tk.Entry(
            self,
            width   = 30,
            justify = "center"
        )
        self.entry_server_port.insert(tk.END, "27603")

        # BUTTON RUN SERVER
        button_width = 20
        button_run_server = tk.Button(
            self,
            text     = "CONNECT",
            width    = button_width,
            command  = lambda: self.connect_server()
        )

        # IP AUTO FILL BUTTONS

        button_ip_loopback = tk.Button(
            self,
            text     = "Loopback IP",
            width    = button_width,
            command  = lambda: self.set_ip_loopback()
        )

        button_PC_IP = tk.Button(
            self,
            text     = "Your IP",
            width    = button_width,
            command  = lambda: self.set_ip_this()
        )

        button_run_server.grid(
            row    = 4,
            column = 1
        )

        button_ip_loopback.grid(
            row    = 5,
            column = 1
        )

        button_PC_IP.grid(
            row    = 6,
            column = 1
        )

        self.entry_ip_address.grid(
            row    = 1,
            column = 1
        )
        self.entry_server_port.grid(
            row    = 2,
            column = 1,
            pady  = 10
        )

    def on_closing(self):
        global STATUS

        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            STATUS = False

            self.destroy()

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


    def connect_server(self):
        global SERVER_IP
        global SERVER_PORT
        global STATUS

        global alldata

        ip_entry = self.entry_ip_address.get()
        port_entry = self.entry_server_port.get()

        if (ip_entry == "" or port_entry == ""):
            messagebox.showerror(
                "Error",
                "Please fill IP Address and Port"
            )
            return

        SERVER_IP = ip_entry
        SERVER_PORT = int(port_entry)
    
        client = socket.socket (
            socket.AddressFamily.AF_INET,
            socket.SocketKind.SOCK_STREAM
        )

        try:
            client.connect((
                SERVER_IP,
                SERVER_PORT
            ))

            msg = CHECKIN
            client.sendall(msg.encode(FORMAT))
            client.recv(1024)
            
            client.close()

            messagebox.showinfo (
                "Success",
                "Successfully connected to server"
            )

            STATUS = True

        except Exception as connection_error:
            STATUS = False
            messagebox.showerror(
                "Error",
                connection_error
            )

        self.destroy()

class Socket_App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        # Title + icon
        self.title("Socket App - Phonebook")
        self.iconbitmap(r'app_icon.ico')
        self.geometry("600x660")
        self.resizable(0,0)
        
        # Handle [X] button
        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_closing
        )
      
        container  = tk.Frame()
        container.pack (
            side   = "top",
            fill   = "both",
            expand = True
        )
        
        # config the container
        container.grid_rowconfigure(
            0,
            weight = 1
        )
        container.grid_columnconfigure(
            0,
            weight = 1
        )

        frame = ShowPhoneBook(container, self)
        frame.grid (
            row    = 0,
            column = 0,
            sticky = "nsew"
        )

    def on_closing(self):
        request = DISCONNECT
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                client.sendall(request.encode(FORMAT))
                client.recv(1024)
            except:
                pass
            
            self.destroy()

if __name__ == "__main__":
    app = ClientConfiguration()
    app.mainloop()

    if(STATUS):
        client = socket.socket (
            socket.AddressFamily.AF_INET,
            socket.SocketKind.SOCK_STREAM
        )
        try:
            client.connect((
                SERVER_IP,
                SERVER_PORT
            ))
            print("Connected !")

            try:
                app2 = Socket_App()
                app2.mainloop()

            except KeyboardInterrupt:
                request = DISCONNECT

                client.sendall(request.encode(FORMAT))
                client.recv(1024)

                client.close()

            except Exception as error:
                request = DISCONNECT
                try:
                    client.sendall(request.encode(FORMAT))
                    client.recv(1024)
                except:
                    pass

                messagebox.showerror (
                    "Error",
                    error
                )
                client.close()

            finally:
                request = DISCONNECT
                try:
                    client.sendall(request.encode(FORMAT))
                    client.recv(1024)
                except:
                    pass

                client.close()

        except Exception as error:
            messagebox.showerror (
                "Error",
                error
            )

            client.close()
    else:
        pass
