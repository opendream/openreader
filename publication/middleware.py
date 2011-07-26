from django.shortcuts import get_object_or_404

from publication.models import Publisher

class PublicationMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if 'publisher_id' in callback_kwargs:
            publisher_id = callback_kwargs['publisher_id']
            publisher = get_object_or_404(Publisher, pk=publisher_id)
            request.publisher = publisher
        return None
