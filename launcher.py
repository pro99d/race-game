import PIL.Image
import customtkinter as tk
import os
import datetime
import PIL

time = datetime.datetime.now().hour

def server(*argvs, **kwargs):
    os.system("python3 multiplayer/server.py")

def main():
    app = tk.CTk()
    app.geometry("1000x600")
    app.title("Launcher")
    app.resizable(False, False)
    if time in range(6, 18):
        app._set_appearance_mode("Light")
    else:
        app._set_appearance_mode("Dark")
    image = PIL.Image.open("./icons/PNG/Black/2x/multiplayer.png")
    #image.resize((50, 50))
    start = tk.CTkButton(app, text="", command=server, image=tk.CTkImage(image), width=50, height=50)
    start.grid(row=0, column=0, padx=10, pady=10)

    app.mainloop()
if __name__ == "__main__":
    main()