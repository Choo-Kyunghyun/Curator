import tkinter as tk
from tkinter import ttk
from .main import Curator
import ctypes
import os


class CuratorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.curator = Curator()
        self.field_names = [
            "id",
            "title",
            "album",
            "release_year",
            "thumbnail",
            "url",
            "tags",
            "artists",
            "channel",
            "channel_id",
            "channel_url",
            "duration",
            "duration_string",
        ]

        self.title("Curator")
        self.geometry("1280x720")

        self.create_widgets()
        self.load()

    def open_file(self, path):
        if not os.path.exists(path):
            open(path, "w").close()
        os.startfile(path)

    def convert_cookie(self):
        if self.curator.youtube.convert_cookie():
            print("Cookie converted")
        else:
            print("Failed to convert cookie")

    def save(self):
        if self.curator.save():
            print("Saved")
        else:
            print("Failed to save")

    def load(self):
        if self.curator.load():
            print("Loaded")
            self.refresh()
        else:
            print("Failed to load")

    def fetch_urls(self):
        self.curator.youtube.block_cookie = self.cookie_block.get()
        if self.curator.fetch_urls():
            print("Fetched URLs")
        else:
            print("Failed to fetch URLs")
        self.save()
        self.refresh()

    def extract_urls(self):
        self.curator.extract_urls()
        print("Extracted URLs")
        self.save()

    def refresh(self):
        self.collection_listbox.delete(0, tk.END)
        count = 0
        for entry in self.curator.collection.collection:
            self.collection_listbox.insert(tk.END, entry["title"])
            count += 1
        print(f"Refreshed {count} items")

    def get_selected_item(self):
        try:
            index = self.collection_listbox.curselection()[0]
            return self.curator.collection.collection[index]
        except IndexError:
            return None

    def on_listbox_select(self, event):
        selected_item = self.get_selected_item()
        if selected_item:
            for i, field in enumerate(self.field_names):
                self.entries[i].delete(0, tk.END)
                self.entries[i].insert(0, selected_item[field])

    def create_widgets(self):
        self.label = ttk.Label(self, text="Curator")
        self.label.grid(row=0, column=0, columnspan=6)

        self.refresh_button = ttk.Button(self, text="Refresh", command=self.refresh)
        self.refresh_button.grid(row=1, column=0)

        self.refresh_button = ttk.Button(self, text="Save", command=self.save)
        self.refresh_button.grid(row=1, column=1)

        self.refresh_button = ttk.Button(self, text="Load", command=self.load)
        self.refresh_button.grid(row=1, column=2)

        self.cookie_block = tk.BooleanVar()
        self.cookie_block_checkbutton = ttk.Checkbutton(
            self, text="Block Cookie", variable=self.cookie_block
        )
        self.cookie_block_checkbutton.grid(row=1, column=3)

        self.open_collection_button = ttk.Button(
            self,
            text="Open Collection",
            command=lambda: self.open_file(os.getcwd() + "/" + self.curator.collection_path),
        )
        self.open_collection_button.grid(row=2, column=0)

        self.open_cookie_button = ttk.Button(
            self, text="Open Cookie", command=lambda: self.open_file(os.getcwd() + "/" + self.curator.youtube.cookie_path)
        )
        self.open_cookie_button.grid(row=2, column=1)

        self.open_urls_button = ttk.Button(
            self, text="Open URLs", command=lambda: self.open_file(os.getcwd() + "/" + self.curator.urls_path)
        )
        self.open_urls_button.grid(row=2, column=2)

        self.convert_cookie_button = ttk.Button(
            self, text="Convert Cookie", command=self.convert_cookie
        )
        self.convert_cookie_button.grid(row=3, column=0)

        self.fetch_urls_button = ttk.Button(
            self, text="Fetch URLs", command=self.fetch_urls
        )
        self.fetch_urls_button.grid(row=3, column=1)

        self.extract_urls_button = ttk.Button(
            self, text="Extract URLs", command=self.extract_urls
        )
        self.extract_urls_button.grid(row=3, column=2)

        self.collection_listbox = tk.Listbox(self)
        self.collection_listbox.grid(row=4, column=0, columnspan=6, sticky="nsew")
        self.collection_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.labels = []
        self.entries = []
        i = 0
        j = 0
        for field in self.field_names:
            label = ttk.Label(self, text=field)
            label.grid(row=5 + i, column=j)
            entry = ttk.Entry(self)
            entry.grid(row=5 + i, column=j + 1)
            self.labels.append(label)
            self.entries.append(entry)
            j += 2
            if j == 6:
                j = 0
                i += 1


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

if __name__ == "__main__":
    app = CuratorApp()
    app.mainloop()
