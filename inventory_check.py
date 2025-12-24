import os

root_path = r"D:\web_proyects\imprenta_gallito\static\media\product_images\postales_publicidad"
with open('images_list.txt', 'w') as f:
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                f.write(os.path.join(root, file) + '\n')

print("Images listed to images_list.txt")

# Check for excel
excel_path = r"D:\web_proyects\imprenta_gallito\products_complete.xlsx"
if os.path.exists(excel_path):
    print(f"Found Excel: {excel_path}")
else:
    print(f"Excel NOT found at: {excel_path}")
    # List dir
    print("Files in root:")
    for f in os.listdir(r"D:\web_proyects\imprenta_gallito"):
        if 'product' in f.lower() and 'xlsx' in f.lower():
            print(f)
