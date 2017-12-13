import datetime

from django.views.generic import View
from django.template import RequestContext, loader
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from models import Product


class ProductListBaseView(View):
    """
    Base class for other Product listing views.
    It implements a default 'get' method allowing
    subclassing views to render fully functional
    Product listings by simply overriding the default
    class level options.
    Subclassing views can still override and implement
    their own get or post methods. However these methods
    can call the base 'render_product_list' method which
    returns the rendered Product list as a string.
    """

    # default Center list options as class level vars:
    queryset = Product.objects.all()  # can be any queryset of Center instances *
    title = "Products"
    description = ""
    username = ""
    zero_items_message = "Sorry, no products found!"
    num_page_items = 15
    min_orphan_items = 2
    show_page_num = 1
    pagination_base_url = ""

    def render_product_list(self, request, **kwargs):
        """ Takes a queryset of product
        """

        # update the default options with any specified as kwargs:
        for arg_name in kwargs:
            try:
                setattr(self, arg_name, kwargs.get(arg_name))
            except:
                pass

        # set the context and render the template to a string:
        products_list_context = RequestContext(request, {'listing': self.get_queryset(),})
        return products_list_context

    def get_queryset(self):
        """ returns the default products queryset.
            override this method to return custom querysets.
        """
        return self.queryset

    def get(self, request, *args, **kwargs):
        """ returns a full featured products-listing page showing
            the products set in 'products' class variable.
        """
        context = {
            'rendered_product_list': self.render_product_list(request),
        }
        return TemplateResponse(request, 'product.html', context)
