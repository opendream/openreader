from django import forms
from django.forms.widgets import RadioSelect

from publication.models import Book, Periodical, Publisher, \
                               PUBLICATION_TYPES


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name',)


class BookForm(forms.ModelForm):
    file_upload = forms.FileField()

    class Meta:
        model = Book
        exclude = ('publisher',)


class PeriodicalForm(forms.ModelForm):
    class Meta:
        model = Periodical
