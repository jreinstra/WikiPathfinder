from django.conf.urls import include, url

import views

urlpatterns = [
    url(r'^find/$', views.find, name="find"),
    url(r'^check/$', views.check, name="check"),
]