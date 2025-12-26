import os
import shutil

source_dir = r"D:\web_proyects\imprenta_gallito\static\media\product_images\ropa_y_bolsos\polos"
dest_dir = r"D:\web_proyects\imprenta_gallito\static\media\product_images\ropa_y_bolsos\bibidis"

# Ensure destination directory exists
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
    print(f"Created directory: {dest_dir}")

count = 0
for filename in os.listdir(source_dir):
    if "tank-top" in filename.lower():
        src_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        
        try:
            shutil.move(src_path, dest_path)
            print(f"Moved: {filename}")
            count += 1
        except Exception as e:
            print(f"Error moving {filename}: {e}")

print(f"Finished. Moved {count} files.")
