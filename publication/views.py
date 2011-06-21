from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from publication.forms import PublisherForm
from publication.models import Publisher


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
            return render(request, 'publication/publisher_form.html', {'form': form})
    else:
        form = PublisherForm()
        context = {'form': form}
        return render(request, 'publication/publisher_form.html', context)

@login_required
def update_publisher(request, id):
    publisher = get_object_or_404(Publisher, id=id)
    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'publication/publisher_form.html', {'form': form})
        return redirect('publication-show-publisher', id=publisher.id)
    else: 
        form = PublisherForm(instance=publisher)
        context = {'form':form}
        return render(request, 'publication/publisher_form.html', context)

@login_required
def show_publisher(request, id):
    publisher = get_object_or_404(Publisher, id=id)
    return render(request, 'publication/publisher.html', {'publisher': publisher})

@login_required
def upload_publication(request):
    if request.method == 'POST':
        pass
    else:
        return render(request, 'publication/upload.html')
