# Generated by Django 4.2.2 on 2023-10-24 06:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0017_alter_user_address_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('description', models.TextField()),
                ('expiry_date', models.DateTimeField(default=None, null=True)),
                ('status', models.BooleanField(default=True)),
                ('restaurant', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='restaurant.restaurants')),
            ],
        ),
    ]
