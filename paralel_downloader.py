import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import threading
import os
from concurrent.futures import ThreadPoolExecutor


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

    def start_download_thread(self):
        if self.is_downloading:
            return

        url = self.url_var.get()
        path = self.path_var.get()

        if not url or not path:
            messagebox.showerror("Error", "You have to enter URL and PATH!")
            return

        self.is_downloading = True
        self.btn_start.config(state="disabled")
        threading.Thread(target=self.run_download, args=(url, path), daemon=True).start()

    def download_chunk(self, url, start, end, part_num, temp_filename):
        headers = {'Range': f'bytes={start}-{end}'}
        try:
            with requests.get(url, headers=headers, stream=True) as r:
                r.raise_for_status()
                with open(temp_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            self.downloaded_bytes += len(chunk)
                            self.update_progress()
        except Exception as e:
            print(f"Error with part {part_num}: {e}")

    def run_download(self, url, path):
        try:
            self.status_var.set("Zjišťuji informace o souboru...")
            file_size, support_ranges = self.get_file_info(url)
            self.total_size = file_size
            self.downloaded_bytes = 0

            cpu_count = os.cpu_count()
            self.status_var.set(f"Paralel download with {cpu_count} threads...")

            chunk_size = file_size // cpu_count
            ranges = []
            temp_files = []

            for i in range(cpu_count):
                start = i * chunk_size
                end = start + chunk_size - 1 if i < cpu_count - 1 else file_size
                temp_name = f"{path}.part{i}"
                ranges.append((start, end, i, temp_name))
                temp_files.append(temp_name)

            with ThreadPoolExecutor(max_workers=cpu_count) as executor:
                futures = [
                    executor.submit(self.download_chunk, url, r[0], r[1], r[2], r[3])
                    for r in ranges
                ]
                for future in futures:
                    future.result()

            self.status_var.set("Merging downloaded parts...")
            with open(path, 'wb') as outfile:
                for temp_file in temp_files:
                    with open(temp_file, 'rb') as infile:
                        outfile.write(infile.read())
                    os.remove(temp_file)

            self.status_var.set("Done! File successfully downloaded.")
            self.progress_var.set(100)
            messagebox.showinfo("Done", "Download completed.")

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.is_downloading = False
            self.btn_start.config(state="normal")

    def update_progress(self):
        if self.total_size > 0:
            percentage = (self.downloaded_bytes / self.total_size) * 100
            self.progress_var.set(percentage)
            self.status_var.set(
                f"Download: {percentage:.1f}% ({self.downloaded_bytes // 1024 // 1024} MB / {self.total_size // 1024 // 1024} MB)")