from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    # path('thanks/<int:order_id>/', views.thanks, name = 'thanks'),
    path('gracias_pago_con_tarjeta_de_credito/', views.thanks_credit_card, name='thanks_credit_card'),
    path('gracias_pago_con_deposito_en_efectivo/', views.thanks_deposit_payment, name='thanks_deposit_payment'),
    path('historial_de_compras/', views.orderHistory, name = 'order_history'),
    # path('<int:order_id>/', views.viewOrder, name = 'order_detail'),
]