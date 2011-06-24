from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from common.models import Loggable


PUBLICATION_TYPES = (
    (1, 'Book'),
    (2, 'Periodical')
)

PERIODICAL_TYPES = (
    (1, 'Magazine'),
    (2, 'Newspaper')
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

    BOOK = 1
    PERIODICAL = 2


class Book(Publication):
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)

    def file_path(self):
        files = FileUpload.objects.filter(publication_type=Publication.BOOK, publication_id=self.id)
        if files:
            return settings.MEDIA_URL + settings.PUBLICATION_DIR + files[0].path
        else:
            return None


class Periodical(Publication):
    periodical_type = models.IntegerField(choices=PERIODICAL_TYPES, db_index=True)


class Issue(Loggable):
    periodical = models.ForeignKey('Periodical')
    issued_at = models.DateField()

    def file_path(self):
        files = FileUpload.objects.filter(publication_type=Publication.PERIODICAL,
            publication_id=self.periodical.id, issue_id=self.id)
        if files:
            return settings.MEDIA_URL + settings.PUBLICATION_DIR + files[0].path
        else:
            return None


class FileUpload(Loggable):
    uploader = models.ForeignKey(User)
    publication_type = models.IntegerField(choices=PUBLICATION_TYPES, db_index=True)
    publication_id = models.CharField(max_length=10, db_index=True)
    issue_id = models.CharField(max_length=10, db_index=True, null=True)
    path = models.CharField(max_length=255)

    def file_name(self):
        return self.path.split('/')[-1]
