# Generated by Django 5.1.6 on 2025-03-30 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['name'], name='idx_restaurant_name'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['status'], name='idx_restaurant_status'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['category'], name='idx_restaurant_category'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['category', 'status'], name='idx_restaurant_category_status'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['latitude', 'longitude'], name='idx_restaurant_location'),
        ),
    ]
