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
        return 'list-group-item-nothing'
    elif s == 'A':
        return 'list-group-item-success'
    elif s == 'M':
        return 'list-group-item-info'
    elif s == 'T':
        return 'list-group-item-warning'
    else:
        return 'error-not-a-valid-response'


@register.filter
@stringfilter
def msg_icon_class(value):
    if value == 'danger':
        return 'glyphicon glyphicon-exclamation-sign'
    elif value == 'warning':
        return value
    elif value == 'success':
        return 'glyphicon glyphicon-info-sign'
    elif value == 'info':
        return value
    elif value == 'debug':
        return value
    else:
        return value


