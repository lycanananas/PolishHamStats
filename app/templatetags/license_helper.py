from django import template
from django.template.defaultfilters import stringfilter
from app.models import License

register = template.Library()

@register.filter
@stringfilter
def license_slug(value):
    return value.replace("/", "-")

@register.filter
@stringfilter
def license_category(value):
    try:
        return License.CATEGORY_MAP[int(value)]
    except (ValueError, TypeError, KeyError):
        return License.CATEGORY_MAP[License.Category.INVALID]

@register.filter
@stringfilter
def license_type(value):
    try:
        return License.TYPE_MAP[int(value)]
    except (ValueError, TypeError, KeyError):
        return License.TYPE_MAP[License.Type.INVALID]