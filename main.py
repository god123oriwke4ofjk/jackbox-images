
import os
import random
import shutil
from PIL import Image

# Set your folder paths here
customImages = "folder1"
jackboxImages = "folder2"
jackboxImagesThumbnail = "folder3"

valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

folder1_images = sorted([f for f in os.listdir(folder1) if f.lower().endswith(valid_exts)])
folder2_images = sorted([f for f in os.listdir(folder2) if f.lower().endswith(valid_exts)])

available_names = folder2_images.copy()

for source_filename in folder1_images:
    if not available_names:
        print("No more available images in folder2/3 to match with.")
        break

    target_filename = random.choice(available_names)
    available_names.remove(target_filename)

    source_path = os.path.join(folder1, source_filename)
    target_path_folder2 = os.path.join(folder2, target_filename)
    target_path_folder3 = os.path.join(folder3, target_filename)

    try:
        with Image.open(target_path_folder2) as target_img:
            target_size = target_img.size  
    except Exception as e:
        print(f"Error opening target image {target_filename} from folder2: {e}")
        continue

    try:
        mod_time = os.path.getmtime(target_path_folder2)
    except Exception as e:
        print(f"Error getting modification time for {target_filename}: {e}")
        mod_time = None

    try:
        with Image.open(source_path) as src_img:
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.ANTIALIAS  

            resized_img = src_img.resize(target_size, resample_filter)
            new_source_path = os.path.join(folder1, target_filename)
            resized_img.save(new_source_path)
    except Exception as e:
        print(f"Error processing source image {source_filename}: {e}")
        continue

    if mod_time:
        os.utime(new_source_path, (mod_time, mod_time))

    try:
        shutil.copy2(new_source_path, target_path_folder2)
        shutil.copy2(new_source_path, target_path_folder3)
    except Exception as e:
        print(f"Error copying new image {target_filename} to folder2/3: {e}")
        continue

    print(f"Replaced '{target_filename}' in folder2 and folder3 with resized '{source_filename}' from folder1.")

print("Processing complete.")
