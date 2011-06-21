from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from membership.models import Profile


@login_required
def setting(request):
    if request.method == 'POST':
        if request.POST['membership_type'] == 'reader':
            membership_type = Profile.TYPE_READER
        elif request.POST['membership_type'] == 'publisher':
            membership_type = Profile.TYPE_PUBLISHER
        else:
            membership_type = Profile.TYPE_NONE
        profile = Profile.objects.get(user=request.user)
        if profile.membership_type != membership_type:
            profile.membership_type = membership_type
            profile.save()
        return redirect('dashboard')
    return render(request, 'membership/setting.html')
