from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


NIGERIAN_BANKS = (
    (1, "Access Bank Plc"), (2, "Citibank Nigeria Limited"), (3, "Diamond Bank Plc"),
    (4, "Ecobank Nigeria Plc"), (5, "Enterprise Bank"), (6, "Fidelity Bank Plc"),
    (7, "FIRST BANK NIGERIA LIMITED"), (8, "First City Monument Bank Plc"), (9, "Guaranty Trust Bank Plc"),
    (10, "Heritage Banking Company Ltd. "), (11, "Key Stone Bank"), (12, "MainStreet Bank "),
    (13, "Skye Bank Plc"), (14, "Stanbic IBTC Bank Ltd."), (15, "Standard Chartered Bank Nigeria Ltd."),
    (16, "Sterling Bank Plc"), (17, "SunTrust Bank Nigeria Limited"), (18, "Union Bank of Nigeria Plc"),
    (19, "United Bank For Africa Plc"), (20, "Unity Bank Plc"), (21, "Wema Bank Plc"),
    (22, "Zenith Bank Plc "),
)


class UserProfile(models.Model):

    user = models.OneToOneField(User)
    is_merchant = models.BooleanField(default=False)
    phonenumber = models.CharField(blank=True, default='', max_length=20)
    location = models.CharField(blank=True, max_length=100, default='')
    alternative_contact_name = models.CharField(blank=True, null=True, max_length=100, default='')
    alternative_contact_phonenumber = models.CharField(blank=True, null=True, default='', max_length=20)

    def check_diff(self, request_value):

        for field in request_value:
            if getattr(self, field, False) != False \
                and getattr(self, field) != request_value[field] and \
                    request_value[field] != '':
                    setattr(self, field, request_value[field])
        self.save()
        return {
            u'is_merchant': self.is_merchant,
            u'phonenumber': self.phonenumber,
            u'location': self.location,
            u'alternative_contact_name': self.alternative_contact_name,
            u'alternative_contact_phonenumber': self.alternative_contact_phonenumber,
        }

    def is_complete(self):
        """Checks if a user's profile is completed"""
        for field in self._meta.get_all_field_names():
            try:
                fieldattr = getattr(self, field)
                if fieldattr == '':
                    return False
                if type(fieldattr) == User:
                    if fieldattr.first_name == '' or fieldattr.last_name == '':
                        return False
            except:
                pass
        return True

    def is_approved_merchant(self):
        """Checks if the user is an approved merchant"""
        try:
            return getattr(self.merchant, 'approved', False)
        except:
            return False

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# Create your models here.
