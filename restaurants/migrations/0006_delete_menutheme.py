# Generated by Django 4.2.7 on 2024-12-03 22:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0005_alter_restaurant_address_alter_restaurant_name_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MenuTheme',
        ),
    ]
