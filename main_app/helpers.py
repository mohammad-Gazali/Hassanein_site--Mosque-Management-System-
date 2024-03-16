from django.utils import timezone
from main_app.point_map import q_map
from typing import List, Literal
from collections.abc import MutableMapping
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
    elif info.message_type == 2:
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

    last_sat = today - timezone.timedelta(idx + 1)
    next_sat = last_sat + timezone.timedelta(7)
    return [last_sat, next_sat]


def get_last_sat_date_range_for_previous_week():
    [last_sat, next_sat] = get_last_sat_date_range()

    return [last_sat - timezone.timedelta(7), next_sat - timezone.timedelta(7)]


def check_q_memo_for_section(student, section: int) -> bool:
    values: List[Literal['NON', 'NEW', 'OLD']] = student.q_memorizing.values()
    converted_bool = list(map(lambda x: x != 'NON', values))

    if section == 1:
        return all(converted_bool[:21])

    if 1 < section <= 29:
        return all(converted_bool[(section - 1) * 20 + 1:section * 20 + 1])

    if section == 30:
        return all(converted_bool[581:])

    return False


# from stackoverflow
def _flatten(dictionary, parent_key='', separator='_'):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(_flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)

def check_q_test_for_student(student, section: int) -> bool:
    new_dict = {}
    for key, value in student.q_test.items():
        new_dict[int(key.split(" ")[-1])] = list(map(lambda x: x != 'NON', _flatten(value).values()))
    

    if any(new_dict[section]):
        return True
    else:
        for key, value in new_dict.items():
            if key != section and any(value) and not all(value):
                return False

        return True