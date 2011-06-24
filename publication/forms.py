from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import HiddenInput

from publication.models import Book, Periodical, Publisher, Issue, \
                               PUBLICATION_TYPES


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name',)


class BookForm(forms.ModelForm):
    file_upload = forms.FileField()
    book_id = forms.CharField(widget=HiddenInput)

    def clean(self):
        if self.cleaned_data.has_key('book_id'): # update
            if self._errors.has_key('file_upload'):
                del self._errors['file_upload'] # file upload isn't required
        else: # create
            del self._errors['book_id']
        return self.cleaned_data

    class Meta:
        model = Book
        exclude = ('publisher',)


class PeriodicalForm(forms.ModelForm):
    class Meta:
        model = Periodical
        exclude = ('publisher',)


class IssueForm(forms.ModelForm):
    file_upload = forms.FileField()
    issue_id = forms.CharField(widget=HiddenInput)

    def clean(self):
        if self.cleaned_data.has_key('issue_id'): # update
            if self._errors.has_key('file_upload'):
                del self._errors['file_upload'] # file upload isn't required
        else: # create
            del self._errors['issue_id']
        return self.cleaned_data

    class Meta:
        model = Issue
        exclude = ('periodical',)
        widgets = {
            'issued_at': SelectDateWidget()
        }
