from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def query_update(context, **kwargs):
    """
    Merge current request GET params with new ones.
    Usage:
      {% query_update low_page=3 %}
    Output:
      ?low_page=3&tx_page=2 (if tx_page already existed in URL)
    """
    request = context['request']
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value
    if params:
        return '?' + params.urlencode()
    return ''
