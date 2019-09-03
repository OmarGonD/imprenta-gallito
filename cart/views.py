from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product, Category, Peru
from .models import Cart, CartItem, SampleItem
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from order.models import Order, OrderItem
from marketing.models import used_cupons
import uuid
import culqipy
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.template.loader import get_template
from django.core.mail import EmailMessage
from marketing.models import Cupons


# Create your views here.

def full_remove(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()

    return redirect('carrito_de_compras:cart_detail')


def full_remove_sample(request, sample_item_id):
    sample_item = SampleItem.objects.get(id=sample_item_id)
    sample_item.delete()

    return redirect('carrito_de_compras:cart_detail')


### CULQI PAYMENT ###

@csrf_exempt
def cart_charge_credit_card(request):

    if request.POST.get('payment_method') == 'credit_card_payment':
        
        culqipy.public_key = settings.CULQI_PUBLISHABLE_KEY
        culqipy.secret_key = settings.CULQI_SECRET_KEY
        amount = request.POST.get('amount')
        currency_code = request.POST.get('currency_code')
        email = request.POST.get('email')
        source_id = request.POST.get('source_id')
        last_four = request.POST.get('last_four')
        shipping_address = request.POST.get('shipping_address')
        shipping_cost = request.POST.get('shipping_cost')

        dir_charge = {"amount": int(amount), "currency_code": currency_code,
                      "email": email,
                      "source_id": source_id}

        print(dir_charge)

        charge = culqipy.Charge.create(dir_charge)
        if not charge:
            print("No se generó CHARGE")

        transaction_amount = int(charge['amount']) / 100  # Necesario dividir entre 100 para obtener el monto real,
        # Esto debido a cómo Culqi recibe los datos de los pagos

        first_name = request.user.first_name

        last_name = request.user.last_name

        phone_number = request.user.profile.phone_number

        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        shipping_address1 = request.user.profile.shipping_address1

        reference = request.user.profile.reference

        shipping_department = request.user.profile.shipping_department

        shipping_province = request.user.profile.shipping_province

        shipping_district = request.user.profile.shipping_district

        order_details = Order.objects.create(
            token=charge['id'],
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,  # Using email entered in Culqi module, NOT user.email. Could be diff.
            total=transaction_amount,
            shipping_cost=shipping_cost,
            last_four=last_four,
            created=current_time,
            shipping_address=shipping_address,
            shipping_address1=shipping_address1,
            reference=reference,
            shipping_department=shipping_department,
            shipping_province=shipping_province,
            shipping_district=shipping_district,
            status='recibido_pagado'
        )

        order_details.save()
        print("La orden fue creada")

        try:
            cart_id = int(request.COOKIES.get("cart_id"))
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                pass

            cart_items = CartItem.objects.filter(cart=cart)

            for order_item in cart_items:
                oi = OrderItem.objects.create(
                    order=order_details,
                    name=order_item.product.name,
                    sku=order_item.product.sku,
                    quantity=order_item.quantity,
                    size=order_item.size,
                    price=order_item.product.price,
                    file_a=order_item.file_a,
                    file_b=order_item.file_b,
                    comment=order_item.comment,
                )
                try:
                    oi.save()
                except oi.DoesNotExist:
                    print("No se creo el Order ITEM")

            ### Sample ITEMS SAVE

            sample_items = SampleItem.objects.filter(cart=cart)

            for order_item in sample_items:
                oi = OrderItem.objects.create(
                    order=order_details,
                    name=order_item.sample.name,
                    sku=order_item.sample.sku,
                    quantity=order_item.quantity,
                    size=order_item.size,
                    price=order_item.sample.price,
                    file_a=order_item.file_a,
                    file_b=order_item.file_b,
                    comment=order_item.comment,
                )
                try:
                    oi.save()
                except oi.DoesNotExist:
                    print("No se creo el Order ITEM")

        except ObjectDoesNotExist:
            pass

        try:
            '''Calling send_email function'''
            send_email_credit_card(order_details.id)
            print("El correo de confirmación por la compra ha sido enviado al cliente")
        except IOError as e:
            return e

        try:

            cupon_name = request.COOKIES.get("cupon")

            cupon = Cupons.objects.get(cupon=cupon_name)

            
            cupon.quantity = cupon.quantity - 1

            cupon.save()

            used_cupon = used_cupons.objects.create(
                cupon=cupon,
                user=request.user.username,
                order=order_details
            )

            used_cupon.save()

        except:
            print("No se detectó cupón o no se pudo guardar cupón usado")
            pass

        response = HttpResponse("Hi")
        response.delete_cookie("cart_id")
        response.delete_cookie("cupon")

        return response


@csrf_exempt
def cart_charge_deposit_payment(request):
    # Pago con Efectivo
    amount = request.POST.get('amount')
    email = request.user.email
    shipping_address = request.POST.get('shipping_address')
    shipping_cost = request.POST.get('shipping_cost')
    discount = request.POST.get('discount')
    stickers_price = request.POST.get('stickers_price')

    last_four = 1111  # No necesario para Pagos con Efectivo, pero si para el Objeto Order
    transaction_amount = amount  # Solo para Culqi se divide entre 100
    
    print("### TRANSACTION AMAOUNT")
    print(transaction_amount)
    print(type(transaction_amount))

    first_name = request.user.first_name

    last_name = request.user.last_name

    phone_number = request.user.profile.phone_number

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    shipping_address1 = request.user.profile.shipping_address1

    reference = request.user.profile.reference

    shipping_department = request.user.profile.shipping_department

    shipping_province = request.user.profile.shipping_province

    shipping_district = request.user.profile.shipping_district

    
    
    ### searching for cupons ###

    try:

        cupon_name = request.COOKIES.get("cupon")

        cupon = Cupons.objects.get(cupon=cupon_name)

        cupon.quantity = cupon.quantity - 1

        cupon.save()

    except:
        print("No hay cupón, none")
        cupon = None

    ############################

    order_details = Order.objects.create(
        token='Random',
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,  # Using email entered in Culqi module, NOT user.email. Could be diff.
        total=transaction_amount,
        stickers_price = stickers_price,
        discount = discount,
        shipping_cost=shipping_cost,
        last_four=last_four,
        created=current_time,
        shipping_address=shipping_address,
        shipping_address1=shipping_address1,
        reference=reference,
        shipping_department=shipping_department,
        shipping_province=shipping_province,
        shipping_district=shipping_district,
        status='recibido_no_pagado',
        cupon=cupon
    )

    #order_details.save(commit=False)
    print("La orden fue creada")


    try:
        used_cupon = used_cupons.objects.create(
            cupon=cupon,
            user=request.user.username,
            order=order_details
        )

        used_cupon.save()
    except:
        print("no se guardó el cupón usado o no hubo cupon")   


    try:
        cart_id = int(request.COOKIES.get("cart_id"))
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            pass

        cart_items = CartItem.objects.filter(cart=cart)

        


        for order_item in cart_items:
            oi = OrderItem.objects.create(
                order=order_details,
                name=order_item.product.name,
                sku=order_item.product.sku,
                quantity=order_item.quantity,
                size=order_item.size,
                price=order_item.sub_total(),
                file_a=order_item.file_a,
                file_b=order_item.file_b,
                comment=order_item.comment,
            )
        try:
            oi.save()
        except oi.DoesNotExist:
            print("No se creo el Order ITEM")
                

        ### Sample ITEMS SAVE

        sample_items = SampleItem.objects.filter(cart=cart)
        for order_item in sample_items:
            print("Sample item name")
            print(order_item.sample.name)

        for order_item in sample_items:
            oi = OrderItem.objects.create(
                order=order_details,
                name=order_item.sample.name,
                sku=order_item.sample.sku,
                quantity=order_item.quantity,
                size=order_item.size,
                price=order_item.sub_total(),
                file_a=order_item.file_a,
                file_b=order_item.file_b,
                comment=order_item.comment,
            )
            try:
                oi.save()
            except oi.DoesNotExist:
                print("No se creo el Order ITEM")
        

        order_details.save()    

        try:
            '''Calling send_email function'''
            send_email_deposit_payment(order_details.id)
        except IOError as e:
            return e


    except ObjectDoesNotExist:
        pass

    response = HttpResponse("Hi")
    response.delete_cookie("cart_id")
    response.delete_cookie("cupon")
    response.delete_cookie("discount")

    return response


###############################################
###############################################


def cart_detail(request, total=0, counter=0, cart_items=None):
    print("cart_details")
    try:
        print("Entrando al try de Cart_Details")
        cart = Cart.objects.get(id=request.COOKIES.get("cart_id"))
        if cart:
            print("Hay carrito")
        else:
            print("No hay carrito")
        cart_items = CartItem.objects.filter(cart=cart)

        print("len of cart_items")
        print(len(cart_items))


        for cart_item in cart_items:
            total += int(cart_item.sub_total())

        sample_items = SampleItem.objects.filter(cart=cart)

        for sample_item in sample_items:
            total += int(sample_item.sub_total())

        categories = Category.objects.exclude(name='Muestras')

        print("Total: ", total)
        ### Calcular costo despacho ###

        try:

            costo_despacho = Peru.objects.filter(departamento=request.user.profile.shipping_department,
                                                 provincia=request.user.profile.shipping_province,
                                                 distrito=request.user.profile.shipping_district).values_list(
                "costo_despacho_con_recojo", flat=True)[0]

        except:
            costo_despacho = 15

            ### ¿tiene un cupón de descuento? ###

            # cupon_used_by_user = used_cupons.objects.filter(user = request.user.username)

        try:
            cupon = Cupons.objects.get(cupon=request.COOKIES.get("cupon"))
        except:
            pass

        try:
            if cupon.free_shipping:
                descuento = costo_despacho
            elif cupon.hard_discount:
                descuento = int(cupon.hard_discount)
            elif cupon.percentage:
                cupon_percentage = int(cupon.percentage) / int(100)
                descuento = total * cupon_percentage
            else:
                descuento = 0
        except:
            descuento = 0

        

        total_a_pagar = int(total) - descuento + costo_despacho


        culqi_my_public_key = settings.CULQI_PUBLISHABLE_KEY  # Es necesario mandar la llave pública para generar un token
        culqi_total = int(total_a_pagar * 100)  # El total para cualqui debe multiplicarse por 100



        return render(request, 'cart.html',
                      dict(cart_items=cart_items, sample_items=sample_items, total=total, counter=counter,
                           culqi_total=culqi_total, culqi_my_public_key=culqi_my_public_key,
                           categories=categories, total_a_pagar=total_a_pagar, descuento=descuento,
                           costo_despacho=costo_despacho))


    except:

        print("cart_details except")
        categories = Category.objects.exclude(name='Muestras')
        return render(request, 'cart.html', {'categories': categories})


def send_email_credit_card(order_id):
    transaction = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=transaction)
    try:
        '''sending the order to the customer'''
        subject = 'Stickers Gallito Perú - Nueva orden #{}'.format(transaction.id)
        to = ['{}'.format(transaction.email), 'stickersgallito@gmail.com', 'oma.gonzales@gmail.com']
        from_email = 'stickersgallito@stickersgallito.pe'
        order_information = {
            'transaction': transaction,
            'order_items': order_items
        }
        message = get_template('email/email_credit_card.html').render(order_information)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
    except IOError as e:
        return e


def send_email_deposit_payment(order_id):
    transaction = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=transaction)
    revenue = transaction.total - transaction.shipping_cost
    try:
        '''sending the order to the customer'''
        subject = 'Stickers Gallito Perú - Nueva orden #{}'.format(transaction.id)
        to = ['{}'.format(transaction.email), 'stickersgallito@gmail.com', 'oma.gonzales@gmail.com']
        from_email = 'stickersgallito@stickersgallito.pe'
        order_information = {
            'transaction': transaction,
            'order_items': order_items,
            'revenue': revenue
        }
        message = get_template('email/email_deposit_payment.html').render(order_information)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
    except IOError as e:
        return e








