from django.contrib import admin
from django.urls import path, re_path

from . import views

app_name = 'shop'

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.allCat, name='allCat'),
    path('muestras/', views.SamplePackPage, name='SamplePackPage'),
    path('province/', views.get_province, name='province'),
    path('district/', views.get_district, name='district'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('como-comprar/', views.como_comprar, name='como_comprar'),
    path('contactanos/', views.contactanos, name='contactanos'),
    path('preguntas-frecuentes/', views.preguntas_frecuentes, name='preguntas_frecuentes'),
    path('legales/privacidad', views.legales_privacidad, name='legales_privacidad'),
    path('legales/terminos', views.legales_terminos, name='legales_terminos'),
    path('muestras/<slug:sample_slug>/medida-y-cantidad', views.StepOneView_Sample.as_view(), name='SampleDetail'),
    path('muestras/<slug:sample_slug>/subir-arte', views.StepTwoView_Sample.as_view(), name='UploadArt'),
    path('<slug:c_slug>/<slug:product_slug>/medida-y-cantidad', views.StepOneView.as_view(), name='ProdDetail'),
    path('<slug:c_slug>/<slug:product_slug>/subir-arte', views.StepTwoView.as_view(), name='UploadArt'),
    path('<slug:c_slug>/<slug:product_slug>', views.SamplePack, name='SamplePack'),
    path('<slug:c_slug>', views.ProdCatDetail, name='ProdCatDetail'),
    path('make_review/', views.make_review_view, name='make_review_view'),
    path('prices/', views.prices, name='prices'),
    path('email_confirmation_needed/', views.email_confirmation_needed, name='email_confirmation_needed'),
    re_path(r'^confirmacion-de-correo-electronico/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate')
]