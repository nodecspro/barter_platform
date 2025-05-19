from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag
def get_current_page_params(request, **kwargs_to_remove):
    """
    Возвращает строку текущих GET-параметров, исключая указанные.
    Например, если URL /search/?q=test&page=2, и мы хотим сохранить q,
    но удалить page для ссылки пагинации.
    Использование: {% get_current_page_params request page='any_value' as current_params %}
    Затем: <a href="?page={{ new_page_num }}{{ current_params }}">
    """
    updated_params = request.GET.copy()
    params_to_remove = ["page"]  # Всегда удаляем 'page' для пагинации

    for param_name in params_to_remove:
        if param_name in updated_params:
            del updated_params[param_name]

    if updated_params:
        return f"&{updated_params.urlencode()}"
    return ""
