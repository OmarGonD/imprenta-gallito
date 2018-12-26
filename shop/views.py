from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, render_to_response
from django.http import HttpResponse
from .models import Category, Product, Peru
from django.contrib.auth.models import Group, User
from .forms import SignUpForm, StepOneForm, StepTwoForm, ProfileForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.views.generic.edit import CreateView, FormView
from cart.models import Cart
from cart.views import _cart_id
from django.db import transaction


# Create your views here.

def index(request):
    text_var = 'This is my first Django WebPage'
    return HttpResponse(text_var)

# Category View


def allProdCat(request, c_slug=None):
    c_page = None
    products = None
    if c_slug != None:
        c_page = get_object_or_404(Category, slug = c_slug)
        products = Product.objects.filter(category=c_page, available=True)
    else:
        products = Product.objects.all().filter(available=True)

    return render(request, 'shop/category.html', {'category':c_page, 'products': products})




# def ProdCatDetail(request, c_slug, product_slug):
#     try:
#         product = Product.objects.get(category__slug=c_slug, slug = product_slug)
#     except Exception as e:
#         raise e
#     return render(request, 'shop/product-original.html', {'product':product})
#




# Tamanos y cantidades

class StepOneView(FormView):
    form_class = StepOneForm
    template_name = 'shop/product.html'
    success_url = 'subir-arte'

    def get_initials(self):
         # pre-populate form if someone goes back and forth between forms
         initial = super(StepOneView, self).get_initials()
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





### Registro y Login/Logout de usuarios


# def signupView(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             signup_user = User.objects.get(username = username)
#             customer_group = Group.objects.get(name = 'Clientes')
#             customer_group.user_set.add(signup_user)
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('cart:cart_detail')
#     else:
#         form = SignUpForm()
#
#     return render(request, 'accounts/signup.html', {'form':form})


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
                return redirect('shop:allProdCat')
            else:
                return redirect('signup')

    else:
        form = AuthenticationForm()
    return render(request, 'accounts/signin.html', {'form':form})


def signoutView(request):
    logout(request)
    return redirect('signin')





### New SignUp Extended

@transaction.atomic


def signupView(request):
    peru = Peru.objects.all()
    print(peru)
    department_list = set()
    province_list = set()
    district_list = set()
    for p in peru:
        department_list.add(p.departamento)
        province_list.add(p.provincia)
        district_list.add(p.distrito)

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



