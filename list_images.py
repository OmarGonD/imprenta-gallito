import os

root_path = r"D:\web_proyects\imprenta_gallito\static\media\product_images\postales_publicidad"
for root, dirs, files in os.walk(root_path):
    for file in files:
        if file.lower().endswith(('.jpg', '.png', '.jpeg')):
            print(os.path.join(root, file))
