import cloudinary
from cloudinary.forms import cl_init_js_callbacks

from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext, Engine, loader
from django.utils import timezone
from django.views.generic.list import ListView
from django.forms import modelformset_factory
from datetime import datetime, timedelta
from background_task import background

from .forms import OfferingForm, CounterOfferForm, ImageForm, ProductForm
from .models import Product, Offering, ProductPhoto, CounterOffering
from products.context_processor import Image_Effects


EMAIL_SENDER = 'karamba.com.ng'


class ProductListView(ListView):
    model = Product
    template_name = 'product_listing.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['Image_Effects'] = Image_Effects
        return context

    def get_queryset(self):
        product = self.model.objects.all()
        query = self.request.GET.get("q")
        if query:
            return product.filter(name=query.capitalize())
        return product

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    photo = ProductPhoto.objects.filter(product_id=product)
    if photo:
        for image in photo:
            image = image.image
    else:
        image = ""

    return render(request, 'product_detail.html', {
        'product_id': product.id,
        'product_name': product.name,
        'product_description':product.description,
        'product_price':product.price,
        'product_owner':product.owner,
        'product_address':product.address,
        'product_slug':product.slug,
        'product_quantity':product.quantity,
        'Image_Effects':Image_Effects,
        'photo':photo,
        'image':image
    })

def counter_offer_view(request, slug, id_params=None, model_class=Product, form_class=CounterOfferForm, template_name='products/new_offer.html'):

    cls_default_msgs = {
        'not_signed_in': 'You must be signed in to purchase this product',
        'min_price': 'Product price cannot go below offer amount'
    }
    offer_made = False
    product = get_object_or_404(model_class, slug=slug)
    args = dict()

    if request.POST:
        form = form_class(request.user, product, request.POST)
        if request.user.is_authenticated():
            if form.is_valid():
                if id_params:
                    deal = Offering.objects.get(id=id_params)
                    update_fields = {
                        'counter_price': form.cleaned_data.get("counter_price"),
                        'counter_price_text': form.cleaned_data.get("counter_price_text"),
                        'previous_counter_price': deal.counter_price
                    }
                    Offering.objects.filter(id=id_params).update(**update_fields)
                else:
                    offering = form.save(commit=False)
                    offering.product = product
                    offering.user_id = request.user.id
                    offering.customer_name = request.user.username
                    offering.customer_email = request.user.email
                    offering.is_accepted = False

                    counter_price = form.cleaned_data.get("counter_price")
                    counter_price_text = form.cleaned_data.get("counter_price_text")

                    # TODO: There need to be a check in here so that we can know 
                    # if the countere offer is not less than the merchants minimum
                    # asking price otherwise it's a waste of time for the buyer.

                    offering.save()
                    args["slug"] = slug
                    args["product"] = product.name
                    offer_made = True
            return render(request, 'thank_you.html', {'product': product})
    else:
        return render(
            request,
            template_name,
            {
                'product': product,
            }
        )

    if offer_made:
        notify_user(request.user.id)

@background(schedule=60)
def notify_user(user_id):
    print("sending mail to {}".format(user_id))

def offering_view(request, slug, id_params=None, model_class=Product, form_class=OfferingForm, template_name='products/offering_form.html'):

    cls_default_msgs = {
        'not_signed_in': 'You must be signed in to purchase this product',
    }
    product = get_object_or_404(model_class, slug=slug)
    args = dict()

    if request.POST:
        form = form_class(request.user, product, request.POST)
        offer_obj = Offering.objects.filter(id=id_params)
        if request.user.is_authenticated():
            if form.is_valid():
                if offer_obj:
                    if offer_obj[0].is_accepted:
                        update_fields = {
                            'phone_number': form.cleaned_data.get("phone_number"),
                            'address': form.cleaned_data.get("address"),
                            'customer_name': form.cleaned_data.get("customer_name")
                        }
                        offer_obj.update(**update_fields)
                else:
                    offering = form.save(commit=False)
                    offering.product = product
                    offering.user_id = request.user.id
                    offering.is_approved = False

                    offering.save()
                    args["slug"] = slug
                    args["product"] = product.name

                    # compose the email
                    booking_email_context = RequestContext(
                        request,
                        {'username': offering.customer_name,
                         'product': product.name,
                         'offering': offering.customer_email,
                        },
                    )

                    receipient = str(offering.customer_email)

                    subject, from_email, to = 'TheEventDiary: Booking Recieved', EMAIL_SENDER, receipient
                    html_content=loader.get_template('products/booking_email.html').render(booking_email_context)
                    text_content=loader.get_template('products/booking_email.txt').render(booking_email_context)

                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    response = msg.send()

                    if response == 1:
                        messages.add_message(request, messages.INFO, offering.customer_email)

                return render(request, 'thank_you.html', {"product": product.name})
            else :
                return render(request, template_name, {'form': form})
        else:
            # Set error context
            error_msg = cls_default_msgs['not_signed_in']
            messages.add_message(request, messages.INFO, error_msg, form.errors)
            # Set template
            template = Engine.get_default().get_template('login.html')
            # Set result in RequestContext
            context = RequestContext(request)
            return HttpResponse(template.render(context))

    else:
        form = form_class(request.user, product)
        return render(request, template_name, {
            'product': product,
            'form': form,
        })

def offerings_by_user(request, slug):
    userid = request.user.id
    offerings = Offering.objects.filter(user_id=userid).order_by('-date_last_modified')
    return render(request, "user_offers.html", {"offers":offerings})

def new_product(request):
    cls_default_msgs = {
        'not_signed_in': 'You must be signed in to list your product',
        'invalid_param': 'Invalid parameters. \
                        Please make sure you fill in all fields',
    }

    product_form = ProductForm()
    ImageFormSet = modelformset_factory(ProductPhoto, form=ImageForm, extra=3)
    userid = request.user.id
    form = ProductForm(request.POST or None)
    formset = ImageFormSet(request.POST, request.FILES, queryset=ProductPhoto.objects.none())

    if request.POST:
        if request.user.is_authenticated():
            if form.is_valid() and formset.is_valid():
                product = form.save(commit=False)
                product.owner = request.user
                product.user_id = userid
                product.active = True
                product.slug = form.cleaned_data['name'].replace(" ", "")
                product.date_created = timezone.now()
                product.date_last_modified = timezone.now()
                product.save()
                for form in formset:
                    if form.cleaned_data:
                        image = form.cleaned_data['image']
                    photo = ProductPhoto(product=product, image=image)
                    photo.user_id = userid
                    photo.save()
                return render(request, "updated_product.html", {"product":product})
        else:
            # Set error context
            error_msg = cls_default_msgs['not_signed_in']
            messages.add_message(request, messages.INFO, error_msg, form.errors)
            # Set template
            template = Engine.get_default().get_template('login.html')
            # Set result in RequestContext
            context = RequestContext(request)
            return HttpResponse(template.render(context))

    return render(request, 'products/new_product.html', {'form': form, 'formset': ImageFormSet(queryset=ProductPhoto.objects.none())})

@login_required
def edit_product(request, slug=None):
    product = Product.objects.get(slug=slug)
    ImageFormSet = modelformset_factory(ProductPhoto, form=ImageForm)

    if request.user.is_merchant:
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product)
            formset = ImageFormSet(request.POST, request.FILES, queryset=ProductPhoto.objects.filter(product=product))

            if form.is_valid() and formset.is_valid():
                form.save()
                for form in formset:
                    try:
                        image = form.cleaned_data['image']
                        photo = ProductPhoto(product=product, image=image)
                        photo.user_id = request.user.id
                        photo.save()
                    except:
                        messages.error(request, 'Technical error')
                return render(request, "updated_product.html", locals())
        else:
            form = ProductForm(instance=product)
            formset = ImageFormSet(queryset=ProductPhoto.objects.filter(product=product))
        return render(request, 'product_edit.html', {'form': form, 'formset': formset})
    else:
        messages.add_message(
            request, messages.ERROR,
            'You are not allowed to edit this product. Contact an eventdiary admin'
        )
        return redirect(reverse('product_listing'))
