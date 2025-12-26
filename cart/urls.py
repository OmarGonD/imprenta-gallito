from django.urls import path
from . import views

app_name = 'carrito-de-compras'

urlpatterns = [
    # path('add/<int:product_id>/', views.add_cart, name = 'add_cart'),
    path('', views.cart_detail, name='cart_detail'),
    # path('remove/<int:cart_item_id>/', views.cart_remove, name = 'cart_remove'),
    path('full_remove/<int:cart_item_id>/', views.delete_item, name='delete_item'),
    path('charge_deposit_payment/', views.cart_charge_deposit_payment, name='cart_charge_deposit_payment'),

    path('upload-design/<int:item_id>/', views.upload_design, name='upload_design'),
    path('checkout/', views.checkout, name='checkout'),
    path('add/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),
    path('update-contact/<int:item_id>/', views.update_contact, name='update_contact'),
    path('update-template/', views.update_template, name='update_template'),
    path('order/pending/<int:order_id>/', views.order_pending_payment, name='order_pending_payment'),
    path('order/upload-receipt/<int:order_id>/', views.upload_payment_receipt, name='upload_payment_receipt'),

]
