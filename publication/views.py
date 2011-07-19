import datetime
import simplejson as json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from publication.forms import BookForm, CategoryForm, IssueForm, PeriodicalForm, \
                              PublisherForm
from publication.models import Book, Category, FileUpload, Issue, Periodical, \
                               Publication, Publisher, PublisherUserPermission, \
                               TopicOfContents \


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
            return redirect('publication-publisher-dashboard', id=publisher.id)
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
            return redirect('publication-publisher-dashboard', id=id)
    else:
        form = PublisherForm(instance=publisher)
    return render(request, 'publication/publisher_form.html', {'form': form, 'publisher': publisher})

@login_required
def publisher_team(request, id):
    publisher = get_object_or_404(Publisher, pk=id)
    if request.method == 'POST' and request.is_ajax():
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return HttpResponse(json.dumps({'success': False}))

        collaborators = []
        for collaborator in publisher.collaborators.all():
            collaborators.append(collaborator)

        if action == 'show':
            permissions = []
            pub_user_permissions = PublisherUserPermission.objects.filter(
                                        publisher=publisher, user=user)
            for p in pub_user_permisssions:
                permissions.append(p.permission)
            return HttpResponse(json.dumps({'success': True, 'permissions': permissions}))
        elif action == 'create':
            if user not in collaborators:
                collaborators.append(user)
                publisher.collaborators = collaborators
                publisher.save()
                return HttpResponse(json.dumps({'success': True}))
        elif action == 'update':
            new_permissions = []
            old_permissions = []
            pub_user_permissions = PublisherUserPermission.objects.filter(
                                        publisher=publisher, user=user)
            for p in pub_user_permissions:
                old_permissions.append(p.permission)

            permissions_post = json.loads(request.POST.get('permissions'))
            for p in permissions_post:
                new_permissions.append(get_object_or_404(Permission, pk=p))

            for p in old_permissions:
                if p not in new_permissions:
                    pub_user_permissions.get(permission=p).delete()
            for p in new_permissions:
                if p not in old_permissions:
                    PublisherUserPermission.objects.create(
                        publisher=publisher,
                        user=user,
                        permission=p
                    )
            return HttpResponse(json.dumps({'success': True}))
        elif action == 'delete':
            if publisher.owner == user:
                return HttpResponse(json.dumps({'success': False}))

            if user in collaborators:
                collaborators.remove(user)
                publisher.collaborators = collaborators
                publisher.save()

                PublisherUserPermission.objects.filter(
                    publisher=publisher, user=user).delete()
                
                return HttpResponse(json.dumps({'success': True}))
        return HttpResponse(json.dumps({'success': False}))
    
    content_type = ContentType.objects.get_by_natural_key(
                        'publication', 'publisheruserpermission')
    auth_permissions = Permission.objects.filter(content_type=content_type)
    return render(request, 'publication/publisher_team.html',
                {'publisher': publisher, 'auth_permissions': auth_permissions})

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

            uploaded_file = request.FILES['file_upload']
            pre_filename = 'u%d_b%d' % (request.user.id, book.id)
            post_filename = _complete_filename(uploaded_file.name, pre_filename)
            file_upload = FileUpload.objects.create(
                                uploader=request.user,
                                publication_type=Publication.BOOK,
                                publication_id=book.id)
            file_upload.uploaded_file.save(post_filename, uploaded_file)
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

                uploaded_file = request.FILES['file_upload']
                pre_filename = file_upload.uploaded_file.name
                post_filename = _complete_filename(uploaded_file.name, pre_filename, update=True)
                file_upload.uploader = request.user
                file_upload.uploaded_file.save(post_filename, uploaded_file)
                file_upload.save()
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
            try:
                pending_until = "%s %s" % (request.POST['pending_date'], request.POST['pending_time'])
                pending_until = datetime.datetime.strptime(pending_until, '%Y/%m/%d %H:%M')
                book.pending_until = pending_until
            except ValueError:
                book.status = status
                status = {
                    'DRAFT': Publication.STATUS_DRAFT,
                    'PENDING': Publication.STATUS_PENDING,
                    'PUBLISHED': Publication.STATUS_PUBLISHED,
                    'UNPUBLISHED': Publication.STATUS_UNPUBLISHED
                }
                return render(request, 'publication/status_form.html', {'obj': book, 'status': status})
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
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST' and request.is_ajax():
        action = request.POST.get('action')
        page = request.POST.get('page')
        title = request.POST.get('title')
        old_title = request.POST.get('old_title')

        ret = []
        if action == 'show':
            topics = book.topic_of_contents({'page': page})
            for topic in topics:
                ret.append({'page': topic.page, 'title': topic.title})
            if len(ret) == 0:
                ret.append({'page': page, 'title': ''})
        elif action == 'create':
            TopicOfContents.objects.create(
                publication_type=Publication.BOOK,
                publication_id=book_id,
                page=page,
                title=title
            )
            ret.append({'page': page, 'title': title})
        elif action == 'update':
            try:
                toc = book.topic_of_contents({'page': page, 'title': old_title})
                toc.title = title
                toc.save()
            except TopicOfContents.DoesNotExist:
                TopicOfContents.objects.create(
                    publication_type=Publication.BOOK,
                    publication_id=book_id,
                    page=page,
                    title=title
                )
            ret.append({'page': page, 'title': title})
        elif action == 'delete':
            try:
                book.topic_of_contents({'page': page, 'title': title}).delete()
                ret.append({'page': '', 'title': ''})
            except TopicOfContents.DoesNotExist:
                return HttpResponse(json.dumps({'success': False}))

        return HttpResponse(json.dumps({'success': True, 'topics': ret}))

    pages = book.thumbnail_pages
    return render(request, 'publication/toc_form.html', {'obj': book, 'pages': pages})

@login_required
def delete_book(request, publisher_id, book_id):
    get_object_or_404(Book, pk=book_id).delete()

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
                 'categories': categories, 'periodical_id': periodical_id})

@login_required
def delete_periodical(request, publisher_id, periodical_id):
    get_object_or_404(Periodical, pk=periodical_id).delete()

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
            path = _handle_uploaded_file(request.FILES['file_upload'], file_name=file_name)
            FileUpload.objects.create(uploader=request.user,
                publication_type=Publication.PERIODICAL,
                publication_id=issue.id,
                path=path)
            return redirect('publication-show-issue',
                        publisher_id=publisher_id, periodical_id=periodical_id, issue_id=issue.id)
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
                    path = _handle_uploaded_file(request.FILES['file_upload'],
                                file_name=file_upload.file_name(), update=True)
                except FileUpload.DoesNotExist:
                    file_upload = FileUpload(
                        publication_type=Publication.PERIODICAL,
                        publication_id=issue_id
                    )
                    file_name = 'u' + str(request.user.id) + '_p' + str(periodical_id) + \
                                '_s' + str(issue.id)
                    path = _handle_uploaded_file(request.FILES['file_upload'], file_name=file_name)
                file_upload.uploader = request.user # may another collaborator has updated
                file_upload.path = path # may the file extension has been changed
                file_upload.save() # save updated_at
            return redirect('publication-show-issue',
                        publisher_id=publisher_id, periodical_id=periodical_id, issue_id=issue_id)
    else:
        form = IssueForm(instance=issue, initial={'issue_id': issue_id})
    return render(request, 'publication/issue_form.html', {'form': form, 'issue': issue})

@login_required
def update_issue_status(request, publisher_id, periodical_id, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == 'POST':
        status = int(request.POST['status'])
        if status == Publication.STATUS_PENDING:
            try:
                pending_until = "%s %s" % (request.POST['pending_date'], request.POST['pending_time'])
                pending_until = datetime.datetime.strptime(pending_until, '%Y/%m/%d %H:%M')
                issue.pending_until = pending_until
            except ValueError:
                issue.status = status
                status = {
                    'DRAFT': Publication.STATUS_DRAFT,
                    'PENDING': Publication.STATUS_PENDING,
                    'PUBLISHED': Publication.STATUS_PUBLISHED,
                    'UNPUBLISHED': Publication.STATUS_UNPUBLISHED
                }
                return render(request, 'publication/status_form.html', {'obj': issue, 'status': status})
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
            if len(ret) == 0:
                ret.append({'page': page, 'title': '', 'author': ''})
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

    pages = issue.thumbnail_pages
    return render(request, 'publication/toc_form.html', {'obj': issue, 'pages': pages})

@login_required
def delete_issue(request, publisher_id, periodical_id, issue_id):
    get_object_or_404(Issue, pk=issue_id).delete()


# PRIVATE ---------------------------------------------------------------------

def _complete_filename(uploaded_filename, pre_filename, update=False):
    # Get original file extension
    file_extension = uploaded_filename.split('.')[-1]
    if update:
        file_paths = pre_filename.split('/')
        created_at = datetime.datetime(int(file_paths[1]), int(file_paths[2]), 1)
        # Remove current file extension
        filename = file_paths[3].split('.')[0]
        # Concate new file extension
        post_filename = '%s.%s' % (filename, file_extension)
    else:
        created_at = datetime.datetime.now()
        post_filename = '%s_%s.%s' % (pre_filename, created_at.strftime('%s'), file_extension)
    return '%d/%d/%s' % (created_at.year, created_at.month, post_filename)
