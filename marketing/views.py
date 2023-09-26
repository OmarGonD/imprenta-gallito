from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
import json
from requests.auth import HTTPBasicAuth
import requests
from django.views.decorators.csrf import csrf_exempt
from .forms import EmailSignUpForm
from .models import SignUp, Cupons
from django.contrib.auth.models import User



@csrf_exempt
def email_signup_form(request):
    form = EmailSignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user_signup_qs = User.objects.filter(email = form.instance.email)
            email_signup_qs = SignUp.objects.filter(email = form.instance.email)
            if email_signup_qs.exists() or user_signup_qs.exists():
                messages.info(request, "Usted ya está registrado en nuestro sistema.")
            else:
                print("Antes de suscribirse")
                subscribe(form.instance.email)
                form.save()
    return HttpResponse("Hi")


### CUPONES ###

@csrf_exempt
def cupons(request):
    if request.method == 'POST':
        user_cupon = request.POST.get('user_cupon')
        if user_cupon:
            print("## USER CUPON")
        else:
            print("## NO USER CUPON")    
        response = HttpResponse("Hi")
        response.set_cookie("cupon", user_cupon)
        return response



# def cupons(request):
#     if request.method == 'POST':
#         user_cupon = request.POST.get('user_cupon')
#         try:
#             cupon = Cupons.objects.get(cupon=user_cupon)
#             if cupon.active:
#                 if cupon.percentage:
#                     response = HttpResponse("Hi")
#                     response.set_cookie("cupon_percentage_discount", cupon.percentage)
#                     return response
#
#                 else:
#                     response = HttpResponse("Hi")
#                     response.set_cookie("cupon_hard_discount", cupon.hard_discount)
#                     return response
#             else:
#                 print("El cupón no está activo")
#
#         except:
#             print("El cupón introducido no es válido.")
#
#     return response




