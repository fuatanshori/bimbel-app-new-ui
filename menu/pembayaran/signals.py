from django.db.models.signals import post_save,post_delete,pre_save
from .models import Tarif
from django.dispatch import receiver

@receiver(post_save,sender=Tarif)
def add_is_used_tarif(sender, instance, created, **kwargs):
    if instance.is_used:
        Tarif.objects.filter(is_used=True).exclude(
            pk=instance.pk).update(is_used=False)
    else:
        Tarif.objects.filter(is_used=False).exclude(pk=instance.pk).update(is_used=True)

    tarif_obj = Tarif.objects.all()
    is_used_list = []
    for tarif in tarif_obj:
        is_used_list.append(tarif.is_used)
        
    if all(not item for item in is_used_list):
        obj = Tarif.objects.get(pk=instance.pk)
        obj.is_used = True
        obj.save()

@receiver(post_delete, sender=Tarif)
def deleted_is_used_tarif(sender, instance, *args, **kwargs):
    if instance.is_used:
        obj = Tarif.objects.all().first()
        obj.is_used = True
        obj.save()
