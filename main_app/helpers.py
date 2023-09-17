from django.utils import timezone
from main_app.point_map import q_map
import math

def give_section_from_page(page_num: int) -> str:
    if page_num % 21 == 0 and page_num != 21:
        return str(int(page_num / 21 + 1))
    return str(math.ceil(page_num / 21))


def give_num_pages(info):
    """
    - param `info` has type of `MemorizeMessage`
    - `MemorizeMessage` exists in `./models.py`
    """
    data = info.second_info
    result = 0

    # q_memo
    if info.message_type == 1:
        for item in data:
            if len(item) <= 3 and item != "عبس":
                result += 1
            else:
                result += q_map[item] / 5

    # q_test
    else:
        if data["type"] == "quarter":
            result += 2.5
        elif data["type"] == "half":
            result += 5
        else:
            result += 10
            
    return result


def get_last_sat_date_range():
    today = timezone.datetime.today().date()

    # When day is saturday
    if today.weekday() == 5:
        next_sat = today + timezone.timedelta(7)
        return [today, next_sat]

    idx = (today.weekday() + 1) % 7

    last_sat = today - timezone.timedelta(idx+1)
    next_sat = last_sat + timezone.timedelta(7)
    return [last_sat, next_sat]