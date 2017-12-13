from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from .views import home

urlpatterns = [
    # Examples:
    # url(r'^$', 'bargain.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home, name='home'),
    url(r'^', include('authentication.urls')),
    url(r'^account/', include('accounts.urls')),
    url(r'^products/', include('products.urls')),
    url(r'^merchant/', include('merchant.urls')),
]
