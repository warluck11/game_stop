# Generated by Django 5.0.6 on 2024-07-10 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamestopapp', '0004_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='image',
            field=models.ImageField(default=1, upload_to='reviewimage'),
            preserve_default=False,
        ),
    ]
