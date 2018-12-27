from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem, Transactions
from django.contrib.auth.decorators import login_required

# Create your views here.


def thanks(request):

    order_number = Transactions.objects.latest('transaction_id').transaction_id

    return render(request, 'thanks.html', dict(order_number=order_number))



@login_required()
def orderHistory(request):
    if request.user.is_authenticated:
        email = str(request.user.email)
        print(email)
        order_details = Transactions.objects.filter(email=email)
        # order_details = get_object_or_404(Order, emailAddress=email)
        if not order_details:
            print("No hay orden")
        else:
            print("Hay orden")
    return render(request, 'order/orders_list.html', {'order_details': order_details})


@login_required()
def viewOrder(request, order_id):
    if request.user.is_authenticated:
        # email = str(request.user.email)
        email = "tester2@gmail.com"
        order = Order.objects.get(id = order_id, emailAddress=email)
        order_items = OrderItem.objects.filter(order = order)
    return render(request, 'order/order_detail.html', {'order': order,
                                                       'order_items': order_items})


