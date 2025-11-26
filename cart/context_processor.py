from django.core.exceptions import ObjectDoesNotExist

from cart.models import Cart, CartItem, SampleItem, PackItem, UnitaryProductItem


def cart_items_counter(request):
    cart_id = request.COOKIES.get("cart_id")
    cart_items_count = CartItem.objects.filter(cart_id=cart_id).count()
    sample_items_count = SampleItem.objects.filter(cart_id=cart_id).count()
    pack_items_count = PackItem.objects.filter(cart_id=cart_id).count()
    unitary_product_items_count = UnitaryProductItem.objects.filter(cart_id=cart_id).count()

    total_items = cart_items_count + sample_items_count + pack_items_count + unitary_product_items_count

    return {'cart_items_counter': total_items}
