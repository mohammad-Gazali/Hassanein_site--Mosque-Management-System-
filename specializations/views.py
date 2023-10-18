from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, JsonResponse
from specializations.models import Specialization, Subject, Part, SpecializationMessage, StudentSpecializationPartRelation
from specializations.check_functions import check_specializations
from main_app.models import Master
import json



@user_passes_test(check_specializations)
@login_required
def main_specialization(request: HttpRequest):
    specializations = Specialization.objects.all()
    if request.method == "POST":

        master = Master.objects.get(user=request.user)

        pid = int(request.POST.get("part"))
        sid = int(request.POST.get("student-id"))

        relation = StudentSpecializationPartRelation.objects.filter(
            student_id=sid,
            part_id=pid,
        )

        if relation:
            return render(
                request,
                "error_repeated_specialization.html",
                {"error": "إن هذا القسم قد تم إضافته بالفعل للطالب سابقاً"},
            )

        StudentSpecializationPartRelation.objects.create(
            student_id=sid,
            part_id=pid,
        )

        SpecializationMessage.objects.create(
            master=master,
            part_id=pid,
            student_id=sid,
        )

    return render(
        request,
        "main_specialization.html",
        {
            "specializations": specializations,
        },
    )



# ajax views
def subjects_ajax(request: HttpRequest):
    if request.method == "POST":

        sid = get_id_from_request(request, "sid")

        subjects = Specialization.objects.get(pk=sid).subject_set.all()

        result = []

        for subject in subjects:
            result.append({"id": subject.id, "name": subject.name})

        return JsonResponse({"result": result}, status=200)


def parts_ajax(request: HttpRequest):
    if request.method == "POST":

        lid = get_id_from_request(request, "lid")

        parts = Subject.objects.get(pk=lid).part_set.all()

        result = []

        for part in parts:
            result.append(
                {
                    "id": part.id,
                    "part_number": part.part_number,
                    "part_content": part.part_content,
                }
            )

        return JsonResponse({"result": result}, status=200)


# helper functions
def get_id_from_request(request: HttpRequest, key: str) -> int:
    return int(json.loads(request.body)[key])


def apply_edit_changes(edit: list[str]) -> None:
    existing_relations_ids = []
    for item in edit:
        part_id = int(item.split("_")[1])
        student_id = int(item.split("_")[3])

        relation, _ = StudentSpecializationPartRelation.objects.get_or_create(
            part_id=part_id,
            student_id=student_id,
        )

        existing_relations_ids.append(relation.id)
    
    StudentSpecializationPartRelation.objects.exclude(id__in=existing_relations_ids).exclude(is_old=True).delete()
