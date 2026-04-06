from django.utils.translation import gettext as _


def paginate_list(data, page: int = 1, page_size: int = 24) -> dict:
    """
    Нарізає список на сторінки.

    :param data: повний список елементів
    :param page: номер сторінки (починається з 1)
    :param page_size: кількість елементів на сторінку
    :return: dict з даними пагінації
    :raises ValueError: якщо page < 1
    """
    if page < 1:
        raise ValueError(_("Page number must be >= 1"))

    total_items = len(data)
    total_pages = (total_items + page_size - 1) // page_size

    if page > total_pages:
        paged_data = []
    else:
        start = (page - 1) * page_size
        end = start + page_size
        paged_data = data[start:end]

    return {
        "page": page,
        "page_size": page_size,
        "total": total_items,
        "total_pages": total_pages,
        "results": paged_data,
    }
