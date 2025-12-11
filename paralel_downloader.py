import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests


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

        self.create_widgets()


    def create_widgets(self):
        frame_url = tk.LabelFrame(self.root, text="File URL", padx=10, pady=10)
        frame_url.pack(fill="x", padx=10, pady=5)

        entry_url = tk.Entry(frame_url, textvariable=self.url_var)
        entry_url.pack(fill="x")

        frame_path = tk.LabelFrame(self.root, text="Save PATH", padx=10, pady=10)
        frame_path.pack(fill="x", padx=10, pady=5)

        path_container = tk.Frame(frame_path)
        path_container.pack(fill="x")

        entry_path = tk.Entry(path_container, textvariable=self.path_var)
        entry_path.pack(side="left", fill="x", expand=True)

        btn_browse = tk.Button(path_container, text="Choose PATH", command=self.browse_file)
        btn_browse.pack(side="right", padx=(5, 0))

        frame_control = tk.Frame(self.root, padx=10, pady=10)
        frame_control.pack(fill="x", padx=10)

        self.btn_start = tk.Button(frame_control, text="DOWNLOAD", command=self.start_download_thread,
                                   font=("Arial", 10))
        self.btn_start.pack(fill="x", pady=5)

        self.progress_bar = ttk.Progressbar(frame_control, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=10)

        self.lbl_status = tk.Label(frame_control, textvariable=self.status_var, font=("Arial", 10))
        self.lbl_status.pack()

    def get_file_info(self, url):
        try:
            response = requests.head(url, allow_redirects=True)
            size = int(response.headers.get('content-length', 0))
            accept_ranges = response.headers.get('accept-ranges', 'none')
            return size, accept_ranges == 'bytes'
        except Exception as e:
            return 0, False

    def browse_file(self):
        filename = filedialog.asksaveasfilename(title="Save as")
        if filename:
            self.path_var.set(filename)


