import codecs
import datetime

from django.conf import settings
from django.core import signing
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import render
# from pyaes256 import PyAES256  # Our Library

from .models import *
from .utils import get_ip


def get_top_foto(model_criteria):    
    ''' contoh :
        field_name = berita__id             # field
        field_value = 'photo__berita__id'   # string

        model_criteria = (berita__id=OuterRef('photo__berita__id'))
    '''
    return Subquery(Photo.objects.filter(**model_criteria) \
        .order_by('id').values('file_path')[:1])  # slice 1 data return (antisipasi HIGHLIGH1 lebih dari satu)

def index(request):
    context = {}

    # get top 3 category for menu 
    category = Categories.objects.order_by('id')[:3]
    context['category'] = category

    # get top 4 News for home page
    # news = News.objects.order_by('-created_at')[:4]
    # context['news'] = news

    model_criteria = {'object_id' : OuterRef('id')}
    news = News.objects.annotate(foto=get_top_foto(model_criteria)) \
                .order_by('-created_at')[:4]              
    context['news'] = news
    # print(object_list)

    documents = Documents.objects.order_by('-created_at')[:5]
    context['documents'] = documents
 
    return render(request, 'news/index.html', context) 


# def redir_view(request):
#     signer = signing.Signer(salt='safe-redirect')
#     try:
#         url = signer.unsign(request.GET.get('url', ''))
#     except signing.BadSignature:
#         return HttpResponseBadRequest('Invalid parameter')
#     return HttpResponseRedirect(url)


def download_link(request, pk=None):
    context = {}

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

            # aes256 = PyAES256()
            # enc = aes256.encrypt(doc.file_path.url, secret_key)
            # print('result = ')
            # print(enc)
            # simpan signature for decrypt process
            

            # Ubah data dengan type byte menjadi string
            # enc['salt'] = bytes.decode(enc['salt'])
            # enc['iv'] = bytes.decode(enc['iv'])
            # print('result_after = ')
            # print(enc)

            # signature = signing.dumps(enc, key=secret_key, compress=True)
            # a = enc['iv']
            # print(codecs.encode(a,'utf-8'))
            # signing ada key, salt
            # key ambil dari key library
            # salt ambil dari salt library
            # url adalah data yg di signing

            # enc_link = signing.dumps(enc['url'], key=enc['iv'], salt=enc['salt'], compress=True)
            # enc_link = enc['url'].replace('=', '-')
            # print('result enc_signing = ')
            # print(enc_link)
            # # enc_link = enc_link.replace(':','+')
            # context['enc_link'] = enc_link
            

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
            # context['enc_link'] = obj.enc_link

            # try:
            #     signer = signing.loads(obj.signature, key=secret_key, max_age=expired_link)    
            #     # print('signer = ')
            #     # print(signer)
            # except signing.BadSignature:
            #     # print('bad dignature')
            #     context['expired'] = 'expired'  # link is expired
            
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