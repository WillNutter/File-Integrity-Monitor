import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import hashlib
import os
import json
from datetime import datetime

class FileIntegrityMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("File Integrity Monitor")

        self.path = ""
        self.baseline_file = "baseline_data/baseline.json"
        os.makedirs("baseline_data", exist_ok=True)

        # GUI Elements
        self.text = tk.Text(root, wrap='word', height=20, width=80)
        self.text.pack(pady=10)

        frame = tk.Frame(root)
        frame.pack()

        tk.Button(frame, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Create Baseline", command=self.create_baseline).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Compare", command=self.compare_files).pack(side=tk.LEFT, padx=5)

        # Hash type selection
        self.hash_type = tk.StringVar(value="sha256")
        hash_menu = ttk.Combobox(frame, textvariable=self.hash_type, values=["md5", "sha1", "sha256", "sha512"])
        hash_menu.pack(side=tk.LEFT, padx=5)

    def select_folder(self):
        self.path = filedialog.askdirectory()
        self.text.insert(tk.END, f"Selected path: {self.path}
")

    def compute_hashes(self, directory):
        file_hashes = {}
        algo = getattr(hashlib, self.hash_type.get(), hashlib.sha256)

        for root, _, files in os.walk(directory):
            for name in files:
                filepath = os.path.join(root, name)
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = algo(f.read()).hexdigest()
                    file_hashes[os.path.relpath(filepath, directory)] = {
                        "hash": file_hash,
                        "timestamp": os.path.getmtime(filepath)
                    }
                except Exception as e:
                    self.text.insert(tk.END, f"Error reading {filepath}: {e}\n")
        return file_hashes

    def create_baseline(self):
        if not self.path:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        baseline = self.compute_hashes(self.path)
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline, f, indent=4)
        self.text.insert(tk.END, "Baseline created successfully.\n")

    def compare_files(self):
        if not self.path:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        try:
            with open(self.baseline_file, 'r') as f:
                old_hashes = json.load(f)
        except FileNotFoundError:
            self.text.insert(tk.END, "No baseline found. Create one first.\n")
            return

        new_hashes = self.compute_hashes(self.path)
        changes = []

        for file, info in new_hashes.items():
            if file not in old_hashes:
                changes.append(f"New file: {file}")
            elif old_hashes[file]["hash"] != info["hash"]:
                changes.append(f"Modified: {file}")

        for file in old_hashes:
            if file not in new_hashes:
                changes.append(f"Deleted: {file}")

        if changes:
            self.text.insert(tk.END, "Changes detected:\n" + "\n".join(changes) + "\n")
        else:
            self.text.insert(tk.END, "No changes detected.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileIntegrityMonitor(root)
    root.mainloop()
