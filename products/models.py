from cloudinary.models import CloudinaryField
from hvad.models import TranslatableModel, TranslatedFields
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from smart_selects.db_fields import ChainedForeignKey

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_libs.models_mixins import TranslationModelMixin


def valid_pct(val):
    if val.endswith("%"):
       return float(val[:-1])/100
    else:
       try:
          return float(val)
       except ValueError:          
          raise ValidationError(
              _('%(value)s is not a valid pct'),
                params={'value': value},
           )

class Product(models.Model):
    user = models.ForeignKey(User)
    price = models.IntegerField()
    quantity = models.IntegerField(blank=True, default=1)
    owner = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(blank=True, default='')
    slug = models.SlugField(blank=True, null=False, unique=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    address = models.CharField(max_length=100, blank=False, default='')
    date_created = models.DateField(auto_now_add=True)
    date_last_modified = models.DateField(auto_now=True)
    commission = models.CharField(max_length=10, validators=[valid_pct])
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/product/{}/" .format(self.id)


class ProductPhoto(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    product = models.ForeignKey(Product, null=True, blank=True)
    image = CloudinaryField(
        resource_type='image',
        type='upload',
        blank=True,
        default="http://res.cloudinary.com/theeventdiary/image/upload/v1483614044/lg_m8sc17.jpg",
    )

    """ Informative name for mode """
    def __unicode__(self):
        try:
            public_id = self.image.public_id
        except AttributeError:
            public_id = ''
        return "Photo <%s:%s>" % (self.product, public_id) or u''


class Offering(models.Model):
    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    customer_name = models.CharField(max_length=100, null=False, blank=False)
    customer_email = models.EmailField(max_length=70, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=100, null=False, blank=False)
    is_approved = models.BooleanField(default=False)
    counter_price = models.IntegerField(blank=True, null=True)
    previous_counter_price = models.IntegerField(blank=True, null=True)
    counter_price_text = models.CharField(max_length=250, blank=True, null=True)
    is_accepted = models.BooleanField(default=False)
    approved_price = models.IntegerField(blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    date_last_modified = models.DateField(auto_now=True)


class CounterOffering(models.Model):
    user = models.ForeignKey(User)
    product = models.ForeignKey(Product) 
    customer_name = models.CharField(max_length=100, null=False, blank=False)
    customer_email = models.EmailField(max_length=70, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    date_last_modified = models.DateField(auto_now=True)


class OfferingStatus(TranslationModelMixin, TranslatableModel):
    """
    Master data containing all offering status.
    For translatable fields check ``OfferingStatusTranslation``.
    :slug: A unique slug identifier.
    translated:
    :name: The displayable name for the status.
    """
    slug = models.SlugField(
        verbose_name=_('Slug'),
    )

    translations = TranslatedFields(
        name=models.CharField(
            verbose_name=_('Name'),
            max_length=128,
        )
    )
        
