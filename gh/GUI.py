from pathlib import Path
import tkinter as tk
# from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox
from tkinter import *

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH_SIGN_IN = OUTPUT_PATH / Path("./assets_signin")
ASSETS_PATH_SIGN_UP = OUTPUT_PATH / Path("./assets_signup")


def relative_to_assets_signup(path: str) -> Path:
    return ASSETS_PATH_SIGN_UP / Path(path)

def relative_to_assets_signin(path: str) -> Path:
    return ASSETS_PATH_SIGN_IN / Path(path)

class Sign_up():
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
            outline=""
        )

        entry_image_1 = tk.PhotoImage(
            file=relative_to_assets_signup("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            308.0,
            356.99999999999994,
            image=entry_image_1
        )
        tk.entry_1 = tk.Entry(
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0
        )
        entry_1.place(
            x=153.0,
            y=335.99999999999994,
            width=310.0,
            height=40.0
        )

        canvas.create_text(
            155.0,
            317.99999999999994,
            anchor="nw",
            text="Password",
            fill="#352F2F",
            font=("RobotoCondensed BoldItalic", 15 * -1)
        )

        entry_image_2 = tk.PhotoImage(
            file=relative_to_assets_signup("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            308.0,
            275.99999999999994,
            image=entry_image_2
        )
        entry_2 = tk.Entry(
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0
        )
        entry_2.place(
            x=153.0,
            y=254.99999999999994,
            width=310.0,
            height=40.0
        )

        canvas.create_text(
            152.0,
            236.99999999999994,
            anchor="nw",
            text="Username",
            fill="#352F2F",
            font=("RobotoCondensed BoldItalic", 15 * -1)
        )

        button_image_1 = tk.PhotoImage(
            file=relative_to_assets_signup("button_1.png"))
        button_1 = tk.Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_1 clicked"),
            relief="flat"
        )
        button_1.place(
            x=217.0,
            y=409.99999999999994,
            width=182.0,
            height=25.0
        )

        canvas.create_text(
            145.0,
            163.99999999999994,
            anchor="nw",
            text="Sign up",
            fill="#353030",
            font=("Roboto Bold", 50 * -1)
        )

class Sign_in():
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

        entry_image_1 = tk.PhotoImage(
            file=relative_to_assets_signin("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            308.0,
            357.0,
            image=entry_image_1
        )
        entry_1 = tk.Entry(
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0
        )
        entry_1.place(
            x=153.0,
            y=336.0,
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

        entry_image_2 = tk.PhotoImage(
            file=relative_to_assets_signin("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            308.0,
            276.0,
            image=entry_image_2
        )
        entry_2 = tk.Entry(
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0
        )
        entry_2.place(
            x=153.0,
            y=255.0,
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

        button_image_1 = tk.PhotoImage(
            file=relative_to_assets_signin("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_1 clicked"),
            relief="flat"
        )
        button_1.place(
            x=181.0,
            y=410.0,
            width=120.0,
            height=25.0
        )

        button_image_2 = tk.PhotoImage(
            file=relative_to_assets_signin("button_2.png"))
        button_2 = tk.Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_2 clicked"),
            relief="flat"
        )
        button_2.place(
            x=316.0,
            y=410.0,
            width=120.0,
            height=25.0
        )

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
        self.resizable(False, False)
        
        # Handle [X] button
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        container = tk.Frame()
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def showPage(self, FrameName_Class):
        self.frames[FrameName_Class].tkraise()

if __name__ == "__main__":
    app = Socket_App()
    app.showPage(Sign_in)
    app.mainloop()