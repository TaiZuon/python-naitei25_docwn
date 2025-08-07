from django import template
from django.core.paginator import Page

register = template.Library()

@register.inclusion_tag('admin/includes/pagination_range.html', takes_context=True)
def pagination_with_range(context, page_obj, page_range=3):
    """
    Template tag to render pagination with a configurable page range.
    
    Usage:
    {% load admin_pagination_tags %}
    {% pagination_with_range page_obj %}
    """
    from constants import PAGINATION_PAGE_RANGE
    
    if not hasattr(page_obj, 'number'):
        return {'show_pagination': False}
    
    # Use the constant if page_range not provided
    if page_range == 3:  # default value
        page_range = PAGINATION_PAGE_RANGE
    
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    
    # Calculate start and end page numbers
    start_page = max(1, current_page - page_range)
    end_page = min(total_pages, current_page + page_range)
    
    # Adjust start_page if we're near the end
    if end_page - start_page < 2 * page_range:
        start_page = max(1, end_page - 2 * page_range)
    
    # Adjust end_page if we're near the beginning  
    if end_page - start_page < 2 * page_range:
        end_page = min(total_pages, start_page + 2 * page_range)
    
    page_numbers = list(range(start_page, end_page + 1))
    
    # Add ellipsis logic
    show_first_ellipsis = start_page > 2
    show_last_ellipsis = end_page < total_pages - 1
    show_first_page = start_page > 1
    show_last_page = end_page < total_pages
    
    template_context = {
        'page_obj': page_obj,
        'page_numbers': page_numbers,
        'show_first_page': show_first_page,
        'show_last_page': show_last_page,
        'show_first_ellipsis': show_first_ellipsis,
        'show_last_ellipsis': show_last_ellipsis,
        'show_pagination': total_pages > 1,
        'request': context.get('request'),  # Pass request from context
    }
    
    return template_context

@register.simple_tag
def url_replace(request, field, value):
    """
    Replace a GET parameter in the current URL.
    
    Usage:
    {% url_replace request 'page' 2 %}
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
