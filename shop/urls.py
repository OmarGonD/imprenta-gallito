from django.contrib import admin
from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.allCat, name='allCat'),
    path('muestras/', views.SamplePackPage, name='SamplePackPage'),
    path('province/', views.get_province, name='province'),
    path('district/', views.get_district, name='district'),
    path('quienes_somos/', views.quienes_somos, name='quienes_somos'),
    path('como_comprar/', views.como_comprar, name='como_comprar'),
    path('contactanos/', views.contactanos, name='contactanos'),
    path('muestras/<slug:sample_slug>/medida-y-cantidad', views.StepOneView_Sample.as_view(), name='SampleDetail'),
    path('muestras/<slug:sample_slug>/subir-arte', views.StepTwoView_Sample.as_view(), name='UploadArt'),
    path('<slug:c_slug>/<slug:product_slug>/medida-y-cantidad', views.StepOneView.as_view(), name='ProdDetail'),
    path('<slug:c_slug>/<slug:product_slug>/subir-arte', views.StepTwoView.as_view(), name='UploadArt'),
    path('<slug:c_slug>/<slug:product_slug>', views.SamplePack, name='SamplePack'),
    path('<slug:c_slug>', views.ProdCatDetail, name='ProdCatDetail'),
    path('make_review/', views.make_review_view, name='make_review_view'),
]
