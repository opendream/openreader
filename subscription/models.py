from django.contrib.auth.models import User
from django.db import models

from common.models import Loggable
from publication.models import Publication, PUBLICATION_TYPES


class Library(Loggable):
    owner = models.ForeignKey(User)
    publication_id = models.CharField(max_length=10, db_index=True)
    publication_type = models.IntegerField(choices=PUBLICATION_TYPES, db_index=True)
