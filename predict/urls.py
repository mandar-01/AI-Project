from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^show_graph$', views.show_graph, name='index'),
    url(r'^home/$', views.home_page, name='home'),
    url(r'^contrast_caps/$', views.contrast_caps, name='contrast_caps'),
    url(r'^predict_caps/$', views.predict_caps, name='predict_caps'),
    url(r'^contrast/$', views.contrast, name='contrast'),
    url(r'^predict_stock/$', views.stock, name='stock'),
    url(r'^history/$', views.history, name='history'),
]