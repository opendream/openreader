from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.db import models

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
    (4, 'Unpublished')
)

PERIODICAL_TYPES = (
    (1, 'Magazine'),
)

# Manager ----------------------------------------------------------------------

class PublicationManager:
    def topic_of_contents(self, kwargs=None):
        if kwargs:
            if 'page' in kwargs and 'title' in kwargs:
                return TopicOfContents.objects.get(
                            publication_type=self.TYPE,
                            publication_id=self.id,
                            page=kwargs['page'],
                            title=kwargs['title'])
            elif 'page' in kwargs:
                return TopicOfContents.objects.filter(
                            publication_type=self.TYPE,
                            publication_id=self.id,
                            page=kwargs['page'])
            elif 'title' in kwargs:
                return TopicOfContents.objects.filter(
                            publication_type=self.TYPE,
                            publication_id=self.id,
                            title=kwargs['title'])
            else:
                return []
        else:
            return TopicOfContents.objects.filter(
                        publication_type=self.TYPE,
                        publication_id=self.id)

    def file_path(self):
        try:
            f = FileUpload.objects.get(publication_type=self.TYPE, publication_id=self.id)
            return settings.MEDIA_URL + settings.PUBLICATION_DIR + f.path
        except:
            return ''

    def thumbnail_pages(self):
        return [1, 2, 3] # TODO: generate thumbnail of pages

    def instance_of(self):
        return self.__class__.__name__

# DB Models --------------------------------------------------------------------

class Publisher(Loggable):
    owner = models.ForeignKey(User, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborators')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)

    def draft_issues(self):
        periodicals = self.periodical_set.all().values('pk')
        return Issue.objects.filter(periodical__in=periodicals,
                                    status=Publication.STATUS_DRAFT)

    def pending_issues(self):
        periodicals = self.periodical_set.all().values('pk')
        return Issue.objects.filter(periodical__in=periodicals,
                                    status=Publication.STATUS_PENDING)

    def published_issues(self):
        periodicals = self.periodical_set.all().values('pk')
        return Issue.objects.filter(periodical__in=periodicals,
                                    status=Publication.STATUS_PUBLISHED)


class Publication(Loggable):
    publisher = models.ForeignKey('Publisher')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    BOOK = 1
    PERIODICAL = 2

    STATUS_DRAFT = 1
    STATUS_PENDING = 2
    STATUS_PUBLISHED = 3
    STATUS_UNPUBLISHED = 4

    def save_categories(self, post_vars):
        categories = []
        for key in post_vars:
            if key.find('category_') == 0:
                pk = key.split('_')[1]
                categories.append(Category.objects.get(pk=pk))
        self.categories = categories
        self.save()

    class Meta:
        abstract = True


class Book(Publication, PublicationManager):
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    status = models.IntegerField(choices=PUBLICATION_STATUSES, default=1, db_index=True)
    pending_until = models.DateTimeField(null=True, blank=True)
    categories = models.ManyToManyField('Category', related_name='book_categories')

    TYPE = Publication.BOOK


class Periodical(Publication):
    periodical_type = models.IntegerField(choices=PERIODICAL_TYPES, default=1, db_index=True)
    categories = models.ManyToManyField('Category', related_name='periodical_categories')


class Issue(Loggable, PublicationManager):
    periodical = models.ForeignKey('Periodical')
    issued_at = models.DateField()
    description = models.TextField(null=True, blank=True)
    status = models.IntegerField(choices=PUBLICATION_STATUSES, default=1, db_index=True)
    pending_until = models.DateTimeField(null=True, blank=True)

    TYPE = Publication.PERIODICAL

    class Meta:
        get_latest_by = 'created_at'


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
    author = models.CharField(max_length=100, null=True, blank=True)


class Category(Loggable):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)


class PublisherUserPermission(Loggable):
    publisher = models.ForeignKey(Publisher)
    user = models.ForeignKey(User)
    permission = models.ForeignKey(Permission)

    class Meta:
        db_table = 'publication_publisher_user_permissions'


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
