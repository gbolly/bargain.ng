from django.contrib import admin
from .models import Product, ProductPhoto, Offering

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductPhoto)
admin.site.register(Offering)
