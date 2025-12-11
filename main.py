import tkinter as tk
from paralel_downloader import ParallelDownloader

if __name__ == "__main__":
    root = tk.Tk()
    app = ParallelDownloader(root)
    root.mainloop()