from django.contrib.auth.models import User
from django.db import models

from core.models import Loggable


class Profile(Loggable):
    user = models.ForeignKey(User)
