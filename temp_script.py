from cart.models import CartItem

for item in CartItem.objects.all():
    print(f"Item ID: {item.id}")
    print(f"Product: {item.product.name}")
    print(f"Design File: {item.design_file}")
    print(f"File exists: {bool(item.design_file)}")
    if item.design_file:
        print(f"File path: {item.design_file.path}")
        print(f"File URL: {item.design_file.url}")
    print("-" * 50)
