from django.conf.urls import url
from merchant.views import ManageProductView, offering_list_view, edit_merchant_product, offering_action


urlpatterns = [
    url(r'^(?P<username>\w+)/products/$', ManageProductView.as_view(), name='merchant_manage_products'),
    url(r'^(?P<username>\w+)/offerings/$', offering_list_view, name='offering_list'),
    url(r'^(?P<username>\w+)/offerings/approved/$', offering_action, name='offering_status'),
    url(r'^(?P<username>\w+)/(?P<product_slug>\w+)/$', edit_merchant_product, name='merchant_manage_indv_products'),
]
