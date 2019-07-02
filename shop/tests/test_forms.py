from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from shop.models import Peru
from shop.forms import SignUpForm, ProfileForm
from django.contrib.auth import get_user_model
from django.core.management import call_command

import datetime


#coverage run manage.py test shop/tests -v 2

class SignUpFormTest(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', email='testemail@example.com',
            password='secret')

    
    def test_signup_form(self):
        form_data = {'first_name': 'oma',
                     'last_name': 'gonza',
                     'username': 'omagonza',
                     'email': 'oma.gonzales@gmail.com',
                     'password1': 'caballo123',
                     'password2': 'caballo123'}
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_profile_form(self):
        
        call_command('ubigeo_peru')

        peru = Peru.objects.all()
        department_list = set()
        province_list = set()
        district_list = set()
        for p in peru:
            department_list.add(p.departamento)
        department_list = list(department_list)
        
        if len(department_list):
            province_list = set(Peru.objects.filter(departamento=department_list[0]).values_list("provincia", flat=True))
            province_list = list(province_list)
           
        else:
            province_list = set()
        if len(province_list):
            district_list = set(
                Peru.objects.filter(departamento=department_list[0], provincia=province_list[0]).values_list("distrito", flat=True))                                                                                             
            district_list = list(district_list)
        else:
            district_list = set()
        
        form_data = {'user': self.user,
                     'dni': 454545,
                     'phone_number': 96959495,
                     'birthdate': datetime.datetime.now(),
                     'shipping_address1': 'Urb. Los Leones',
                     'shipping_address2': 'Colegio X',
                     'shipping_department': department_list[0],
                     'shipping_province': province_list[0],
                     'shipping_district': district_list[0]}
        form = ProfileForm(district_list=district_list, province_list=province_list,
                           department_list=department_list, data=form_data)
        print(form.errors)
        self.assertTrue(form.is_valid())
