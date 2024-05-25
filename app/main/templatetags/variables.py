from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def setvar(val=None):
    return val


@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    """
    usage example {{ your_dict|get_value_from_dict:your_key }}
    """
    if key:
        return dict_data.get(key)


@register.simple_tag
def get_env_val(val=None):
    """
    usage example {{ get_env_val|"DEBUG" }}
    """
    return settings.__getattr__(val)
