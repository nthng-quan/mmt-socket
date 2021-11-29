import pyodbc

import os,io
from io import BytesIO

from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog, messagebox, Frame

from PIL import Image


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

# -- CONFIRM BUTTON -- #
def insert_info():
    global SELECT_FILE_PATH
    name = entry_fullName.get()
    phone_number = entry_phone_number.get()
    email = entry_email.get()
    avatar = SELECT_FILE_PATH

    if(name == "" or phone_number == "" or email == "" or avatar == ""):
        messagebox.showerror("Error","Please fill in all information")
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
# ------------------- INSERTION ------------------- #
# --- INITIALIZE WINDOW --- #
window = Tk()
window.title("Insert phonebook")
window.geometry('350x150')
window.resizable(False, False)
# -- FULLNAME -- #
label_fullName = Label(
    window,
    text="Full Name: ",
    font=("Arial Bold", 12)
).grid(column = 0, row = 0)

entry_fullName = Entry(                     
    window
)
entry_fullName.grid(column = 1, row = 0)                 
# -- PHONE NUMBER -- #
label_phone_number = Label(
    window,
    text="Phone number: ",
    font=("Arial Bold", 12)
).grid(column = 0, row = 1)

entry_phone_number = Entry(
    window
)
entry_phone_number.grid(column = 1, row = 1)
# -- EMAIL -- #
label_email = Label(
    window,
    text="Email: ",
    font=("Arial Bold", 12)
).grid(column = 0, row = 2)

entry_email = Entry(
    window
)
entry_email.grid(column = 1, row = 2)
# -- AVATAR -- #
label_avatar = Label(
    window,
    text="Select image for avatar:",
    font=("Arial Bold", 12)
).grid(column=0, row=3)

button_choose_avatar = Button(
    window,
    text = "Choose File",
    command = lambda: get_file_path()
).grid(column=1, row=3)

# -- CONFIRM BUTTON -- #
button_confirm = Button(
    window,
    text = "Confirm",
    command = lambda: insert_info()
).grid(column=0, row=4)
# ------------------- SEARCH by ID ------------------- #
# id_to_search = input("> Enter id to search: ")

# status = cursor.execute("SELECT * FROM Phonebook WHERE ID = ?", id_to_search)
# data = status.fetchone()

# userid = data[0]
# fullname = data[2]
# phonenumber = data[3]
# email = data[4]

# print("- ID: ", userid)
# print("- fullName: ", fullname)
# print("- phoneNumer: ", phonenumber)
# print("- email: ", email)

# img = Image.open(io.BytesIO(data[1]))
# img.show()
# playboyCarti
# 969420
# h0mebboicr34t1n@gmail.com

if __name__ == "__main__":
    try:
        window.mainloop()
    except Exception as e:
        messagebox.showerror("Error", e)
        con_DB.close()
    finally:
        con_DB.close()