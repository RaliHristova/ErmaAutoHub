from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile
from accounts.roles import assign_user_to_default_group, ensure_role_groups


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        assign_user_to_default_group(instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_migrate)
def create_default_role_groups(sender, **kwargs):
    ensure_role_groups()
