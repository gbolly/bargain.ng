from django.conf.urls import url

from products import views

urlpatterns = [
    url(r'^$', views.ProductListView.as_view(), name='product_listing'),
    url(r'^new/$', views.new_product, name='new_product'),
    url(r'^edit-product/(?P<slug>[\w\-]+)/$', views.edit_product, name='edit-product'),
    url(r'^(?P<slug>[\w\-]+)/$', views.product_detail, name='product_detail'),
    url(r'^(?P<slug>[\w\-]+)/offering/$', views.offering_view, name='offering_create'),
    url(r'^(?P<slug>[\w\-]+)/offering/(?P<id_params>\d+)/$', views.offering_view, name='offering_create'),
    url(r'^(?P<slug>[\w\-]+)/new-offer/$', views.counter_offer_view, name='counter_offer'),
    url(r'^(?P<slug>[\w\-]+)/new-offer/(?P<id_params>\d+)/$', views.counter_offer_view, name='counter_offer'),
    url(r'^offers/(?P<slug>[\w\-]+)/$', views.offerings_by_user, name='user_offers'),
]
