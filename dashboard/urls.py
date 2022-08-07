from django.urls import path, include
from . import views

urlpatterns = [    
    path('', views.index, name='index'),

    path('news/', views.news, name='news'),
    path('news/<str:mode>/', views.news, name='news'),          # mode add
    path('news/<str:mode>/<uuid:pk>', views.news, name='news'),  # mode edit, delete
    path('news_ajax/', views.news_ajax, name='news_ajax'),

    path('categories/', views.categories, name='categories'),
    path('categories/<str:mode>/', views.categories, name='categories'),          # mode add
    path('categories/<str:mode>/<uuid:pk>', views.categories, name='categories'),  # mode edit, delete
    path('categories_ajax/', views.categories_ajax, name='categories_ajax'),

    path('documents/', views.documents, name='documents'),
    path('documents/<str:mode>/', views.documents, name='documents'),          # mode add
    path('documents/<str:mode>/<uuid:pk>', views.documents, name='documents'),  # mode edit, delete
    path('documents_ajax/', views.documents_ajax, name='documents_ajax'),

    path('download-link/', views.download_link, name='download_link'),   
    path('download_link_ajax/', views.download_link_ajax, name='download_link_ajax'), 
]