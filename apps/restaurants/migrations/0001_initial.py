# Generated by Django 5.1.6 on 2025-03-29 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('address', models.TextField(verbose_name='Address')),
                ('rating', models.DecimalField(decimal_places=1, help_text='Rating from 0.0 to 5.0', max_digits=2, verbose_name='Rating')),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('maintenance', 'Under Maintenance')], default='open', max_length=20, verbose_name='Status')),
                ('category', models.CharField(max_length=100, verbose_name='Category')),
                ('latitude', models.DecimalField(decimal_places=11, max_digits=14, verbose_name='Latitude')),
                ('longitude', models.DecimalField(decimal_places=11, max_digits=14, verbose_name='Longitude')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Restaurant',
                'verbose_name_plural': 'Restaurants',
                'db_table': 'RESTAURANTS',
                'ordering': ['-created_at'],
                'constraints': [models.CheckConstraint(condition=models.Q(('rating__gte', 0), ('rating__lte', 5)), name='rating_range')],
            },
        ),
    ]
