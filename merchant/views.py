from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View, ListView
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext, Engine, loader

from products.baseviews import ProductListBaseView
from products.forms import ProductForm, ImageForm
from products.models import Product, ProductPhoto, Offering
from products.context_processor import Image_Effects

LOGIN_URL = '/login/'
EMAIL_SENDER = 'karamba.com.ng'

class ManageProductView(ProductListBaseView):
    """Manage a single product"""

    def get(self, request, username):
        """Renders a page showing a product that was created by a merchant
        """

        list_title = "My Products"
        list_description = "All products posted by you"
        template = "product.html"

        if request.user.is_authenticated:
            if request.user.userprofile.is_merchant:
                merchant_id = request.user.id
                products = Product.objects.filter(user_id=merchant_id)
                # get the rendered list of deals
                rendered_product_list = self.render_product_list(request, queryset=products, title=list_title, description=list_description, username=request.user)
                context = {
                    'rendered_product_list': rendered_product_list,
                    'Image_Effects' : Image_Effects,
                }
                return render(request, template, context)
            else:
                messages.add_message(
                    request, messages.INFO,
                    'Forbidden Page'
                )
                return redirect(reverse('product_listing'))
        else:
            messages.add_message(
                request, messages.ERROR,
                'You need to log in to view this page'
            )
            return redirect(reverse('login'))

@login_required(login_url=LOGIN_URL)
def offering_list_view(request, username):
    merchant_id = request.user.id
    products = Product.objects.filter(user_id=merchant_id)
    offering_list = list()

    for product in products:
        offerings = Offering.objects.filter(product_id=product.id)
        for i, offering in enumerate(offerings):
            offering_dict = {
                'offering': offering
            }
            offering_list.append(offering_dict)
    return render(request, "manage_offerings.html", {'offering_list': offering_list})

def offering_action(request, username):
    merchant_id = request.user.id
    products = Product.objects.filter(user_id=merchant_id)
    offering_list = list()
    ids = list()

    for product in products:
        offerings = Offering.objects.filter(product_id=product.id)
        for i, offering in enumerate(offerings):
            offering_dict = {
                'offering': offering
            }
            offering_list.append(offering_dict)

    for o_list in offering_list:
        offering_id = o_list.get('offering').id
        ids.append(offering_id)

    for i in ids:
        action_button_clicked = request.GET.keys()
        for val in action_button_clicked:
            offering = Offering.objects.filter(id=i).get()
            args = dict()
            if val == 'accept':
                if offering.is_accepted == False:
                    offering.is_accepted = True
                    offering.approved_price = offering.counter_price
                    args["email"] = offering.customer_email
                    args["name"] = offering.customer_name
                    offering.save()
                    return render(request, 'manage_offering_success.html', args)
            if val == 'approve':
                if offering.is_approved == False:
                    offering.is_approved = True
                    args["email"] = offering.customer_email
                    args["name"] = offering.customer_name
                    offering.save()
                    # send email to customer of approval
                    product = Product.objects.filter(id=offering.product_id).get()

                    offering_approved_email_context = RequestContext(
                        request,
                        {
                            'product_name': product.name,
                            'product_description': product.description,
                            'username': offering.customer_name,
                            'offering': offering.phone_number,
                        },
                    )

                    receipient = str(offering.customer_email)

                    subject, from_email, to = 'Bargain.ng: Offer Approved', EMAIL_SENDER, receipient
                    html_content=loader.get_template('offering_approved.html').render(offering_approved_email_context)
                    text_content=loader.get_template('offering_approved.txt').render(offering_approved_email_context)

                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    response = msg.send()

                    if response == 1:
                        messages.add_message(request, messages.INFO, 'Purchase approved')

                    return render(request, 'manage_offering_success.html', args)

                else:
                    messages.add_message(
                        request, messages.ERROR,
                        'This request as already being approved by you.'
                    )
                return render(request, "manage_offerings.html", {'offering_list': offering_list})

@login_required(login_url=LOGIN_URL)
def edit_merchant_product(request, username, product_slug=None):
    """Updates information about a product that was created by a merchant.
    """

    product = Product.objects.get(slug=product_slug)
    ImageFormSet = modelformset_factory(ProductPhoto, form=ImageForm)

    if product.user.userprofile.is_merchant != request.user.userprofile.is_merchant:
        messages.add_message(
            request, messages.ERROR,
            'You are not allowed to manage this product'
        )
        return redirect(reverse('product_listing'))

    if request.method == 'POST':
        productform = ProductForm(request.POST, instance=product)
        formset = ImageFormSet(request.POST, request.FILES, queryset=ProductPhoto.objects.filter(product=product))

        if productform.is_valid() and formset.is_valid():
            productform.save(product)
            for form in formset:
                try:
                    image = form.cleaned_data['image']
                    photo = ProductPhoto(product=product, image=image)
                    photo.user_id = request.user.id
                    photo.save()
                except:
                    messages.error(request, 'Technical error')

            messages.add_message(
                request, messages.SUCCESS, 'The product was updated successfully.'
            )
        else:
            messages.add_message(
                request, messages.ERROR,
                'An error occurred while performing the operation.'
            )
        return redirect(reverse('merchant_manage_products', kwargs={'username': request.user}))
    else:
        form = ProductForm(instance=product)
        formset = ImageFormSet(queryset=ProductPhoto.objects.filter(product=product))
    return render(request, 'product_edit.html', {'form': form, 'formset': formset})
