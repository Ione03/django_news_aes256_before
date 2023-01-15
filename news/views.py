# import codecs
import datetime

from django.apps import apps
from django.conf import settings
# from django.contrib.contenttypes.models import ContentType
from django.core import signing
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _
from pyaes256 import PyAES256  # Our Library

from .models import *
from .utils import get_ip

# def get_top_foto(model_criteria):    
#     ''' contoh :
#         field_name = berita__id             # field
#         field_value = 'photo__berita__id'   # string

#         model_criteria = (berita__id=OuterRef('photo__berita__id'))
#     '''
#     return Subquery(Photo.objects.filter(**model_criteria) \
#         .order_by('id').values('file_path')[:1])  # slice 1 data return (antisipasi HIGHLIGH1 lebih dari satu)

def get_photo(model_name): # model name in string
    return Subquery(Photo.objects.filter(object_id=OuterRef('id'), content_type__model=model_name) \
        .values('file_path')[:1])

def get_date_time():
    skrg = datetime.datetime.today()
    hari = _(skrg.strftime("%A"))
    tgl = skrg.strftime("%d")
    bln = skrg.strftime("%B")
    tahun = skrg.strftime("%Y")

    tgl = tgl + " " + bln + " " + tahun

    return {        
        "hari": hari,
        "tgl": tgl,
    }

def index(request):
    context = {}

    # print(get_date_time())
    context.update(get_date_time())

    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category
    

    # get top 4 News for home page
    # news = News.objects.order_by('-created_at')[:4]
    # context['news'] = news

    # model_criteria = {'object_id' : OuterRef('id')}
    news = News.objects.annotate(foto=get_photo('news')) \
                .order_by('-created_at')[:4]              
    context['news'] = news
    # print(object_list)

    documents = Documents.objects.order_by('-created_at')[:5]
    context['documents'] = documents

    video = Video.objects.annotate(foto=get_photo('video')) \
        .order_by('-created_at')
    context['video'] = video


    logo = Logo.objects.annotate(foto=get_photo('logo')) \
                .order_by('-created_at')[:1]              
    context['logo'] = logo

    
    about_us = Pages.objects.filter(kind='about us')[:1]       
    print('about_us', about_us)       
    if about_us:        
        context['about_us'] = about_us.get()
    

    social_media = SocialMedia.objects.all().order_by('-created_at')            
    context['social_media'] = social_media

    recent_posts = News.objects.annotate(foto=get_photo('news')) \
                .order_by('-created_at')[:4]              
    context['recent_posts'] = recent_posts

    category_list = Categories.objects.order_by('id')
    context['category_list'] = category_list
 
    return render(request, 'news/index.html', context) 

def detail(request, slug):
    context = {}

    # print(get_date_time())
    context.update(get_date_time())

    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category
    
    news = get_object_or_404(News, slug=slug)    
    context['news'] = news

    # Subquery(Photo.objects.filter(object_id=OuterRef('id'), content_type__model=model_name) \
    #     .values('file_path')[:1])
    foto = Photo.objects.filter(object_id = news.id, content_type__model='news')[:1]
    if foto:
        foto = foto.get()
        context['newsfoto'] = foto        
        print('foto=', foto)

    model_criteria = {'object_id' : OuterRef('id')}
    # news = News.objects.annotate(foto=get_top_foto(model_criteria)) \
    #             .order_by('-created_at')[:4]              
    # context['news'] = news
    # print(object_list)

    # documents = Documents.objects.order_by('-created_at')[:5]
    # context['documents'] = documents

    # Relate POST
    # get 2 news except slug

    related_news = News.objects.exclude(slug=slug) \
        .annotate(foto=get_photo('news')) \
        .order_by('-created_at')[:2]
    # print('rel = ' , related_news)
    context['related_news'] = related_news

    trending_news = News.objects.exclude(slug=slug) \
        .annotate(foto=get_photo('news')) \
        .order_by('view_count')[:3]
    # print('rel = ' , related_news)
    context['trending_news'] = trending_news
    
    category_list = Categories.objects.order_by('id')
    context['category_list'] = category_list

    logo = Logo.objects.annotate(foto=get_photo('logo')) \
                .order_by('-created_at')[:1]              
    context['logo'] = logo
    
    about_us = Pages.objects.filter(kind='about us')[:1]       
    # print('about_us', about_us)       
    if about_us:        
        context['about_us'] = about_us.get()
    
    recent_posts = News.objects.annotate(foto=get_photo('news')) \
                .order_by('-created_at')[:4]              
    context['recent_posts'] = recent_posts

    social_media = SocialMedia.objects.all().order_by('-created_at')            
    context['social_media'] = social_media
 
    return render(request, 'news/detail.html', context) 

def get_content_list(model, kind, slug):
    # print(site_id, lang, model, kind, slug)
    # Proses Slug Dulu
    if not slug:
        raise Http404("Halaman tidak ditemukan!")

    subquery_foto = get_photo(kind)
    # print(slug.lower)
    if slug == 'all':    
        return model.objects.annotate(file_path=subquery_foto) \
                .order_by('-created_at') # ALL data (tambah paginasi di halaman list)
        # if obj:            
        # return obj
        # else:
        #     raise Http404("Halaman tidak ditemukan!")
    else:
        # Get categori ID first
        categories = Categories.objects.filter(slug=slug)
        categories = categories.get() if categories else None

        if categories:
            return model.objects.filter(category_id=categories.id) \
                .annotate(file_path=subquery_foto) \
                .order_by('-created_at') # ALL data (tambah paginasi di halaman list)

        else:
            raise Http404("Categories "+ slug +" tidak ditemukan!")

def list(request, kind, slug):
    context = {}

 
    # print(get_date_time())
    # context.update(get_date_time())

    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category
    
    # news = get_object_or_404(News, slug=slug)    
    # context['news'] = news

    # foto = Photo.objects.filter(object_id = news.id)[:1]
    # if foto:
    #     foto = foto.get()
    #     context['newsfoto'] = foto       

    context['kind'] = kind
    context['slug'] = slug

    model = apps.get_model('news', kind) 
    content_list = get_content_list(model, kind, slug)    

    if content_list:
        kind_data_per_page = 8

        paginator = Paginator(content_list, kind_data_per_page) # Show 25 contacts per page.
        page_number = request.GET.get('page', 1) # default = 1

        # if not page_number:
        #     page_number = 1 # jika tidak ada parameter (default = 1)
                
        # if page_number:
        context['page_list'] = paginator.get_page(page_number)     

    # model_criteria = {'object_id' : OuterRef('id')}
    # news = News.objects.annotate(foto=get_top_foto(model_criteria)) \
    #             .order_by('-created_at')[:4]              
    # context['news'] = news
    # print(object_list)

    # documents = Documents.objects.order_by('-created_at')[:5]
    # context['documents'] = documents

    # Relate POST
    # get 2 news except slug

    related_news = News.objects.exclude(slug=slug) \
        .annotate(foto=get_photo('news')) \
        .order_by('-created_at')[:2]
    # print('rel = ' , related_news)
    context['related_news'] = related_news

    trending_news = News.objects.exclude(slug=slug) \
        .annotate(foto=get_photo('news')) \
        .order_by('view_count')[:3]
    # print('rel = ' , related_news)
    context['trending_news'] = trending_news
    
    category_list = Categories.objects.order_by('id')
    context['category_list'] = category_list

    logo = Logo.objects.annotate(foto=get_photo('logo')) \
                .order_by('-created_at')[:1]              
    context['logo'] = logo
    
    about_us = Pages.objects.filter(kind='about us')[:1]       
    # print('about_us', about_us)       
    if about_us:        
        context['about_us'] = about_us.get()
    
    recent_posts = News.objects.annotate(foto=get_photo('news')) \
                .order_by('-created_at')[:4]              
    context['recent_posts'] = recent_posts

    social_media = SocialMedia.objects.all().order_by('-created_at')            
    context['social_media'] = social_media
 
    return render(request, 'news/list.html', context) 

def about_us(request):
    context = {}

    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category

    model_criteria = {'object_id' : OuterRef('id')}
    logo = Logo.objects.annotate(foto=get_photo('logo')) \
                .order_by('-created_at')[:1]              
    context['logo'] = logo

    social_media = SocialMedia.objects.all().order_by('-created_at')            
    context['social_media'] = social_media
 
    
    about_us = Pages.objects.filter(kind='about us')[:1]       
    # print('about_us', about_us)       
    if about_us:        
        context['about_us'] = about_us.get()
    # get top 3 category for menu 
    # category = Categories.objects.order_by('id')[:3]
    # context['category'] = category

    # get top 4 News for home page
    # news = News.objects.order_by('-created_at')[:4]
    # context['news'] = news

    # model_criteria = {'object_id' : OuterRef('id')}
    # news = News.objects.annotate(foto=get_top_foto(model_criteria)) \
    #             .order_by('-created_at')[:4]              
    # context['news'] = news
    # print(object_list)

    # documents = Documents.objects.order_by('-created_at')[:5]
    # context['documents'] = documents

    category_list = Categories.objects.order_by('id')
    context['category_list'] = category_list


    
    
    recent_posts = News.objects.annotate(foto=get_photo('news')) \
                .order_by('-created_at')[:4]              
    context['recent_posts'] = recent_posts
 
    return render(request, 'news/about_us.html', context) 

def contact_us(request):
    context = {}

    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category


    model_criteria = {'object_id' : OuterRef('id')}
    logo = Logo.objects.annotate(foto=get_photo('logo')) \
                .order_by('-created_at')[:1]              
    context['logo'] = logo

    social_media = SocialMedia.objects.all().order_by('-created_at')            
    context['social_media'] = social_media
 
    
    contact_us = Pages.objects.filter(kind='contact us')[:1]           
    if contact_us:        
        context['contact_us'] = contact_us.get()
    # get top 3 category for menu 
    # category = Categories.objects.order_by('id')[:3]
    # context['category'] = category

    # get top 4 News for home page
    # news = News.objects.order_by('-created_at')[:4]
    # context['news'] = news

    # model_criteria = {'object_id' : OuterRef('id')}
    # news = News.objects.annotate(foto=get_top_foto(model_criteria)) \
    #             .order_by('-created_at')[:4]              
    # context['news'] = news
    # print(object_list)

    # documents = Documents.objects.order_by('-created_at')[:5]
    # context['documents'] = documents

    category_list = Categories.objects.order_by('id')
    context['category_list'] = category_list


    
    
    recent_posts = News.objects.annotate(foto=get_photo('news')) \
                .order_by('-created_at')[:4]              
    context['recent_posts'] = recent_posts

    about_us = Pages.objects.filter(kind='about us')[:1]       
    # print('about_us', about_us)       
    if about_us:        
        context['about_us'] = about_us.get()
 
    return render(request, 'news/contact_us.html', context)     

def send_writing(request):
    context = {}

    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category


    # model_criteria = {'object_id' : OuterRef('id')}
    logo = Logo.objects.annotate(foto=get_photo('logo')) \
                .order_by('-created_at')[:1]              
    context['logo'] = logo

    social_media = SocialMedia.objects.all().order_by('-created_at')            
    context['social_media'] = social_media
 
    send_writing = Pages.objects.filter(kind='send writing')[:1]              
    if send_writing:
        context['send_writing'] = send_writing.get()
    # get top 3 category for menu 
    # category = Categories.objects.order_by('id')[:3]
    # context['category'] = category

    # get top 4 News for home page
    # news = News.objects.order_by('-created_at')[:4]
    # context['news'] = news

    # model_criteria = {'object_id' : OuterRef('id')}
    # news = News.objects.annotate(foto=get_top_foto(model_criteria)) \
    #             .order_by('-created_at')[:4]              
    # context['news'] = news
    # print(object_list)

    # documents = Documents.objects.order_by('-created_at')[:5]
    # context['documents'] = documents
    category_list = Categories.objects.order_by('id')
    context['category_list'] = category_list


    
    
    recent_posts = News.objects.annotate(foto=get_photo('news')) \
                .order_by('-created_at')[:4]              
    context['recent_posts'] = recent_posts


    about_us = Pages.objects.filter(kind='about us')[:1]       
    # print('about_us', about_us)       
    if about_us:        
        context['about_us'] = about_us.get()
 
    return render(request, 'news/send_writing.html', context) 

# def redir_view(request):
#     signer = signing.Signer(salt='safe-redirect')
#     try:
#         url = signer.unsign(request.GET.get('url', ''))
#     except signing.BadSignature:
#         return HttpResponseBadRequest('Invalid parameter')
#     return HttpResponseRedirect(url)


def download_link(request, pk=None):
    context = {}

    logo = Logo.objects.annotate(foto=get_photo('logo')) \
                .order_by('-created_at')[:1]              
    context['logo'] = logo

    social_media = SocialMedia.objects.all().order_by('-created_at')            
    context['social_media'] = social_media

    # get setting expired value in second
    expired_link = getattr(settings, "EXPIRED_LINK", None)
    context['expired_link'] = expired_link
    
    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category

    # get setting SECRET_KEY for password
    secret_key = getattr(settings, "SECRET_KEY", None)
    # media_url = getattr(settings, "MEDIA_URL", None)

    # print('secret_key = ')    
    # print(secret_key)        

    # init variable to store in database
    # session_key = request.session.session_key
    ip = get_ip(request)
    domain = request.get_host()
    context['domain'] = domain
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

    # aes256 = PyAES256()    
    # signature = '23242432423'        
    signer = None
    context['expired'] = None

    doc = Documents.objects.filter(uuid = pk)    
    if doc:
        doc = doc.get()

        obj = DownloadLink.objects.filter(documents_id = doc.id, ip = ip, user_agent = user_agent,
            domain = domain, status=StatusActive.ACTIVE)
        if not obj:
            # data belum ada di database, create enkripsi
            # print('doc filepath = ')
            # print(doc.file_path.url)

            aes256 = PyAES256()
            enc = aes256.encrypt(doc.file_path.url, secret_key)
            # print('result = ')
            # print(enc)
            # simpan signature for decrypt process
            

            # Ubah data dengan type byte menjadi string
            enc['salt'] = bytes.decode(enc['salt'])
            enc['iv'] = bytes.decode(enc['iv'])
            # print('result_after = ')
            # print(enc)

            signature = signing.dumps(enc, key=secret_key, compress=True)
            # a = enc['iv']
            # print(codecs.encode(a,'utf-8'))
            # signing ada key, salt
            # key ambil dari key library
            # salt ambil dari salt library
            # url adalah data yg di signing

            # enc_link = signing.dumps(enc['url'], key=enc['iv'], salt=enc['salt'], compress=True)
            enc_link = enc['url'].replace('=', '-')
            # print('result enc_signing = ')
            # print(enc_link)
            # # enc_link = enc_link.replace(':','+')
            context['enc_link'] = enc_link
            

            # satu file download per session
            obj2 = DownloadLink.objects.filter(documents_id = doc.id, ip = ip, user_agent = user_agent,
                domain = domain, status=StatusActive.NOT_ACTIVE).order_by('-created_at')[:1]
            if obj2:
                obj2 = obj2.get()
                # print(obj2)

                a = obj2.created_at
                b = datetime.datetime.now()
                interval = b-a
                # konversi ke detik
                interval = (interval.days * 24 * 60 * 60) + interval.seconds
                # print('interval = ')
                # print(interval)
                if (interval > (60 * 60 * 24)): # tunggu sampai 1 hari baru download file yg sama aktif kembali
                    

                    # obj = DownloadLink.objects.filter(documents_id = doc.id, ip = ip, user_agent = user_agent,
                    #     domain = domain, status=StatusActive.ACTIVE)
                                        
                    obj = DownloadLink.objects.create(
                        documents_id = doc.id,
                        ip = ip,
                        # session = session_key,
                        user_agent = user_agent,
                        domain = domain,                
                        signature = signature,
                        enc_link = enc_link,
                    
                    )
                    context['id'] = obj.id
                    
                else:
                    context['expired'] = 'expired'  # link is expired
                    context['id'] = obj2.id

            else:
                obj = DownloadLink.objects.create(
                    documents_id = doc.id,
                    ip = ip,
                    # session = session_key,
                    user_agent = user_agent,
                    domain = domain,                
                    signature = signature,
                    enc_link = enc_link,
                
                )
                context['id'] = obj.id

        else:
            # lanjutkan tampilkan count down di interface
            obj = obj.get()
            context['id'] = obj.id
            context['enc_link'] = obj.enc_link

            try:
                signer = signing.loads(obj.signature, key=secret_key, max_age=expired_link)    
                # print('signer = ')
                # print(signer)
            except signing.BadSignature:
                # print('bad dignature')
                context['expired'] = 'expired'  # link is expired
            
            # hitung sisa waktu berjalan untuk di tampilkan di interface
            # print('next ()')
            if signer:
                a = obj.created_at
                b = datetime.datetime.now()
                interval = b-a
                # konversi ke detik
                interval = (interval.days * 24 * 60 * 60) + interval.seconds
                # print('interval = ')
                # print(interval)
                context['expired_link'] = expired_link - interval

    # get top 4 News for home page
    # news = News.objects.order_by('-created_at')[:4]
    # context['news'] = news

    # model_criteria = {'object_id' : OuterRef('id')}
    # news = News.objects.annotate(foto=get_top_foto(model_criteria)) \
    #             .order_by('-created_at')[:4]              
    # context['news'] = news
    # print(object_list)

    # documents = Documents.objects.order_by('-created_at')[:5]
    # context['documents'] = documents
# 
    return render(request, 'news/documents-detail.html', context) 

def redirect_link(request, slug):
    # print(slug)
    context = {}
    context['expired'] = 'expired'
    expired_link = getattr(settings, "EXPIRED_LINK", None)

    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category


    id = request.GET['id']
    # print(id)
    doc = DownloadLink.objects.filter(id=id, enc_link=slug)
    # print(doc)
    if doc:
        # print('enter doc')
        doc = doc.get()
        file_path = doc.documents.file_path.url
        # print(file_path)

        a = doc.created_at
        b = datetime.datetime.now()
        interval = b-a
        interval = (interval.days * 24 * 60 * 60) + interval.seconds
        if (expired_link - interval) >= 0:            
            context['expired'] = None
            context['url'] = file_path
        else:
            # update status jadi false agar tidak masuk kondisi lagi
            # doc.status = StatusActive.NOT_ACTIVE
            # doc.save(self)
            DownloadLink.objects.filter(id=id, enc_link=slug).update(status=StatusActive.NOT_ACTIVE)

    return render(request, 'news/documents-download.html', context) 

def set_inactive_link(request, slug):
    id = request.GET['id']
    DownloadLink.objects.filter(id=id, enc_link=slug).update(status=StatusActive.NOT_ACTIVE)
    return HttpResponse('Done')