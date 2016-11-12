from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def response(value):
    if value == '':
        return ''

    s = value[0].upper()
    if s == 'N':
        return ''
    elif s == 'A':
        return 'list-group-item-success'
    elif s == 'M':
        return 'list-group-item-info'
    elif s == 'T':
        return 'list-group-item-warning'

    return ''