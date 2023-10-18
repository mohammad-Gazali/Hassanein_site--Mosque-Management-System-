from django import template

register = template.Library()


@register.filter("quarter")
def quarter(str):
    return int(str.split(" ")[1]) % 2 == 0


@register.filter("part_format")
def part_format(str):
    return str.split()[1]


@register.filter("mylist")
def mylist(val1, val2):
    return [val1, val2]


@register.filter("money_deleting_remove_points")
def money_deleting_remove_points(values: list[int], point_value: int) -> int:
    money_points = values[1] / point_value
    return int(money_points + values[0])


@register.filter("list_of_tests_ids")
def list_of_tests_ids(queryset):
    result = [i.id for i in queryset]
    return result


@register.filter("list_of_tests_ids_from_relations")
def list_of_tests_ids_from_relations(queryset):
    result = [i.test_id for i in queryset]
    return result


@register.filter("is_new_relation")
def is_new_relation(mylist, relations):
    relations_list = list(relations)
    relations_list = list(
        filter(
            lambda x: x["test_id"] == mylist[0] and x["student_id"] == mylist[1],
            relations_list,
        )
    )
    if relations_list:
        return not relations_list[0]["is_old"]
    else:
        return False


@register.filter()
def all_points_handling(values: list[int], point_value: int) -> int:
    money_points = values[1] / point_value
    return int(values[0] - money_points)
