from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from shop.models import Product_Review, Sample_Review, ProductsPricing
from cart.models import Cart, CartItem, SampleItem
from .forms import SignUpForm, StepOneForm, StepTwoForm, ProfileForm, StepOneForm_Sample, StepTwoForm_Sample
from .models import Category, Product, Peru, Sample
from marketing.forms import EmailSignUpForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


# Create your views here.

# Category View


def allCat(request):
    # Muestras todas las categorias de productos en el home, menos "Muestras"
    categories = Category.objects.exclude(name='Muestras')
    email_signup_form = EmailSignUpForm()

    # return render(request, 'shop/index.html', {'categories': categories}, context_instance=RequestContext(request))
    return render(request, 'shop/index.html', {'categories': categories, 'email_signup_form': email_signup_form})


def ProdutcsByCategory(request, c_slug):
    # Para obtener el título de la categoría

    category = Category.objects.filter(slug=c_slug)

    # Obtiene los productos de la categoría
    products = Product.objects.filter(slug=c_slug)
    return render(request, 'shop/productos_por_categoria.html', {'products': products})


def ProdCatDetail(request, c_slug):
    if c_slug is not "muestras":

        try:
            category = Category.objects.get(slug=c_slug)
            products = Product.objects.filter(category__slug=c_slug)
        except Exception as e:
            raise e

    return render(request, 'shop/productos_por_categoria.html', {'category': category, 'products': products})


def SamplePackPage(request):
    # La categoria es necesaria para mostrar el video de c/categoria

    categoria_muestras = Category.objects.get(slug='muestras')

    # Productos que pertenecen a la categoria muestras

    c_slug = 'muestras'

    # muestras = Product.objects.filter(category__slug=c_slug)

    muestras = Sample.objects.filter(category__slug=c_slug).exclude(slug='sobre-con-muestras')

    return render(request, 'shop/muestras.html', {'categoria_muestras': categoria_muestras,
                                                  'muestras': muestras})


def SamplePack(request, c_slug, product_slug):
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
        sample = Sample.objects.get(
            category__slug=c_slug,
            slug=product_slug,
        )

        item = SampleItem.objects.create(
            cart=cart,
            sample=sample,
            size="varios",
            quantity="10",
            file=sample.image,
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
        cart_item.file = form.cleaned_data["file"]
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
            quantity=10,
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
        sample_item.file = form.cleaned_data["file"]
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



### Email Confirmation Needed ###

def email_confirmation_needed(request):
    return render(request, "accounts/email_confirmation_needed.html")



def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('shop:allCat')
    else:
        return HttpResponse('¡Enlace de activación inválido! Intente registrarse nuevamente.')



@transaction.atomic
def signupView(request):
    peru = Peru.objects.all()
    department_list = set()
    province_list = set()
    district_list = set()
    for p in peru:
        department_list.add(p.departamento)
    department_list = list(department_list)
    # print("Department List: ", department_list)
    if len(department_list):
        province_list = set(Peru.objects.filter(departamento=department_list[0]).values_list("provincia", flat=True))
        # print("Provice List: ", province_list)
        province_list = list(province_list)
        # print("dfsfs", province_list)
    else:
        province_list = set()
    if len(province_list):
        district_list = set(
            Peru.objects.filter(departamento=department_list[0], provincia=province_list[0]).values_list("distrito",
                                                                                                         flat=True))
        # print("district List: ", district_list)
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
        print("Department List in POST: ", department_list)
        if len(department_list):
            province_list = set(
                Peru.objects.filter(departamento__in=department_list).values_list("provincia", flat=True))

            province_list = list(province_list)
            print("Province LIST in POST", province_list)
        else:
            province_list = set()
        if len(province_list):
            district_list = set(
                Peru.objects.filter(departamento__in=department_list, provincia__in=province_list).values_list(
                    "distrito",
                    flat=True))
            print("District LIST in POST", district_list)
        else:
            district_list = set()

        #####

        user_form = SignUpForm(request.POST)
        profile_form = ProfileForm(district_list, province_list, department_list, request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
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

            # user = authenticate(username=username, password=raw_password)
            # login(request, user) #Cannot login a NOT Active user

            current_site = get_current_site(request)
            mail_subject = 'Confirmación de correo electrónico'
            message = render_to_string('accounts/acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            # to_email = user_form.cleaned_data.get('email')
            to_email = 'oma.gonzales@gmail.com'
            from_email = 'stickersgallito@stickersgallito.pe'
            email = EmailMessage(
                mail_subject, message, to=[to_email], from_email=from_email
            )
            email.send()

            return redirect('shop:email_confirmation_needed')


        else:
            print(user_form.errors)
            print(profile_form.errors)


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


### Reviews ###


@csrf_exempt
def make_review_view(request):
    user = request.user
    category_slug = request.POST.get('category_slug')
    print("Category Slug:")
    print(category_slug)
    product_slug = request.POST.get("product_slug")

    sample_slug = request.POST.get("sample_slug")
    print(sample_slug)

    review = request.POST.get("review")
    stars = float(request.POST.get("stars"))
    print("Stars Type")
    print(stars)
    print(type(stars))

    if category_slug == 'muestras':

        print("Enters if of Samples")
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
                print("Se guardo el Review")

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
                print("Se guardo el Review")

        except Product_Review.DoesNotExist:
            print("No se creo el Review")


    return HttpResponse("Hi")



from django.http.response import JsonResponse
def prices(request):
    size_selected = request.GET.get("size_selected")
    c_slug = 'stickers'
    product_slug = 'stickers-transparentes'


    prices = list(ProductsPricing.objects.filter(category=Category.objects.get(slug=c_slug),
                                              product=Product.objects.get(slug=product_slug),
                                              size=size_selected).values_list("price",flat=True))

    return JsonResponse({'prices': prices})