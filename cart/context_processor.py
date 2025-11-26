from django.core.exceptions import ObjectDoesNotExist

from cart.models import Cart, CartItem


def cart_items_counter(request):
    cart_id = request.COOKIES.get("cart_id")
    cart_items_count = CartItem.objects.filter(cart_id=cart_id).count()

    total_items = cart_items_count
    return {'cart_items_counter': total_items}
