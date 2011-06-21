from django.forms import ModelForm

from publication.models import Publisher


class PublisherForm(ModelForm):
    class Meta:
        model = Publisher
        fields = ('name',)
