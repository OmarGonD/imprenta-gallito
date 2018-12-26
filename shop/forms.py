import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm

from cart.models import SizeQuantity
from django.db import transaction
from .models import Profile

# Variables

TAMANIOS = (('variante_50', '50 mm x 50 mm',), ('variante_75', '75 mm x 75 mm',),
            ('variante_100', '100 mm x 100 mm',), ('variante_125', '125 mm x 125 mm',))

CANTIDADES = (('cantidad_50', '50',), ('cantidad_100', '100',),
              ('cantidad_200', '200',), ('cantidad_300', '300',),
              ('cantidad_500', '500',), ('cantidad_1000', '1000',),
              ('cantidad_2000', '2000',), ('cantidad_3000', '3000',),
              ('cantidad_4000', '4000',), ('cantidad_5000', '5000',),
              ('cantidad_1000', '1000',))


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label= "Nombre", max_length=100, required=True)
    last_name = forms.CharField(label = 'Apellido', max_length=100, required=True)
    username = forms.CharField(label='Nombre de usuario', max_length=100, required=True)
    password1 = forms.CharField(label = 'Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1',
                 'password2')
        # help_texts = {
        #     'username': '',
        #     'password': '',
        # }


class ProfileForm(ModelForm):

    def __init__(self, district_list, province_list, department_list, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['shipping_district'] = forms.ChoiceField(choices=tuple([(name, name) for name in district_list]))
        self.fields['shipping_province'] = forms.ChoiceField(choices=tuple([(name, name) for name in province_list]))
        self.fields['shipping_department'] = forms.ChoiceField(choices=tuple([(name, name) for name in department_list]))
    #
    # # birth_date = forms.DateTimeField(required=False)
    dni = forms.CharField(label = 'DNI', max_length=100, required=True)
    email = forms.EmailField(label = 'Correo electrónico', max_length=254, widget=forms.TextInput(attrs={'placeholder': 'micorreo@correo.com'}))
    cellphone = forms.CharField(label = 'Celular o  teléfono', max_length=15, required=True)
    shipping_address1 = forms.CharField(label = 'Dirección de envío', max_length=100, required=True)
    shipping_address2 = forms.CharField(label = 'Dirección de envío 2 (opcional)', max_length=100, required=False)
    # shipping_district = forms.ChoiceField(label='Distrito', required=True)
    # shipping_province = forms.ChoiceField(label = 'Provincia', required=True)
    # shipping_department = forms.ChoiceField(label = 'Departamento', required=True)

    class Meta:
        model = Profile
        fields = ('dni',  'email', 'cellphone', 'shipping_address1',
                  'shipping_address2', 'shipping_department', 'shipping_province', 'shipping_district')








class StepOneForm(forms.Form):
    size = forms.ChoiceField(choices=TAMANIOS, widget=forms.RadioSelect(), label='Selecciona un tamaño')
    quantity = forms.ChoiceField(choices=CANTIDADES, widget=forms.RadioSelect(), label='Selecciona la cantidad')


class StepTwoForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = SizeQuantity
        fields = ('image', 'comment')

    def __init__(self, *args, **kwargs):
        super(StepTwoForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = False
        self.fields['image'].required = False

    def save(self, commit=True):
        instance = super(StepTwoForm, self).save(commit=commit)
        # self.send_email()
        return instance

    # def send_email(self):
    #     send_mail('Django Test', 'My message', 'oma.oma@gmail.com',
    #               ['oma.oma@gmail.com'], fail_silently=False)




