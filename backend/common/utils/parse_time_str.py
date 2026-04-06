from datetime import timedelta


def parse_time_str(time_str: str) -> timedelta:
    """Конвертує рядок 'HH:MM:SS' у timedelta"""
    h, m, s = map(int, time_str.split(":"))
    return timedelta(hours=h, minutes=m, seconds=s)
