from django import template

register = template.Library()

@register.filter('quarter')
def quarter(str):
    return str.split(' ')[0]






