# Generated by Django 4.0.6 on 2023-01-14 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0019_alter_pages_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='view_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]