from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, render_to_response
from django.http import HttpResponse
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

def index(request):
    text_var = 'This is my first Django WebPage'
    return HttpResponse(text_var)

# Category View


def allCat(request):
    #Muestras todas las categorias de productos en el home, menos "Muestras"
    categories = Category.objects.exclude(name='Muestras')
    return render(request, 'shop/category.html', {'categories': categories})





def SamplePackPage(request):

    #La categoria es necesaria para mostrar el video de c/categoria

    categoria_muestras = Category.objects.get(slug='muestras')

    # Productos que pertenecen a la categoria muestras

    muestras = Product.objects.filter(category__slug='muestras')

    return render(request, 'shop/muestras.html', {'categoria_muestras': categoria_muestras,'muestras': muestras})



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
            slug = product_slug,
        )

        cart_item = CartItem.objects.create(
            cart = cart,
            product = product,
            size = "",
            quantity= "",
            image = product.image,
            comment = "",
        )



        return redirect('/cart/')

    except Exception as e:
        raise e

    return HttpResponse("Hi")



def ProdCatDetail(request, c_slug):

    if c_slug is not "muestras":

        category = Category.objects.get(slug=c_slug)

        try:
            products = Product.objects.filter(category__slug=c_slug)
        except Exception as e:
            raise e

        return render(request, 'shop/products.html', {'category': category, 'products': products})


# Tamanos y cantidades

class StepOneView(FormView):
    form_class = StepOneForm
    template_name = 'shop/product.html'
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

         # pre-populate form if someone goes back and forth between forms

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
        # In form_valid method we can access the form data in dict format
        # and will store it in django session
        print('--Step One: Form is Valid', Product.objects.get(
            category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['product_slug']
        ).id)
        self.request.session['product'] = form.cleaned_data.get('product')
        self.request.session['size'] = form.cleaned_data.get('size')
        self.request.session['quantity'] = form.cleaned_data.get('quantity')


        return HttpResponseRedirect(self.get_success_url())



# here we are going to use CreateView to save the Third step ModelForm
class StepTwoView(CreateView):
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

        self.request.session['cart_id'] = secrets.token_urlsafe(22)

        try:
            cart = Cart.objects.get(cart_id=_cart_id(self.request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                    cart_id = _cart_id(self.request)
                )

            cart.save()

        form.instance.cart = cart
        form.instance.product = Product.objects.get(
            category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['product_slug']
        )  # get tamanios from session
        form.instance.size = self.request.session.get('size')  # get tamanios from session
        form.instance.quantity = self.request.session.get('quantity')  # get cantidades from session
        del self.request.session['quantity']  # delete cantidades value from session
        del self.request.session['size']  # delete tamanios value from session
        self.request.session.modified = True
        return super(StepTwoView, self).form_valid(form)






def signinView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # username = request.POST['username']
            # password = request.POST['password']
            print(username)
            print(password)
            user = authenticate(username = username,
                                password = password)
            if user is not None:
                login(request, user)
                cart_id =_cart_id(request)
                request.session['cart_id'] = cart_id
                return redirect('shop:allCat')
            else:
                return redirect('signup')

    else:
        form = AuthenticationForm()
    return render(request, 'accounts/signin.html', {'form':form})


def signoutView(request):
    if request.user.is_superuser:
        request.session.modified = True
        logout(request)
        return redirect('signin')
    else:
        del request.session['cart_id']
        request.session.modified = True
        logout(request)
        return redirect('signin')






### New SignUp Extended

from django.shortcuts import render



@transaction.atomic
def signupView(request):
    peru = Peru.objects.all()
    print(peru)
    department_list = set()
    province_list = set()
    district_list = set()
    for p in peru:
        department_list.add(p.departamento)
        district_list.add(p.distrito)

    province_list = set(Peru.objects.filter(departamento=peru.first().departamento).values_list("provincia", flat=True))

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
            profile_form = ProfileForm(district_list, province_list, department_list, request.POST, instance=user.profile)  # Reload the profile form with the profile instance
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
