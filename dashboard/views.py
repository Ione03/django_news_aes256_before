import os

from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import naturalday
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.html import strip_tags
from django.utils.text import Truncator
from humanize import intcomma, naturalsize
from news.models import Categories, Documents, DownloadLink, News, Photo, StatusActive

from . import forms


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
