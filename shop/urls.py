from django.urls import path, re_path

from . import views

app_name = "shop"

urlpatterns = [
    path('', views.allCat, name='allCat'),
    path('packs/', views.PacksPage, name='PacksPage'), #Todos los packs
    path('catalogo', views.CatalogoListView.as_view(), name='catalogo'), #Todos los productos unitarios
    path('muestras/', views.SamplePackPage, name='SamplePackPage'), #Todas las muestras
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
    path('<slug:c_slug>/<slug:product_slug>', views.AddProduct, name='AddProduct'),
    path('agregar-pack/', views.AddPack, name='AddPack'),
    path('stickers-por-unidad/', views.AddUnitaryProduct, name='AddUnitaryProduct'),
    path('<slug:c_slug>', views.ProdCatDetail, name='ProdCatDetail'),
    path('make_review/', views.make_review_view, name='make_review_view'),
    path('prices/', views.prices, name='prices'),
    path('email_confirmation_needed/', views.email_confirmation_needed, name='email_confirmation_needed'),
    re_path(r'^confirmacion-de-correo-electronico/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('tarjetas-de-presentacion/', views.TarjetasPresentacionListView.as_view(), name='tarjetas_presentacion'),
    path('publicidad-impresa/', views.publicidad_impresa, name='publicidad_impresa'),
    path('banners-posters/', views.banners_posters, name='banners_posters'),
    path('etiquetas-stickers/', views.etiquetas_stickers, name='etiquetas_stickers'),
    path('ropa-bolsos/', views.ropa_bolsos, name='ropa_bolsos'),
    path('productos-promocionales/', views.productos_promocionales, name='productos_promocionales'),
    path('empaques/', views.EmpaquesListView.as_view(), name='empaques-list'),
    path('folletoss/', views.FolletosListView.as_view(), name='folletos-list'),
    path('posters/', views.PostersListView.as_view(), name='posters'),
    path('invitaciones-regalos/', views.invitaciones_regalos, name='invitaciones_regalos'),
    path('bodas/', views.bodas, name='bodas'),
    path('servicios-diseno/', views.servicios_diseno, name='servicios_diseno'),
]
