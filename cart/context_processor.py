from django.core.exceptions import ObjectDoesNotExist

from cart.models import Cart, CartItem, SampleItem, PackItem


def cart_items_counter(request):
    cart_id = request.COOKIES.get("cart_id")
    cart_items_count = CartItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
    sample_items_count = SampleItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
    pack_items_count = PackItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()

    total_items = cart_items_count + sample_items_count + pack_items_count

    return {'cart_items_counter': total_items}
