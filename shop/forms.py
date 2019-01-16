import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm

from cart.models import CartItem
from django.db import transaction
from shop.models import Peru
from .models import Profile

# Variables


TAMANIOS = (('50mm x 50mm', '50 mm x 50 mm',), ('75mm x 75mm', '75 mm x 75 mm',),
            ('100mm x 100mm', '100 mm x 100 mm',), ('125mm x 125mm', '125 mm x 125 mm',))

CANTIDADES = (('50', '50',), ('100', '100',),
              ('200', '200',), ('300', '300',),
              ('500', '500',), ('1000', '1000',),
              ('2000', '2000',), ('3000', '3000',),
              ('4000', '4000',), ('5000', '5000',),
              ('10000', '10000',))



my_default_errors = {
    'required': 'Este campo es obligatorio',
    'invalid': 'Ingrese un valor válido'
}

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label= "Nombre", max_length=100, required=True)
    last_name = forms.CharField(label = 'Apellido', max_length=100, required=True)
    username = forms.CharField(label='Nombre de usuario', max_length=100, required=True, error_messages=my_default_errors)
    email = forms.EmailField(label='Correo electrónico', max_length=60, required=True)
    password1 = forms.CharField(label = 'Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1',
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

    dni = forms.CharField(label = 'DNI', max_length=100, required=True)
    # email = forms.EmailField(label = 'Correo electrónico', max_length=254, widget=forms.TextInput(attrs={'placeholder': 'micorreo@correo.com'}))
    cellphone = forms.CharField(label = 'Celular o  teléfono', max_length=15, required=True)
    shipping_address1 = forms.CharField(label = 'Dirección de envío', max_length=100, required=True)
    shipping_address2 = forms.CharField(label = 'Dirección de envío 2 (opcional)', max_length=100, required=False)

    class Meta:
        model = Profile
        fields = ('dni', 'cellphone', 'shipping_address1',
                  'shipping_address2', 'shipping_department', 'shipping_province', 'shipping_district')






class StepOneForm(forms.Form):
    size = forms.ChoiceField(choices=TAMANIOS, widget=forms.RadioSelect(), label='Selecciona un tamaño')
    quantity = forms.ChoiceField(choices=CANTIDADES, widget=forms.RadioSelect(), label='Selecciona la cantidad')


class StepTwoForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CartItem
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




class SamplePackForm(forms.ModelForm):


    class Meta:
        model = CartItem
        fields = ()

    def __init__(self, *args, **kwargs):
        super(SamplePackForm, self).__init__(*args, **kwargs)
        self.fields['cart'].required = False
        self.fields['size'].required = False
        self.fields['quantity'].required = False
        self.fields['comment'].required = False
        self.fields['image'].required = False

    def save(self, commit=True):
        instance = super(SamplePackForm, self).save(commit=commit)
        # self.send_email()
        return instance
