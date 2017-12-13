from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db import models
from accounts.models import UserProfile
from products.models import Product


class Merchant(models.Model):

    userprofile = models.OneToOneField(User)
    user_products = models.OneToOneField(Product, blank=True,)
    bank_acc_num = models.CharField(blank=True, default='', max_length=10)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Merchant with username %s' % (self.userprofile.username)
