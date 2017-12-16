import datetime
from django import forms
from django.db import models
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import widgets
from cloudinary.forms import CloudinaryJsFileField, CloudinaryUnsignedJsFileField

from .models import Offering, OfferingStatus, Product, ProductPhoto, CounterOffering


class OfferingForm(forms.ModelForm):

    def __init__(self, user, product, *arg, **kwargs):
        self.user = user
        self.product = product
        super(OfferingForm, self).__init__(*arg, **kwargs)
        self.fields['phone_number'].error_messages = {'invalid': 'Please make sure you use your country code (e.g. +2340000000000)', 'required': 'Enter a valid phone number'}

    class Meta:
        model = Offering
        fields = ['customer_name', 'customer_email', 'phone_number', 'address']


class CounterOfferForm(forms.ModelForm):

    def __init__(self, user, product, *arg, **kwargs):
        self.user = user
        self.product = product
        super(CounterOfferForm, self).__init__(*arg, **kwargs)

    class Meta:
        model = Offering
        fields = ['counter_price', 'counter_price_text']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", 'quantity', "address", "description"]


class ImageForm(forms.ModelForm):    
    class Meta:
        model = ProductPhoto
        fields = ['image']
