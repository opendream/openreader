from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag()
def site_title():
    return settings.SITE_TITLE

@register.simple_tag()
def render_pending_time_options():
    tags = []
    for hour in range(24):
        if len(str(hour)) == 1:
            hour = '0%s' % hour
        tags.append('<option value="%s:00">%s:00</option>' % (hour, hour))
        tags.append('<option value="%s:30">%s:30</option>' % (hour, hour))
    return ''.join(tags)
