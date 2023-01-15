# from django import forms
# from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from news.models import *


class PhotoForm(ModelForm):
    # str_file_path = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})
    class Meta:
        model = Photo
        fields = ('file_path',)
        exclude = ('content_type', 'object_id', 'content_object', 'created_at', 'updated_at')


class LogoForm(ModelForm):
    # str_file_path = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(LogoForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})
    class Meta:
        model = Logo
        fields = ('name',)
        exclude = ('created_at', 'updated_at')


class VideoForm(ModelForm):
    # str_file_path = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})
    class Meta:
        model = Video
        fields = ('title', 'embed',)
        exclude = ('created_at', 'updated_at')


class NewsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})

    class Meta:
        model = News
        fields = '__all__'
        exclude = ('slug', 'admin', 'created_at', 'updated_at')


class CategoriesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoriesForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})

    class Meta:
        model = Categories
        fields = '__all__'
        exclude = ('slug', 'created_at', 'updated_at')


class DocumentsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})

    class Meta:
        model = Documents
        fields = '__all__'
        exclude = ('size', 'count', 'created_at', 'updated_at')        


class PagesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PagesForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})

    class Meta:
        model = Pages
        fields = '__all__'
        exclude = ('slug', 'admin', 'created_at', 'updated_at')


class SocialMediaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SocialMediaForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})

    class Meta:
        model = SocialMedia
        fields = '__all__'
        exclude = ('slug', 'created_at', 'updated_at')
