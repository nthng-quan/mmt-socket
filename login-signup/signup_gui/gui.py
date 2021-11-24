from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("617x600")
window.configure(bg = "#FFFFFF")


canvas = Canvas(
    window,
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

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    308.0,
    356.99999999999994,
    image=entry_image_1
)
entry_1 = Entry(
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

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    308.0,
    275.99999999999994,
    image=entry_image_2
)
entry_2 = Entry(
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

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
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
window.resizable(False, False)
window.mainloop()
