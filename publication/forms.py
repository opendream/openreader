from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import HiddenInput

from publication.models import Book, Category, Issue, Periodical, Publisher, \
                               PUBLICATION_TYPES


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name', 'address', 'telephone', 'website')


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
        exclude = ('publisher', 'status', 'pending_until', 'categories')


class PeriodicalForm(forms.ModelForm):
    class Meta:
        model = Periodical
        exclude = ('periodical_type', 'publisher', 'categories')


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
        exclude = ('periodical', 'status', 'pending_until')
        widgets = {
            'issued_at': SelectDateWidget()
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
