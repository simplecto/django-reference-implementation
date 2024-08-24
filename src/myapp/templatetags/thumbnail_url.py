from django import template

register = template.Library()


@register.simple_tag
def thumbnail(something):  # noqa: ANN201, ANN001, D103
    return something
