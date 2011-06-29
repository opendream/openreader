from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

#from djangotoolbox.fields import EmbeddedModelField, ListField

from common.models import Loggable


PUBLICATION_TYPES = (
    (1, 'Book'),
    (2, 'Periodical')
)

PUBLICATION_STATUSES = (
    (1, 'Draft'),
    (2, 'Pending'),
    (3, 'Published'),
    (4, 'Unpublished'),
)

PERIODICAL_TYPES = (
    (1, 'Magazine'),
)


class Publisher(Loggable):
    owner = models.ForeignKey(User, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborators')
    name = models.CharField(max_length=255)


class Publication(Loggable):
    publisher = models.ForeignKey('Publisher')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.IntegerField(choices=PUBLICATION_STATUSES, default=1, db_index=True)
    pending_until = models.DateTimeField(null=True, blank=True)

    BOOK = 1
    PERIODICAL = 2

    STATUS_DRAFT = 1
    STATUS_PENDING = 2
    STATUS_PUBLISHED = 3
    STATUS_UNPUBLISHED = 4

    class Meta:
        abstract = True


class Book(Publication):
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)

    def file_path(self):
        try:
            f = FileUpload.objects.get(publication_type=Publication.BOOK, publication_id=self.id)
            return settings.MEDIA_URL + settings.PUBLICATION_DIR + f.path
        except:
            return ''

    def topic_of_contents(self):
        return TopicOfContents.objects.filter(publication_type=Publication.BOOK,
                                              publication_id=self.id)


class Periodical(Publication):
    periodical_type = models.IntegerField(choices=PERIODICAL_TYPES, default=1, db_index=True)
    categories = models.ManyToManyField('Category', related_name='periodical_categories')


class Issue(Loggable):
    periodical = models.ForeignKey('Periodical')
    issued_at = models.DateField()
    description = models.TextField(null=True, blank=True)

    def file_path(self):
        try:
            f = FileUpload.objects.get(publication_type=Publication.PERIODICAL, publication_id=self.id)
            return settings.MEDIA_URL + settings.PUBLICATION_DIR + f.path
        except:
            return ''

    def topic_of_contents(self):
        return TopicOfContents.objects.filter(publication_type=Publication.PERIODICAL,
                                              publication_id=self.id)


class FileUpload(Loggable):
    uploader = models.ForeignKey(User)
    publication_type = models.IntegerField(choices=PUBLICATION_TYPES, db_index=True)
    publication_id = models.CharField(max_length=10, db_index=True)
    path = models.CharField(max_length=255)

    def file_name(self):
        return self.path.split('/')[-1]


class TopicOfContents(Loggable):
    publication_type = models.IntegerField(choices=PUBLICATION_TYPES, db_index=True)
    publication_id = models.CharField(max_length=10, db_index=True)
    page = models.CharField(max_length=3)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)


class Category(Loggable):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)


# MongoDB ---------------------------------------------------------------------

#class TopicOfContents(models.Model):
#    page = models.CharField(max_length=3)
#    title = models.CharField(max_length=255)
#    author = models.CharField(max_length=100)
#
#
#class BookMetadata(models.Model):
#    book_id = models.CharField(max_length=10)
#    toc = ListField(EmbeddedModelField('TopicOfContents'))
#
#
#class IssueMetadata(models.Model):
#    issue_id = models.CharField(max_length=10)
#    toc = ListField(EmbeddedModelField('TopicOfContents'))


# Signals ---------------------------------------------------------------------

@receiver(post_save)
def save_category(sender, **kwargs):
    if issubclass(sender, Publication):
        pass
        # TODO: logic for category saving here.
        #if kwargs['created']:
        #    kwargs['instance'].categories
        #    Category.objects.create()
        #else:
        #    pass
