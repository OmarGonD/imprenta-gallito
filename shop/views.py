from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, render_to_response
from django.http import HttpResponse
from django.template import RequestContext

from .models import Category, Product, Peru
from django.contrib.auth.models import Group, User
from .forms import SignUpForm, StepOneForm, StepTwoForm, ProfileForm, SamplePackForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.views.generic.edit import CreateView, FormView
from cart.models import Cart, CartItem
from cart.views import _cart_id
from django.db import transaction
from django.urls import reverse
import secrets


# Create your views here.

# Category View


def allCat(request):
    # Muestras todas las categorias de productos en el home, menos "Muestras"
    categories = Category.objects.exclude(name='Muestras')

    # return render(request, 'shop/index.html', {'categories': categories}, context_instance=RequestContext(request))
    return render(request, 'shop/index.html', {'categories': categories})


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

    muestras = Product.objects.filter(category__slug='muestras')

    return render(request, 'shop/muestras.html', {'categoria_muestras': categoria_muestras, 'muestras': muestras})


def SamplePack(request, c_slug, product_slug):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))

    except Cart.DoesNotExist:

        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )

    try:
        product = Product.objects.get(
            category__slug=c_slug,
            slug=product_slug,
        )

        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            size="",
            quantity="",
            image=product.image,
            comment="",
        )

        return redirect('/cart/')

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
        if not cart_id:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.id
        cart = Cart.objects.get(id=cart_id)
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
    success_url = '/cart/'

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
        cart_item.image = form.cleaned_data["image"]
        cart_item.comment = form.cleaned_data["comment"]
        cart_item.save()
        response = HttpResponseRedirect(self.get_success_url())
        response.delete_cookie("item_id")
        return response


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
                return redirect('cart:cart_detail')
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
    return response


### New SignUp Extended

from django.shortcuts import render


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
        user_form = SignUpForm(request.POST)
        profile_form = ProfileForm(district_list, province_list, department_list, request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            username = user_form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            customer_group = Group.objects.get(name='Clientes')
            customer_group.user_set.add(signup_user)
            raw_password = user_form.cleaned_data.get('password1')
            user.refresh_from_db()  # This will load the Profile created by the Signal
            profile_form = ProfileForm(district_list, province_list, department_list, request.POST,
                                       instance=user.profile)  # Reload the profile form with the profile instance
            profile_form.full_clean()  # Manually clean the form this time. It is implicitly called by "is_valid()" method
            profile_form.save()  # Gracefully save the form

            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('cart:cart_detail')
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
