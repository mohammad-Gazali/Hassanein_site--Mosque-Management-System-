from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.db.models import Prefetch, Sum, Q
from main_app.models import (
    MemorizeNotes,
    Student,
    Category,
    MemorizeMessage,
    Coming,
    ControlSettings,
    DoublePointMessage,
    Master,
    PointsAddingCause,
    PointsDeletingCause,
    PointsAdding,
    PointsDeleting,
    MoneyDeleting,
    MoneyDeletingCause,
    ComingCategory,
    AwqafTestNoQ,
    AwqafNoQStudentRelation,
)
from main_app.forms import SettingForm
from main_app.point_map import apply_q_map, q_map
from specializations.models import Part, SpecializationMessage, Specialization, Level
from specializations.views import apply_edit_changes
from datetime import datetime, date
import pytz
import math
import json
import re


def index(request):
    control_settings = ControlSettings.objects.get(pk=1)

    ramadan = False

    if control_settings.double_points:
        ramadan = True

    return render(request, "index.html", {"ramadan": ramadan})


def search_results_of_student(request):

    query_text = request.GET.get("q_text")
    query_id = request.GET.get("q_search_id")

    specializations = Specialization.objects.prefetch_related(
        "level_set__part_set"
    ).all()
    levels = Level.objects.all()
    all_tests = AwqafTestNoQ.objects.all()
    all_relations = AwqafNoQStudentRelation.objects.all().values(
        "test_id", "student_id", "is_old"
    )

    if query_id:
        student = Student.objects.filter(pk=query_id)
        return render(
            request,
            "search_results.html",
            {
                "one_student": student,
                "students": None,
                "text": False,
                "specializations": specializations,
                "levels": levels,
                "all_tests": all_tests,
                "all_relations": all_relations,
            },
        )

    if query_text:
        my_regex = r""
        for word in re.split(r"\s+", query_text.strip()):
            my_regex += word + r".*"

        students = (
            Student.objects.prefetch_related(
                "memorizenotes_set",
                "part_set__level__specialization",
                "awqafnoqstudentrelation_set",
            )
            .select_related("category")
            .filter(name__iregex=r"{}".format(my_regex))
            .order_by("id")
        )

        return render(
            request,
            "search_results.html",
            {
                "students": students,
                "one_student": None,
                "text": True,
                "specializations": specializations,
                "levels": levels,
                "all_tests": all_tests,
                "all_relations": all_relations,
            },
        )


@login_required
def before_logout(request):
    return render(request, "before_logout.html")


@login_required
def add_q_memorize(request, sid):
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        student = Student.objects.get(pk=sid)
        q_memo_before_edit = student.q_memorizing
        form = list(request.POST.items())
        single_page = form[1][1]
        start_page = form[2][1]
        end_page = form[3][1]
        q_names = []
        if len(form) >= 6:
            for i in form[5:]:
                q_names.append(i[0])

        # Errors handling section start

        if single_page:
            if (
                q_memo_before_edit[single_page] == "NEW"
                or q_memo_before_edit[single_page] == "OLD"
            ):
                return render(
                    request,
                    "error_page.html",
                    {
                        "error": "يوجد تكرار في التسميع, الرجاء مراجعة تفاصيل الطالب",
                        "sid": sid,
                    },
                )

        for name in q_names:
            if q_memo_before_edit[name] == "NEW" or q_memo_before_edit[name] == "OLD":
                return render(
                    request,
                    "error_page.html",
                    {
                        "error": "يوجد تكرار في التسميع, الرجاء مراجعة تفاصيل الطالب",
                        "sid": sid,
                    },
                )

        if start_page and end_page:
            for i in range(int(start_page), int(end_page) + 1):
                if (
                    q_memo_before_edit[str(i)] == "NEW"
                    or q_memo_before_edit[str(i)] == "OLD"
                ):
                    return render(
                        request,
                        "error_page.html",
                        {
                            "error": "يوجد تكرار في التسميع, الرجاء مراجعة تفاصيل الطالب",
                            "sid": sid,
                        },
                    )

        # Errors handling section end

        q_memo_before_edit = {}
        total_list = []
        if not single_page and q_names:
            total_list = [*q_names]

        elif single_page and not q_names:
            total_list = [single_page]

        elif not single_page and not q_names:
            total_list = []

        else:
            total_list = [*q_names] + [single_page]

        if start_page and end_page:
            total_list += [str(i) for i in range(int(start_page), int(end_page) + 1)]

        for j in total_list:
            q_memo_before_edit[j] = "NON"

        total_list = list(set(total_list))

        q_memo_after_edit = {i: "NEW" for i in q_memo_before_edit}

        master_pers = []
        for i in master.permissions["q_memo"]:
            if master.permissions["q_memo"][i] != "NON":
                master_pers.append(i)

        for item in q_memo_after_edit:
            if len(item) < 3 and item != "عبس":
                if give_section_from_page(int(item)) not in master_pers:
                    return HttpResponseForbidden(
                        "<h1>ليس هذا التسميع من صلاحياتك</h1><h1>403<h1/>"
                    )
            else:
                if "30" not in master_pers:
                    return HttpResponseForbidden(
                        "<h1>ليس هذا التسميع من صلاحياتك</h1><h1>403<h1/>"
                    )

        student.q_memorizing.update(q_memo_after_edit)
        student.save()

        new_message = MemorizeMessage.objects.create(
            master_name=master,
            student_id=student.id,
            student_string=student,
            first_info=q_memo_after_edit,
            second_info=q_memo_before_edit,
        )

        control_settings = ControlSettings.objects.get(pk=1)

        if control_settings.double_points:
            DoublePointMessage.objects.create(
                student_id=student.id,
                content=total_list,
                points=apply_q_map(total_list),
                memorize_message_id=new_message.id,
            )

        return redirect(request.META.get("HTTP_REFERER"))

    else:

        return redirect("home")


@login_required
def add_q_test(request):
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        sid = request.POST.get("student-id")
        test_type = request.POST.get("q-test-type-filter")
        test_type_normal = request.POST.get("add-q-test-filter")

        # part_number_normal = رقم الحزب في السبر العادي
        part_number_normal = request.POST.get("q-part-number")

        # quarter_q_part_number = رقم ربع الحزب
        quarter_q_part_number = request.POST.get("quarter-q-part-number")

        # half_q_part_number = رقم نصف الحزب
        half_q_part_number = request.POST.get("half-q-part-number")

        student = Student.objects.get(pk=int(sid))

        if test_type == "normal-test":

            if (
                master.permissions["q_test"][
                    str(math.ceil(int(part_number_normal) / 2))
                ]
                == "NON"
            ):
                return HttpResponseForbidden(
                    "<h1>هذا السبر ليس من صلاحياتك</h1><h1>403</h1>"
                )

            normal_test = student.q_test

            # section <==> الجزء
            number_of_section = math.ceil(int(part_number_normal) / 2)

            # part <==> الحزب
            part = normal_test[f"الجزء {number_of_section}"][
                f"الحزب {part_number_normal}"
            ]

            if test_type_normal == "qurater-part":

                if quarter_q_part_number == "first-quarter":
                    val = part["الربع 1"]
                    if val == "OLD" or val == "NEW":
                        return render(
                            request,
                            "error_page.html",
                            {
                                "error": "يوجد تكرار في السبر, الرجاء مراجعة تفاصيل الطالب",
                                "sid": sid,
                            },
                        )

                    student.q_test[f"الجزء {number_of_section}"][
                        f"الحزب {part_number_normal}"
                    ].update({"الربع 1": "NEW"})
                    student.save()

                    q_test_normal_detail = {
                        "type": "quarter",
                        "section": f"الجزء {number_of_section}",
                        "part": f"الحزب {part_number_normal}",
                        "quarter": "الربع 1",
                    }
                    q_test_normal_show = {
                        "content": f"الربع الأول من الحزب {part_number_normal}"
                    }

                    new_message = MemorizeMessage.objects.create(
                        master_name=master,
                        student_id=student.id,
                        student_string=student,
                        first_info=q_test_normal_show,
                        second_info=q_test_normal_detail,
                        message_type=2,
                    )

                    control_settings = ControlSettings.objects.get(pk=1)

                    if control_settings.double_points:
                        DoublePointMessage.objects.create(
                            student_id=student.id,
                            content=q_test_normal_show,
                            points=13,
                            memorize_message_id=new_message.id,
                            message_type=2,
                        )

                elif quarter_q_part_number == "second-quarter":
                    val = part["الربع 2"]
                    if val == "OLD" or val == "NEW":
                        return render(
                            request,
                            "error_page.html",
                            {
                                "error": "يوجد تكرار في السبر, الرجاء مراجعة تفاصيل الطالب",
                                "sid": sid,
                            },
                        )

                    student.q_test[f"الجزء {number_of_section}"][
                        f"الحزب {part_number_normal}"
                    ].update({"الربع 2": "NEW"})
                    student.save()

                    q_test_normal_detail = {
                        "type": "quarter",
                        "section": f"الجزء {number_of_section}",
                        "part": f"الحزب {part_number_normal}",
                        "quarter": "الربع 2",
                    }
                    q_test_normal_show = {
                        "content": f"الربع الثاني من الحزب {part_number_normal}"
                    }

                    new_message = MemorizeMessage.objects.create(
                        master_name=master,
                        student_id=student.id,
                        student_string=student,
                        first_info=q_test_normal_show,
                        second_info=q_test_normal_detail,
                        message_type=2,
                    )

                    control_settings = ControlSettings.objects.get(pk=1)

                    if control_settings.double_points:
                        DoublePointMessage.objects.create(
                            student_id=student.id,
                            content=q_test_normal_show,
                            points=13,
                            memorize_message_id=new_message.id,
                            message_type=2,
                        )

                elif quarter_q_part_number == "third-quarter":
                    val = part["الربع 3"]
                    if val == "OLD" or val == "NEW":
                        return render(
                            request,
                            "error_page.html",
                            {
                                "error": "يوجد تكرار في السبر, الرجاء مراجعة تفاصيل الطالب",
                                "sid": sid,
                            },
                        )

                    student.q_test[f"الجزء {number_of_section}"][
                        f"الحزب {part_number_normal}"
                    ].update({"الربع 3": "NEW"})
                    student.save()

                    q_test_normal_detail = {
                        "type": "quarter",
                        "section": f"الجزء {number_of_section}",
                        "part": f"الحزب {part_number_normal}",
                        "quarter": "الربع 3",
                    }
                    q_test_normal_show = {
                        "content": f"الربع الثالث من الحزب {part_number_normal}"
                    }

                    new_message = MemorizeMessage.objects.create(
                        master_name=master,
                        student_id=student.id,
                        student_string=student,
                        first_info=q_test_normal_show,
                        second_info=q_test_normal_detail,
                        message_type=2,
                    )

                    control_settings = ControlSettings.objects.get(pk=1)

                    if control_settings.double_points:
                        DoublePointMessage.objects.create(
                            student_id=student.id,
                            content=q_test_normal_show,
                            points=13,
                            memorize_message_id=new_message.id,
                            message_type=2,
                        )

                elif quarter_q_part_number == "fourth-quarter":
                    val = part["الربع 4"]
                    if val == "OLD" or val == "NEW":
                        return render(
                            request,
                            "error_page.html",
                            {
                                "error": "يوجد تكرار في السبر, الرجاء مراجعة تفاصيل الطالب",
                                "sid": sid,
                            },
                        )

                    student.q_test[f"الجزء {number_of_section}"][
                        f"الحزب {part_number_normal}"
                    ].update({"الربع 4": "NEW"})
                    student.save()

                    q_test_normal_detail = {
                        "type": "quarter",
                        "section": f"الجزء {number_of_section}",
                        "part": f"الحزب {part_number_normal}",
                        "quarter": "الربع 4",
                    }
                    q_test_normal_show = {
                        "content": f"الربع الرابع من الحزب {part_number_normal}"
                    }

                    new_message = MemorizeMessage.objects.create(
                        master_name=master,
                        student_id=student.id,
                        student_string=student,
                        first_info=q_test_normal_show,
                        second_info=q_test_normal_detail,
                        message_type=2,
                    )

                    control_settings = ControlSettings.objects.get(pk=1)

                    if control_settings.double_points:
                        DoublePointMessage.objects.create(
                            student_id=student.id,
                            content=q_test_normal_show,
                            points=13,
                            memorize_message_id=new_message.id,
                            message_type=2,
                        )

                else:
                    return render(
                        request,
                        "error_page.html",
                        {"error": "يوجد خطأ في الإرسال", "sid": sid},
                    )

            elif test_type_normal == "half-part":
                if half_q_part_number == "first-half":
                    val = part["الربع 1"], part["الربع 2"]
                    if (
                        val[0] == "NEW"
                        or val[1] == "NEW"
                        or val[0] == "OLD"
                        or val[1] == "OLD"
                    ):
                        return render(
                            request,
                            "error_page.html",
                            {
                                "error": "يوجد تكرار في السبر, الرجاء مراجعة تفاصيل الطالب",
                                "sid": sid,
                            },
                        )

                    student.q_test[f"الجزء {number_of_section}"][
                        f"الحزب {part_number_normal}"
                    ].update({"الربع 1": "NEW", "الربع 2": "NEW"})
                    student.save()

                    q_test_normal_detail = {
                        "type": "half",
                        "section": f"الجزء {number_of_section}",
                        "part": f"الحزب {part_number_normal}",
                        "half": "النصف الأول",
                    }
                    q_test_normal_show = {
                        "content": f"النصف الأول من الحزب {part_number_normal}"
                    }

                    new_message = MemorizeMessage.objects.create(
                        master_name=master,
                        student_id=student.id,
                        student_string=student,
                        first_info=q_test_normal_show,
                        second_info=q_test_normal_detail,
                        message_type=2,
                    )

                    control_settings = ControlSettings.objects.get(pk=1)

                    if control_settings.double_points:
                        DoublePointMessage.objects.create(
                            student_id=student.id,
                            content=q_test_normal_show,
                            points=26,
                            memorize_message_id=new_message.id,
                            message_type=2,
                        )

                elif half_q_part_number == "second-half":
                    val = part["الربع 3"], part["الربع 4"]
                    if (
                        val[0] == "NEW"
                        or val[1] == "NEW"
                        or val[0] == "OLD"
                        or val[1] == "OLD"
                    ):
                        return render(
                            request,
                            "error_page.html",
                            {
                                "error": "يوجد تكرار في السبر, الرجاء مراجعة تفاصيل الطالب",
                                "sid": sid,
                            },
                        )

                    student.q_test[f"الجزء {number_of_section}"][
                        f"الحزب {part_number_normal}"
                    ].update({"الربع 3": "NEW", "الربع 4": "NEW"})
                    student.save()

                    q_test_normal_detail = {
                        "type": "half",
                        "section": f"الجزء {number_of_section}",
                        "part": f"الحزب {part_number_normal}",
                        "half": "النصف الثاني",
                    }
                    q_test_normal_show = {
                        "content": f"النصف الثاني من الحزب {part_number_normal}"
                    }

                    new_message = MemorizeMessage.objects.create(
                        master_name=master,
                        student_id=student.id,
                        student_string=student,
                        first_info=q_test_normal_show,
                        second_info=q_test_normal_detail,
                        message_type=2,
                    )

                    control_settings = ControlSettings.objects.get(pk=1)

                    if control_settings.double_points:
                        DoublePointMessage.objects.create(
                            student_id=student.id,
                            content=q_test_normal_show,
                            points=26,
                            memorize_message_id=new_message.id,
                            message_type=2,
                        )

                else:
                    return render(
                        request,
                        "error_page.html",
                        {"error": "يوجد خطأ في الإرسال", "sid": sid},
                    )

            elif test_type_normal == "whole-part":
                q_test_normal_after_edit = {}
                for quart, val in part.items():
                    if val == "OLD" or val == "NEW":
                        return render(
                            request,
                            "error_page.html",
                            {
                                "error": "يوجد تكرار في السبر, الرجاء مراجعة تفاصيل الطالب",
                                "sid": sid,
                            },
                        )
                    q_test_normal_after_edit[quart] = "NEW"

                student.q_test[f"الجزء {number_of_section}"][
                    f"الحزب {part_number_normal}"
                ].update(q_test_normal_after_edit)
                student.save()

                q_test_normal_detail = {
                    "type": "whole",
                    "section": f"الجزء {number_of_section}",
                    "part": f"الحزب {part_number_normal}",
                }

                new_message = MemorizeMessage.objects.create(
                    master_name=master,
                    student_id=student.id,
                    student_string=student,
                    first_info=q_test_normal_after_edit,
                    second_info=q_test_normal_detail,
                    message_type=2,
                )

                control_settings = ControlSettings.objects.get(pk=1)

                if control_settings.double_points:
                    DoublePointMessage.objects.create(
                        student_id=student.id,
                        content=q_test_normal_detail,
                        points=52,
                        memorize_message_id=new_message.id,
                        message_type=2,
                    )

            else:
                return render(
                    request,
                    "error_page.html",
                    {"error": "يوجد خطأ في الإرسال", "sid": sid},
                )

        else:
            return render(
                request, "error_page.html", {"error": "يوجد خطأ في الإرسال", "sid": sid}
            )

        return redirect(request.META.get("HTTP_REFERER"))

    else:
        return redirect("home")


class MessagesList(LoginRequiredMixin, ListView):
    model = MemorizeMessage
    template_name = "master_activity.html"

    def get_queryset(self):
        query_set = super().get_queryset()
        master = Master.objects.get(user=self.request.user)
        return (
            query_set.select_related("student", "doublepointmessage")
            .filter(master_name=master)
            .order_by("-sended_at")
        )


class MessageDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MemorizeMessage
    template_name = "master_activity_delete.html"

    def test_func(self):
        master = Master.objects.get(user=self.request.user)
        return self.get_object().master_name == master

    def get_success_url(self):

        if self.get_object().message_type == 1:
            q_memo = self.get_object().second_info
            student = self.get_object().student
            student.q_memorizing.update(q_memo)
            student.save()

        elif self.get_object().message_type == 2:
            q_memo = self.get_object().second_info
            student = self.get_object().student
            if q_memo["type"] == "whole":
                for k in student.q_test[q_memo["section"]][q_memo["part"]]:
                    student.q_test[q_memo["section"]][q_memo["part"]][k] = "NON"
                student.save()

            elif q_memo["type"] == "half":

                if q_memo["half"] == "النصف الأول":
                    student.q_test[q_memo["section"]][q_memo["part"]]["الربع 1"] = "NON"
                    student.q_test[q_memo["section"]][q_memo["part"]]["الربع 2"] = "NON"
                    student.save()

                else:
                    student.q_test[q_memo["section"]][q_memo["part"]]["الربع 3"] = "NON"
                    student.q_test[q_memo["section"]][q_memo["part"]]["الربع 4"] = "NON"
                    student.save()

            else:
                student.q_test[q_memo["section"]][q_memo["part"]][
                    q_memo["quarter"]
                ] = "NON"
                student.save()

        return reverse("master_activity")


@login_required
def create_memorizing_note(request):
    if request.method == "POST":
        form = list(request.POST.items())
        master = Master.objects.get(user=request.user)
        sid = int(form[1][1])
        content = form[2][1]

        student_name = Student.objects.get(pk=sid).name

        MemorizeNotes.objects.create(
            master_name=master,
            student_id=sid,
            content=content,
            student_string=student_name,
        )

        return redirect(request.META.get("HTTP_REFERER"))

    else:
        return redirect("home")


@login_required
def del_note(request, nid):

    memoize_note = MemorizeNotes.objects.get(pk=nid)
    memoize_note.delete()

    if request.META.get("HTTP_REFERER"):
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        return redirect("home")


# Coming class functions/classes


def check_coming(user):
    groups = map(lambda x: x.name, user.groups.all())
    return user.is_superuser or ("حضور" in groups)


@user_passes_test(check_coming)
@login_required
def search_coming(request):
    return render(request, "coming/search_coming.html")


@user_passes_test(check_coming)
@login_required
def search_results_of_student_coming(request):

    query_text = request.GET.get("q_text")
    query_id = request.GET.get("q_search_id")

    registered_today = Coming.objects.filter(registered_at__date=date.today())
    registered_today_ids = set(map(lambda x: x.student_id, registered_today))

    com_cats = ComingCategory.objects.all()

    if query_id:
        student = Student.objects.filter(pk=query_id)
        return render(
            request,
            "search_results_coming.html",
            {
                "one_student": student,
                "students": None,
                "text": False,
                "reg_today": registered_today_ids,
                "coming_categories": com_cats,
            },
        )

    if query_text:
        my_regex = r""
        for word in re.split(r"\s+", query_text.strip()):
            my_regex += word + r".*"

        students = (
            Student.objects.select_related("category")
            .filter(name__iregex=r"{}".format(my_regex))
            .order_by("id")
        )

        return render(
            request,
            "search_results_coming.html",
            {
                "students": students,
                "one_student": None,
                "text": True,
                "reg_today": registered_today_ids,
                "coming_categories": com_cats,
            },
        )


@user_passes_test(check_coming)
@login_required
def add_coming(request):
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        student_id = int(request.POST.get("student-id"))
        points = int(request.POST.get("points"))
        category_id = int(request.POST.get("coming-category"))
        note = request.POST.get("note-for-coming") or None

        Coming.objects.create(
            master_name=master,
            student_id=student_id,
            category_id=category_id,
            points=points,
            note=note if note is not None else "لا يوجد",
        )

        return redirect(request.META.get("HTTP_REFERER"))

    else:
        return redirect("home")


class ComingList(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = Coming
    template_name = "coming/coming_list.html"

    def get_queryset(self):
        query_set = super().get_queryset()
        master = Master.objects.get(user=self.request.user)
        return (
            query_set.select_related("student", "category")
            .filter(master_name=master)
            .order_by("-registered_at")
        )

    def test_func(self):
        return check_coming(self.request.user)


class ComingDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Coming
    template_name = "coming/coming_delete.html"
    success_url = reverse_lazy("list_coming")

    def test_func(self):
        master = Master.objects.get(user=self.request.user)
        return (self.get_object().master_name == master) and check_coming(
            self.request.user
        )


# admin control functions/classes


def check_admin(user):
    return user.is_superuser


@user_passes_test(check_admin)
@login_required
def admin_main(request):

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    students = Student.objects.select_related("category").all().order_by("id")

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            students = (
                Student.objects.select_related("category")
                .filter(name__iregex=r"{}".format(my_regex))
                .order_by("id")
            )
        else:
            students = (
                Student.objects.select_related("category")
                .filter(pk=int(q))
                .order_by("id")
            )

    return render(
        request, "control_panel/admin_main.html", {"students": students, "val": q}
    )


@user_passes_test(check_admin)
@login_required
def admin_points_information(request):
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    point_value = ControlSettings.objects.get(pk=1).point_value

    students = (
        Student.objects.prefetch_related(
            Prefetch(
                "doublepointmessage_set",
                queryset=DoublePointMessage.objects.filter(message_type=1),
                to_attr="message_type_1",  # * this is the name of the attribute we will use to access specific query in points_of_q_memo property method inside Student model
            ),
            Prefetch(
                "doublepointmessage_set",
                queryset=DoublePointMessage.objects.filter(message_type=2),
                to_attr="message_type_2",  # * this is the name of the attribute we will use to access specific query in points_of_q_test property method inside Student model
            ),
            Prefetch(
                "moneydeleting_set",
                queryset=MoneyDeleting.objects.filter(active_to_points=True),
                to_attr="money_deleting_info",
            ),
            "pointsdeleting_set",
            "pointsadding_set",
            "coming_set",
        )
        .all()
        .order_by("id")
    )

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            students = (
                Student.objects.prefetch_related(
                    Prefetch(
                        "doublepointmessage_set",
                        queryset=DoublePointMessage.objects.filter(message_type=1),
                        to_attr="message_type_1",
                    ),
                    Prefetch(
                        "doublepointmessage_set",
                        queryset=DoublePointMessage.objects.filter(message_type=2),
                        to_attr="message_type_2",
                    ),
                    Prefetch(
                        "moneydeleting_set",
                        queryset=MoneyDeleting.objects.filter(active_to_points=True),
                        to_attr="money_deleting_info",
                    ),
                    "pointsdeleting_set",
                    "pointsadding_set",
                    "coming_set",
                    "moneydeleting_set",
                )
                .filter(name__iregex=r"{}".format(my_regex))
                .order_by("id")
            )
        else:
            students = Student.objects.prefetch_related(
                Prefetch(
                    "doublepointmessage_set",
                    queryset=DoublePointMessage.objects.filter(message_type=1),
                    to_attr="message_type_1",
                ),
                Prefetch(
                    "doublepointmessage_set",
                    queryset=DoublePointMessage.objects.filter(message_type=2),
                    to_attr="message_type_2",
                ),
                Prefetch(
                    "moneydeleting_set",
                    queryset=MoneyDeleting.objects.filter(active_to_points=True),
                    to_attr="money_deleting_info",
                ),
                "pointsdeleting_set",
                "pointsadding_set",
                "coming_set",
                "moneydeleting_set",
            ).filter(pk=int(q))

    return render(
        request,
        "control_panel/admin_points_information.html",
        {"students": students, "val": q, "point_value": point_value},
    )


class AdminSettingsSiteView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = ControlSettings
    template_name = "control_panel/admin_settings.html"
    form_class = SettingForm
    success_url = reverse_lazy("admin_main")

    def test_func(self):
        return self.request.user.is_superuser


@user_passes_test(check_admin)
@login_required
def admin_awqaf(request):
    test_types = AwqafTestNoQ.objects.all()
    if request.method == "POST":
        student_id = int(request.POST.get("student-id"))
        test_type = request.POST.get("type")
        sections = request.POST.get("sections")

        filterd_sections = list(set(re.split(r"\s+", sections.strip())))

        list_of_sections = list(map(lambda x: "الجزء " + x, filterd_sections))

        student = Student.objects.get(pk=student_id)

        if test_type == "normal":
            new_sections = {s: "NEW" for s in list_of_sections}
            for section, value in student.q_awqaf_test.items():
                if value == "OLD":
                    new_sections[section] = "OLD"
                elif section in new_sections:
                    pass
                else:
                    new_sections[section] = value

            student.q_awqaf_test = new_sections
            student.save()

        elif test_type == "looking":
            new_sections = {s: "NEW" for s in list_of_sections}
            for section, value in student.q_awqaf_test_looking.items():
                if value == "OLD":
                    new_sections[section] = "OLD"
                elif section in new_sections:
                    pass
                else:
                    new_sections[section] = value

            student.q_awqaf_test_looking = new_sections
            student.save()

        else:
            new_sections = {s: "NEW" for s in list_of_sections}
            for section, value in student.q_awqaf_test_explaining.items():
                if value == "OLD":
                    new_sections[section] = "OLD"
                elif section in new_sections:
                    pass
                else:
                    new_sections[section] = value

            student.q_awqaf_test_explaining = new_sections
            student.save()

    return render(request, "awqaf_tests.html", {"test_types": test_types})


@user_passes_test(check_admin)
@login_required
def admin_awqaf_no_q(request):
    test_types = AwqafTestNoQ.objects.all()
    if request.method == "POST":
        student_id = int(request.POST.get("student-id"))
        test_id = int(request.POST.get("type"))

        if not AwqafNoQStudentRelation.objects.filter(
            student_id=student_id, test_id=test_id
        ):
            AwqafNoQStudentRelation.objects.create(
                student_id=student_id, test_id=test_id
            )

        else:
            return render(
                request, "error_page.html", {"error": "هذا السبر قد تم تسجيله مسبقاً"}
            )

    return render(request, "awqaf_tests.html", {"test_types": test_types})


@user_passes_test(check_admin)
@login_required
def admin_awqaf_table(request):

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    all_relations = AwqafNoQStudentRelation.objects.all().values(
        "test_id", "student_id", "is_old"
    )
    all_tests = AwqafTestNoQ.objects.all()
    students = (
        Student.objects.prefetch_related("awqafnoqstudentrelation_set")
        .exclude(awqafnoqstudentrelation__isnull=True)
        .order_by("id")
    )

    if request.method == "POST":

        relations = AwqafNoQStudentRelation.objects.select_related(
            "student", "test"
        ).filter(is_old=False, student__in=students)

        form_items = list(request.POST)[1:]

        list_ids = [
            {"test_id": int(i.split("-")[1]), "student_id": int(i.split("-")[3])}
            for i in form_items
        ]

        filter_query = Q()

        for item in list_ids:
            filter_query = filter_query | Q(**item)

        relations_from_form = AwqafNoQStudentRelation.objects.select_related(
            "student", "test"
        ).filter(filter_query)

        for relation in relations:
            if relation not in relations_from_form:
                relation.delete()
            else:
                list_ids.remove(
                    {"test_id": relation.test_id, "student_id": relation.student_id}
                )

        AwqafNoQStudentRelation.objects.bulk_create(
            [
                AwqafNoQStudentRelation(
                    test_id=item["test_id"], student_id=item["student_id"]
                )
                for item in list_ids
            ]
        )

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            students = (
                Student.objects.prefetch_related("awqafnoqstudentrelation_set")
                .exclude(awqafnoqstudentrelation__isnull=True)
                .filter(name__iregex=r"{}".format(my_regex))
                .order_by("id")
            )
        else:
            students = Student.objects.exclude(
                awqafnoqstudentrelation__isnull=True
            ).filter(pk=int(q))

    return render(
        request,
        "awqaf_tests_table.html",
        {
            "all_tests": all_tests,
            "students": students,
            "val": q,
            "all_relations": all_relations,
        },
    )


@user_passes_test(check_admin)
@login_required
def admin_activity_master(request):
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None
    messages = (
        MemorizeMessage.objects.select_related(
            "student", "master_name__user", "doublepointmessage"
        )
        .all()
        .order_by("-sended_at")
    )
    if (q is not None) and (search_type is not None):
        if search_type == "by-master":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            messages = (
                MemorizeMessage.objects.select_related(
                    "student", "master_name__user", "doublepointmessage"
                )
                .filter(master_name__user__username__iregex=r"{}".format(my_regex))
                .order_by("-sended_at")
            )
            return render(
                request,
                "control_panel/admin_master_activities.html",
                {"messages": messages, "val": q},
            )
        else:
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            messages = (
                MemorizeMessage.objects.select_related(
                    "student", "master_name__user", "doublepointmessage"
                )
                .filter(student_string__iregex=r"{}".format(my_regex))
                .order_by("-sended_at")
            )
            return render(
                request,
                "control_panel/admin_master_activities.html",
                {"messages": messages, "val": q},
            )
    return render(
        request,
        "control_panel/admin_master_activities.html",
        {"messages": messages, "val": ""},
    )


@user_passes_test(check_admin)
@login_required
def admin_coming_list(request):
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None
    coming_list = (
        Coming.objects.select_related("student", "master_name__user", "category")
        .all()
        .order_by("-registered_at")
    )
    if (q is not None) and (search_type is not None):
        if search_type == "by-master":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            coming_list = (
                Coming.objects.select_related(
                    "student", "master_name__user", "category"
                )
                .filter(master_name__user__username__iregex=r"{}".format(my_regex))
                .order_by("-registered_at")
            )
            return render(
                request,
                "control_panel/admin_coming_list.html",
                {"coming_list": coming_list, "val": q},
            )
        else:
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            coming_list = (
                Coming.objects.select_related(
                    "student", "master_name__user", "category"
                )
                .filter(student__name__iregex=r"{}".format(my_regex))
                .order_by("-registered_at")
            )
            return render(
                request,
                "control_panel/admin_coming_list.html",
                {"coming_list": coming_list, "val": q},
            )
    return render(
        request,
        "control_panel/admin_coming_list.html",
        {"coming_list": coming_list, "val": ""},
    )


class DeleteMessageAdminPanel(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = MemorizeMessage
    template_name = "master_activity_delete.html"

    def test_func(self):
        return check_admin(self.request.user)

    def get_success_url(self):

        if self.get_object().message_type == 1:
            q_memo = self.get_object().second_info
            student = self.get_object().student
            student.q_memorizing.update(q_memo)
            student.save()

        elif self.get_object().message_type == 2:
            q_memo = self.get_object().second_info
            student = self.get_object().student
            if q_memo["type"] == "whole":
                for k in student.q_test[q_memo["section"]][q_memo["part"]]:
                    student.q_test[q_memo["section"]][q_memo["part"]][k] = "NON"
                student.save()

            elif q_memo["type"] == "half":

                if q_memo["half"] == "النصف الأول":
                    student.q_test[q_memo["section"]][q_memo["part"]]["الربع 1"] = "NON"
                    student.q_test[q_memo["section"]][q_memo["part"]]["الربع 2"] = "NON"
                    student.save()

                else:
                    student.q_test[q_memo["section"]][q_memo["part"]]["الربع 3"] = "NON"
                    student.q_test[q_memo["section"]][q_memo["part"]]["الربع 4"] = "NON"
                    student.save()

            else:
                student.q_test[q_memo["section"]][q_memo["part"]][
                    q_memo["quarter"]
                ] = "NON"
                student.save()

        return reverse("admin_master_activities")


class DeleteComingAdminPanel(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Coming
    template_name = "coming/coming_delete.html"
    success_url = reverse_lazy("admin_coming_list")

    def test_func(self):
        return check_admin(self.request.user)


@user_passes_test(check_admin)
@login_required
def master_list_admin(request):
    q = request.GET.get("text-search-table") or None
    masters = Master.objects.select_related("user").all().order_by("id")
    if q is not None:
        my_regex = r""
        for word in re.split(r"\s+", q.strip()):
            my_regex += word + r".*"
        masters = (
            Master.objects.select_related("user")
            .filter(user__username__iregex=r"{}".format(my_regex))
            .order_by("id")
        )
    return render(
        request, "control_panel/admin_list_masters.html", {"masters": masters, "val": q}
    )


@user_passes_test(check_admin)
@login_required
def master_edit_permissions(request, mid):
    if request.method == "POST":
        master = Master.objects.get(pk=mid)
        update_dictionary = {"q_memo": {}, "q_test": {}}
        if len(list(request.POST)) > 1:
            checked_permissions = list(request.POST)[1:]

            for permission in checked_permissions:
                my_list = permission.split("_")
                my_type = my_list[0] + "_" + my_list[1]

                if len(my_list) == 4:
                    my_type = my_list[0] + "_" + my_list[1] + "_" + my_list[2]

                part_number = my_list[-1]
                update_dictionary[my_type][part_number] = "YES"

        for i in range(1, 31):
            if str(i) not in update_dictionary["q_memo"]:
                update_dictionary["q_memo"][str(i)] = "NON"
            if str(i) not in update_dictionary["q_test"]:
                update_dictionary["q_test"][str(i)] = "NON"

        master.permissions.update(update_dictionary)
        master.save()

        return redirect("admin_master_list")
    else:
        return HttpResponseNotAllowed("")


@user_passes_test(check_admin)
@login_required
def admin_editing_points_log(request):
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None
    delete_messages = (
        PointsDeleting.objects.select_related("student", "master_name__user", "cause")
        .all()
        .order_by("-created_at")
    )
    add_messages = (
        PointsAdding.objects.select_related("student", "master_name__user", "cause")
        .all()
        .order_by("-created_at")
    )
    if (q is not None) and (search_type is not None):
        if search_type == "by-master":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            delete_messages = (
                PointsDeleting.objects.select_related(
                    "student", "master_name__user", "cause"
                )
                .filter(master_name__user__username__iregex=r"{}".format(my_regex))
                .order_by("-created_at")
            )
            add_messages = (
                PointsAdding.objects.select_related(
                    "student", "master_name__user", "cause"
                )
                .filter(master_name__user__username__iregex=r"{}".format(my_regex))
                .order_by("-created_at")
            )
            return render(
                request,
                "control_panel/admin_editing_points_log.html",
                {"d_msgs": delete_messages, "a_msgs": add_messages, "val": q},
            )
        else:
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            delete_messages = (
                PointsDeleting.objects.select_related(
                    "student", "master_name__user", "cause"
                )
                .filter(student__name__iregex=r"{}".format(my_regex))
                .order_by("-created_at")
            )
            add_messages = (
                PointsAdding.objects.select_related(
                    "student", "master_name__user", "cause"
                )
                .filter(student__name__iregex=r"{}".format(my_regex))
                .order_by("-created_at")
            )
            return render(
                request,
                "control_panel/admin_editing_points_log.html",
                {"d_msgs": delete_messages, "a_msgs": add_messages, "val": q},
            )

    return render(
        request,
        "control_panel/admin_editing_points_log.html",
        {"d_msgs": delete_messages, "a_msgs": add_messages},
    )


@user_passes_test(check_admin)
@login_required
def admin_specializations(request):
    if request.method == "POST":
        edits = list(request.POST)[1:]

        apply_edit_changes(edits)

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    specializations = Specialization.objects.all()
    parts = (
        Part.objects.select_related("level__specialization")
        .prefetch_related("students")
        .all()
        .order_by("level__specialization", "level", "part_number")
    )
    students = Student.objects.exclude(part__isnull=True).order_by("id")

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            students = (
                Student.objects.exclude(part__isnull=True)
                .filter(name__iregex=r"{}".format(my_regex))
                .order_by("id")
            )
        else:
            students = (
                Student.objects.exclude(part__isnull=True)
                .filter(pk=int(q))
                .order_by("id")
            )

    messages = (
        SpecializationMessage.objects.select_related(
            "student", "master_name__user", "part__level__specialization"
        )
        .filter(student__in=students)
        .order_by("-created_at")
    )

    return render(
        request,
        "control_panel/admin_specializations.html",
        {
            "specializations": specializations,
            "parts": parts,
            "students": students,
            "messages": messages,
            "val": q,
        },
    )


@user_passes_test(check_admin)
@login_required
def admin_test_certificates(request):

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    # for updating certificates state for students
    for st in Student.objects.all():
        if st.q_test_certificate == "لا يوجد":
            st.is_q_test_certificate = False
        else:
            st.is_q_test_certificate = True
        st.save()

    students = Student.objects.filter(is_q_test_certificate=True).order_by("id")

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            students = Student.objects.filter(
                is_q_test_certificate=True, name__iregex=r"{}".format(my_regex)
            ).order_by("id")
        else:
            students = Student.objects.filter(
                is_q_test_certificate=True, pk=int(q)
            ).order_by("id")

    ordered_students_by_q_test_certificates = []
    for student in students:
        item = {}
        item["id"] = student.id
        item["name"] = student.name
        item["q_test_certificate"] = student.q_test_certificate
        item["length"] = len(student.q_test_certificate)

        ordered_students_by_q_test_certificates.append(item)

    ordered_students_by_q_test_certificates = sorted(
        ordered_students_by_q_test_certificates, key=lambda x: x["length"], reverse=True
    )

    return render(
        request,
        "control_panel/admin_test_certificates.html",
        {"students": ordered_students_by_q_test_certificates, "val": q},
    )


@user_passes_test(check_admin)
@login_required
def admin_info(request):
    students = Student.objects.all()

    number_of_pages = sum([s.number_of_q_memo for s in students])
    number_of_parts = sum([s.number_of_q_test for s in students])
    number_of_parts_awqaf_normal = sum(
        [s.number_of_parts_awqaf_normal_tests for s in students]
    )
    number_of_parts_awqaf_looking = sum(
        [s.number_of_parts_awqaf_looking_tests for s in students]
    )
    number_of_parts_awqaf_explaining = sum(
        [s.number_of_parts_awqaf_explaining_tests for s in students]
    )

    return render(
        request,
        "control_panel/admin_info.html",
        {
            "number_of_pages": int(number_of_pages),
            "number_of_parts": int(number_of_parts),
            "number_of_parts_awqaf_normal": number_of_parts_awqaf_normal,
            "number_of_parts_awqaf_looking": number_of_parts_awqaf_looking,
            "number_of_parts_awqaf_explaining": number_of_parts_awqaf_explaining,
        },
    )


# adding and deleting points
def check_editing_points(user):
    groups = map(lambda x: x.name, user.groups.all())
    return user.is_superuser or ("نقاط" in groups)


@user_passes_test(check_editing_points)
@login_required
def editing_points(request):
    if request.method == "GET":
        adding_causes = PointsAddingCause.objects.all()
        deleting_causes = PointsDeletingCause.objects.all()
        return render(
            request,
            "editing_points.html",
            {"adding_causes": adding_causes, "deleting_causes": deleting_causes},
        )

    elif request.method == "POST":
        master = Master.objects.get(user=request.user)
        sid = int(request.POST.get("student-id"))
        value = int(request.POST.get("value"))
        cid = int(request.POST.get("cause-id"))
        editing_type = request.POST.get("type")

        if editing_type == "add":
            PointsAdding.objects.create(
                master_name=master, cause_id=cid, student_id=sid, value=value
            )

            return render(
                request,
                "editing_points_result.html",
                {"content": "تمت عملية الإضافة بنجاح"},
            )

        else:
            PointsDeleting.objects.create(
                master_name=master, cause_id=cid, student_id=sid, value=value
            )

            return render(
                request,
                "editing_points_result.html",
                {"content": "تمت عملية الخصم بنجاح"},
            )

    else:
        return HttpResponseNotAllowed("")


@user_passes_test(check_editing_points)
@login_required
def editing_points_log(request):

    master = Master.objects.get(user=request.user)

    points_adding_msgs = (
        PointsAdding.objects.select_related("student", "cause")
        .filter(master_name=master)
        .order_by("-created_at")
    )
    points_deleting_msgs = (
        PointsDeleting.objects.select_related("student", "cause")
        .filter(master_name=master)
        .order_by("-created_at")
    )

    return render(
        request,
        "editing_points_log.html",
        {"adding_msgs": points_adding_msgs, "deleting_msgs": points_deleting_msgs},
    )


@user_passes_test(check_editing_points)
@login_required
def deleting_editing_points_add(request, aid):
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        edit_id = int(request.POST.get("id"))
        edit = PointsAdding.objects.get(pk=edit_id)
        if request.user.is_superuser or edit.master_name == master:
            edit.delete()
        return redirect("editing_points_log")
    return render(request, "editing_points_delete_add.html", {"id": aid})


@user_passes_test(check_editing_points)
@login_required
def deleting_editing_points_remove(request, rid):
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        edit_id = int(request.POST.get("id"))
        edit = PointsDeleting.objects.get(pk=edit_id)
        if request.user.is_superuser or edit.master_name == master:
            edit.delete()
        return redirect("editing_points_log")
    return render(request, "editing_points_delete_remove.html", {"id": rid})


@user_passes_test(check_admin)
@login_required
def deleting_editing_points_add_admin(request, aid):
    edit = PointsAdding.objects.get(pk=aid)
    edit.delete()
    return redirect("admin_editing_points_log")


@user_passes_test(check_admin)
@login_required
def deleting_editing_points_remove_admin(request, rid):
    edit = PointsDeleting.objects.get(pk=rid)
    edit.delete()
    return redirect("admin_editing_points_log")


@user_passes_test(check_admin)
@login_required
def students_reports(request):
    if request.method == "POST":
        sid = request.POST.get("student-id") or None
        reports_type = request.POST.get("type")
        start = request.POST.get("start").split("-")
        end = request.POST.get("end").split("-")

        start = datetime(
            year=int(start[0]), month=int(start[1]), day=int(start[2]), tzinfo=pytz.UTC
        )
        end = datetime(
            year=int(end[0]), month=int(end[1]), day=int(end[2]), tzinfo=pytz.UTC
        )
        if reports_type == "all":
            data = {}
            reports = []
            students = Student.objects.all()

            for student in students:
                data[student.id, student.name] = student.memorizemessage_set.filter(
                    sended_at__range=[start, end], message_type__in=[1, 2]
                )

            for personal_info, messages in data.items():
                sum_pages = 0
                for message in messages:
                    sum_pages += give_num_pages(message)
                reports.append([personal_info, sum_pages])

            reports.sort(key=lambda x: x[1], reverse=True)

            return render(
                request,
                "reports/reports_results.html",
                {
                    "reports": reports,
                    "start": request.POST.get("start"),
                    "end": request.POST.get("end"),
                    "one_report": False,
                },
            )

        else:
            result = {}
            student = Student.objects.get(pk=int(sid))
            result["student"] = student
            messages = student.memorizemessage_set.filter(
                sended_at__range=[start, end], message_type__in=[1, 2]
            )
            sum_pages = 0
            for message in messages:
                sum_pages += give_num_pages(message)
            result["sum_pages"] = sum_pages
            result["messages"] = messages

            return render(
                request,
                "reports/reports_results.html",
                {
                    "reports": result,
                    "start": request.POST.get("start"),
                    "end": request.POST.get("end"),
                    "one_report": True,
                },
            )

    else:
        return render(request, "reports/all_students_reports.html")


@user_passes_test(check_admin)
@login_required
def deleting_money(request):
    causes = MoneyDeletingCause.objects.all()
    students_categories = Category.objects.all()

    if request.method == "POST":
        student_id = int(request.POST.get("student-id"))
        cause_id = int(request.POST.get("cause"))
        deleting_type = request.POST.get("type")
        value_in_money = request.POST.get("value-in-money") or None
        value_in_points = request.POST.get("value-in-points") or None

        if deleting_type == "money":

            MoneyDeleting.objects.create(
                student_id=student_id,
                cause_id=cause_id,
                value=int(value_in_money),
            )

        else:

            MoneyDeleting.objects.create(
                student_id=student_id,
                cause_id=cause_id,
                value=int(value_in_points),
                is_money_main_value=False,
            )

    return render(
        request,
        "deleting_money.html",
        {"causes": causes, "students_categories": students_categories},
    )


@user_passes_test(check_admin)
@login_required
def deleting_money_category(request):
    causes = MoneyDeletingCause.objects.all()
    students_categories = Category.objects.all()

    if request.method == "POST":
        cause_id = int(request.POST.get("cause"))
        category_id = int(request.POST.get("category"))
        deleting_type = request.POST.get("type")
        value_in_money = request.POST.get("value-in-money") or None
        value_in_points = request.POST.get("value-in-points") or None

        students = Student.objects.filter(category_id=category_id)

        if deleting_type == "money":
            for student in students:
                MoneyDeleting.objects.create(
                    student_id=student.id,
                    cause_id=cause_id,
                    value=int(value_in_money),
                )

        else:
            for student in students:
                MoneyDeleting.objects.create(
                    student_id=student.id,
                    cause_id=cause_id,
                    value=int(value_in_points),
                    is_money_main_value=False,
                )

    return render(
        request,
        "deleting_money.html",
        {"causes": causes, "students_categories": students_categories},
    )


@user_passes_test(check_admin)
@login_required
def deleting_money_table(request):

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    point_value = ControlSettings.objects.get(pk=1).point_value

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            deletings = (
                MoneyDeleting.objects.select_related("student", "cause")
                .filter(student__name__iregex=r"{}".format(my_regex))
                .order_by("-created_at")
            )
        else:
            deletings = (
                MoneyDeleting.objects.select_related("student", "cause")
                .filter(student__id=int(q))
                .order_by("-created_at")
            )
    else:
        deletings = (
            MoneyDeleting.objects.select_related("student", "cause")
            .all()
            .order_by("-created_at")
        )

    return render(
        request,
        "deleting_money_table.html",
        {
            "deletings": deletings,
            "point_value": point_value,
            "val": q,
        },
    )


@user_passes_test(check_admin)
@login_required
def deleting_money_total_table(request):

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += word + r".*"
            data = (
                MoneyDeleting.objects.select_related("student", "cause")
                .filter(
                    active_to_points=True, student__name__iregex=r"{}".format(my_regex)
                )
                .values("student")
                .annotate(sum_money=Sum("value", filter=Q(is_money_main_value=True)))
                .annotate(sum_points=Sum("value", filter=Q(is_money_main_value=False)))
                .values("student__id", "student__name", "sum_money", "sum_points")
                .order_by("student__id")
            )
        else:
            data = (
                MoneyDeleting.objects.select_related("student", "cause")
                .filter(active_to_points=True, student__id=int(q))
                .values("student")
                .annotate(sum_money=Sum("value", filter=Q(is_money_main_value=True)))
                .annotate(sum_points=Sum("value", filter=Q(is_money_main_value=False)))
                .values("student__id", "student__name", "sum_money", "sum_points")
                .order_by("student__id")
            )

    else:
        data = (
            MoneyDeleting.objects.select_related("student", "cause")
            .filter(active_to_points=True)
            .values("student")
            .annotate(sum_money=Sum("value", filter=Q(is_money_main_value=True)))
            .annotate(sum_points=Sum("value", filter=Q(is_money_main_value=False)))
            .values("student__id", "student__name", "sum_money", "sum_points")
            .order_by("student__id")
        )

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    return render(request, "deleting_money_total_table.html", {"data": data, "val": q})


# ajax views


def students_ajax(request):
    if request.method == "POST":
        query = json.loads(request.body)["content"]
        if query is not None:
            my_regex = r""
            for word in re.split(r"\s+", query.strip()):
                my_regex += word + r".*"
            students = Student.objects.filter(
                name__iregex=r"{}".format(my_regex)
            ).order_by("id")
            response = []
            for student in students:
                response.append(
                    {
                        "id": student.id,
                        "name": student.name,
                    }
                )

            return JsonResponse({"students": response}, status=200)
    else:
        return HttpResponseNotAllowed("")


@user_passes_test(check_admin)
@login_required
def switch_deleting_active_to_points_state(request):
    if request.method == "POST":

        data = json.loads(request.body)["delete_id"] or None

        delete_id = int(data)

        delete_money = MoneyDeleting.objects.get(pk=delete_id)

        delete_money.active_to_points = not delete_money.active_to_points

        delete_money.save()

        return JsonResponse({"message": delete_money.active_to_points}, status=200)

    return HttpResponseNotAllowed("")


# helper functions


def give_section_from_page(page_num):
    if page_num % 21 == 0 and page_num != 21:
        return str(page_num / 21 + 1)
    return str(math.ceil(page_num / 21))


def give_num_pages(info):
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
