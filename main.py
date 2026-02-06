import os
import random
import sys
from PIL import Image

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None
    filedialog = None

customImages = ""
jackboxImages = ""

if not customImages or not jackboxImages:
    if tk and filedialog:
        root = tk.Tk()
        root.withdraw()
        if not customImages:
            print("The next window will ask you to select the folder containing your custom images.")
            customImages = filedialog.askdirectory(title="Select Custom Images Folder")
            if not customImages:
                print("No custom images folder selected. Exiting.")
                sys.exit(1)
        if not jackboxImages:
            print("The next window will ask you to select the folder containing the Jackbox images (the main STIPhoto directory).")
            jackboxImages = filedialog.askdirectory(title="Select Jackbox Images Folder")
            if not jackboxImages:
                print("No jackbox images folder selected. Exiting.")
                sys.exit(1)
    else:
        print("Tkinter not available for folder selection. Using input instead.")
        if not customImages:
            customImages = input("Enter path to custom images folder: ").strip()
            if not customImages:
                print("No custom images folder provided. Exiting.")
                sys.exit(1)
        if not jackboxImages:
            jackboxImages = input("Enter path to jackbox images folder (the main STIPhoto directory): ").strip()
            if not jackboxImages:
                print("No jackbox images folder provided. Exiting.")
                sys.exit(1)

if not os.path.isdir(customImages):
    print(f"Custom images folder does not exist: {customImages}. Exiting.")
    sys.exit(1)

if not os.path.isdir(jackboxImages):
    print(f"Jackbox images folder does not exist: {jackboxImages}. Exiting.")
    sys.exit(1)

jackboxImagesThumbnail = os.path.join(jackboxImages, "Thumbnails")

if not os.path.isdir(jackboxImagesThumbnail):
    print(f"Thumbnails folder does not exist: {jackboxImagesThumbnail}. Continuing without thumbnails.")

valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

folder1_images = sorted([f for f in os.listdir(customImages) if f.lower().endswith(valid_exts)])

available_main = [f for f in os.listdir(jackboxImages) if f.lower().endswith(valid_exts)]
available_thumb = [f for f in os.listdir(jackboxImagesThumbnail) if f.lower().endswith(valid_exts)] if os.path.isdir(jackboxImagesThumbnail) else []

for source_filename in folder1_images:
    source_path = os.path.join(customImages, source_filename)
    
    try:
        src_img = Image.open(source_path)
    except Exception as e:
        print(f"Error opening source image {source_filename}: {e}")
        continue
    
    target_filename = None
    replace_main = False
    replace_thumb = False
    mod_time_main = None
    target_size_main = None
    mod_time_thumb = None
    target_size_thumb = None
    
    if available_main:
        target_filename = random.choice(available_main)
        available_main.remove(target_filename)
        
        target_path_folder2 = os.path.join(jackboxImages, target_filename)
        
        if os.path.exists(target_path_folder2):
            try:
                mod_time_main = os.path.getmtime(target_path_folder2)
            except Exception as e:
                print(f"Error getting modification time for main {target_filename}: {e}")
            
            try:
                with Image.open(target_path_folder2) as target_img_main:
                    target_size_main = target_img_main.size
                    replace_main = True
            except Exception as e:
                print(f"Error opening main target image {target_filename}: {e}")
        
        # Check for corresponding thumbnail
        target_path_folder3 = os.path.join(jackboxImagesThumbnail, target_filename)
        if target_filename in available_thumb and os.path.exists(target_path_folder3):
            try:
                mod_time_thumb = os.path.getmtime(target_path_folder3)
            except Exception as e:
                print(f"Error getting modification time for thumbnail {target_filename}: {e}")
            
            try:
                with Image.open(target_path_folder3) as target_img_thumb:
                    target_size_thumb = target_img_thumb.size
                    replace_thumb = True
            except Exception as e:
                print(f"Error opening thumbnail target image {target_filename}: {e}")
            
            if replace_thumb:
                available_thumb.remove(target_filename)
    
    elif available_thumb:
        target_filename = random.choice(available_thumb)
        available_thumb.remove(target_filename)
        
        target_path_folder3 = os.path.join(jackboxImagesThumbnail, target_filename)
        
        if os.path.exists(target_path_folder3):
            try:
                mod_time_thumb = os.path.getmtime(target_path_folder3)
            except Exception as e:
                print(f"Error getting modification time for thumbnail {target_filename}: {e}")
            
            try:
                with Image.open(target_path_folder3) as target_img_thumb:
                    target_size_thumb = target_img_thumb.size
                    replace_thumb = True
            except Exception as e:
                print(f"Error opening thumbnail target image {target_filename}: {e}")
    
    else:
        print("No more available images in jackboxImages or Thumbnails to match with.")
        src_img.close()
        break
    
    if target_filename is None or (not replace_main and not replace_thumb):
        print(f"No valid replacement targets for {source_filename}. Skipping.")
        src_img.close()
        continue
    
    try:
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.ANTIALIAS
        
        if replace_main and target_size_main:
            resized_main = src_img.resize(target_size_main, resample_filter)
            resized_main.save(target_path_folder2)
            if mod_time_main is not None:
                os.utime(target_path_folder2, (mod_time_main, mod_time_main))
        
        if replace_thumb and target_size_thumb:
            resized_thumb = src_img.resize(target_size_thumb, resample_filter)
            resized_thumb.save(target_path_folder3)
            if mod_time_thumb is not None:
                os.utime(target_path_folder3, (mod_time_thumb, mod_time_thumb))
        
        replaced_parts = []
        if replace_main:
            replaced_parts.append("jackboxImages")
        if replace_thumb:
            replaced_parts.append("jackboxImagesThumbnail")
        print(f"Replaced '{target_filename}' with resized '{source_filename}' in {', '.join(replaced_parts)}.")
    
    except Exception as e:
        print(f"Error processing and saving for {target_filename}: {e}")
    
    src_img.close()

print("Processing complete.")
