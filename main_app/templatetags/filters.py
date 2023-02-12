from django import template

register = template.Library()


@register.filter('quarter')
def quarter(str):
    return int(str.split(' ')[1]) % 2 == 0
