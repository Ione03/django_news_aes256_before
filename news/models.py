import uuid, os
from django.dispatch import receiver
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models
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