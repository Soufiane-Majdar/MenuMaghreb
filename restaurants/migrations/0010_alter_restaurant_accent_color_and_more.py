# Generated by Django 4.2.7 on 2024-12-04 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0009_restaurant_email_alter_menuitem_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='accent_color',
            field=models.CharField(default='#10B981', help_text='Used for highlights and call-to-action elements', max_length=7),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='background_color',
            field=models.CharField(default='#F3F4F6', help_text='Background color of the menu', max_length=7),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='font_family',
            field=models.CharField(choices=[('Poppins', 'Poppins'), ('Montserrat', 'Montserrat'), ('Open Sans', 'Open Sans'), ('Roboto', 'Roboto'), ('Lato', 'Lato')], default='Poppins', help_text='Main font family for the menu', max_length=50),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='menu_style',
            field=models.CharField(choices=[('modern', 'Modern Grid'), ('elegant', 'Elegant Cards'), ('classic', 'Classic List'), ('minimal', 'Minimal')], default='modern', help_text='Overall layout style of the menu', max_length=20),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='primary_color',
            field=models.CharField(default='#2563EB', help_text='Main brand color, used for headers and primary buttons', max_length=7),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='secondary_color',
            field=models.CharField(default='#4B5563', help_text='Secondary color for accents and secondary buttons', max_length=7),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='text_color',
            field=models.CharField(default='#1F2937', help_text='Main text color', max_length=7),
        ),
    ]
