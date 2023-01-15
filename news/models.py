import os
import uuid

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify


class BaseModel(models.Model):
    # All model using di base model
    id = models.BigAutoField(primary_key=True, editable=False)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        app_label = 'news'
        abstract = True
        ordering = ['-created_at']        

class Photo(BaseModel):            
    # Image File Path
    file_path = models.ImageField()    

    # Generic relation from other model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True)    
    object_id = models.PositiveIntegerField(blank=True)
    content_object = GenericForeignKey('content_type','object_id')

    def __str__(self):
        return self.file_path.url

class Logo(BaseModel):    
    name = models.CharField(max_length=100)
    photo = GenericRelation(Photo)    

    def __str__(self):
        return self.name       

class Categories(BaseModel):
    # News categories    
    name = models.CharField(max_length=50)   
    slug = models.SlugField(max_length=50, default='', unique=True, blank=True, editable=False)         

    def __str__(self):
        return self.name

    # untuk slug
    def save(self, *args, **kwargs):                
        self.slug = slugify(self.name)
        super(Categories, self).save(*args, **kwargs)

class StatusPublish(models.TextChoices):
    DRAFT = 'draft'
    PUBLISHED = 'published'

class StatusActive(models.TextChoices):
    NOT_ACTIVE = 'not active'
    ACTIVE = 'active'

class News(BaseModel):
    # judul berita
    title = models.CharField(max_length=500)    
    view_count = models.PositiveIntegerField(default=0, editable=False)         # jumlah views / read    
    
    # slug dari judul berita
    # mariaDB cannot create unique ID more than 255 char
    slug = models.SlugField(max_length=255, default='', unique=True, blank=True, editable=False)

    # gunakan ckeditor blank=True, null=True
    content = RichTextUploadingField()    

    # foreign key
    category = models.ForeignKey(Categories, on_delete=models.PROTECT)    
    admin = models.ForeignKey(User, on_delete=models.PROTECT, blank=True)
    photo = GenericRelation(Photo, related_query_name='news')  # relasi many2many
        
    # publish or draft
    status = models.CharField(max_length=20, choices=StatusPublish.choices, default=StatusPublish.PUBLISHED)    

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/%s/%s' % ( 'news', self.slug)         

    # untuk slug
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)        
        super(News, self).save(*args, **kwargs)

class Documents(BaseModel):
    file_path = models.FileField()    
    name = models.CharField(max_length=150)        
    size = models.BigIntegerField(null=True, blank=True, default=0, editable=False)                
    file_type = models.CharField(max_length=10, null=True, blank=True, default='', editable=False)               
    count = models.PositiveIntegerField(null=True, blank=True, default=0, editable=False)      
    status = models.CharField(max_length=20, choices=StatusPublish.choices, default=StatusPublish.PUBLISHED)      

    def __str__(self):
        return self.name

class DownloadLink(BaseModel):
    '''
        Data ini di generate saat ada permintaan download link
    '''
    documents = models.ForeignKey(Documents, on_delete=models.PROTECT)        
    # alamat lengkap
    # berisi url lengkap, sign key=key, salt=salt, max_age=3600) pwd = setting.secret_key 
    signature = models.TextField(null=True, blank=True)       # complete url after decoding

    # encrypt link
    enc_link = models.TextField(null=True, blank=True)       # complete url after decoding
    
    # aktif atau tidak
    status = models.CharField(max_length=20, choices=StatusActive.choices, default=StatusActive.ACTIVE)

    # url = models.URLField(max_length=500)       # complete url after decoding
    # expired = models.DateTimeField()          # already include in second
    # salt = models.CharField(max_length=200)   # simpan di signing
    # iv = models.CharField(max_length=200)     # simpan di signing as key
    # password 256bit = 32byte char
    # pwd = models.CharField(max_length=200)    # simpan di SETTINGS.SECRET_KEY

    # untuk mendeteksi user yg sama click download link yg sama
    ip = models.CharField(max_length=40, editable=False, db_index=True)
    # session = models.CharField(max_length=40, editable=False, db_index=True)
    # session berhubungan dengan login user, tidak digunakan di interface
    user_agent = models.CharField(max_length=255, editable=False)
    domain = models.CharField(max_length=255, editable=False, default='')

def save_embed_video(embed):
    '''
        Change from embed code to URL 
    '''
    jml = 0
    res = ''
    arr1 = embed.split(' ')
    found = False
    for i in arr1:
        if found:
            break
        arr2 = i.split('=')
        found = False
        for j in arr2:
            if (not found) and (j.lower()=='src'):
                found = True

            if found and (j.lower()!='src'):                
                if jml==0:
                    res += j     
                    jml += 1
                else:
                    res += '=' + j
                
                # print(res)               
                # self.embed_video = j.replace("\"","")
                # self.embed_video = self.embed_video.replace("&quot;","")                    
                #break
        
    if res.find('watch') <= 0:
        res = res.replace("\"","")
        res = res.replace("&quot;","")  
        
        # https://www.youtube.com/watch?v=AD8MaRZdOsY&amp;t=9s 
        # invalid embed
        return res       
    else:
        return None    

class Video(BaseModel):
    
    admin = models.ForeignKey(User, on_delete=models.PROTECT)    
    view_count = models.PositiveIntegerField(default=0, editable=False)         # jumlah views / read    
    
    title = models.CharField(max_length=500)
    embed = RichTextUploadingField(blank=True, null=True, config_name='embed_video') # , config_name='embed_video')        
    
    # ISI otomatis dari function save di bawah ini
    # field ini berguna untuk django-embed-video
    # ganti embed video supaya tidak perlu klik source dulu, bisa langsung paste dari embed youtube
    # embed_video = EmbedVideoField(blank=True, null=True)  # same like models.URLField()
    embed_video = models.URLField(blank=True, null=True)  # same like models.URLField()
    status = models.CharField(max_length=20, choices=StatusPublish.choices, default=StatusPublish.PUBLISHED)      

    # for save embed youtube
    photo = GenericRelation(Photo)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):                
        self.embed_video = save_embed_video(self.embed)

        # Download youtube thumbnail (PROHIBIT to UNSAVE content_objects) -- >> Move to views
        # video_id = get_video_id(self.embed_video)
        # file_path = download_thumbnail(exposed_request, video_id)
        # Photo.objects.create(content_object=self, file_path=file_path)    

        super(Video, self).save(*args, **kwargs)   

class PagesKind(models.TextChoices):
    ABOUT_US = 'about us'
    SEND_WRITING = 'send writing'
    CONTACT_US = 'contact us'

class Pages(BaseModel):        
    admin = models.ForeignKey(User, on_delete=models.PROTECT) # translatenya sama aja=admin juga

    view_count = models.PositiveIntegerField(default=0, editable=False)         # jumlah views / read
    share_count = models.PositiveIntegerField(default=0, editable=False)
    
    slug = models.SlugField(max_length=255, default='', unique=True, blank=True, editable=False)
    
    # site = models.ForeignKey(Site, on_delete=models.CASCADE)
    # admin = models.ForeignKey(User, on_delete=models.PROTECT)
    
    title = models.CharField(max_length=500)
    # slug = models.SlugField(max_length=255, default='', unique=True, blank=True),    
    # photo = GenericRelation(Photo)
    kind = models.CharField(max_length=20, choices=PagesKind.choices)    
    content = RichTextUploadingField(blank=True, null=True)

    def __str__(self):
        return self.title  

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)                        
        super(Pages, self).save(*args, **kwargs)    

class OptSocialMediaKinds(models.IntegerChoices):
    '''        
        Ubah jadi small Integer agar lebih hemat space database
    '''    
    FACEBOOK = 1, 'Facebook'
    TWITTER = 2, 'Twitter'
    PINTEREST = 3, 'Pinterest'
    YOUTUBE = 4, 'Youtube'
    INSTAGRAM = 5, 'Instagram'

class SocialMedia(BaseModel):    
    kind = models.SmallIntegerField(choices=OptSocialMediaKinds.choices)
    link =  models.URLField(max_length=255)
    # status = models.SmallIntegerField(choices=OptStatusPublish.choices, default=OptStatusPublish.PUBLISHED)
    status = models.CharField(max_length=20, choices=StatusPublish.choices, default=StatusPublish.PUBLISHED)    

    def __str__(self):
        #return {"%s %s"} % (self.jenis, self.site.name)
        return "{}".format(self.kind)

    # def save(self, *args, **kwargs):                
    #     super(SocialMedia, self).save(*args, **kwargs)  

# trigger         

@receiver(models.signals.post_delete, sender=Photo)
@receiver(models.signals.post_delete, sender=Documents)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    try:
        if instance.file_path:
            if os.path.isfile(instance.file_path.path):
                os.remove(instance.file_path.path)
    finally:
        # do nothing
        return True

@receiver(models.signals.pre_save, sender=Photo)
@receiver(models.signals.pre_save, sender=Documents)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    print('delete old photo')
    print(instance.pk)
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file_path
        print(old_file)
    except sender.DoesNotExist:
        return False

    # kemungkinan ada file latihan yg error, pastikan tidak menimbulkan 
    # server error dengan try finally
    try:
        new_file = instance.file_path
        print(new_file)
        if not old_file == new_file:
            if old_file:
                if os.path.isfile(old_file.path):
                    print('remove old file')
                    # img = Image.open(old_file.path)
                    # if img: img.close() # pastikan image sudah di close (antisipasi error file is open by another process)
                    os.remove(old_file.path)
        #post_delete.connect(file_cleanup, sender=photo, dispatch_uid="photo.file_cleanup")        
    finally:
        return True # jika ada error, dianggap file telah berhasil di hapus


@receiver(models.signals.post_save, sender=Documents)
def auto_update_file_size(sender, instance, *args, **kwargs):
    print('update size')
    # sender.update(size = os.stat(instance.file_path.path).st_size)
    # print(instance.id)
    # print(sender)
    # print(os.stat(instance.file_path.path).st_size)

    Documents.objects.filter(pk=instance.id) \
        .update(size=os.stat(instance.file_path.path).st_size \
        ,file_type=os.path.splitext(instance.file_path.path)[1])
    return True