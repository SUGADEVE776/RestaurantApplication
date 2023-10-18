# Generated by Django 4.2.2 on 2023-10-13 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_alter_feedback_restaurant_alter_feedback_user_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='bookmarks',
            constraint=models.UniqueConstraint(fields=('user', 'restaurant'), name='unique_bookmarks'),
        ),
    ]
