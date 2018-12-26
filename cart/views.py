from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product
from .models import Cart, SizeQuantity, Transactions
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from order.models import Order, OrderItem
import uuid
import culqipy
import os
from django.views.decorators.csrf import csrf_exempt



# Create your views here.

def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        request.session.create()  # it does not return anything. that is why `cart = request.session.create()` will not work
        cart = request.session.session_key
    return cart  # Ultimately return cart


#
# def add_cart(request, product_id):
#     product = Product.objects.get(id = product_id)
#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#     except Cart.DoesNotExist:
#         cart = Cart.objects.create(
#             cart_id = _cart_id(request)
#         )
#
#         cart.save()
#     try:
#         cart_item = CartItem.objects.get(product = product, cart = cart)
#         if cart_item.quantity < cart_item.product.stock:
#             cart_item.quantity += 1
#         cart_item.save()
#     except CartItem.DoesNotExist:
#         cart_item = CartItem.objects.create(
#             product = product,
#             quantity= 1,
#             cart = cart,
#         )
#         cart_item.save()
#     return redirect('cart:cart_detail')



# def add_cart(request, sizequantity_id):
#     sizequantity = SizeQuantity.objects.get(id = sizequantity_id)
#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#     except Cart.DoesNotExist:
#         cart = Cart.objects.create(
#             cart_id = _cart_id(request)
#         )
#
#         cart.save()
#
#     cart_item = SizeQuantity.objects.get(sizequantity = sizequantity, cart = cart)
#         # if cart_item.quantity < cart_item.product.stock:
#         #     cart_item.quantity += 1
#     cart_item.save()
#     # except CartItem.DoesNotExist:
#     #     cart_item = CartItem.objects.create(
#     #         sizequantity = sizequantity,
#     #         # quantity= 1,
#     #         cart = cart,
#     #     )
#         cart_item.save()
#     return redirect('cart:cart_detail')



# def cart_detail(request, total = 0, counter = 0, cart_items = None):
#     try:
#         cart = Cart.objects.get(cart_id = _cart_id(request))
#         cart_items = SizeQuantity.objects.filter(cart = cart)
#         for cart_item in cart_items:
#             total += (cart_item.product.price * 2)
#
#
#     except ObjectDoesNotExist:
#         pass
#
#
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     stripe_total = int(total * 100)
#     description = "Stickers Gallito - Nueva orden"
#     data_key = settings.STRIPE_PUBLISHABLE_KEY
#
#
#     if request.method == 'POST':
#         print ("StripToken:")
#         print(request.POST)
#         try:
#             token = request.POST['stripeToken']
#             email = request.POST['stripeEmail']
#             print("This is the token: " + token)
#             print("This is the user's email: " + email)
#             customer = stripe.Customer.create(
#                 email = email,
#                 source = token
#             )
#             charge = stripe.Charge.create(
#                 amount = stripe_total,
#                 currency = "pen",
#                 description = description,
#                 customer = customer.id,
#             )
#         except stripe.error.CardError as e:
#             return False, e
#
#
#     return render(request, 'cart.html', dict(cart_items = cart_items, total = total, counter = counter, data_key = data_key,
#                                              stripe_total = stripe_total, description = description))
#

    #
    # return render(request, 'cart.html', dict(cart_items = cart_items, total = total, counter = counter, data_key = data_key,
    #                                          culqi_total = culqi_total, description = description))
    #
    #




def full_remove(request, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    cart_item = SizeQuantity.objects.get(id=cart_item_id, cart=cart)
    cart_item.delete()

    return redirect('cart:cart_detail')



### CULQI PAYMENT ###

@csrf_exempt
def cart_charge(request):

    print("CART CHARGEEEE!!!")

    culqipy.public_key = settings.CULQI_PUBLISHABLE_KEY
    culqipy.secret_key = settings.CULQI_SECRET_KEY

    print("This is request POST:")
    print(request.POST)
    print("This is the AJAX PART")
    amount = request.POST.get('amount')
    currency_code = request.POST.get('currency_code')
    email = request.POST.get('email')
    source_id = request.POST.get('source_id')
    last_four = request.POST.get('last_four')

    print("Amount from AJAX (POST):" + str(amount))
    print("Currency Code from AJAX (POST):" + str(currency_code))
    print("Email: " + str(email))
    print("Source_ID: " + str(source_id))

    print("---------")

    dir_charge = {"amount": int(amount), "currency_code": currency_code,
                  "email": email,
                  "source_id": source_id}

    print(dir_charge)

    charge = culqipy.Charge.create(dir_charge)
    print("Charge: ")
    print(charge)
    print("Charge ID: ")
    print(charge['id'])
    print(charge['amount'])

    transaction_amount = int(charge['amount'])/100 #Necesario dividir entre 100 para obtener el monto real,
                                                   #Esto debido a cómo Culqi recibe los datos de los pagos

    transaction = Transactions.objects.create(
        charge_id = charge['id'],
        last_four = last_four,
        email = email,
        amount = transaction_amount,

    )

    transaction.save()

    return HttpResponse('Hi')



def cart_detail(request, total = 0, counter = 0, cart_items = None):



    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = SizeQuantity.objects.filter(cart = cart)
        for cart_item in cart_items:
            total += (cart_item.product.price)



    except ObjectDoesNotExist:
        pass



    culqi_my_public_key = settings.CULQI_PUBLISHABLE_KEY #Es necesario mandar la llave pública para generar un token
    culqi_total = int(total * 100) #El total para cualqui debe multiplicarse por 100



    return render(request, 'cart.html', dict(cart_items = cart_items, total = total, counter = counter,
                                             culqi_total = culqi_total, culqi_my_public_key = culqi_my_public_key))




def thank_you(request):

    order_number = Transactions.objects.latest('transaction_id').transaction_id

    return render(request, 'thank-you.html', dict(order_number=order_number))