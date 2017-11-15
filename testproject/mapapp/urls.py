
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.form_test), 
    url(r'^search-results/',views.test), 
    url(r'^comparison/',views.comparison)
]
