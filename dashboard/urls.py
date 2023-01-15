from django.urls import path
from . import views

urlpatterns = [    
    path('', views.index, name='index'),

    path('news/', views.news, name='news'),
    path('news/<str:mode>/', views.news, name='news'),          # mode add
    path('news/<str:mode>/<uuid:pk>', views.news, name='news'),  # mode edit, delete
    path('news_ajax/', views.news_ajax, name='news_ajax'),

    path('logo/', views.logo, name='logo'),
    path('logo/<str:mode>/', views.logo, name='logo'),          # mode add
    path('logo/<str:mode>/<uuid:pk>', views.logo, name='logo'),  # mode edit, delete
    path('logo_ajax/', views.logo_ajax, name='logo_ajax'),

    path('video/', views.video, name='video'),
    path('video/<str:mode>/', views.video, name='video'),          # mode add
    path('video/<str:mode>/<uuid:pk>', views.video, name='video'),  # mode edit, delete
    path('video_ajax/', views.video_ajax, name='video_ajax'),

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

    path('pages/', views.pages, name='pages'),
    path('pages/<str:mode>/', views.pages, name='pages'),          # mode add
    path('pages/<str:mode>/<uuid:pk>', views.pages, name='pages'),  # mode edit, delete
    path('pages_ajax/', views.pages_ajax, name='pages_ajax'),

    path('socialmedia/', views.socialmedia, name='socialmedia'),
    path('socialmedia/<str:mode>/', views.socialmedia, name='socialmedia'),          # mode add
    path('socialmedia/<str:mode>/<uuid:pk>', views.socialmedia, name='socialmedia'),  # mode edit, delete
    path('socialmedia_ajax/', views.socialmedia_ajax, name='socialmedia_ajax'),
]