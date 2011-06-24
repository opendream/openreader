from django import forms
from django.forms.widgets import HiddenInput

from publication.models import Book, Periodical, Publisher, \
                               PUBLICATION_TYPES


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name',)


class BookForm(forms.ModelForm):
    file_upload = forms.FileField()
    book_id = forms.CharField(widget=HiddenInput)

    def clean(self):
        if self.cleaned_data['book_id']:
            if self._errors.has_key('file_upload'):
                del self._errors['file_upload']
        else:
            del self._errors['book_id']
        return self.cleaned_data

    class Meta:
        model = Book
        exclude = ('publisher',)


class PeriodicalForm(forms.ModelForm):
    class Meta:
        model = Periodical
