import os
import urllib
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import naturalday
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.html import strip_tags
from django.utils.text import Truncator
from humanize import intcomma, naturalsize

from news.models import *

from . import forms

    # Categories, Documents, DownloadLink, News, Photo, StatusActive, Logo

def redirect_to_login(request):  

    if request.user.is_authenticated:
        #logger.error('is_authenticated()')   
        return redirect('/dashboard')
    else:
        #logger.error('NOT is_authenticated()')   
        return redirect('/account/login')    
    #return render(request, "dashboard.html"),


@login_required(login_url='/account/login')
def index(request):
    '''
        to dashboard page
    '''
    context = {}    
        
    context['news'] = News.objects.count()
    context['documents'] = Documents.objects.count()
    context['active_link'] = DownloadLink.objects.filter(status=StatusActive.ACTIVE).count()
    context['inctive_link'] = DownloadLink.objects.filter(status=StatusActive.NOT_ACTIVE).count()

    return render(request, 'dashboard/index.html', context) 


@login_required(login_url='/account/login')
def news(request, mode='', pk=None ):
    context = {
        'mode': mode,
    }

    if mode == 'add':    
        if request.method == "POST":                
            form = forms.NewsForm(request.POST)     
            formset_img = forms.PhotoForm(request.FILES) 

            if form.is_valid():
                obj = News.objects.create (
                    title = request.POST.get('title'),                    
                    content = request.POST.get('content'),                    
                    category_id = request.POST.get('category'),
                    admin_id = request.user.id,                
                    status = request.POST.get('status'),                                        
                )

                photo = Photo.objects.create (
                    file_path = request.FILES.get('file_path'),
                    content_object = obj
                )
            
                return redirect('/dashboard/news') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.NewsForm(label_suffix='') 
            formset_img = forms.PhotoForm(label_suffix='')            
            context['form'] = form
            context['formset_img'] = formset_img
    
    elif mode == 'edit':    
        post = News.objects.filter(uuid=pk).get()
        news_photo = post.photo.all()
        photo = None
        for i in news_photo:
            photo = i   # get top foto
            break
        # print(news_photo)

        if request.method == "POST":                
            form = forms.NewsForm(request.POST, instance=post)     
            formset_img = forms.PhotoForm(request.FILES, instance=photo) 

            if form.is_valid():
                obj = form.save(commit=False)
                obj.admin_id = request.user.id
                obj.save()

                # update photo    
                # print(formset_img)
                if formset_img.is_valid():    
                    print('image valid')            
                    if request.FILES.get('file_path'):
                        photo.file_path = request.FILES.get('file_path')                    
                        photo.save()

                return redirect('/dashboard/news') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.NewsForm(instance=post, label_suffix='') 
            formset_img = forms.PhotoForm(instance=photo, label_suffix='')            
            context['form'] = form
            context['formset_img'] = formset_img
    
    elif mode == 'delete':
        post = News.objects.filter(uuid=pk).get()
        news_photo = post.photo.all().delete()
        post.delete()
        return redirect('/dashboard/news')

    return render(request, 'dashboard/news.html', context) 

# Logo CRUD
# ---------
@login_required(login_url='/account/login')
def logo(request, mode='', pk=None ):
    context = {
        'mode': mode,
    }

    if mode == 'add':    
        if request.method == "POST":                
            form = forms.LogoForm(request.POST)     
            formset_img = forms.PhotoForm(request.FILES) 

            if form.is_valid():
                obj = Logo.objects.create (
                    name = request.POST.get('name'),                                        
                )

                photo = Photo.objects.create (
                    file_path = request.FILES.get('file_path'),
                    content_object = obj
                )
            
                return redirect('/dashboard/logo') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.LogoForm(label_suffix='') 
            formset_img = forms.PhotoForm(label_suffix='')            
            context['form'] = form
            context['formset_img'] = formset_img
    
    elif mode == 'edit':    
        post = Logo.objects.filter(uuid=pk).get()
        logo_photo = post.photo.all()
        photo = None
        for i in logo_photo:
            photo = i   # get top foto
            break
        # print(logo_photo)

        if request.method == "POST":                
            form = forms.LogoForm(request.POST, instance=post)     
            formset_img = forms.PhotoForm(request.FILES, instance=photo) 

            if form.is_valid():
                obj = form.save(commit=False)
                obj.admin_id = request.user.id
                obj.save()

                # update photo    
                # print(formset_img)
                if formset_img.is_valid():    
                    print('image valid')            
                    if request.FILES.get('file_path'):
                        photo.file_path = request.FILES.get('file_path')                    
                        photo.save()

                return redirect('/dashboard/logo') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.LogoForm(instance=post, label_suffix='') 
            formset_img = forms.PhotoForm(instance=photo, label_suffix='')            
            context['form'] = form
            context['formset_img'] = formset_img
    
    elif mode == 'delete':
        post = Logo.objects.filter(uuid=pk).get()
        logo_photo = post.photo.all().delete()
        post.delete()
        return redirect('/dashboard/logo')

    return render(request, 'dashboard/logo.html', context) 


## VIDEO ##
# ---------

def create_unique_name(request):
    '''
        Create name base on date and active site 
    '''    
    tgl = datetime.now()
    return tgl.strftime("%Y%m%d-%H%M%S-%f")  # Tambah domain untuk pengaman (multi user upload gambar di saat bersamaan)

def download_image(request, url):
    '''
        Download image from URL for thumbnail youtube
        media_root / path BUG DI MINIFY
        GANTI MENJADI 
        media_root_path = os.path.join(media_root, path)
    '''
    name = create_unique_name(request)    
    media_root = settings.MEDIA_ROOT
    path = 'youtube/'
    media_root_path = os.path.join(media_root, path)

    res = os.makedirs(media_root_path, exist_ok=True)
    print('create dir = ', res)
    ext = ".jpg"

    path = path + name + ext # ini untuk keperluan return
    
    filename = name + ext
    fullname = os.path.join(media_root_path, filename) # Check on pythonanywhere first
    print('full name = ', fullname)

    # BUG FIX https://github.com/ytdl-org/youtube-dl/issues/23521#top
    # YouTube] "urlopen error Tunnel connection failed: 403 Forbidden" while using proxy ON python anywhere
    # thankyou for : https://stackoverflow.com/questions/32597390/open-url-from-pythonanywhere
    # urllib2 replace to urllib.request in python 3
    urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({'http': 'proxy.server:3128'})))

    # back to business
    urllib.request.urlretrieve(url,fullname)
    return path # for save to database

# ---VIDEOGALLERY------------------------------
def get_video_id(url_video):
    '''
        Get Video ID from Youtube
        https://www.youtube.com/embed/UdTipDMRQ_8
        get UdTipDMRQ_8
    '''
    tmp = url_video.split('/') 
    # print(tmp)
    # print(tmp.length)
    if tmp:
        return tmp[len(tmp)-1]

def download_thumbnail(request, video_id):
    '''
        Donwload thumbnail from youtube
    '''
    # print('begin download image')
    # print(download_image(request, 'https://img.youtube.com/vi/mRKCoRMtn78/mqdefault.jpg'))
    # print('end download image')

    # return and save to database
    download_url = 'https://img.youtube.com/vi/'+ video_id +'/mqdefault.jpg'
    return download_image(request, download_url)

@login_required(login_url='/account/login')
def video(request, mode='', pk=None ):
    context = {
        'mode': mode,
    }

    if mode == 'add':    
        if request.method == "POST":                
            form = forms.VideoForm(request.POST)     
            # formset_img = forms.PhotoForm(request.FILES) 

            if form.is_valid():
                obj = Video.objects.create (
                    title = request.POST.get('title'),                                        
                    embed = request.POST.get('embed'),  
                    admin_id = request.user.id,                                      
                )

                video_id = get_video_id(obj.embed_video)
                file_path = download_thumbnail(request, video_id)
                Photo.objects.create(content_object=obj, file_path=file_path)    
            

                # photo = Photo.objects.create (
                #     file_path = request.FILES.get('file_path'),
                #     content_object = obj
                # )
            
                return redirect('/dashboard/video') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.VideoForm(label_suffix='') 
            # formset_img = forms.PhotoForm(label_suffix='')            
            context['form'] = form
            # context['formset_img'] = formset_img
    
    elif mode == 'edit':    
        post = Video.objects.filter(uuid=pk).get()
        video_photo = post.photo.all()
        photo = None
        for i in video_photo:
            photo = i   # get top foto
            break
        # print(video_photo)

        if request.method == "POST":                
            form = forms.VideoForm(request.POST, instance=post)     
            # formset_img = forms.PhotoForm(request.FILES, instance=photo) 

            if form.is_valid():
                obj = form.save(commit=False)
                obj.admin_id = request.user.id
                obj.save()


                video_id = get_video_id(obj.embed_video)
                file_path = download_thumbnail(request, video_id)

                obj.photo.clear()
                Photo.objects.create(content_object=obj, file_path=file_path)   

                # update photo    
                # print(formset_img)
                # if formset_img.is_valid():    
                #     print('image valid')            
                #     if request.FILES.get('file_path'):
                #         photo.file_path = request.FILES.get('file_path')                    
                #         photo.save()

                return redirect('/dashboard/video') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.VideoForm(instance=post, label_suffix='') 
            formset_img = forms.PhotoForm(instance=photo, label_suffix='')            
            context['form'] = form
            # context['formset_img'] = formset_img
    
    elif mode == 'delete':
        post = Video.objects.filter(uuid=pk).get()
        video_photo = post.photo.all().delete()
        post.delete()
        return redirect('/dashboard/video')

    return render(request, 'dashboard/video.html', context) 


# CRUD PAGES
# ----------

def is_pages_exists(kind):
    '''
        Pages per kind hanya boleh ada 1, selanjutnya tinggal di edit saja
    '''
    return Pages.objects.filter(kind=kind).exists()

@login_required(login_url='/account/login')
def pages(request, mode='', pk=None ):
    context = {
        'mode': mode,
    }

    if mode == 'add':    
        if request.method == "POST":                
            form = forms.PagesForm(request.POST)             

            if form.is_valid():
                if not is_pages_exists(request.POST.get('kind')):
                    obj = Pages.objects.create (
                        title = request.POST.get('title'),                    
                        content = request.POST.get('content'),                                        
                        admin_id = request.user.id,                
                        kind = request.POST.get('kind'),                                               
                    )
                
                    return redirect('/dashboard/pages') # Default (supaya tidak ada erro tidak ada return)                                                         
                else:
                    messages.info(request, '\'' + request.POST.get('kind') + '\' sudah ada, silahkan di edit!') 
                    form = forms.PagesForm(request.POST)       # get previous data      
                    context['form'] = form            
        else:                
            form = forms.PagesForm(label_suffix='')             
            context['form'] = form            
    
    elif mode == 'edit':    
        post = Pages.objects.filter(uuid=pk).get()
        # pages_photo = post.photo.all()
        # photo = None
        # for i in pages_photo:
        #     photo = i   # get top foto
        #     break
        # # print(pages_photo)

        if request.method == "POST":                
            form = forms.PagesForm(request.POST, instance=post)                 

            if form.is_valid():
                obj = form.save(commit=False)
                obj.admin_id = request.user.id
                obj.save()

                # update photo    
                # print(formset_img)
                # if formset_img.is_valid():                        
                #     if request.FILES.get('file_path'):
                #         photo.file_path = request.FILES.get('file_path')                    
                #         photo.save()

                return redirect('/dashboard/pages') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.PagesForm(instance=post, label_suffix='')             
            context['form'] = form            
    
    elif mode == 'delete':
        post = Pages.objects.filter(uuid=pk).get()
        # pages_photo = post.photo.all().delete()
        post.delete()
        return redirect('/dashboard/pages')

    return render(request, 'dashboard/pages.html', context) 

# CRUD SOCIAL MEDIA
# ----------

@login_required(login_url='/account/login')
def socialmedia(request, mode='', pk=None ):
    context = {
        'mode': mode,
    }

    if mode == 'add':    
        if request.method == "POST":                
            form = forms.SocialMediaForm(request.POST)                 

            if form.is_valid():
                obj = SocialMedia.objects.create (
                    kind = request.POST.get('kind'),                    
                    link = request.POST.get('link'),                                        
                    status = request.POST.get('status'),                                        
                )

                # photo = Photo.objects.create (
                #     file_path = request.FILES.get('file_path'),
                #     content_object = obj
                # )
            
                return redirect('/dashboard/socialmedia') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.SocialMediaForm(request.POST or None)             
            context['form'] = form            
    
    elif mode == 'edit':    
        post = SocialMedia.objects.filter(uuid=pk).get()
        # socialmedia_photo = post.photo.all()
        # photo = None
        # for i in socialmedia_photo:
        #     photo = i   # get top foto
        #     break
        # print(socialmedia_photo)

        if request.method == "POST":                
            form = forms.SocialMediaForm(request.POST, instance=post)                 

            if form.is_valid():
                obj = form.save(commit=False)
                # obj.admin_id = request.user.id
                obj.save()

                # update photo    
                # print(formset_img)
                # if formset_img.is_valid():    
                #     print('image valid')            
                #     if request.FILES.get('file_path'):
                #         photo.file_path = request.FILES.get('file_path')                    
                #         photo.save()

                return redirect('/dashboard/socialmedia') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.SocialMediaForm(instance=post, label_suffix='') 
            # formset_img = forms.PhotoForm(instance=photo, label_suffix='')            
            context['form'] = form
            # context['formset_img'] = formset_img
    
    elif mode == 'delete':
        post = SocialMedia.objects.filter(uuid=pk).get()
        # socialmedia_photo = post.photo.all().delete()
        post.delete()
        return redirect('/dashboard/socialmedia')

    return render(request, 'dashboard/socialmedia.html', context) 

@login_required(login_url='/account/login')
def categories(request, mode='', pk=None ):
    context = {
        'mode': mode,
    }

    if mode == 'add':    
        if request.method == "POST":                
            form = forms.CategoriesForm(request.POST)     

            if form.is_valid():
                obj = Categories.objects.create (
                    name = request.POST.get('name'),                                        
                )                
            
                return redirect('/dashboard/categories') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.CategoriesForm(label_suffix='')             
            context['form'] = form
    
    elif mode == 'edit':    
        post = Categories.objects.filter(uuid=pk).get()

        if request.method == "POST":                
            form = forms.CategoriesForm(request.POST, instance=post)                

            if form.is_valid():
                form.save()

                return redirect('/dashboard/categories') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.CategoriesForm(instance=post, label_suffix='')             
            context['form'] = form            
    
    elif mode == 'delete':
        post = Categories.objects.filter(uuid=pk).delete()                
        return redirect('/dashboard/categories')

    return render(request, 'dashboard/categories.html', context) 

@login_required(login_url='/account/login')
def documents(request, mode='', pk=None ):
    context = {
        'mode': mode,
    }

    if mode == 'add':    
        if request.method == "POST":                
            form = forms.DocumentsForm(request.POST, request.FILES)                 

            if form.is_valid():
                obj = Documents.objects.create (
                    file_path = request.FILES.get('file_path'),                                        
                    name = request.POST.get('name'),                                        
                    status = request.POST.get('status'),                                        
                )

                # obj.size = os.stat(obj.file_path.path).st_size
                # obj.save()
            
                return redirect('/dashboard/documents') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.DocumentsForm(label_suffix='') 
            context['form'] = form            
    
    elif mode == 'edit':    
        post = Documents.objects.filter(uuid=pk).get()        

        if request.method == "POST":                
            form = forms.DocumentsForm(request.POST, request.FILES, instance=post)     
            
            if form.is_valid():
                obj = form.save()
                # obj.size = os.stat(obj.file_path.path).st_size
                # obj.save()

                # update photo    
                # print(formset_img)
                # if formset_img.is_valid():    
                #     print('image valid')            
                #     if request.FILES.get('file_path'):
                #         photo.file_path = request.FILES.get('file_path')                    
                #         photo.save()

                return redirect('/dashboard/documents') # Default (supaya tidak ada erro tidak ada return)                                         
        else:                
            form = forms.DocumentsForm(instance=post, label_suffix='')             
            context['form'] = form            
    
    elif mode == 'delete':
        post = Documents.objects.filter(uuid=pk).delete()        
        return redirect('/dashboard/documents')

    return render(request, 'dashboard/documents.html', context) 

@login_required(login_url='/account/login')
def download_link(request, mode='', pk=None ):
    context = {
        'mode': mode,
    }

    return render(request, 'dashboard/download_link.html', context)     

def news_ajax(request):    
    obj_list = News.objects.values('uuid', 'title', 'content', 'category__name', 
        'admin__username', 'status', 'updated_at') \
        .order_by('-updated_at')
    
    for i in obj_list:
        i['content'] = Truncator(strip_tags(i['content'])).words(10)
        i['updated_at'] = naturalday(i['updated_at'])

    mData = list(obj_list)               
    return JsonResponse(mData, safe=False)    

def logo_ajax(request):    
    obj_list = Logo.objects.values('uuid', 'name', 'updated_at') \
        .order_by('-updated_at')
    
    for i in obj_list:
        i['name'] = i['name']
        i['updated_at'] = naturalday(i['updated_at'])

    mData = list(obj_list)               
    return JsonResponse(mData, safe=False)    

def video_ajax(request):    
    obj_list = Video.objects.values('uuid', 'title', 'updated_at') \
        .order_by('-updated_at')
    
    for i in obj_list:
        i['title'] = i['title']
        i['updated_at'] = naturalday(i['updated_at'])

    mData = list(obj_list)               
    return JsonResponse(mData, safe=False)    

def categories_ajax(request):    
    obj_list = Categories.objects.values('uuid', 'name', 'updated_at') \
        .order_by('-updated_at')
    
    for i in obj_list:        
        i['updated_at'] = naturalday(i['updated_at'])

    mData = list(obj_list)               
    return JsonResponse(mData, safe=False)    

def documents_ajax(request):    
    obj_list = Documents.objects.values('uuid', 'name', 'size', 'count', 'status', 'updated_at') \
        .order_by('-updated_at')
    
    for i in obj_list:        
        i['updated_at'] = naturalday(i['updated_at'])
        i['size'] = naturalsize(i['size'])
        i['count'] = intcomma(i['count'])

    mData = list(obj_list)               
    return JsonResponse(mData, safe=False)    

def download_link_ajax(request):    
    obj_list = DownloadLink.objects.values('uuid', 'documents__name', 'signature', 'enc_link', 'status', 'updated_at') \
        .order_by('-updated_at')
    
    for i in obj_list:        
        i['updated_at'] = naturalday(i['updated_at'])
        i['enc_link'] = Truncator(i['enc_link']).chars(30)
    

    mData = list(obj_list)               
    return JsonResponse(mData, safe=False)    

def pages_ajax(request):    
    obj_list = Pages.objects.values('uuid', 'kind', 'title', 'content', 'updated_at') \
        .order_by('-updated_at')
    
    for i in obj_list:
        i['content'] = Truncator(strip_tags(i['content'])).words(10)
        i['updated_at'] = naturalday(i['updated_at'])

    mData = list(obj_list)               
    return JsonResponse(mData, safe=False)    

def socialmedia_ajax(request):    
    #  .values('uuid', 'kind', 'link', 'updated_at') \
    obj_list = SocialMedia.objects.all() \
        .order_by('-updated_at')
    
    lst = []
    for i in obj_list:        
        res = {}
        res['uuid'] = i.uuid
        res['kind'] = i.get_kind_display()
        res['link'] = i.link        
        res['updated_at'] = naturalday(i.updated_at)
        lst.append(res)

    # mData = list(obj_list)               
    return JsonResponse(lst, safe=False)    

