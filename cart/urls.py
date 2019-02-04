from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # path('add/<int:product_id>/', views.add_cart, name = 'add_cart'),
    path('', views.cart_detail, name='cart_detail'),
    # path('remove/<int:cart_item_id>/', views.cart_remove, name = 'cart_remove'),
    path('full_remove/<int:cart_item_id>/', views.full_remove, name='full_remove'),
    path('full_remove_sample/<int:sample_item_id>/', views.full_remove_sample, name='full_remove_sample'),
    path('charge/', views.cart_charge, name='cart_charge'),


]
