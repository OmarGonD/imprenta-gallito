from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
import json
from django.core.serializers import serialize

# Create your views here.


def thanks_credit_card(request):
    order_number = Order.objects.latest('id').id

    total = Order.objects.latest('id').total

    costo_despacho = Order.objects.latest('id').shipping_cost

    order_items = OrderItem.objects.filter(order=Order.objects.latest('id'))

    order_items = serialize('json', order_items, fields=['id', 'sku', 'name', 'price', 'size', 'quantity'])

    response = render(request, 'thanks_credit_card.html', dict(order_number=order_number, total=total,
                                                                   order_items=order_items,
                                                                   costo_despacho=costo_despacho))
    return response


def thanks_deposit_payment(request):
    order_number = Order.objects.latest('id').id

    total = Order.objects.latest('id').total

    costo_despacho = Order.objects.latest('id').shipping_cost

    order_items = OrderItem.objects.filter(order=Order.objects.latest('id'))


    order_items = serialize('json', order_items, fields=['id', 'sku', 'name', 'price', 'size', 'quantity'])



    response = render(request, 'thanks_deposit_payment.html', dict(order_number=order_number, total=total,
                                                                   order_items=order_items, costo_despacho=costo_despacho))
    return response



@login_required()
def orderHistory(request):
    if request.user.is_authenticated:
        email = str(request.user.email)
        print(email)
        order_details = Order.objects.filter(email=email)
        # order_details = get_object_or_404(Order, emailAddress=email)
        if not order_details:
            print("No hay orden")
        else:
            order_details
            print("Hay orden")
            print(order_details)
    return render(request, 'order/orders_list.html', {'order_details': order_details})


@login_required()
def viewOrder(request, order_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order = Order.objects.get(id = order_id, email=email)
        order_items = OrderItem.objects.filter(order = order)
    return render(request, 'order/order_detail.html', {'order': order,
                                                       'order_items': order_items})


