from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, JsonResponse
from .models import Specialization, Level, Part, SpecializationMessage
from main_app.models import Student, Master
import json



def check_specializations(user):
    groups = map(lambda x: x.name, user.groups.all())
    return user.is_superuser or ('اختصاصات' in groups)


@user_passes_test(check_specializations)
@login_required
def main_specialization(request: HttpRequest):
    specializations = Specialization.objects.all()
    if request.method == "POST":

        master = Master.objects.get(user=request.user)

        pid = int(request.POST.get('part'))
        sid = int(request.POST.get('student-id'))

        part = Part.objects.get(pk=pid)
        student = Student.objects.get(pk=sid)

        if student in part.students.all():
            return render(request, "error_repeated_specialization.html", {"error": "إن هذا القسم قد تم إضافته بالفعل للطالب سابقاً"})

        part.students.add(student)

        SpecializationMessage.objects.create(
            master_name=master,
            part_id=pid,
            student_id=sid,
        )

    return render(request, 'main_specialization.html', {
        "specializations": specializations,
    })



# ajax views

def levels_ajax(request: HttpRequest):
    if request.method == "POST":

        sid = get_id_from_request(request, 'sid')

        levels = Specialization.objects.get(pk=sid).level_set.all()

        result = []

        for level in levels:
            result.append({
                "id": level.id,
                "level_number": level.level_number
            })

        return JsonResponse({
            "result": result
        })


def parts_ajax(request: HttpRequest):
    if request.method == "POST":

        lid = get_id_from_request(request, 'lid')

        parts = Level.objects.get(pk=lid).part_set.all()

        result = []

        for part in parts:
            result.append({
                "id": part.id,
                "part_number": part.part_number,
                "part_start": part.part_start,
                "part_end": part.part_end,
            })

        return JsonResponse({
            "result": result
        })



# helper functions

def get_id_from_request(request: HttpRequest, key: str) -> int:
    return int(json.loads(request.body)[key])


def check_student_with_level(level: Level, student: Student) -> bool:
    for part in level.part_set.all():
        if student not in part.students.all():
            return False
        
    return True


def apply_edit_changes(edit: list[str]) -> None:
    parts = []
    data = []
    for item in edit:
        part_id = int(item.split("_")[1])
        student_id = int(item.split("_")[3])

        data.append((
            part_id, 
            student_id
        ))

        parts.append(part_id)


    parts_ids = list(set(parts))

    parts = Part.objects.filter(pk__in=parts_ids)

    for part in parts:
        students = []
        for value in data:
            if value[0] == part.id:
                students.append(value[1])
        part.students.set(students)