import pyodbc

import os,io
from io import BytesIO

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog, messagebox, Frame

from PIL import Image, ImageTk


SELECT_FILE_PATH = ""

con_DB = pyodbc.connect('\
    DRIVER={ODBC Driver 17 for SQL Server};\
    SERVER=WINDOWS\SQL19;\
    DATABASE=SOCKET_ACCOUNT;\
    UID=hquan;PWD=26102002'
)
cursor = con_DB.cursor()

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
# ------------------- INSERTION ------------------- #
class HomePage(tk.Frame):
    def __init__(self,parent,appController):
        tk.Frame.__init__(self,parent)
        label_title = tk.Label(self, text="HOME PAGE")
        btn_insertion = tk.Button(
            self,
            text="insertion",
            command=lambda: appController.showPage(Insertion)
        )

        btn_search = tk.Button(
            self,
            text="search",
            command=lambda: appController.showPage(Search_by_id)
        )

        label_title.pack()
        btn_insertion.pack()
        btn_search.pack() 

class Insertion(tk.Frame):
    def __init__(self, parent, appController):
        tk.Frame.__init__(self, parent)
        # -- FULLNAME -- #
        self.label_fullName = tk.Label(
            self,
            text="Full Name: ",
            font=("Arial", 12)
        )

        self.entry_fullName = tk.Entry(self)
        # -- PHONE NUMBER -- #
        self.label_phone_number = tk.Label(
            self,
            text="Phone number: ",
            font=("Arial", 12)
        )

        self.entry_phone_number = tk.Entry(self)
        # -- EMAIL -- #
        self.label_email = tk.Label(
            self,
            text="Email: ",
            font=("Arial", 12)
        )

        self.entry_email = tk.Entry(self)

        self.label_fullName.grid(column = 0, row = 0)
        self.entry_fullName.grid(column = 1, row = 0)                 
        self.label_phone_number.grid(column = 0, row = 1)
        self.entry_phone_number.grid(column = 1, row = 1)
        self.label_email.grid(column = 0, row = 2)
        self.entry_email.grid(column = 1, row = 2)

        # -- AVATAR -- #
        self.label_avatar = tk.Label(
            self,
            text="Select image for avatar:",
            font=("Arial", 12)
        ).grid(column=0, row=3)

        self.button_choose_avatar = tk.Button(
            self,
            text = "Choose File",
            command = lambda: get_file_path()
        ).grid(column=1, row=3)

        # -- CONFIRM BUTTON -- #
        self.button_confirm = tk.Button(
            self,
            text = "Confirm",
            command = self.insert_info
        ).grid(column=0, row=4)

        self.button_back = tk.Button(
            self,
            text = "Back",
            command = lambda: appController.showPage(ShowPhoneBook)
        ).grid(column=1, row=4, pady = 3)

    def insert_info(self):
        global SELECT_FILE_PATH
        
        name = self.entry_fullName.get()
        phone_number = self.entry_phone_number.get()
        email = self.entry_email.get()
        avatar = SELECT_FILE_PATH
        
        if(name == "" or phone_number == "" or email == "" or avatar == ""):
            messagebox.showerror("Error", "Please fill in all the information")
            return

        elif not check_phone_number(phone_number):
            messagebox.showerror("Error", "Phone number already exists!")
            return
        
        else:
            try:
                cursor.execute("\
                    INSERT INTO dbo.Phonebook\
                        (Avatar\
                        ,FullName\
                        ,PhoneNumber\
                        ,Email)\
                    SELECT BulkColumn,?,?,?\
                        from OPENROWSET(BULK '"+ avatar +"', SINGLE_BLOB) IMG_DATA;",
                    name, phone_number, email
                )
                con_DB.commit()
                messagebox.showinfo("Success", "Insert successfully !")

            except Exception as e:
                messagebox.showerror("Error", e)

        SELECT_FILE_PATH = ""

class ShowPhoneBook(tk.Frame):
    def __init__(self, parent, appController):
        self.SortDir = True

        tk.Frame.__init__(self, parent)

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
            # command=self.find_by_id
            command=lambda: self.find_by_id()
        )

        # ---- Insert Button ---- #
        self.button_confirm_insert = tk.Button(
            self,
            text="Add more user",
            # command=self.find_by_id
            command= lambda: appController.showPage(Insertion)
        )

        # -- DOWNLOAD -- #
        self.button_download_all_img = tk.Button(
            self,
            text="Download all images",
            # command=self.find_by_id
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
        self.tree.delete(*self.tree.get_children())

        self.status = cursor.execute("SELECT * FROM Phonebook")
        self.fetch_data()

        # LAYER ORDER
        self.label_title.pack()
        self.tree.pack(side = 'left')
        self.verscrlbar.pack(side = 'right', fill = 'y')

        self.label_id.pack()
        self.entry_id.pack(pady=3)
        self.button_confirm_id.pack(pady=3)
        
        self.button_refresh_phone_book.pack(pady=3)
        self.button_confirm_insert.pack(pady=3)
        self.button_download_all_img.pack(pady=3)

    def fetch_data(self):
        self.tree.delete(*self.tree.get_children())

        self.status = cursor.execute("SELECT * FROM Phonebook")
        self.data = self.status.fetchall()
        
        index = 0

        for row in self.data:
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
        
        try:
            status = cursor.execute("SELECT * FROM Phonebook WHERE ID = ?", id_to_search)
            data = status.fetchone()

            userid = data[0]
            fullname = data[2]
            phonenumber = data[3]
            email = data[4]
            img = data[1]

            popup_information(userid, fullname, phonenumber, email, img)


        except:
            messagebox.showinfo("Error", "ID not found !")
    
    def save_all_image(self):
        folder_path = filedialog.askdirectory(
            title = "Select/Create folder to save all the images"
        )
        try:
            status = cursor.execute("SELECT Avatar, FullName FROM Phonebook")
            avatar = status.fetchall()
            
            count = len(avatar)
            index = 0

            while index < count:
                img = Image.open(io.BytesIO(avatar[index][0]))
                img.save(folder_path + "\\" + avatar[index][1] + ".png")
                index = index + 1

                if (index == count - 1):
                    messagebox.showinfo("Success", "All images have been saved")

        except Exception as e:
            messagebox.showinfo("Error", e)
    
class Search_by_id(tk.Frame):
    def __init__(self, parent, appController):
        tk.Frame.__init__(self, parent)
        self.label_id = tk.Label(
            self,
            text="Insert ID: ",
            font=("Arial Bold", 12)
        ).grid(column=0, row=0)

        self.entry_id = tk.Entry(
            self
        )
        self.entry_id.grid(column=1, row=0)

        self.confirm_id = Button(
            self,
            text="Confirm",
            command=self.find_by_id
        ).grid(column=2, row=0)

    def find_by_id(self):
        id_to_search = self.entry_id.get()
        status = cursor.execute("SELECT * FROM Phonebook WHERE ID = ?", id_to_search)
        data = status.fetchone()

        userid = data[0]
        fullname = data[2]
        phonenumber = data[3]
        email = data[4]

        print("- ID: ", userid)
        print("- fullName: ", fullname)
        print("- phoneNumer: ", phonenumber)
        print("- email: ", email)

        img = Image.open(io.BytesIO(data[1]))
        img.show()

class Socket_App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        # Title + icon
        self.title("Socket App")
        self.geometry("600x680")

        self.resizable(width=False, height=False)
        
        #Handle [X] button
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
      
        container = tk.Frame()
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, Insertion, Search_by_id, ShowPhoneBook):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showPage(ShowPhoneBook)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def showPage(self, FrameName_Class):
        self.frames[FrameName_Class].tkraise()

## TODO : DELETE()
# DBCC CHECKIDENT ('dbo.Phonebook', RESEED, prev_index)
if __name__ == "__main__":
    app = Socket_App()
    try:
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error", e)
        con_DB.close()
    finally:
        con_DB.close()
    # print(check_phone_number("8329329"))