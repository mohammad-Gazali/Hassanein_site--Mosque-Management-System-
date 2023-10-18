from django import template
from django.db.models import QuerySet
from specializations.models import StudentSpecializationPartRelation

register = template.Library()


@register.filter("get_relation")
def get_relation(relations: QuerySet[StudentSpecializationPartRelation], student_id: int) -> StudentSpecializationPartRelation:
    for relation in relations:
        if relation.student.id == student_id:
            return relation
    