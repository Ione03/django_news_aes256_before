# Generated by Django 4.0.6 on 2023-01-11 06:03

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0015_videogallery'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VideoGallery',
            new_name='Video',
        ),
    ]
