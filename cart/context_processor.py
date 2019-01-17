from django.core.exceptions import ObjectDoesNotExist

from cart.models import Cart, CartItem
from cart.views import _cart_id


def cart_items_counter(request):
    cart_id = request.COOKIES.get("cart_id")
    return {'cart_items_counter': CartItem.objects.filter(cart_id=cart_id).count()}
