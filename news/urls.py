from django.urls import path
from . import views

urlpatterns = [    
    path('', views.index, name='index'),
    path('detail/<slug:slug>/', views.detail, name='detail'),
    path('<str:kind>/list/<slug:slug>/', views.list, name='list'),

    path('tentang-kami/', views.about_us, name='about_us'),
    path('hubungi-kami/', views.contact_us, name='contact_us'),
    path('kirim-tulisan/', views.send_writing, name='send_writing'),

    #path('download-link/<uuid:pk>', views.download_link, name='download_link'),
    #path('redirect-link/<slug:slug>', views.redirect_link, name='redirect_link'),
    #path('set-inactive-link/<slug:slug>', views.set_inactive_link, name='set_inactive_link'),
    
]
