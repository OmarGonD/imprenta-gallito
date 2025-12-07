from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product, Category, Peru
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from order.models import Order, OrderItem
from marketing.models import used_cupons
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.template.loader import get_template
from django.core.mail import EmailMessage
from marketing.models import Cupons
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def add_to_cart(request, product_slug):
    print("=" * 60)
    print("🚀 add_to_cart iniciado")
    print(f"Method: {request.method}")
    print(f"Product slug: {product_slug}")
    try:
        if request.method == 'POST':
            print("✅ Es POST")
            print("\n📦 POST data:")
            for key, value in request.POST.items():
                print(f"   {key}: '{value}'")
            product = get_object_or_404(Product, slug=product_slug)
            print(f"✅ Producto encontrado: {product.name}")
            quantity = int(request.POST.get('quantity', 1))
            print(f"✅ Cantidad: {quantity}")
            uploaded_file = request.FILES.get('uploaded_file')
            
            # ⭐ NUEVOS: Obtener color y talla
            color = request.POST.get('color', '').strip()
            size = request.POST.get('size', '').strip()
            print(f"✅ Color recibido: '{color}'")
            print(f"✅ Size recibido: '{size}'")
            color_image_url = request.POST.get('color_image_url', '').strip()
            # Get or create cart (TU LÓGICA EXISTENTE - NO CAMBIAR)
            cart_id = request.COOKIES.get('cart_id')
            print(f"🍪 Cart ID de cookie: {cart_id}")
            if cart_id:
                try:
                    cart = Cart.objects.get(id=cart_id)
                    print(f"✅ Cart encontrado: {cart.id}")
                except Cart.DoesNotExist:
                    print("⚠️ Cart no existe, creando nuevo...")
                    cart = Cart.objects.create()
                    print(f"✅ Nuevo cart creado: {cart.id}")
            else:
                print("⚠️ No hay cart_id, creando nuevo...")
                cart = Cart.objects.create()
                print(f"✅ Nuevo cart creado: {cart.id}")

            # ⭐ MODIFICADO: Buscar item con mismo producto, color y talla
            print("\n🔄 Intentando crear/obtener CartItem...")
            from cart.models import CartItem
            fields = [f.name for f in CartItem._meta.get_fields()]
            print(f"Campos disponibles en CartItem: {fields}")

            if 'color' not in fields:
                print("❌ ERROR: CartItem NO tiene campo 'color'")
                return JsonResponse({
                    'success': False,
                    'error': 'CartItem no tiene campo color. Ejecuta: python manage.py makemigrations && python manage.py migrate'
                }, status=500)

            try:
                cart_item = CartItem.objects.get(
                    cart=cart,
                    product=product,
                    color=color if color else None,
                    size=size if size else None
                )
                # Si existe, sumar cantidad
                cart_item.quantity += quantity
                cart_item.color_image_url = color_image_url
                created = False
                print(f"✅ CartItem existente actualizado")
            except CartItem.DoesNotExist:
                # Si no existe, crear nuevo
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    color=color if color else None,
                    size=size if size else None,
                    quantity=quantity,
                    color_image_url=color_image_url
                )
                created = True
                print(f"✅ Nuevo CartItem creado: {cart_item.id}")
            
            # Manejar archivo (TU LÓGICA EXISTENTE)
            if uploaded_file:
                cart_item.file_a = uploaded_file
                print(f"✅ Archivo adjuntado")
            
            cart_item.save()
            print(f"💾 CartItem guardado - Color: '{cart_item.color}', Size: '{cart_item.size}'")

            print("=" * 60)

            # Respuesta mejorada
            response = JsonResponse({
                'success': True, 
                'message': 'Producto agregado al carrito',
                'product_name': product.name,
                'color': color if color else 'N/A',
                'size': size if size else 'N/A',
                'quantity': quantity
            })
            response.set_cookie('cart_id', cart.id)
            return response
        
    except Exception as e:
        print("=" * 60)
        print("❌ ERROR CAPTURADO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        import traceback
        print("\nTraceback completo:")
        traceback.print_exc()
        print("=" * 60)
        
        return JsonResponse({
            'success': False,
            'error': f'{type(e).__name__}: {str(e)}'
        }, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

def full_remove(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()

    return redirect('carrito-de-compras:cart_detail')

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
                color=order_item.color,
                price=order_item.product.price,
                file_a=order_item.file_a,
                file_b=order_item.file_b,
                comment=order_item.comment)
                
            oi.save()

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
    comments = request.POST.get('comments')
    print("### COMMENTSSS CART_PAYMENT ###")
    print(comments)

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
        cupon=cupon,
        comments=comments
    )

    #order_details.save(commit=False)
    print("La orden fue creada")
    
    try:
        used_cupon = used_cupons.objects.create(
        cupon=cupon,
        user=request.user.username,
        order=order_details)
        used_cupon.save()
    except:
        print("no se guardó el cupón usado o no hubo cupon")   


    
    cart_id = int(request.COOKIES.get("cart_id"))
    try:
        cart = Cart.objects.get(id=cart_id)
    except cart.DoesNotExist:
        pass

    cart_items = CartItem.objects.filter(cart=cart)
    
    for order_item in cart_items:
        oi = OrderItem.objects.create(
            order=order_details,
            name=order_item.product.name,
            sku=order_item.product.sku,
            quantity=order_item.quantity,
            size=order_item.size,
            color=order_item.color,
            price=order_item.sub_total(),
            file_a=order_item.file_a,
            file_b=order_item.file_b,
            comment=order_item.comment)
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

    response = HttpResponse("Hi")
    response.delete_cookie("cart_id")
    response.delete_cookie("cupon")
    response.delete_cookie("discount")

    return response


def cart_detail(request, total=0, counter=0, cart_items=None):
    
    try:
        cart_id = request.COOKIES.get('cart_id')
        cart = Cart.objects.get(id=cart_id)
    except ObjectDoesNotExist:
        cart = Cart.objects.create(cart_id="Random")
      
    cart_items = CartItem.objects.filter(cart=cart)

    
    for cart_item in cart_items:
        total += Decimal(cart_item.sub_total) #quité parentesis

    categories = Category.objects.exclude(name='Muestras')

    ### Calcular costo despacho ###

    if request.user.is_authenticated:
        try:

            costo_despacho = Peru.objects.filter(departamento=request.user.profile.shipping_department,
                                                     provincia=request.user.profile.shipping_province,
                                                     distrito=request.user.profile.shipping_district).values_list(
                                                     "costo_despacho_con_recojo", flat=True)[0]

        except:
            costo_despacho = 15
    else:
        costo_despacho = 15

    ### ¿tiene un cupón de descuento? ###

    # cupon_used_by_user = used_cupons.objects.filter(user = request.user.username)

    descuento_por_cupon = 0

    try:
        cupon = Cupons.objects.get(cupon=request.COOKIES.get("cupon"))
    except:
        cupon = None

    if cupon:
        if cupon.free_shipping:
            descuento_por_cupon += costo_despacho
        elif cupon.hard_discount:
            descuento_por_cupon += round(Decimal(cupon.hard_discount),2)
        elif cupon.percentage:
            cupon_percentage = int(cupon.percentage) / int(100)
            print(cupon_percentage)
            descuento_por_cupon += round(total * Decimal(cupon_percentage),2)
   
        
    
    ###############################
    #Monto mínimo para FreeShipping
    ###############################

    free_shipping_min_amount = 2000 # Un número muy alto.

    

    total_a_pagar = Decimal(total) + Decimal(costo_despacho) - Decimal(descuento_por_cupon)

    return render(request, 'cart.html',
                      dict(cart_items=cart_items, total=total, free_shipping_min_amount = free_shipping_min_amount,
                       counter=counter, categories=categories, total_a_pagar=total_a_pagar, descuento_por_cupon=descuento_por_cupon, costo_despacho=costo_despacho))


    


def send_email_credit_card(order_id):
    transaction = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=transaction)
    try:
        '''sending the order to the customer'''
        subject = 'Imprenta Gallito Perú - Nueva orden #{}'.format(transaction.id)
        to = ['{}'.format(transaction.email), 'imprentagallito@gmail.com', 'oma.gonzales@gmail.com']
        from_email = 'imprentagallito@imprentagallito.pe'
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
        print("#Entra a send_email_deposti")
        '''sending the order to the customer'''
        subject = 'Imprenta Gallito Perú - Nueva orden #{}'.format(transaction.id)
        print("###subject")
        print(subject)
        to = ['{}'.format(transaction.email), 'imprentagallito@gmail.com', 'oma.gonzales@gmail.com']
        print("###to")
        print(to)
        from_email = 'imprentagallito@imprentagallito.pe'
        order_information = {
            'transaction': transaction,
            'order_items': order_items,
            'revenue': revenue
        }
        print("###order information")
        print(order_information)
        message = get_template('email/email_deposit_payment.html').render(order_information)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
    except IOError as e:
        print("#Va al except a send_email_deposti")
        print(e)
        return e


from shop.forms import StepTwoForm
from django.shortcuts import get_object_or_404


@csrf_exempt
def upload_design(request, item_id):
    """Vista AJAX para actualizar el archivo de diseño"""
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(id=item_id)
            design_file = request.FILES.get('design_file')
            
            if not design_file:
                return JsonResponse({'success': False, 'error': 'No se recibió archivo'})
            
            # Validar tamaño (50MB max)
            if design_file.size > 50 * 1024 * 1024:
                return JsonResponse({'success': False, 'error': 'Archivo muy grande (max 50MB)'})
            
            # Validar extensión
            import os
            ext = os.path.splitext(design_file.name)[1].lower()
            allowed = ['.png', '.jpg', '.jpeg', '.pdf', '.ai', '.psd', '.svg', '.eps']
            
            if ext not in allowed:
                return JsonResponse({'success': False, 'error': 'Tipo de archivo no válido'})
            
            # Actualizar archivo
            cart_item.design_file = design_file
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Diseño actualizado correctamente'
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item no encontrado'})
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@csrf_exempt
def update_contact(request, item_id):
    if request.method == 'POST':
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.contact_name = request.POST.get('contact_name', '').strip() or None
        cart_item.contact_phone = request.POST.get('contact_phone', '').strip() or None
        # ... demás campos
        cart_item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@csrf_exempt
def update_contact(request, item_id):
    """
    Vista AJAX para actualizar los datos de contacto de un CartItem.
    Se llama desde el modal de edición en cart.html
    """
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(id=item_id)
            
            # Actualizar datos de contacto
            cart_item.contact_name = request.POST.get('contact_name', '').strip() or None
            cart_item.contact_phone = request.POST.get('contact_phone', '').strip() or None
            cart_item.contact_email = request.POST.get('contact_email', '').strip() or None
            cart_item.contact_job_title = request.POST.get('contact_job_title', '').strip() or None
            cart_item.contact_company = request.POST.get('contact_company', '').strip() or None
            cart_item.contact_social = request.POST.get('contact_social', '').strip() or None
            cart_item.contact_address = request.POST.get('contact_address', '').strip() or None
            
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Datos actualizados correctamente'
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Item no encontrado'
            })
        except Exception as e:
            print(f"Error en update_contact: {str(e)}")
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@csrf_exempt
def update_template(request):
    """Actualiza SOLO la plantilla de un CartItem existente."""
    if request.method == 'POST':
        try:
            item_id = request.POST.get('item_id')
            template_slug = request.POST.get('template_slug', '')
            
            cart_item = CartItem.objects.get(id=item_id)
            
            if template_slug == 'custom':
                cart_item.comment = 'custom'
                if request.FILES.get('design_file'):
                    if cart_item.design_file:
                        cart_item.design_file.delete(save=False)
                    cart_item.design_file = request.FILES.get('design_file')
            else:
                cart_item.comment = f'template:{template_slug[:80]}'
                if cart_item.design_file:
                    cart_item.design_file.delete(save=False)
                    cart_item.design_file = None
            
            cart_item.save()
            return JsonResponse({'success': True})
            
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item no encontrado'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
