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


# Create your views here.

MAILCHIMP_API_KEY = settings.MAILCHIMP_API_KEY
MAILCHIMP_DATA_CENTER = settings.MAILCHIMP_DATA_CENTER
MAILCHIMP_EMAIL_LIST_ID = settings.MAILCHIMP_EMAIL_LIST_ID

api_url = f'https://{MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0'

members_endpoint = f'{api_url}/lists/{MAILCHIMP_EMAIL_LIST_ID}/members'


def subscribe(email):
    data = {
        'email_address': email,
        'status': 'subscribed'
    }
    r = requests.post(
        members_endpoint,
        auth=HTTPBasicAuth("", MAILCHIMP_API_KEY),
        data=json.dumps(data)
    )
    print(r.status_code)
    print(r.json())
    print("Members EndPoint: ",members_endpoint)
    return r.status_code, r.json()

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

def cupons(request):
    if request.method == 'POST':
        user_cupon = request.POST.get('user_cupon')
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




