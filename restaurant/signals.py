from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *  # Import your Wallet model


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
        Cart.objects.create(user=instance)
