from django.db.models.signals import post_save
from .models import Token,Users,Profile
from django.dispatch import receiver
from core.utils.internet_connection import internetConnection
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .utils.kirim_email import kirim_email_activate
from .token import account_activation_token
from django.core.cache import cache

def generatorTokenSignal(sender,instance, created,**kwargs):
    if created:
        conn = internetConnection()
        if conn:
            try:
                token_obj = Token.objects.get(pk=instance.id)
            except Token.DoesNotExist:
                token_obj = None
            if token_obj is not None:
                try:
                    user_obj = Users.objects.get(pk=token_obj.user.pk)
                except Users.DoesNotExist:
                    user_obj = None       
                    
                if user_obj is not None:
                    uid = urlsafe_base64_encode(force_bytes(user_obj.pk))
                    token = account_activation_token.make_token(user_obj)
                    token_obj.token = token
                    token_obj.save()
                    # user activation
                    kirim_email_activate(
                        uid=uid, token=token, user_obj=user_obj)            


@receiver(post_save, sender=Users)
def userCreatedSignal(sender, instance, created, **kwargs):
    if not created:
        post_save.disconnect(userCreatedSignal, sender=Users)
        profile_obj = Profile.objects.get(user=instance)
        profile_obj.nama_lengkap = instance.full_name
        profile_obj.save()
        post_save.connect(userCreatedSignal, sender=Users)
    else:
        Profile.objects.create(
            user=instance,
            nama_lengkap=instance.full_name,
        )
        cache_key = f'foto_profile_{instance.pk}'
        cache.delete(cache_key)

@receiver(post_save, sender=Profile)
def profileSignal(sender, instance, created, **kwargs):
    if not created:
        post_save.disconnect(profileSignal, sender=Profile)
        user = Users.objects.get(pk=instance.user.pk)
        user.full_name = instance.nama_lengkap
        user.save()
        post_save.connect(profileSignal, sender=Profile)

