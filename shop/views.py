from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, HttpResponseRedirect, render
from django.template.loader import get_template
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.views.generic import ListView
from shop.models import Product_Review, Sample_Review, ProductsPricing, Profile, UnitaryProduct, Sample, Peru
from shop.tokens import account_activation_token
from cart.models import Cart, CartItem, SampleItem, PackItem, UnitaryProductItem
from .forms import SignUpForm, StepOneForm, StepTwoForm, ProfileForm, StepOneForm_Sample, StepTwoForm_Sample
from .models import TarjetaPresentacion, Folleto, Poster, Etiqueta, Empaque
from .models import Product, Category, Pack
from marketing.forms import EmailSignUpForm


class TarjetasPresentacionListView(ListView):
    model = TarjetaPresentacion
    template_name = 'shop/tarjetas_presentacion.html'
    context_object_name = 'tarjetas'

class FolletosListView(ListView):
    model = Folleto
    template_name = 'shop/folletos.html'
    context_object_name = 'folletos-list'

class PostersListView(ListView):
    model = Poster
    template_name = 'shop/posters.html'
    context_object_name = 'posters'

class EtiquetasListView(ListView):
    model = Etiqueta
    template_name = 'shop/etiquetas.html'
    context_object_name = 'etiquetas'

class EmpaquesListView(ListView):
    model = Empaque
    template_name = 'shop/empaques.html'
    context_object_name = 'empaques'



# Create your views here.

# Category View


def allCat(request):
    # Muestras todas las categorias de productos en el home, menos "Muestras"
    categories = Category.objects.exclude(name='Muestras')
    email_signup_form = EmailSignUpForm()
    
    # Get popular products (can be based on reviews, orders, or just recent products)
    popular_products = Product.objects.filter(available=True).order_by('-created')[:6]

    # Fix: use the correct template path
    return render(request, 'shop/index.html', {
        'categories': categories,
        'email_signup_form': email_signup_form,
        'popular_products': popular_products,
    })


def ProdCatDetail(request, c_slug):
    ### Para mostrar una sección de la página, primero se debe crear su categoría.
    ### Dependiendo de la categoría, se mostrará la sección: para Comprar, se debe crear la categoría: "stickers", para "muestras", la categoría "muestras".
    print("### INGRESA A PRODCATDETAIL ###")
    print("c_slug is: ", c_slug)
    if c_slug not in ["muestras", "packs"]:
        print("### INGRESA A C_SLUG  ###")
        try:
            category = Category.objects.get(slug=c_slug)
            products = Product.objects.filter(category__slug=c_slug, available=True)
            print("### RETURN PRODUCTS POR CATEGORÍA  ###")
            return render(request, 'shop/productos_por_categoria.html', {'category': category, 'products': products})

        except Exception as e:
            raise e
    
    print("### ANTES DEL ELIF  ###")
    if c_slug == "packs":
        categoria = Category.objects.get(slug='packs')

        # Productos que pertenecen a la categoria muestras

        c_slug = 'packs'

        # muestras = Product.objects.filter(category__slug=c_slug)

        packs = Pack.objects.filter(category__slug=c_slug).exclude(available=False)
        print("### RENDERS PACKS HTML  ###")
        return render(request, 'shop/packs.html', {'category': categoria, 'packs': packs})


   



#### PACKS PAGE #####

def PacksPage(request):
    print("### INGRESA A PACKSPAGE ###")
    # La categoria es necesaria para mostrar el video de c/categoria

    categoria = Category.objects.get(slug='packs')

    # Productos que pertenecen a la categoria muestras

    c_slug = 'packs'

    # muestras = Product.objects.filter(category__slug=c_slug)

    packs = Pack.objects.filter(category__slug=c_slug).exclude(available=False)

    return render(request, 'shop/packs.html', {'category': categoria,
                                                  'packs': packs})

#### PACKS ####

def PackFun(request, c_slug, pack_slug):
    cart_id = request.COOKIES.get('cart_id')
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
        except ObjectDoesNotExist:
            # supplied ID doesn't match a Cart from your BD
            cart = Cart.objects.create(cart_id="Random")
    else:
        cart = Cart.objects.create(cart_id="Random")
        cart_id = cart.id
    try:
        pack = Pack.objects.get(
            category__slug=c_slug,
            slug=pack_slug,
        )

        pack_item = PackItem.objects.create(
            cart=cart,
            pack=pack,
            size=pack.size,
            quantity=pack.quantity,
            file_a=pack.image,
            file_b=pack.image,
            comment="",
            step_two_complete=True,
        )
        response = redirect('/carrito_de_compras/')
        response.set_cookie("cart_id", cart_id)
        response.set_cookie("item_id", item.id)
        return response

    except Exception as e:
        raise e

    return HttpResponse("Hi")


################



def SamplePackPage(request):
    # La categoria es necesaria para mostrar el video de c/categoria

    c_slug = 'muestras'

    categoria_muestras = Category.objects.get(slug=c_slug)

    # Productos que pertenecen a la categoria muestras

    muestras = Sample.objects.filter(category__slug=c_slug).exclude(slug='sobre-con-muestras').exclude(available=False)

    return render(request, 'shop/muestras.html', {'categoria_muestras': categoria_muestras,
                                                  'muestras': muestras})



@csrf_exempt
def AddUnitaryProduct(request):

    cart_id = request.COOKIES.get('cart_id')
    if cart_id:
            cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart.objects.create(cart_id="Random")
        cart_id = cart.id

    c_slug = request.POST.get('c_slug')
    product_slug = request.POST.get('product_slug')
    quantity = request.POST.get('quantity')
 
    try:

        unitary_product = UnitaryProduct.objects.get(
            category__slug=c_slug,
            slug=product_slug)

        unitary_product_item = UnitaryProductItem.objects.create(
            cart=cart,
            unitaryproduct=unitary_product,
            size=unitary_product.size,
            quantity=quantity,
            file_a=unitary_product.image,
            file_b=unitary_product.image,
            comment="",
            step_two_complete=True)
       
        cart_items_count = CartItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
        sample_items_count = SampleItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
        pack_items_count = PackItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
        unitary_product_items_count = UnitaryProductItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()

        total_items = cart_items_count + sample_items_count + pack_items_count + unitary_product_items_count

        response = JsonResponse({'cart_items_counter':total_items})
        response.set_cookie("cart_id", cart_id)
        response.set_cookie("item_id", unitary_product_item.id)

        return response

    except Exception as e:
        raise e



### Add Pack ###

@csrf_exempt
def AddPack(request):

    cart_id = request.COOKIES.get('cart_id')
    if cart_id:
            cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart.objects.create(cart_id="Random")
        cart_id = cart.id

    c_slug = request.POST.get('c_slug')
    pack_slug = request.POST.get('pack_slug')
    
    try:

        pack = Pack.objects.get(
                category__slug=c_slug,
                slug=pack_slug)

        pack_item = PackItem.objects.create(
                cart=cart,
                pack=pack,
                size=pack.size,
                quantity=pack.quantity,
                file_a=pack.image,
                file_b=pack.image,
                comment="",
                step_two_complete=True)

        
        cart_items_count = CartItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
        sample_items_count = SampleItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
        pack_items_count = PackItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
        unitary_product_items_count = UnitaryProductItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()

        total_items = cart_items_count + sample_items_count + pack_items_count + unitary_product_items_count

        response = JsonResponse({'cart_items_counter':total_items}) #To update items counter
        response.set_cookie("cart_id", cart_id)
        response.set_cookie("item_id", pack_item.id)

        return response

    except Exception as e:
        raise e

################


def AddProduct(request, c_slug, product_slug):

    cart_id = request.COOKIES.get('cart_id')
    if cart_id:
            cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart.objects.create(cart_id="Random")
        cart_id = cart.id
    
    if c_slug == "muestras":
        
        try:
            sample = Sample.objects.get(
                category__slug=c_slug,
                slug=product_slug)

            item = SampleItem.objects.create(
                cart=cart,
                sample=sample,
                size="varios",
                quantity="5",
                file_a=sample.image,
                file_b=sample.image,
                comment="",
                step_two_complete=True)

            response = redirect('/carrito_de_compras/')
            response.set_cookie("cart_id", cart_id)
            response.set_cookie("item_id", item.id)
            return response     

        except Exception as e:
            raise e        

    elif c_slug == "packs":
        
        try:
            pack = Pack.objects.get(
                category__slug=c_slug,
                slug=product_slug)

            pack_item = PackItem.objects.create(
                cart=cart,
                pack=pack,
                size=pack.size,
                quantity=pack.quantity,
                file_a=pack.image,
                file_b=pack.image,
                comment="",
                step_two_complete=True)

            response = HttpResponseRedirect('/carrito_de_compras/')
            response.set_cookie("cart_id", cart_id)
            response.set_cookie("item_id", pack_item.id)
            return response    

        except Exception as e:
            raise e

   
           


# Tamanos y cantidades

class StepOneView(FormView):
    form_class = StepOneForm
    template_name = 'shop/medidas-cantidades.html'
    success_url = 'subir-arte'

    def get_initial(self):
        # pre-populate form if someone goes back and forth between forms
        initial = super(StepOneView, self).get_initial()
        initial['size'] = self.request.session.get('size', None)
        initial['quantity'] = self.request.session.get('quantity', None)
        initial['product'] = Product.objects.get(
            category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['product_slug']
        )

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(
            category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['product_slug']
        )
        return context

    def form_invalid(self, form):
        print('Step one: form is NOT valid')

    def form_valid(self, form):
        cart_id = self.request.COOKIES.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except ObjectDoesNotExist:
                # supplied ID doesn't match a Cart from your BD
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.id
        item = CartItem.objects.create(
            size=form.cleaned_data.get('size'),
            quantity=form.cleaned_data.get('quantity'),
            product=Product.objects.get(
                category__slug=self.kwargs['c_slug'],
                slug=self.kwargs['product_slug']
            ),
            cart=cart
        )

        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie("cart_id", cart_id)
        response.set_cookie("item_id", item.id)
        return response


# here we are going to use CreateView to save the Third step ModelForm
class StepTwoView(FormView):
    form_class = StepTwoForm
    template_name = 'shop/subir-arte.html'
    success_url = '/carrito_de_compras/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(
            category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['product_slug']
        )
        return context

    def form_invalid(self, form):
        print('StepTwoForm is not Valid', form.errors)

    def form_valid(self, form):
        item_id = self.request.COOKIES.get("item_id")

        cart_item = CartItem.objects.get(id=item_id)
        cart_item.file_a = form.cleaned_data["file_a"]
        cart_item.file_b = form.cleaned_data["file_b"]
        cart_item.comment = form.cleaned_data["comment"]
        cart_item.step_two_complete = True
        cart_item.save()
        response = HttpResponseRedirect(self.get_success_url())
        response.delete_cookie("item_id")
        return response


### STEPS ONE & TWO FOR SAMPLES


# Tamanos y cantidades

class StepOneView_Sample(FormView):
    form_class = StepOneForm_Sample
    template_name = 'shop/medidas-cantidades.html'
    success_url = 'subir-arte'

    def get_initial(self):
        # pre-populate form if someone goes back and forth between forms
        initial = super(StepOneView_Sample, self).get_initial()
        initial['size'] = self.request.session.get('size', None)
        initial['sample'] = Sample.objects.get(
            # category=self.kwargs['muestras'],
            slug=self.kwargs['sample_slug']
        )

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sample'] = Sample.objects.get(
            # category=self.kwargs['muestras'],
            slug=self.kwargs['sample_slug']
        )
        context['sample_form'] = context.get('form')
        return context

    def form_invalid(self, form):
        print('Step one: form is NOT valid')

    def form_valid(self, form):
        cart_id = self.request.COOKIES.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except ObjectDoesNotExist:
                # supplied ID doesn't match a Cart from your BD
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.id
        item = SampleItem.objects.create(
            size=form.cleaned_data.get('size'),
            quantity=2,
            sample=Sample.objects.get(
                # category=self.kwargs['muestras'],
                slug=self.kwargs['sample_slug']
            ),
            cart=cart
        )

        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie("cart_id", cart_id)
        response.set_cookie("item_id", item.id)
        return response


# here we are going to use CreateView to save the Third step ModelForm

class StepTwoView_Sample(FormView):
    form_class = StepTwoForm_Sample
    template_name = 'shop/subir-arte.html'
    success_url = '/carrito_de_compras/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Sample.objects.get(
            # category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['sample_slug']
        )
        return context

    def form_invalid(self, form):
        print('StepTwoForm is not Valid', form.errors)

    def form_valid(self, form):
        item_id = self.request.COOKIES.get("item_id")

        sample_item = SampleItem.objects.get(id=item_id)
        sample_item.file_a = form.cleaned_data["file_a"]
        sample_item.file_b = form.cleaned_data["file_b"]
        sample_item.comment = form.cleaned_data["comment"]
        sample_item.step_two_complete = True
        sample_item.save()
        response = HttpResponseRedirect(self.get_success_url())
        response.delete_cookie("item_id")
        return response


###############################
###############################


def signinView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # username = request.POST['username']
            # password = request.POST['password']
            print(username)
            print(password)
            user = authenticate(username=username,
                                password=password)
            if user is not None:
                login(request, user)
                # cart_id =_cart_id(request)
                # request.session['cart_id'] = cart_id
                return redirect('carrito_de_compras:cart_detail')
            else:
                return redirect('signup')

    else:
        form = AuthenticationForm()
    return render(request, 'accounts/signin.html', {'form': form})


def signoutView(request):
    if request.user.is_superuser:
        request.session.modified = True

        logout(request)

    else:
        # del request.session['cart_id']
        request.session.modified = True
        logout(request)

    response = redirect('signin')
    response.delete_cookie("cart_id")
    response.delete_cookie("cupon")
    return response


### New SignUp Extended

from django.shortcuts import render
from django.contrib.auth.decorators import login_required



### Email Confirmation Needed ###

def email_confirmation_needed(request):
    return render(request, "accounts/email_confirmation_needed.html")



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        print("############")
        print("Enters if of activate function")
        print("############")
        user.is_active = True
        user.save()
        login(request, user)
        '''send email to admin when a new user has activate his/her account'''
        print("############")
        print(user.id)
        print(type(user.id))
        print("############")
        send_email_new_registered_user(user.id)
        return redirect('shop:allCat')
    else:
        return HttpResponse('¡Enlace de activación inválido! Intente registrarse nuevamente.')



def send_email_new_registered_user(user_id):
    try:
        print("Enters send_email_new_registed_user try")
        profile = Profile.objects.latest('id')
        if profile:
            print("Se obtuvo profile")
        '''sending the order to the customer'''
        subject = f"Imprenta Gallito Perú - Nuevo usuario registrado #{profile.id}"
        to = [f'{profile.user.email}', 'imprentagallito@gmail.com', 'oma.gonzales@gmail.com']
        from_email = 'imprentagallito@imprentagallito.pe'
        user_information = {
            'user_id': profile.user.id,
            'user_name': profile.user.username,
            'user_full_name': profile.user.get_full_name,
            'user_dni': profile.dni,
            'user_deparment': profile.shipping_deparment,
            'user_province': profile.shipping_province,
            'user_disctrict': profile.shipping_district,
            'user_shipping_address': profile.shipping_address1,
            'user_email': profile.user.email,
            'user_phone': profile.phone_number,
            'user_is_active': profile.user.is_active,
        }
        message = get_template('accounts/new_registered_user.html').render(user_information)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
        print("Se envió msj")
    except:
        pass


@transaction.atomic
def signupView(request):
    peru = Peru.objects.all()
    department_list = set()
    province_list = set()
    district_list = set()
    for p in peru:
        department_list.add(p.departamento)
    department_list = list(department_list)
    if len(department_list):
        province_list = set(Peru.objects.filter(departamento=department_list[0]).values_list("provincia", flat=True))
        province_list = list(province_list)
    else:
        province_list = set()
    if len(province_list):
        district_list = set(
            Peru.objects.filter(departamento=department_list[0], provincia=province_list[0]).values_list("distrito",
                                                                                                         flat=True))
    else:
        district_list = set()

    if request.method == 'POST':

        peru = Peru.objects.all()
        department_list = set()
        province_list = set()
        district_list = set()
        for p in peru:
            department_list.add(p.departamento)
        department_list = list(department_list)
        if len(department_list):
            province_list = set(
                Peru.objects.filter(departamento__in=department_list).values_list("provincia", flat=True))

            province_list = list(province_list)
        else:
            province_list = set()
        if len(province_list):
            district_list = set(
                Peru.objects.filter(departamento__in=department_list, provincia__in=province_list).values_list(
                    "distrito",
                    flat=True))
        else:
            district_list = set()

        #####

        user_form = SignUpForm(request.POST)
        profile_form = ProfileForm(district_list, province_list, department_list, request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = True
            user.save()
            username = user_form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            customer_group = Group.objects.get(name='Clientes')
            customer_group.user_set.add(signup_user)
            raw_password = user_form.cleaned_data.get('password1')
            user.refresh_from_db()  # This will load the Profile created by the Signal

            profile_form = ProfileForm(district_list, province_list, department_list, request.POST, request.FILES,
                                       instance=user.profile)  # Reload the profile form with the profile instance
            profile_form.full_clean()  # Manually clean the form this time. It is implicitly called by "is_valid()" method
            profile_form.save()  # Gracefully save the form
            send_email_new_registered_user(user.id) # send email to admin when a new user registers himself
            login(request, user)

            return redirect('carrito_de_compras:cart_detail')

        else:
            pass


    else:

        user_form = SignUpForm()

        profile_form = ProfileForm(district_list, province_list, department_list)

    return render(request, 'accounts/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def get_province(request):
    d_name = request.GET.get("d_name")
    data = Peru.objects.filter(departamento=d_name).values_list("provincia", flat=True)
    return render(request, "accounts/province_dropdown.html", {
        "provinces": set(list(data))
    })


def get_district(request):
    d_name = request.GET.get("d_name")
    p_name = request.GET.get("p_name")
    data = Peru.objects.filter(departamento=d_name, provincia=p_name).values_list("distrito", flat=True)
    return render(request, "accounts/district_dropdown.html", {
        "districts": set(list(data))
    })


### ¿Quiénes somos? ###

def quienes_somos(request):
    return render(request, "footer_links/quienes_somos.html")


### ¿Cómo comprar? ###

def como_comprar(request):
    return render(request, "footer_links/como_comprar.html")


### Contactanos ###

def contactanos(request):
    return render(request, "footer_links/contactanos.html")


### Legales - Privacidad ###


def legales_privacidad(request):
    return render(request, 'footer_links/legales_privacidad.html')

### Legales - Términos ###

def legales_terminos(request):
    return render(request, 'footer_links/legales_terminos.html')    

### Preguntas frecuentes ###

def preguntas_frecuentes(request):
    return render(request, 'footer_links/preguntas_frecuentes.html')



### Reviews ###


@csrf_exempt
def make_review_view(request):
    user = request.user
    category_slug = request.POST.get('category_slug')
    product_slug = request.POST.get("product_slug")

    sample_slug = request.POST.get("sample_slug")
    review = request.POST.get("review")
    stars = float(request.POST.get("stars"))
    
    if category_slug == 'muestras':

        try:

            category = Category.objects.get(
                slug=category_slug,
            )

            sample = Sample.objects.get(
                slug=sample_slug,
            )

            review = Sample_Review.objects.create(
                user=user,
                category=category,
                sample=sample,
                review=review,
                stars=stars
            )

            if not review:
                print("No se creó Review Object")
            else:
                review.save()
        except Sample_Review.DoesNotExist:
            print("No se creo el Review")

    else:

        try:

            category = Category.objects.get(
                slug=category_slug,
            )

            product = Product.objects.get(
                slug=product_slug,
            )

            review = Product_Review.objects.create(
                user=user,
                category=category,
                product=product,
                review=review,
                stars=stars
            )

            if not review:
                print("No se creó Review Object")
            else:
                review.save()      
        except Product_Review.DoesNotExist:
            print("No se creo el Review")


    return HttpResponse("Hi")



from django.http.response import JsonResponse
def prices(request):
    size_selected = request.GET.get("size_selected")
    c_slug = request.GET.get("c_slug")
    product_slug = request.GET.get("product_slug")


    prices = list(ProductsPricing.objects.filter(category=Category.objects.get(slug=c_slug),
                                              product=Product.objects.get(slug=product_slug),
                                              size=size_selected).values_list("price",flat=True))
    
    return JsonResponse({'prices': prices})


#####################
### Catalogo View ###
#####################

class CatalogoListView(ListView):

    model = UnitaryProduct
    template_name = "shop/catalogo.html"
    paginate_by = 9

    def get_queryset(self):
        filter_val = self.request.GET.get('filtro', 'todas')
        filter_val = filter_val.lower()
        order = self.request.GET.get('orderby', 'created')
        if filter_val == "todas":
            context = UnitaryProduct.objects.all().filter(available=True).order_by('-created')
            return context
        else:    
            context = UnitaryProduct.objects.filter(
                subcategory2=filter_val,
            ).filter(available=True).order_by('-created')
            return context

    def get_context_data(self, **kwargs):
        context = super(CatalogoListView, self).get_context_data(**kwargs)
        context['filtro'] = self.request.GET.get('filtro', 'todas')
        context['orderby'] = self.request.GET.get('orderby', 'created')
        context['category'] = Category.objects.get(slug="catalogo")
        context['total_stickers'] = UnitaryProduct.objects.filter(available=True).count()
        context['product_count'] = self.get_queryset().count()
        
        return context

def tarjetas_presentacion(request):
    return render(request, 'shop/tarjetas_presentacion.html')

def postales(request):
    return render(request, 'shop/postales.html')

def publicidad_impresa(request):
    return render(request, 'shop/publicidad_impresa.html')

def banners_posters(request):
    return render(request, 'shop/banners_posters.html')

def etiquetas_stickers(request):
    return render(request, 'shop/etiquetas_stickers.html')

def ropa_bolsas(request):
    """Main Clothing & Bags page - VistaPrint style"""
    from .models import ClothingCategory, ClothingProduct, ClothingColor, ClothingSize
    
    categories = ClothingCategory.objects.filter(available=True).prefetch_related('subcategories')
    
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    color_filter = request.GET.getlist('color')
    size_filter = request.GET.getlist('size')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', 'featured')
    
    # Base queryset
    products = ClothingProduct.objects.filter(available=True)
    
    # Apply filters
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    if color_filter:
        products = products.filter(available_colors__slug__in=color_filter).distinct()
    
    if size_filter:
        products = products.filter(available_sizes__name__in=size_filter).distinct()
    
    if price_min:
        products = products.filter(base_price__gte=float(price_min))
    
    if price_max:
        products = products.filter(base_price__lte=float(price_max))
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # featured
        products = products.order_by('-is_featured', '-is_bestseller', 'name')
    
    # Get all colors and sizes for filter sidebar
    all_colors = ClothingColor.objects.all()
    all_sizes = ClothingSize.objects.filter(size_type='clothing')
    
    context = {
        'categories': categories,
        'products': products,
        'all_colors': all_colors,
        'all_sizes': all_sizes,
        'selected_category': category_filter,
        'selected_colors': color_filter,
        'selected_sizes': size_filter,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
        'product_count': products.count(),
    }
    
    return render(request, 'shop/ropa_bolsas.html', context)


def clothing_category(request, category_slug):
    """Category page for clothing - e.g., /ropa-bolsas/gorras/"""
    from .models import ClothingCategory, ClothingProduct, ClothingColor, ClothingSize
    
    category = ClothingCategory.objects.get(slug=category_slug, available=True)
    subcategories = category.subcategories.filter(available=True)
    
    # Get filter parameters
    subcategory_filter = request.GET.get('subcategory', '')
    color_filter = request.GET.getlist('color')
    size_filter = request.GET.getlist('size')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', 'featured')
    
    # Base queryset
    products = ClothingProduct.objects.filter(category=category, available=True)
    
    # Apply filters
    if subcategory_filter:
        products = products.filter(subcategory__slug=subcategory_filter)
    
    if color_filter:
        products = products.filter(available_colors__slug__in=color_filter).distinct()
    
    if size_filter:
        products = products.filter(available_sizes__name__in=size_filter).distinct()
    
    if price_min:
        products = products.filter(base_price__gte=float(price_min))
    
    if price_max:
        products = products.filter(base_price__lte=float(price_max))
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-is_featured', '-is_bestseller', 'name')
    
    # Get colors and sizes available in this category
    all_colors = ClothingColor.objects.filter(products__category=category).distinct()
    
    # Determine size type based on category
    size_type = 'clothing'
    if 'gorra' in category.slug or 'sombrero' in category.slug:
        size_type = 'hat'
    elif 'bolsa' in category.slug or 'mochila' in category.slug:
        size_type = 'bag'
    
    all_sizes = ClothingSize.objects.filter(size_type=size_type)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'all_colors': all_colors,
        'all_sizes': all_sizes,
        'selected_subcategory': subcategory_filter,
        'selected_colors': color_filter,
        'selected_sizes': size_filter,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
        'product_count': products.count(),
    }
    
    return render(request, 'shop/clothing_category.html', context)


def clothing_subcategory(request, category_slug, subcategory_slug):
    """Subcategory page - e.g., /ropa-bolsas/gorras/viseras/"""
    from .models import ClothingCategory, ClothingSubCategory, ClothingProduct, ClothingColor, ClothingSize
    
    category = ClothingCategory.objects.get(slug=category_slug, available=True)
    subcategory = ClothingSubCategory.objects.get(category=category, slug=subcategory_slug, available=True)
    
    # Get filter parameters
    color_filter = request.GET.getlist('color')
    size_filter = request.GET.getlist('size')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', 'featured')
    
    # Base queryset
    products = ClothingProduct.objects.filter(subcategory=subcategory, available=True)
    
    # Apply filters
    if color_filter:
        products = products.filter(available_colors__slug__in=color_filter).distinct()
    
    if size_filter:
        products = products.filter(available_sizes__name__in=size_filter).distinct()
    
    if price_min:
        products = products.filter(base_price__gte=float(price_min))
    
    if price_max:
        products = products.filter(base_price__lte=float(price_max))
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-is_featured', '-is_bestseller', 'name')
    
    # Get colors and sizes
    all_colors = ClothingColor.objects.filter(products__subcategory=subcategory).distinct()
    size_type = 'hat' if 'gorra' in category.slug else 'clothing'
    all_sizes = ClothingSize.objects.filter(size_type=size_type)
    
    context = {
        'category': category,
        'subcategory': subcategory,
        'products': products,
        'all_colors': all_colors,
        'all_sizes': all_sizes,
        'selected_colors': color_filter,
        'selected_sizes': size_filter,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
        'product_count': products.count(),
    }
    
    return render(request, 'shop/clothing_subcategory.html', context)


def clothing_product_detail(request, category_slug, product_slug):
    """Product detail page with customization options"""
    from .models import ClothingCategory, ClothingProduct, ClothingProductImage
    
    category = ClothingCategory.objects.get(slug=category_slug)
    product = ClothingProduct.objects.get(category=category, slug=product_slug, available=True)
    
    # Get product images organized by color
    images = product.images.all().select_related('color')
    images_by_color = {}
    default_images = []
    
    for img in images:
        if img.color:
            if img.color.slug not in images_by_color:
                images_by_color[img.color.slug] = []
            images_by_color[img.color.slug].append(img)
        else:
            default_images.append(img)
    
    # Get pricing tiers
    pricing_tiers = product.pricing_tiers.all()
    
    # Get related products
    related_products = ClothingProduct.objects.filter(
        category=category,
        available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'category': category,
        'product': product,
        'images_by_color': images_by_color,
        'default_images': default_images,
        'pricing_tiers': pricing_tiers,
        'related_products': related_products,
    }
    
    return render(request, 'shop/clothing_product_detail.html', context)


@csrf_exempt
def add_clothing_to_cart(request):
    """AJAX endpoint to add clothing product to cart"""
    from .models import ClothingProduct, ClothingColor, ClothingSize
    
    if request.method == 'POST':
        cart_id = request.COOKIES.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.id
        
        product_id = request.POST.get('product_id')
        color_slug = request.POST.get('color')
        size_name = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = ClothingProduct.objects.get(id=product_id)
            color = ClothingColor.objects.get(slug=color_slug) if color_slug else None
            size = ClothingSize.objects.get(name=size_name) if size_name else None
            
            # Create cart item (you may need to extend CartItem model)
            # For now, we'll use the existing UnitaryProductItem structure
            from cart.models import UnitaryProductItem
            
            # Store clothing-specific data in comment field as JSON
            import json
            custom_data = json.dumps({
                'type': 'clothing',
                'color': color.name if color else '',
                'color_hex': color.hex_code if color else '',
                'size': size.name if size else '',
            })
            
            item = UnitaryProductItem.objects.create(
                cart=cart,
                unitaryproduct=None,  # Will need to adapt
                size=size.name if size else '',
                quantity=quantity,
                comment=custom_data,
                step_two_complete=True,
            )
            
            # Count total items
            cart_items_count = CartItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
            sample_items_count = SampleItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
            pack_items_count = PackItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
            unitary_items_count = UnitaryProductItem.objects.filter(cart_id=cart_id, step_two_complete=True).count()
            
            total_items = cart_items_count + sample_items_count + pack_items_count + unitary_items_count
            
            response = JsonResponse({
                'success': True,
                'cart_items_counter': total_items,
                'message': 'Producto agregado al carrito'
            })
            response.set_cookie("cart_id", cart_id)
            return response
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def productos_promocionales(request):
    return render(request, 'shop/productos_promocionales.html')

def empaques(request):
    return render(request, 'shop/empaques.html')

def invitaciones_regalos(request):
    return render(request, 'shop/invitaciones_regalos.html')

def bodas(request):
    return render(request, 'shop/bodas.html')

def servicios_diseno(request):
    return render(request, 'shop/servicios_diseno.html')


### Profile Views ###

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    """View user profile"""
    profile = request.user.profile
    return render(request, 'accounts/profile.html', {
        'profile': profile
    })


@login_required
@transaction.atomic
def profile_edit_view(request):
    """Edit user profile"""
    peru = Peru.objects.all()
    department_list = sorted(set(p.departamento for p in peru))
    
    profile = request.user.profile
    
    if request.method == 'POST':
        # Get the selected department and province for loading districts
        department = request.POST.get('shipping_department')
        province = request.POST.get('shipping_province')
        
        province_list = sorted(set(Peru.objects.filter(
            departamento=department
        ).values_list("provincia", flat=True)))
        
        district_list = sorted(set(Peru.objects.filter(
            departamento=department, 
            provincia=province
        ).values_list("distrito", flat=True)))
        
        profile_form = ProfileForm(
            district_list, 
            province_list, 
            department_list, 
            request.POST, 
            request.FILES,
            instance=profile
        )
        
        if profile_form.is_valid():
            profile_form.save()
            return redirect('shop:profile')
    else:
        # Initialize lists based on current profile data
        if profile.shipping_department:
            province_list = sorted(set(Peru.objects.filter(
                departamento=profile.shipping_department
            ).values_list("provincia", flat=True)))
        else:
            province_list = []
            
        if profile.shipping_department and profile.shipping_province:
            district_list = sorted(set(Peru.objects.filter(
                departamento=profile.shipping_department,
                provincia=profile.shipping_province
            ).values_list("distrito", flat=True)))
        else:
            district_list = []
        
        profile_form = ProfileForm(
            district_list,
            province_list,
            department_list,
            instance=profile
        )
    
    return render(request, 'accounts/profile_edit.html', {
        'profile_form': profile_form,
        'profile': profile
    })
