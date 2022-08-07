from django.urls import path, include
from . import views

urlpatterns = [    
    path('', views.index, name='index'),
    path('download-link/<uuid:pk>', views.download_link, name='download_link'),
    path('redirect-link/<slug:slug>', views.redirect_link, name='redirect_link'),
    path('set-inactive-link/<slug:slug>', views.set_inactive_link, name='set_inactive_link'),
    
]