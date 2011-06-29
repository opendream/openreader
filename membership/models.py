from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from common.models import Loggable


MEMBERSHIP_TYPES = (
    ('1', 'Reader'),
    ('2', 'Publisher')
)


class Profile(Loggable):
    user = models.ForeignKey(User)
    membership_type = models.IntegerField(choices=MEMBERSHIP_TYPES, db_index=True)

    TYPE_NONE = '0'
    TYPE_READER = '1'
    TYPE_PUBLISHER = '2'


@receiver(post_save)
def create_profile(sender, **kwargs):
    if issubclass(sender, User) and kwargs['created']:
        try:
            Profile.objects.get(user=kwargs['instance'])
        except:
            # Create if not exist; signal has been sent twice
            Profile.objects.create(user=kwargs['instance'], membership_type='1')
