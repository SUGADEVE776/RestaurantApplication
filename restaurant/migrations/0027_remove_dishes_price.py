# Generated by Django 4.2.2 on 2023-10-25 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0026_dish_quantity_price_checkout'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dishes',
            name='price',
        ),
    ]
