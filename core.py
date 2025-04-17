# core.py

import os
import random
import string
import json
import logging
from PIL import Image

SETTINGS_FILE = "cs2decalbuilder_settings.json"

CATEGORIES = [
    "Alphabet", "Beach", "Graffiti", "Ground", "Industry", "Leaf",
    "Misc", "Numbers", "Parking", "Puddles", "RoadAssets",
    "RoadMarkings", "Stains", "Trash", "WallDecor"
]

def generate_random_digits(length=3):
    return ''.join(random.choices(string.digits, k=length))

def get_mesh_size(width, height):
    mesh_base = 4
    ratio = width / height
    if ratio >= 1:
        x = round(mesh_base * ratio)
        z = mesh_base
    else:
        x = mesh_base
        z = round(mesh_base / ratio)
    return x, z

def safe_texture_resize(img, min_size=512):
    width, height = img.size
    safe_width = max(min_size, ((width + 3) // 4) * 4)
    safe_height = max(min_size, ((height + 3) // 4) * 4)
    if (width, height) != (safe_width, safe_height):
        logging.info(f"[RESIZE] Resizing from {width}x{height} → {safe_width}x{safe_height}")
        new_img = Image.new("RGBA", (safe_width, safe_height), (0, 0, 0, 0))
        new_img.paste(img, ((safe_width - width) // 2, (safe_height - height) // 2))
        return new_img, safe_width, safe_height
    return img, width, height

def process_images(src_folder, dest_folder, template_path, prefix, category, progress_cb=None):
    logging.info(f"[INFO] Starting processing:\n  Source: {src_folder}\n  Destination: {dest_folder}\n  Template: {template_path}\n  Prefix: {prefix}\n  Category: {category}")

    failed_files = []
    files_to_process = [f for r, _, fs in os.walk(src_folder) for f in fs if os.path.splitext(f)[1].lower() in ['.png', '.jpg', '.jpeg']]
    total_files = len(files_to_process)

    for i, file in enumerate(files_to_process):
        try:
            file_path = os.path.join(src_folder, file)
            logging.info(f"[INFO] Processing file: {file_path}")
            img = Image.open(file_path).convert("RGBA")
            img, width, height = safe_texture_resize(img)
            random_suffix = generate_random_digits()
            folder_name = f"{prefix}{random_suffix}"

            output_folder = os.path.join(dest_folder, category, folder_name)
            os.makedirs(output_folder, exist_ok=True)

            new_image_path = os.path.join(output_folder, "_BaseColorMap.png")
            img.save(new_image_path, format="PNG")
            logging.info(f"[OK] Saved image: {new_image_path}")

            with open(template_path, 'r') as f:
                template = json.load(f)

            mesh_x, mesh_z = get_mesh_size(width, height)
            logging.debug(f"[MESH] Set MeshSize x={mesh_x}, z={mesh_z} for: {file}")
            template["Vector"]["colossal_MeshSize"]["x"] = mesh_x
            template["Vector"]["colossal_MeshSize"]["z"] = mesh_z

            decal_path = os.path.join(output_folder, "decal.json")
            with open(decal_path, 'w') as f:
                json.dump(template, f, indent=4)

            logging.info(f"[OK] Saved decal JSON: {decal_path}")

        except Exception as e:
            logging.error(f"[ERROR] Failed to process {file}: {e}")
            failed_files.append(file)

        if progress_cb:
            progress_cb(i + 1, total_files)

    return failed_files

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}
