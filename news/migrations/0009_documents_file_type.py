# Generated by Django 4.0.6 on 2022-08-04 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_remove_downloadlink_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='documents',
            name='file_type',
            field=models.CharField(default=None, max_length=10),
            preserve_default=False,
        ),
    ]