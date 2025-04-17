# gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
import argparse

from core import process_images, save_settings, load_settings, CATEGORIES

# --- Logging & Argument Setup ---
parser = argparse.ArgumentParser(description="CS2 Decal Builder GUI")
parser.add_argument("--debug", action="store_true", help="Enable debug output")
parser.add_argument("--logfile", type=str, default="process.log", help="Custom log file name")
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(
    filename=args.logfile,
    filemode='w',
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if args.debug:
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

# --- GUI Logic ---
def browse_folder(entry):
    folder = filedialog.askdirectory()
    if folder:
        entry.delete(0, tk.END)
        entry.insert(0, folder)

def browse_file(entry):
    file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file:
        entry.delete(0, tk.END)
        entry.insert(0, file)

def start_processing(src_entry, dest_entry, tmpl_entry, prefix_entry, category_var, progress, status_label):
    src = src_entry.get().strip()
    dest = dest_entry.get().strip()
    tmpl = tmpl_entry.get().strip()
    prefix = prefix_entry.get().strip()
    category = category_var.get()

    if not all([src, dest, tmpl, prefix, category]):
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    def update_progress(current, total):
        progress["value"] = (current / total) * 100
        status_label["text"] = f"Processing {current}/{total}"
        root.update_idletasks()

    failed = process_images(src, dest, tmpl, prefix, category, progress_cb=update_progress)
    if failed:
        messagebox.showerror("Some files failed", f"Failed to process these files:\n{chr(10).join(failed)}")
    else:
        messagebox.showinfo("Done", "Processing complete!")

    save_settings({
        "src": src,
        "dest": dest,
        "tmpl": tmpl,
        "prefix": prefix,
        "category": category
    })

def main_gui():
    global root
    root = tk.Tk()
    root.title("CS2 Decal Builder")

    settings = load_settings()

    def create_row(label_text, row, browse_func=None):
        label = tk.Label(root, text=label_text)
        label.grid(row=row, column=0, sticky="e", padx=5, pady=5)
        entry = tk.Entry(root, width=50)
        entry.grid(row=row, column=1, padx=5, pady=5)
        if browse_func:
            button = tk.Button(root, text="Browse...", command=lambda: browse_func(entry))
            button.grid(row=row, column=2, padx=5, pady=5)
        return entry

    src_entry = create_row("Source Folder:", 0, browse_folder)
    dest_entry = create_row("Destination Folder:", 1, browse_folder)
    tmpl_entry = create_row("Template JSON:", 2, browse_file)

    prefix_label = tk.Label(root, text="Prefix:")
    prefix_label.grid(row=3, column=0, sticky="e", padx=5, pady=5)
    prefix_entry = tk.Entry(root, width=50)
    prefix_entry.grid(row=3, column=1, padx=5, pady=5, columnspan=2)

    cat_label = tk.Label(root, text="Category:")
    cat_label.grid(row=4, column=0, sticky="e", padx=5, pady=5)
    category_var = tk.StringVar(root)
    cat_menu = ttk.Combobox(root, textvariable=category_var, values=CATEGORIES, state="readonly")
    cat_menu.grid(row=4, column=1, padx=5, pady=5, columnspan=2)

    progress = ttk.Progressbar(root, length=300)
    progress.grid(row=5, column=0, columnspan=3, padx=5, pady=10)
    status_label = tk.Label(root, text="")
    status_label.grid(row=6, column=0, columnspan=3)

    start_button = tk.Button(
        root,
        text="Start Processing",
        command=lambda: start_processing(src_entry, dest_entry, tmpl_entry, prefix_entry, category_var, progress, status_label)
    )
    start_button.grid(row=7, column=0, columnspan=3, pady=15)

    if settings:
        src_entry.insert(0, settings.get("src", ""))
        dest_entry.insert(0, settings.get("dest", ""))
        tmpl_entry.insert(0, settings.get("tmpl", ""))
        prefix_entry.insert(0, settings.get("prefix", ""))
        category_var.set(settings.get("category", ""))

    root.mainloop()

if __name__ == "__main__":
    main_gui()
