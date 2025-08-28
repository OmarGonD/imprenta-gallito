from django.contrib import admin
from django.urls import path

from . import views

app_name = 'marketing'

urlpatterns = [
    path('suscribirse/', views.email_signup_form, name='email_signup_form'),
    path('cupones/', views.cupons, name='cupones')
]
