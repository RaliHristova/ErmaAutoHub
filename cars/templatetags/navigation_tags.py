from django import template


register = template.Library()


@register.simple_tag
def nav_match(current_url, route_names):
    if not current_url:
        return False

    valid_names = [name.strip() for name in route_names.split(',') if name.strip()]
    return current_url in valid_names
