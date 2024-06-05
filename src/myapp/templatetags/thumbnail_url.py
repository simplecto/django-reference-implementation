from django import template

register = template.Library()

@register.simple_tag
def thumbnail(something):
    return something
