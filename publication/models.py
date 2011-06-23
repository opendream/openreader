from django.contrib.auth.models import User
from django.db import models

from common.models import Loggable


PUBLICATION_TYPES = (
    ('1', 'Book'),
    ('2', 'Periodical')
)

PERIODICAL_TYPES = (
    ('1', 'Magazine'),
    ('2', 'Newspaper')
)


class Publisher(Loggable):
    owner = models.ForeignKey(User, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborators')
    name = models.CharField(max_length=255)


class Publication(Loggable):
    publisher = models.ForeignKey('Publisher')
    title = models.CharField(max_length=255)

    class Meta:
        abstract = True

    BOOK = '1'
    PERIODICAL = '2'


class Book(Publication):
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)


class Periodical(Publication):
    periodical_type = models.IntegerField(choices=PERIODICAL_TYPES, db_index=True)


class Issue(Loggable):
    periodical = models.ForeignKey('Periodical')
    issued_at = models.DateTimeField()


class FileUpload(Loggable):
    uploader = models.ForeignKey(User)
    publication_id = models.CharField(max_length=10, db_index=True)
    publication_type = models.IntegerField(choices=PUBLICATION_TYPES, db_index=True)
    path = models.CharField(max_length=255)
