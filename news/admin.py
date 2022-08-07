from django.contrib import admin

from .models import *


class CategoriesAdmin(admin.ModelAdmin):    
    list_filter = ('name',)
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ('name',)
    ordering = ('-id',)

class NewsAdmin(admin.ModelAdmin):    
    list_filter = ('title',)
    list_display = ['title', 'category', 'created_at', 'updated_at']
    search_fields = ('title',)
    ordering = ('-id',)

class PhotoAdmin(admin.ModelAdmin):    
    # list_filter = ('title',)
    # list_display = ['title', 'category', 'created_at', 'updated_at']
    # search_fields = ('title',)
    ordering = ('-id',)


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Photo, PhotoAdmin)