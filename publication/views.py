import datetime, time
import os
import simplejson as json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from publication.forms import BookForm, CategoryForm, IssueForm, PeriodicalForm, \
                              PublisherForm
from publication.models import Book, Category, FileUpload, Issue, Periodical, \
                               Publication, Publisher, TopicOfContents \


@login_required
def index_publisher(request):
    return render(request, 'publication/publisher_index.html') 

@login_required
def publisher_dashboard(request, id):
    publisher = get_object_or_404(Publisher, pk=id)
    return render(request, 'publication/dashboard.html', {'publisher': publisher})

@login_required
def manage_publisher(request, id):
    publisher = get_object_or_404(Publisher, pk=id)
    return render(request, 'publication/publisher_management.html', {'publisher': publisher})

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
            return redirect('publication-show-publisher', pk=id)
    else:
        form = PublisherForm(instance=publisher)
    return render(request, 'publication/publisher_form.html', {'form': form})

@login_required
def index_category(request):
    categories = Category.objects.all()
    return render(request, 'publication/category_index.html', {'categories': categories})

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category-index')
    else:
        form = CategoryForm()
    return render(request, 'publication/category_form.html', {'form': form})

@login_required
def update_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category-index')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'publication/category_form.html', {'form': form})

@login_required
def index_book(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/book_index.html', {'publisher': publisher}) 

@login_required
def create_book(request, publisher_id):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.publisher = Publisher.objects.get(pk=publisher_id) 
            book.save()
            book.save_categories(request.POST)

            file_name = 'u' + str(request.user.id) + '_b' + str(book.id)
            path = handle_uploaded_file(request.FILES['file_upload'],
                file_name=file_name)
            FileUpload.objects.create(uploader=request.user,
                publication_type=Publication.BOOK,
                publication_id=book.id,
                path=path)
            return redirect('publication-show-book', publisher_id=publisher_id, book_id=book.id)
    else:
        form = BookForm()
    categories = Category.objects.all()
    return render(request, 'publication/book_form.html', {'form': form, 'categories': categories}) 

@login_required
def show_book(request, publisher_id, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'publication/book_show.html', {'book': book})

@login_required
def update_book(request, publisher_id, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            book.save_categories(request.POST)
            if form.cleaned_data.has_key('file_upload'):
                file_upload = get_object_or_404(FileUpload,
                                    publication_type=Publication.BOOK,
                                    publication_id=book_id)
                path = handle_uploaded_file(request.FILES['file_upload'],
                            file_name=file_upload.file_name(), update=True)
                file_upload.uploader = request.user # may another collaborator has updated
                file_upload.path = path # may the file extension has been changed
                file_upload.save() # save updated_at
            return redirect('publication-show-book', publisher_id=publisher_id, book_id=book_id)
    else:
        form = BookForm(instance=book, initial={'book_id': book_id})
    categories = Category.objects.all()
    book_categories = []
    for category in book.categories.all():
        book_categories.append(category.id)
    return render(request, 'publication/book_form.html',
                {'form': form, 'book_id': book_id, 'book_categories': book_categories, 
                 'categories': categories}) 

@login_required
def update_book_status(request, publisher_id, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        status = int(request.POST['status'])
        if status == Publication.STATUS_PENDING:
            pending_until = "%s %s" % (request.POST['pending_date'], request.POST['pending_time'])
            pending_until = datetime.datetime.strptime(pending_until, '%Y/%m/%d %H:%M')
            book.pending_until = pending_until
        else:
            if book.pending_until:
                book.pending_until = None
        book.status = status
        book.save()
        return redirect('publication-show-book', publisher_id=publisher_id, book_id=book_id)
    status = {
        'DRAFT': Publication.STATUS_DRAFT,
        'PENDING': Publication.STATUS_PENDING,
        'PUBLISHED': Publication.STATUS_PUBLISHED,
        'UNPUBLISHED': Publication.STATUS_UNPUBLISHED
    }
    return render(request, 'publication/status_form.html', {'obj': book, 'status': status})

@login_required
def manage_book_toc(request, publisher_id, book_id):
    pass

@login_required
def delete_book(request, publisher_id, book_id):
    pass

@login_required
def index_periodical(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/periodical_index.html', {'publisher': publisher}) 

@login_required
def create_periodical(request, publisher_id):
    if request.method == 'POST':
        form = PeriodicalForm(request.POST)
        if form.is_valid():
            periodical = form.save(commit=False)
            periodical.publisher = Publisher.objects.get(pk=publisher_id)
            periodical.save()
            periodical.save_categories(request.POST)
            return redirect('publication-show-periodical', publisher_id=publisher_id,
                        periodical_id=periodical.id)
    else:
        form = PeriodicalForm()
    categories = Category.objects.all()
    return render(request, 'publication/periodical_form.html',
                {'form': form, 'categories': categories})

@login_required
def show_periodical(request, publisher_id, periodical_id):
    periodical = get_object_or_404(Periodical, pk=periodical_id)
    return render(request, 'publication/periodical_show.html', {'periodical': periodical})

@login_required
def update_periodical(request, publisher_id, periodical_id):
    periodical = get_object_or_404(Periodical, pk=periodical_id)
    if request.method == 'POST':
        form = PeriodicalForm(request.POST, instance=periodical)
        if form.is_valid():
            periodical = form.save(commit=False)
            periodical.save()
            periodical.save_categories(request.POST)
            return redirect('publication-show-periodical',
                        publisher_id=publisher_id, periodical_id=periodical_id)
    else:
        form = PeriodicalForm(instance=periodical)
    categories = Category.objects.all()
    periodical_categories = []
    for category in periodical.categories.all():
        periodical_categories.append(category.id)
    return render(request, 'publication/periodical_form.html',
                {'form': form, 'periodical_categories': periodical_categories,
                 'categories': categories})

@login_required
def index_issue(request, publisher_id, periodical_id):
    return redirect('publication-show-periodical',
                publisher_id=publisher_id, periodical_id=periodical_id)

@login_required
def create_issue(request, publisher_id, periodical_id):
    periodical = get_object_or_404(Periodical, pk=periodical_id)
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.periodical = periodical
            issue.save()

            file_name = 'u' + str(request.user.id) + '_p' + str(periodical.id) + '_s' + str(issue.id)
            path = handle_uploaded_file(request.FILES['file_upload'], file_name=file_name)
            FileUpload.objects.create(uploader=request.user,
                publication_type=Publication.PERIODICAL,
                publication_id=issue.id,
                path=path)
            return redirect('publication-show-issue',
                        publisher_id=publisher_id, periodical_id=periodical_id, issue_id=issue.id)
        else:
            print form
    else:
        form = IssueForm()
    return render(request, 'publication/issue_form.html', {'form': form, 'periodical': periodical})

@login_required
def show_issue(request, publisher_id, periodical_id, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    return render(request, 'publication/issue_show.html', {'issue': issue})

@login_required
def update_issue(request, publisher_id, periodical_id, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            form.save()
            if form.cleaned_data.has_key('file_upload'):
                try:
                    file_upload = FileUpload.objects.get(
                        publication_type=Publication.PERIODICAL,
                        publication_id=issue_id
                    )
                    path = handle_uploaded_file(request.FILES['file_upload'],
                                file_name=file_upload.file_name(), update=True)
                except FileUpload.DoesNotExist:
                    file_upload = FileUpload(
                        publication_type=Publication.PERIODICAL,
                        publication_id=issue_id
                    )
                    file_name = 'u' + str(request.user.id) + '_p' + str(periodical_id) + \
                                '_s' + str(issue.id)
                    path = handle_uploaded_file(request.FILES['file_upload'], file_name=file_name)
                file_upload.uploader = request.user # may another collaborator has updated
                file_upload.path = path # may the file extension has been changed
                file_upload.save() # save updated_at
            return redirect('publication-show-issue',
                        publisher_id=publisher_id, periodical_id=periodical_id, issue_id=issue_id)
    else:
        form = IssueForm(instance=issue, initial={'issue_id': issue_id})
    return render(request, 'publication/issue_form.html', {'form': form, 'issue_id': issue_id}) 

@login_required
def update_issue_status(request, publisher_id, periodical_id, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == 'POST':
        status = int(request.POST['status'])
        if status == Publication.STATUS_PENDING:
            pending_until = "%s %s" % (request.POST['pending_date'], request.POST['pending_time'])
            pending_until = datetime.datetime.strptime(pending_until, '%Y/%m/%d %H:%M')
            issue.pending_until = pending_until
        else:
            if issue.pending_until:
                issue.pending_until = None
        issue.status = status
        issue.save()
        return redirect('publication-show-issue', publisher_id=publisher_id,
                    periodical_id=periodical_id, issue_id=issue_id)
    status = {
        'DRAFT': Publication.STATUS_DRAFT,
        'PENDING': Publication.STATUS_PENDING,
        'PUBLISHED': Publication.STATUS_PUBLISHED,
        'UNPUBLISHED': Publication.STATUS_UNPUBLISHED
    }
    return render(request, 'publication/status_form.html', {'obj': issue, 'status': status})

@login_required
def manage_issue_toc(request, publisher_id, periodical_id, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == 'POST' and request.is_ajax():
        action = request.POST.get('action')
        page = request.POST.get('page')
        title = request.POST.get('title')
        old_title = request.POST.get('old_title')
        author = request.POST.get('author')

        ret = []
        if action == 'show':
            topics = issue.topic_of_contents({'page': page})
            for topic in topics:
                ret.append({
                    'page': topic.page, 'title': topic.title, 'author': topic.author
                }) 
        elif action == 'create':
            TopicOfContents.objects.create(
                publication_type=Publication.PERIODICAL,
                publication_id=issue_id,
                page=page,
                title=title,
                author=author
            )
            ret.append({'page': page, 'title': title, 'author': author})
        elif action == 'update':
            try:
                toc = issue.topic_of_contents({'page': page, 'title': old_title})
                toc.title = title
                toc.author = author
                toc.save()
            except TopicOfContents.DoesNotExist:
                TopicOfContents.objects.create(
                    publication_type=Publication.PERIODICAL,
                    publication_id=issue_id,
                    page=page,
                    title=title,
                    author=author
                )
            ret.append({'page': page, 'title': title, 'author': author})
        elif action == 'delete':
            try:
                issue.topic_of_contents({'page': page, 'title': title}).delete()
                ret.append({'page': '', 'title': '', 'author': ''})
            except TopicOfContents.DoesNotExist:
                return HttpResponse(json.dumps({'success': False}))

        return HttpResponse(json.dumps({'success': True, 'topics': ret}))

    pages = [1, 2, 3]
    return render(request, 'publication/toc_form.html', {'obj': issue, 'pages': pages})

@login_required
def delete_issue(request, publisher_id, periodical_id, issue_id):
    pass

# private ----------------------------------------------------------------------

def handle_uploaded_file(f, file_name, update=False):
    if update:
        timestamp = file_name.split('_')[-1] # extract timestamp from the file name
        timestamp = timestamp.split('.')[0] # remove file extension
        created_at = datetime.date.fromtimestamp(float(timestamp))
        root_dir = str(created_at.year) + os.sep + str(created_at.month)
        abs_dir_path = settings.MEDIA_ROOT + settings.PUBLICATION_DIR + root_dir
        file_extension = f.name.split('.')[-1] # extract file extension from the uploaded file
        file_name = file_name.split('.')[0] # remove current file extension
        file_path = file_name + '.' + file_extension
    else:
        created_at = datetime.datetime.now()
        root_dir = str(created_at.year) + os.sep + str(created_at.month)
        abs_dir_path = settings.MEDIA_ROOT + settings.PUBLICATION_DIR + root_dir
        if not os.path.exists(abs_dir_path):
            os.makedirs(abs_dir_path)
        file_extension = f.name.split('.')[-1]
        file_path = file_name + '_' + str(int(time.time())) + '.' + file_extension

    abs_file_path = abs_dir_path + os.sep + file_path
    destination = open(abs_file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return root_dir + os.sep + file_path
