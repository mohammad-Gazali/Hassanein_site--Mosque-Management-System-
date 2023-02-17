from django import template

register = template.Library()


@register.filter('quarter')
def quarter(str):
    return int(str.split(' ')[1]) % 2 == 0


@register.filter('part_format')
def part_format(str):
    return str.split()[1]


@register.filter('money_deleting_remove_points')
def money_deleting_remove_points(values: list[int], point_value: int) -> int:
    money_points = values[1] / point_value
    return int(money_points + values[0])