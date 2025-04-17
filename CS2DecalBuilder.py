import os
import shutil
import random
import string
import json
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox


def generate_random_digits(length=3):
    return ''.join(random.choices(string.digits, k=length))


def get_mesh_size(width, height):
    def round_mesh(x):
        return int(round(x))

    mesh_base = 4
    ratio = width / height
    if ratio >= 1:
        x = round_mesh(mesh_base * ratio)
        z = mesh_base
    else:
        x = mesh_base
        z = round_mesh(mesh_base / ratio)

    return x, z


def safe_texture_resize(img, min_size=512):
    width, height = img.size
    safe_width = max(min_size, ((width + 3) // 4) * 4)
    safe_height = max(min_size, ((height + 3) // 4) * 4)

    if (width, height) != (safe_width, safe_height):
        print(f"[RESIZE] Resizing from {width}x{height} → {safe_width}x{safe_height}")
        new_img = Image.new("RGBA", (safe_width, safe_height), (0, 0, 0, 0))
        new_img.paste(img, ((safe_width - width) // 2, (safe_height - height) // 2))
        return new_img, safe_width, safe_height
    return img, width, height


def process_images(src_folder, dest_folder, template_path, prefix):
    print(f"[INFO] Starting processing:\n  Source: {src_folder}\n  Destination: {dest_folder}\n  Template: {template_path}\n  Prefix: {prefix}")
    for root, _, files in os.walk(src_folder):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext not in ['.png', '.jpg', '.jpeg']:
                continue

            try:
                file_path = os.path.join(root, file)
                print(f"[INFO] Processing file: {file_path}")
                img = Image.open(file_path)
                img = img.convert("RGBA")
                img, width, height = safe_texture_resize(img)

                random_suffix = generate_random_digits()
                folder_name = f"{prefix}{random_suffix}"
                output_folder = os.path.join(dest_folder, folder_name)
                os.makedirs(output_folder, exist_ok=True)

                new_image_path = os.path.join(output_folder, "_BaseColorMap.png")
                img.save(new_image_path, format="PNG")
                print(f"[OK] Saved image: {new_image_path}")

                with open(template_path, 'r') as f:
                    template = json.load(f)

                mesh_x, mesh_z = get_mesh_size(width, height)
                template["Vector"]["colossal_MeshSize"]["x"] = mesh_x
                template["Vector"]["colossal_MeshSize"]["z"] = mesh_z

                decal_path = os.path.join(output_folder, "decal.json")
                with open(decal_path, 'w') as f:
                    json.dump(template, f, indent=4)

                print(f"[OK] Saved decal JSON: {decal_path}")

            except Exception as e:
                print(f"[ERROR] Failed to process {file}: {e}")


# --- GUI SETUP --- #
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


def start_processing(src_entry, dest_entry, tmpl_entry, prefix_entry):
    src = src_entry.get().strip()
    dest = dest_entry.get().strip()
    tmpl = tmpl_entry.get().strip()
    prefix = prefix_entry.get().strip()

    if not all([src, dest, tmpl, prefix]):
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    process_images(src, dest, tmpl, prefix)
    messagebox.showinfo("Done", "Processing complete!")


def main_gui():
    root = tk.Tk()
    root.title("Decal Image Processor")

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

    # Prefix row (no browse)
    prefix_label = tk.Label(root, text="Prefix:")
    prefix_label.grid(row=3, column=0, sticky="e", padx=5, pady=5)

    prefix_entry = tk.Entry(root, width=50)
    prefix_entry.grid(row=3, column=1, padx=5, pady=5, columnspan=2)

    # Start button
    start_button = tk.Button(root, text="Start Processing", command=lambda: start_processing(src_entry, dest_entry, tmpl_entry, prefix_entry))
    start_button.grid(row=4, column=0, columnspan=3, pady=15)

    root.mainloop()


if __name__ == "__main__":
    main_gui()
