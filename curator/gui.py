import tkinter as tk
from tkinter import ttk
from .main import Curator
import ctypes
import os


class CuratorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.curator = Curator()
        self.curator.load()

        self.title("Curator")
        self.geometry("800x600")

        self.create_widgets()

    def print(self, string):
        self.text_output.insert(tk.END, string)
        self.text_output.see(tk.END)

    def open_file(self, path):
        if not os.path.exists(path):
            open(path, "w").close()
        os.startfile(path)

    def convert_cookie(self):
        if self.curator.youtube.convert_cookie():
            self.print("Cookie converted\n")
        else:
            self.print("Failed to convert cookie\n")

    def save(self):
        if self.curator.save():
            self.print("Saved\n")
        else:
            self.print("Failed to save\n")

    def load(self):
        if self.curator.load():
            self.print("Loaded\n")
        else:
            self.print("Failed to load\n")

    def fetch_urls(self):
        if self.curator.fetch_urls():
            self.print("Fetched URLs\n")
        else:
            self.print("Failed to fetch URLs\n")
        self.save()

    def extract_urls(self):
        self.curator.extract_urls()
        self.print("Extracted URLs\n")
        self.save()

    def create_widgets(self):
        self.label = ttk.Label(self, text="Curator")
        self.label.pack()

        self.cookie_block = tk.BooleanVar()
        self.cookie_block_checkbutton = ttk.Checkbutton(
            self, text="Block Cookie", variable=self.cookie_block
        )
        self.cookie_block_checkbutton.pack()

        self.convert_cookie_button = ttk.Button(
            self, text="Convert Cookie", command=self.convert_cookie
        )
        self.convert_cookie_button.pack()

        self.fetch_urls_button = ttk.Button(
            self, text="Fetch URLs", command=self.fetch_urls
        )
        self.fetch_urls_button.pack()

        self.extract_urls_button = ttk.Button(
            self, text="Extract URLs", command=self.extract_urls
        )
        self.extract_urls_button.pack()

        self.text_output = tk.Text(self, wrap="word", height=10)
        self.text_output.pack(fill=tk.BOTH, expand=True)


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

if __name__ == "__main__":
    app = CuratorApp()
    app.mainloop()
