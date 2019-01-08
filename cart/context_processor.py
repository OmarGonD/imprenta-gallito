from django.core.exceptions import ObjectDoesNotExist

from cart.models import Cart, CartItem
from cart.views import _cart_id


def cart_items_counter(request):
    cart_items_counter = 0

    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart)
        for cart_item in cart_items:
            cart_items_counter += 1

    except ObjectDoesNotExist:
        pass

    return {'cart_items_counter': cart_items_counter}


