from django.urls import path, re_path
from . import views

app_name = "shop"

urlpatterns = [
    # =============================================
    # PÁGINAS GENERALES
    # =============================================
    path('', views.Home, name='home'),
    path('province/', views.get_province, name='province'),
    path('district/', views.get_district, name='district'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('como-comprar/', views.como_comprar, name='como_comprar'),
    path('contactanos/', views.contactanos, name='contactanos'),
    path('preguntas-frecuentes/', views.preguntas_frecuentes, name='preguntas_frecuentes'),
    path('legales/privacidad', views.legales_privacidad, name='legales_privacidad'),
    path('legales/terminos', views.legales_terminos, name='legales_terminos'),


    
    # =============================================
    # ROPA Y BOLSOS → SIEMPRE ANTES QUE LAS GENÉRICAS
    # =============================================




    # =============================================
    # PERFIL DE USUARIO
    # =============================================
    path('perfil/', views.profile_view, name='profile'),
    path('perfil/editar/', views.profile_edit_view, name='profile_edit'),



    # =============================================
    # CARRITO / API
    # =============================================
    path('agregar-producto-carrito/', views.add_product_to_cart, name='add_product_to_cart'),
    path('api/product-pricing/<str:product_slug>/<int:quantity>/', views.get_product_pricing, name='get_product_pricing'),
    path('api/product/<str:product_slug>/colors/', views.get_product_colors, name='get_product_colors'),
    path('api/clothing/add-to-cart/', views.add_clothing_to_cart, name='add_clothing_to_cart'),
    path('api/cart/add/', views.add_to_cart_api, name='add_to_cart_api'),
    
    # =============================================
    # NUEVO: API para sistema genérico de opciones
    # =============================================
    path('api/product/<str:product_slug>/options/', views.get_product_options, name='get_product_options'),
    path('api/colors/', views.get_available_colors, name='get_available_colors'),


    # =============================================
    # GALERÍA DE DISEÑOS
    # =============================================
    path('<slug:category_slug>/producto/<slug:product_slug>/elegir-diseno/', views.template_gallery_view, name='template_gallery'),

    


    # =============================================
    # ACTIVACIÓN DE EMAIL
    # =============================================
    path('email_confirmation_needed/', views.email_confirmation_needed, name='email_confirmation_needed'),
    re_path(
        r'^confirmacion-de-correo-electronico/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,50})/$',
        views.activate,
        name='activate'
    ),


    # =============================================
    # LISTADOS DE CATEGORÍAS Y SUBCATEGORÍAS (al final)
    # =============================================
    path('<slug:category_slug>/', views.category_view, name='category'),
    path('<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_view, name='subcategory'),
    # =============================================
    # RUTAS GENÉRICAS → CON SUBCATEGORÍA REAL (3 niveles)
    # =============================================
    path('<slug:category_slug>/<slug:subcategory_slug>/<slug:product_slug>/', 
         views.product_detail, name='product_detail'),

   
]
