import tkinter as tk


class ParallelDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Paralel Downloader")
        self.root.geometry("600x350")

        self.url_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        self.is_downloading = False
        self.total_size = 0
        self.downloaded_bytes = 0