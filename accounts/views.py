# import pyotp
# from nexmo.libpynexmo.nexmomessage import NexmoMessage
import StringIO
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateView
from django.utils.text import slugify

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from authentication.views import LoginRequiredMixin

from accounts.models import NIGERIAN_BANKS


class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    Handles display of the account profile form view
    """
    form_class = UserProfileForm
    template_name = "account/profile.html"

    def get_context_data(self, **kwargs):
        context_var = super(UserProfileView, self).get_context_data(**kwargs)
        context_var.update({
            'profile': self.request.user.profile,
            'bank_account_name': {
                'choices': NIGERIAN_BANKS, 'default': 1
            },
            'breadcrumbs': [
                {'name': 'My Account', 'url': reverse_lazy('account')},
                {'name': 'Profile', },
            ]
        })
        return context_var

    def post(self, request, **kwargs):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        address = request.POST['location']
        if request.user.profile.is_merchant:
            bank_name = request.POST['bank_name']
            bank_acc_num = request.POST['bank_acc_num']
            alt_contact_name = request.POST['alt_contact_name']
            alt_contact_num = request.POST['alt_contact_num']

        profile = UserProfile.objects.get(id=request.user.profile.id)
        form_dict = profile.check_diff(request.POST)

        form = self.form_class(form_dict, instance=request.user.profile)
        if form.errors:
            context_var = {}
            empty = "Form should not be submitted empty"
            messages.add_message(request, messages.INFO, empty)
            return TemplateResponse(
                request, self.template_name, context_var
            )

        if form.is_valid():
            profile_data = form.save(commit=False)

            user = User.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.phonenumber = phonenumber
            user.location = address
            if request.user.profile.is_merchant:
                user.bank_name = bank_name
                user.bank_acc_num = bank_acc_num
                user.alt_contact_name = alt_contact_name
                user.alt_contact_num = alt_contact_num

            user.save()

            messages.add_message(
                request, messages.SUCCESS, 'Profile Updated!')
            return redirect(
                reverse_lazy('account_profile'),
                context_instance=RequestContext(request)
            )
