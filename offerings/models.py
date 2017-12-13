from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Offering(object):
    """docstring for Offering"""
    def __init__(self, arg):
        super(Offering, self).__init__()
        self.arg = arg
        