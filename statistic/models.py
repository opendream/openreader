import datetime

from django.db import models
from django.dispatch import receiver

from private_files import pre_download

from common.models import Loggable
from publication.models import FileUpload


class CountedFileDownloads(Loggable):
    target = models.ForeignKey(FileUpload)
    downloads = models.PositiveIntegerField("downloads total", default=0, db_index=True)


class CountedFileDownloadsManager:
    def __init__(self, *args, **kwargs):
        self.obj = kwargs['obj']

    def total_downloads(self):
        try:
            file_upload = FileUpload.objects.filter(publication_type=self.obj.TYPE,
                                                    publication_id=self.obj.id)
        except FileUpload.DoesNotExist:
            return 0

        try:
            file_download = CountedFileDownloads.objects.filter(
                                target=file_upload).latest('created_at')
            return file_download.downloads
        except CountedFileDownloads.DoesNotExist:
            return 0

    def last_week_downloads(self):
        try:
            file_upload = FileUpload.objects.filter(publication_type=self.obj.TYPE,
                                                    publication_id=self.obj.id)
        except FileUpload.DoesNotExist:
            return 0

        last_7_days = datetime.datetime.today() - datetime.timedelta(days=7)
        return CountedFileDownloads.objects.filter(target=file_upload,
                    created_at__gte=last_7_days).count()

    def last_month_downloads(self):
        try:
            file_upload = FileUpload.objects.filter(publication_type=self.obj.TYPE,
                                                    publication_id=self.obj.id)
        except FileUpload.DoesNotExist:
            return 0

        last_30_days = datetime.datetime.today() - datetime.timedelta(days=30)
        return CountedFileDownloads.objects.filter(target=file_upload,
                    created_at__gte=last_30_days).count()


@receiver(pre_download, dispatch_uid='unique')
def handle_file_download(instance, **kwargs):
    try:
        prev_downloaded = CountedFileDownloads.objects.filter(target=instance).latest('created_at')
        next_downloaded = CountedFileDownloads(target=instance)
        next_downloaded.downloads = prev_downloaded.downloads + 1
        next_downloaded.save()
    except CountedFileDownloads.DoesNotExist:
        CountedFileDownloads.objects.create(target=instance, downloads=1)
