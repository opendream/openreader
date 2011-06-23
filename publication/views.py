import datetime, time
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from publication.forms import PublisherForm, BookForm
from publication.models import Book, Publication, Publisher, FileUpload


@login_required
def index_publisher(request):
    return render(request, 'publication/publisher_index.html') 

@login_required
def create_publisher(request):
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save(commit=False)
            publisher.owner = request.user
            publisher.save()
            return redirect('publication-show-publisher', id=publisher.id)
    else:
        form = PublisherForm()
    return render(request, 'publication/publisher_form.html', {'form': form})

@login_required
def show_publisher(request, id):
    publisher = get_object_or_404(Publisher, pk=id)
    return render(request, 'publication/publisher_show.html', {'publisher': publisher})

@login_required
def update_publisher(request, id):
    publisher = get_object_or_404(Publisher, pk=id)
    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            return redirect('publication-show-publisher', pk=publisher.id)
    else:
        form = PublisherForm(instance=publisher)
    return render(request, 'publication/publisher_form.html', {'form': form})

@login_required
def index_book(request, publisher_id):
    return render(request, 'publication/book_index.html') 

@login_required
def create_book(request, publisher_id):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.publisher = Publisher.objects.get(pk=publisher_id) 
            book.save()

            file_name = 'u' + str(request.user.id) + '_b' + str(book.id)
            path = handle_uploaded_file(request.FILES['file_upload'], \
                file_name=file_name)
            FileUpload.objects.create(uploader=request.user, \
                publication_type=Publication.BOOK, \
                publication_id=book.id, path=path)
            return redirect('publication-show-book', publisher_id=publisher_id, book_id=book.id)
    else:
        form = BookForm()
    return render(request, 'publication/book_form.html', {'form': form}) 

@login_required
def show_book(request, publisher_id, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'publication/book_show.html', {'book': book})

@login_required
def update_book(request, publisher_id, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        return render(request, 'publication/book_form.html')
        # TODO: not yet finished
    else:
        form = BookForm(instance=book)
    return render(request, 'publication/book_form.html', {'form': form}) 

# private ----------------------------------------------------------------------

def handle_uploaded_file(f, file_name):
    today = datetime.datetime.now()
    root_dir = str(today.year) + os.sep + str(today.month)
    abs_dir_path = settings.PUBLICATION_DIR + root_dir
    if not os.path.exists(abs_dir_path):
        os.makedirs(abs_dir_path)
    
    file_extension = f.name.split('.')[-1]
    file_path = file_name + '_' + str(int(time.time())) + '.' + file_extension
    abs_file_path = abs_dir_path + os.sep + file_path
    destination = open(abs_file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return file_path
