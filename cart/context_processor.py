from django.core.exceptions import ObjectDoesNotExist

from cart.models import Cart, CartItem



def cart_items_counter(request):
    cart_id = request.COOKIES.get("cart_id")
    return {'cart_items_counter': CartItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()}
