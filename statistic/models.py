from django.db import models
from django.dispatch import receiver

from private_files import pre_download

from common.models import Loggable
from publication.models import FileUpload


class CountedFileDownloads(Loggable):
    target = models.ForeignKey(FileUpload)
    downloads = models.PositiveIntegerField("downloads total", default=0, db_index=True)


@receiver(pre_download)
def handle_file_download(instance, **kwargs):
    try:
        downloaded = CountedFileDownloads.objects.get(target=instance)
        downloaded.downloads += 1
        downloaded.save()
    except CountedFileDownloads.DoesNotExist:
        CountedFileDownloads.objects.create(target=instance, downloads=1)
