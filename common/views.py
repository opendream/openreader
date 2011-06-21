from django.shortcuts import render


def index(request):
    return render(request, 'common/index.html')

def dashboard(request):
    return render(request, 'common/dashboard.html')

def setting(request):
    return render(request, 'common/setting.html')
