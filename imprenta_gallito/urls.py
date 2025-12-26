"""imprenta_gallito URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from shop import views
from allauth.account import views as allauth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuenta-inactiva/', allauth_views.account_inactive, name='account_inactive'),
    path('accounts/', include('allauth.urls')),
    
    # Overrides de Allauth para usar rutas en español y nombres de vista compatibles
    path('registrarse/', views.signupView, name='account_signup'),
    path('ingresar/', views.signinView, name='account_login'),
    path('salir/', views.signoutView, name='account_logout'),
    path('verificacion-enviada/', allauth_views.email_verification_sent, name='account_email_verification_sent'),
    path('confirmar-correo/', allauth_views.confirm_email, name='account_confirm_email_no_key'),
    path('confirmar-correo/<str:key>/', allauth_views.confirm_email, name='account_confirm_email'),
    
    path('carrito-de-compras/', include('cart.urls')),
    path('marketing/', include('marketing.urls')),
    path('email-necesita-validacion/', views.email_confirmation_needed, name='email_confirmation_needed'),
    path('reenviar-confirmacion-email/', views.resend_verification_email, name='resend_verification_email'),
    path('province/', views.get_province, name='province'),
    path('district/', views.get_district, name='district'),
    path('', include('shop.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
