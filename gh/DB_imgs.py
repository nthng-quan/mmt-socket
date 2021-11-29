import pyodbc
import os,io
from io import BytesIO
from PIL import Image

print(pyodbc.drivers())

conx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
    SERVER=NTHQUAN\SQL19;\
        DATABASE=SOCKET_ACCOUNT;\
            UID=hquan;PWD=26102002')

cursor = conx.cursor()

id_to_search = input("> Enter id to search:")


status = cursor.execute("SELECT * FROM Phonebook WHERE ID = 1")
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

conx.close()