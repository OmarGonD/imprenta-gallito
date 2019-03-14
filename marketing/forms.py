from django import forms
from .models import SignUp

class EmailSignUpForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={
        "type":"email",
        "name": "email",
        "id": "email",
        "placeholder": "Ingrese su correo electrónico",
        'class': 'subscribe_field'
    }), label="")
    class Meta:
        model = SignUp
        fields = ('email',)
