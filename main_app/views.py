from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse
from django.db.models import Prefetch, Sum, Q
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from main_app.models import (
    MemorizeNotes,
    MessageTypeChoice,
    Student,
    Category,
    MemorizeMessage,
    Coming,
    ControlSettings,
    DoubleMessageTypeChoice,
    DoublePointMessage,
    Master,
    PointsAddingCause,
    PointsAdding,
    MoneyDeleting,
    MoneyDeletingCause,
    ComingCategory,
    AwqafTestNoQ,
    AwqafNoQStudentRelation,
    StudentGroup,
    AssetsCategory,
)
from main_app.forms import SettingForm, NewStudentForm
from main_app.point_map import apply_q_map
from main_app.check_functions import check_adding_hadeeth, check_admin, check_coming, check_adding_points, check_reports
from main_app.helpers import give_section_from_page, give_num_pages, get_last_sat_date_range, get_last_sat_date_range_for_previous_week, check_q_memo_for_section, check_q_test_for_student
from specializations.models import Part, SpecializationMessage, Specialization, StudentSpecializationPartRelation
from specializations.views import apply_edit_changes
from datetime import datetime, date
import pytz
import math
import json
import re


def index(request: HttpRequest) -> HttpResponse:
    control_settings = ControlSettings.objects.first()

    ramadan = control_settings.double_points

    title = control_settings.event_title

    return render(request, "index.html", {"ramadan": ramadan, "title": title})


def search_results_of_student(request: HttpRequest) -> HttpResponse:
    query_text = request.GET.get("q_text")
    query_id = request.GET.get("q_search_id")

    specializations = Specialization.objects.prefetch_related(
        Prefetch(
            "subject_set__part_set__studentspecializationpartrelation_set",
            queryset=StudentSpecializationPartRelation.objects.select_related("student")
        )
    ).all()
    all_tests = AwqafTestNoQ.objects.all()
    all_relations = AwqafNoQStudentRelation.objects.all().values("test_id", "student_id", "is_old")

    control_settings = ControlSettings.objects.first()

    last_comings_prefetch = Prefetch(
        "coming_set",
        queryset=Coming.objects.filter(category_id=settings.Q_COMING_CATEGORY_ID).order_by("-registered_at"),
        to_attr="last_comings",
    )

    previous_week_prefetch = Prefetch(
        "memorizemessage_set",
        queryset=MemorizeMessage.objects.filter(sended_at__range=get_last_sat_date_range_for_previous_week()),
        to_attr="previous_week_messages",
    )

    current_week_prefetch = Prefetch(
        "memorizemessage_set",
        queryset=MemorizeMessage.objects.filter(sended_at__range=get_last_sat_date_range()),
        to_attr="current_week_messages",
    )

    swap_between_two_halfs = False

    year = timezone.now().year
    month = timezone.now().month

    previous_month = month - 1 if month - 1 >= 1 else 12
    next_month = month + 1 if month + 1 <= 12 else 1
    year_for_previous_month = year if previous_month != 12 else year - 1
    year_for_next_month = year if next_month != 1 else year + 1

    first_half_prefetch = Prefetch(
        "memorizemessage_set",
        queryset=MemorizeMessage.objects.filter(sended_at__range=[
            timezone.datetime(year=year, month=month, day=1, tzinfo=pytz.UTC),
            timezone.datetime(year=year, month=month, day=16, tzinfo=pytz.UTC),
        ]),
        to_attr="first_month_half_messages",
    )
    
    second_half_prefetch = Prefetch(
        "memorizemessage_set",
        queryset=MemorizeMessage.objects.filter(sended_at__range=[
            timezone.datetime(year=year, month=month, day=16, tzinfo=pytz.UTC),
            timezone.datetime(year=year_for_next_month, month=next_month, day=1, tzinfo=pytz.UTC),
        ]),
        to_attr="second_month_half_messages",
    )

    if timezone.now().day <= 15:
        swap_between_two_halfs = True

        second_half_prefetch = Prefetch(
        "memorizemessage_set",
            queryset=MemorizeMessage.objects.filter(sended_at__range=[
                timezone.datetime(year=year_for_previous_month, month=previous_month, day=16, tzinfo=pytz.UTC),
                timezone.datetime(year=year, month=month, day=1, tzinfo=pytz.UTC),
            ]),
            to_attr="second_month_half_messages",
        )

    if query_id:
        # hiding hidden ids from non-authenticated users
        if request.user.is_authenticated:
            student = Student.objects.filter(pk=query_id).prefetch_related(
                last_comings_prefetch,
                previous_week_prefetch,
                current_week_prefetch,
                first_half_prefetch,
                second_half_prefetch,
            )
        else:
            student = Student.objects.filter(pk=query_id).exclude(pk__in=control_settings.hidden_ids).prefetch_related(
                last_comings_prefetch,
                previous_week_prefetch,
                current_week_prefetch,
                first_half_prefetch,
                second_half_prefetch,
            )

        return render(
            request,
            "search_results.html",
            {
                "one_student": student,
                "students": None,
                "text": False,
                "specializations": specializations,
                "all_tests": all_tests,
                "all_relations": all_relations,
                "swap_between_two_halfs": swap_between_two_halfs,
                "month": month,
                "previous_month": previous_month,
            },
        )

    if query_text:
        my_regex = ""

        for word in re.split(r"\s+", query_text.strip()):
            my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"

        if request.user.is_authenticated:
            students = (
                Student.objects.filter(name__iregex="{}".format(my_regex)).prefetch_related(
                    "memorizenotes_set",
                    "studentspecializationpartrelation_set__part",
                    "awqafnoqstudentrelation_set",
                    last_comings_prefetch,
                    previous_week_prefetch,
                    current_week_prefetch,
                    first_half_prefetch,
                    second_half_prefetch,
                )
                .select_related("category", "student_group")
                .order_by("id")
            )
        else:
            students = (
                Student.objects.filter(name__iregex="{}".format(my_regex))
                .exclude(pk__in=control_settings.hidden_ids)
                .prefetch_related(
                    "memorizenotes_set",
                    "studentspecializationpartrelation_set__part",
                    "awqafnoqstudentrelation_set",
                    last_comings_prefetch,
                    previous_week_prefetch,
                    current_week_prefetch,
                    first_half_prefetch,
                    second_half_prefetch,
                )
                .select_related("category", "student_group")
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
                "all_tests": all_tests,
                "all_relations": all_relations,
                "swap_between_two_halfs": swap_between_two_halfs,
                "month": month,
                "previous_month": previous_month,
            },
        )


@login_required
def before_logout(request: HttpRequest) -> HttpResponse:
    return render(request, "before_logout.html")


@login_required
def add_q_memorize(request: HttpRequest, sid: int) -> HttpResponse:
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        student = Student.objects.get(pk=sid)
        q_memo_before_edit = student.q_memorizing
        form = list(request.POST.items())
        single_page = form[1][1]
        start_page = form[2][1]
        end_page = form[3][1]
        q_names = []
        if len(form) >= 5:
            for i in form[4:]:
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
                        "student": student,
                    },
                )

        for name in q_names:
            if q_memo_before_edit[name] == "NEW" or q_memo_before_edit[name] == "OLD":
                return render(
                    request,
                    "error_page.html",
                    {
                        "error": "يوجد تكرار في التسميع, الرجاء مراجعة تفاصيل الطالب",
                        "student": student,
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
                            "student": student,
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
        for i, val in master.permissions["q_memo"].items():
            if val != "NON":
                master_pers.append(i)

        for item in q_memo_after_edit:
            if len(item) <= 3 and item != "عبس":
                if give_section_from_page(int(item)) not in master_pers:
                    return HttpResponseForbidden(
                        "<h1>ليس هذا التسميع من صلاحياتك</h1><h1>403<h1/>"
                    )
            else:
                if "30" not in master_pers:
                    return HttpResponseForbidden(
                        "<h1>ليس هذا التسميع من صلاحياتك</h1><h1>403<h1/>"
                    )

        if (not q_memo_before_edit) or (not q_memo_after_edit) or (not total_list):
            return redirect(request.META.get("HTTP_REFERER"))

        student.q_memorizing.update(q_memo_after_edit)
        student.save()

        new_message = MemorizeMessage.objects.create(
            master=master,
            student_id=student.id,
            student_string=student,
            first_info=q_memo_after_edit,
            second_info=q_memo_before_edit,
        )

        control_settings = ControlSettings.objects.first()

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
def add_q_test(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        sid = request.POST.get("student-id")
        test_type_normal = request.POST.get("add-q-test-filter")

        # part_number_normal = رقم الحزب في السبر العادي
        part_number_normal = request.POST.get("q-part-number")

        # quarter_q_part_number = رقم ربع الحزب
        quarter_q_part_number = request.POST.get("quarter-q-part-number")

        # half_q_part_number = رقم نصف الحزب
        half_q_part_number = request.POST.get("half-q-part-number")

        student = Student.objects.get(pk=int(sid))

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

        # checking the q_memo of the section before continue
        if not check_q_memo_for_section(student, number_of_section):
            return render(
                request,
                "error_page.html",
                {
                    "error": f"لا يمكن سبر أي قسم من الجزء {number_of_section} ما لم يتم تسميعه كاملاً",
                    "student": student,
                },
            )

        # checking the q_test of all sections is completed, for
        # example if section 20 is not completed then the student
        # can't q_test from any section (except for the non-completed but
        # start with it)
        if not check_q_test_for_student(student, number_of_section):
            return render(
                request,
                "error_page.html",
                {
                    "error": f"لا يمكن سبر أي قسم من الجزء {number_of_section}, ما لم يتم الانتهاء من الأجزاء الأخرى غير الكاملة بالسبر",
                    "student": student,
                },
            )

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
                            "student": student,
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
                    master=master,
                    student_id=student.id,
                    student_string=student,
                    first_info=q_test_normal_show,
                    second_info=q_test_normal_detail,
                    message_type=2,
                )

                control_settings = ControlSettings.objects.first()

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
                            "student": student,
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
                    master=master,
                    student_id=student.id,
                    student_string=student,
                    first_info=q_test_normal_show,
                    second_info=q_test_normal_detail,
                    message_type=2,
                )

                control_settings = ControlSettings.objects.first()

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
                            "student": student,
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
                    master=master,
                    student_id=student.id,
                    student_string=student,
                    first_info=q_test_normal_show,
                    second_info=q_test_normal_detail,
                    message_type=2,
                )

                control_settings = ControlSettings.objects.first()

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
                            "student": student,
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
                    master=master,
                    student_id=student.id,
                    student_string=student,
                    first_info=q_test_normal_show,
                    second_info=q_test_normal_detail,
                    message_type=2,
                )

                control_settings = ControlSettings.objects.first()

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
                            "student": student,
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
                    master=master,
                    student_id=student.id,
                    student_string=student,
                    first_info=q_test_normal_show,
                    second_info=q_test_normal_detail,
                    message_type=2,
                )

                control_settings = ControlSettings.objects.first()

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
                            "student": student,
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
                    master=master,
                    student_id=student.id,
                    student_string=student,
                    first_info=q_test_normal_show,
                    second_info=q_test_normal_detail,
                    message_type=2,
                )

                control_settings = ControlSettings.objects.first()

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
                            "student": student,
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
                master=master,
                student_id=student.id,
                student_string=student,
                first_info=q_test_normal_after_edit,
                second_info=q_test_normal_detail,
                message_type=2,
            )

            control_settings = ControlSettings.objects.first()

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
            .filter(master=master)
            .order_by("-sended_at")
        )


class MessageDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MemorizeMessage
    template_name = "master_activity_delete.html"

    def test_func(self):
        master = Master.objects.get(user=self.request.user)
        return self.get_object().master == master

    def get_success_url(self):

        if self.get_object().message_type == MessageTypeChoice.MEMO:
            q_memo = self.get_object().second_info
            student = self.get_object().student
            student.q_memorizing.update(q_memo)
            student.save()

        elif self.get_object().message_type == MessageTypeChoice.TEST:
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
                student.q_test[q_memo["section"]][q_memo["part"]][q_memo["quarter"]] = "NON"
                student.save()
        
        elif self.get_object().message_type == MessageTypeChoice.ALNAWAWIA:
            student = self.get_object().student
            student.alarbaein_alnawawia_old = self.get_object().second_info["old"]
            student.alarbaein_alnawawia_new = self.get_object().second_info["new"]
            student.save()

        elif self.get_object().message_type == MessageTypeChoice.ALSAALIHIN:
            student = self.get_object().student
            student.riad_alsaalihin_old = self.get_object().second_info["old"]
            student.riad_alsaalihin_new = self.get_object().second_info["new"]
            student.save()
    
        elif self.get_object().message_type == MessageTypeChoice.ALLAH_NAMES:
            student = self.get_object().student
            student.allah_names_new = False
            student.save()

        return reverse("master_activity")


@login_required
def create_memorizing_note(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = list(request.POST.items())
        master = Master.objects.get(user=request.user)
        sid = int(form[1][1])
        content = form[2][1]

        student_name = Student.objects.get(pk=sid).name

        MemorizeNotes.objects.create(
            master=master,
            student_id=sid,
            content=content,
            student_string=student_name,
        )

        return redirect(request.META.get("HTTP_REFERER"))

    else:
        return redirect("home")


@login_required
def del_note(request: HttpRequest, nid: int) -> HttpResponse:
    memoize_note = MemorizeNotes.objects.get(pk=nid)
    memoize_note.delete()

    if request.META.get("HTTP_REFERER"):
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        return redirect("home")



# Coming class functions/classes
@user_passes_test(check_coming)
@login_required
def search_coming(request: HttpRequest) -> HttpResponse:
    coming_categories = ComingCategory.objects.all()
    return render(request, "coming/search_coming.html", {"coming_categories": coming_categories})


@user_passes_test(check_coming)
@login_required
def search_results_of_student_coming(request: HttpRequest) -> HttpResponse:
    query_text = request.GET.get("q_text")
    query_id = request.GET.get("q_search_id")
    category_id = request.GET.get("category_id")

    registered_today = Coming.objects.filter(registered_at__date=date.today(), category_id=category_id)
    registered_today_ids = set(map(lambda x: x.student_id, registered_today))

    com_cats = ComingCategory.objects.all()

    if query_id:
        student = Student.objects.filter(pk=query_id).exclude(id__in=registered_today_ids)
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
            my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"

        students = (
            Student.objects.select_related("category")
            .filter(name__iregex=r"{}".format(my_regex))
            .exclude(id__in=registered_today_ids)
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
def add_coming(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        student_id = request.POST.get("student-id")
        category_id = request.POST.get("category-id")

        control_settings = ControlSettings.objects.first()

        coming_today = Coming.objects.filter(registered_at__date=date.today(), category_id=category_id, student_id=student_id)

        if coming_today:
            return HttpResponseForbidden("<h1>403</h1><h1>Forbidden</h1>")

        Coming.objects.create(
            master=master,
            student_id=student_id,
            category_id=category_id,
            is_doubled=control_settings.double_points,
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
            .filter(master=master)
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
        return (self.get_object().master == master) and check_coming(
            self.request.user
        )


# admin control functions/classes
@user_passes_test(check_admin)
@login_required
def admin_main(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    students = []

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
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
def admin_points_information(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    point_value = ControlSettings.objects.first().point_value

    students = []

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
            students = (
                Student.objects.prefetch_related(
                    Prefetch(
                        "doublepointmessage_set",
                        queryset=DoublePointMessage.objects.filter(message_type=1),
                        to_attr="message_type_1", # * this is the name of the attribute we will use to access specific query in points_of_q_memo property method inside Student model
                    ),
                    Prefetch(
                        "doublepointmessage_set",
                        queryset=DoublePointMessage.objects.filter(message_type=2),
                        to_attr="message_type_2", # * this is the name of the attribute we will use to access specific query in points_of_q_test property method inside Student model
                    ),
                    Prefetch(
                        "doublepointmessage_set",
                        queryset=DoublePointMessage.objects.filter(message_type=3),
                        to_attr="message_type_3",
                    ),
                    Prefetch(
                        "doublepointmessage_set",
                        queryset=DoublePointMessage.objects.filter(message_type=4),
                        to_attr="message_type_4",
                    ),
                    Prefetch(
                        "doublepointmessage_set",
                        queryset=DoublePointMessage.objects.filter(message_type=5),
                        to_attr="message_type_5",
                    ),
                    Prefetch(
                        "moneydeleting_set",
                        queryset=MoneyDeleting.objects.filter(active_to_points=True),
                        to_attr="money_deleting_info",
                    ),
                    Prefetch(
                        "studentspecializationpartrelation_set",
                        queryset=StudentSpecializationPartRelation.objects.filter(is_old=False).select_related("part"),
                        to_attr="parts_relation_info",
                    ),
                    Prefetch(
                        "awqafnoqstudentrelation_set",
                        queryset=AwqafNoQStudentRelation.objects.filter(is_old=False).select_related("test"),
                        to_attr="awqaf_no_q_info",
                    ),
                    "pointsadding_set",
                    "coming_set__category",
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
                    "doublepointmessage_set",
                    queryset=DoublePointMessage.objects.filter(message_type=3),
                    to_attr="message_type_3",
                ),
                Prefetch(
                    "doublepointmessage_set",
                    queryset=DoublePointMessage.objects.filter(message_type=4),
                    to_attr="message_type_4",
                ),
                Prefetch(
                    "doublepointmessage_set",
                    queryset=DoublePointMessage.objects.filter(message_type=5),
                    to_attr="message_type_5",
                ),
                Prefetch(
                    "moneydeleting_set",
                    queryset=MoneyDeleting.objects.filter(active_to_points=True),
                    to_attr="money_deleting_info",
                ),
                Prefetch(
                    "studentspecializationpartrelation_set",
                    queryset=StudentSpecializationPartRelation.objects.filter(is_old=False),
                    to_attr="parts_relation_info",
                ),
                Prefetch(
                    "awqafnoqstudentrelation_set",
                    queryset=AwqafNoQStudentRelation.objects.filter(is_old=False),
                    to_attr="awqaf_no_q_info",
                ),
                "pointsadding_set",
                "coming_set__category",
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
def admin_awqaf(request: HttpRequest) -> HttpResponse:
    test_types = AwqafTestNoQ.objects.all()
    if request.method == "POST":
        student_id = int(request.POST.get("student-id"))
        test_type = request.POST.get("type")
        sections = request.POST.get("sections")

        filterd_sections = list(set(re.split(r"\s+", sections.strip())))

        new_sections = {s: "NEW" for s in filterd_sections}

        student = Student.objects.get(pk=student_id)

        if test_type == "normal":
            for section, val in student.q_awqaf_test.items():
                if val == "OLD" and section in new_sections:
                    new_sections[section] = "OLD"
            student.q_awqaf_test.update(new_sections)
        elif test_type == "looking":
            for section, val in student.q_awqaf_test_looking.items():
                if val == "OLD" and section in new_sections:
                    new_sections[section] = "OLD"
            student.q_awqaf_test_looking.update(new_sections)
        else:
            for section, val in student.q_awqaf_test_explaining.items():
                if val == "OLD" and section in new_sections:
                    new_sections[section] = "OLD"
            student.q_awqaf_test_explaining.update(new_sections)

        student.save()

    return render(request, "awqaf_tests.html", {"test_types": test_types})


@user_passes_test(check_admin)
@login_required
def admin_awqaf_no_q(request: HttpRequest) -> HttpResponse:
    test_types = AwqafTestNoQ.objects.all()
    if request.method == "POST":
        student_id = int(request.POST.get("student-id"))
        test_id = int(request.POST.get("type"))

        student = get_object_or_404(Student, pk=student_id)

        if not AwqafNoQStudentRelation.objects.filter(
            student_id=student_id,
            test_id=test_id,
        ):
            AwqafNoQStudentRelation.objects.create(
                student_id=student_id,
                test_id=test_id,
            )

        else:
            return render(
                request, "error_page.html", {
                    "error": "هذا السبر قد تم تسجيله مسبقاً",
                    "student": student,
                },
            )

    return render(request, "awqaf_tests.html", {"test_types": test_types})


@user_passes_test(check_admin)
@login_required
def admin_awqaf_table(request: HttpRequest) -> HttpResponse:
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
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
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
def admin_activity_master(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None
    messages = (
        MemorizeMessage.objects.select_related(
            "student", "master__user", "doublepointmessage"
        )
        .filter(sended_at__date=date.today())
        .order_by("-sended_at")
    )
    if (q is not None) and (search_type is not None):
        if search_type == "by-master":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
            messages = (
                MemorizeMessage.objects.select_related(
                    "student", "master__user", "doublepointmessage"
                )
                .filter(master__user__username__iregex=r"{}".format(my_regex))
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
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
            messages = (
                MemorizeMessage.objects.select_related(
                    "student", "master__user", "doublepointmessage"
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
def admin_coming_list(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None
    coming_list = (
        Coming.objects.select_related("student", "master__user", "category")
        .filter(registered_at__date=date.today())
        .order_by("-registered_at")
    )
    if (q is not None) and (search_type is not None):
        if search_type == "by-master":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
            coming_list = (
                Coming.objects.select_related(
                    "student", "master__user", "category"
                )
                .filter(master__user__username__iregex=r"{}".format(my_regex))
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
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
            coming_list = (
                Coming.objects.select_related(
                    "student", "master__user", "category"
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

        if self.get_object().message_type == MessageTypeChoice.MEMO:
            q_memo = self.get_object().second_info
            student = self.get_object().student
            student.q_memorizing.update(q_memo)
            student.save()

        elif self.get_object().message_type == MessageTypeChoice.TEST:
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
                student.q_test[q_memo["section"]][q_memo["part"]][q_memo["quarter"]] = "NON"
                student.save()

        elif self.get_object().message_type == MessageTypeChoice.ALNAWAWIA:
            student = self.get_object().student
            student.alarbaein_alnawawia_old = self.get_object().second_info["old"]
            student.alarbaein_alnawawia_new = self.get_object().second_info["new"]
            student.save()

        elif self.get_object().message_type == MessageTypeChoice.ALSAALIHIN:
            student = self.get_object().student
            student.riad_alsaalihin_old = self.get_object().second_info["old"]
            student.riad_alsaalihin_new = self.get_object().second_info["new"]
            student.save()
    
        elif self.get_object().message_type == MessageTypeChoice.ALLAH_NAMES:
            student = self.get_object().student
            student.allah_names_new = False
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
def master_list_admin(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("text-search-table") or None
    masters = Master.objects.select_related("user").all().order_by("id")
    if q is not None:
        my_regex = r""
        for word in re.split(r"\s+", q.strip()):
            my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
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
def master_edit_permissions(request: HttpRequest, mid: int) -> HttpResponse:
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
def admin_adding_points_log(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None
    add_messages = (
        PointsAdding.objects.select_related("student", "master__user", "cause")
        .filter(created_at__date=date.today())
        .order_by("-created_at")
    )
    if (q is not None) and (search_type is not None):
        if search_type == "by-master":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
            add_messages = (
                PointsAdding.objects.select_related(
                    "student", "master__user", "cause"
                )
                .filter(master__user__username__iregex=r"{}".format(my_regex))
                .order_by("-created_at")
            )
            return render(
                request,
                "control_panel/admin_adding_points_log.html",
                {"a_msgs": add_messages, "val": q},
            )
        else:
            my_regex = ""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
            add_messages = (
                PointsAdding.objects.select_related(
                    "student", "master__user", "cause"
                )
                .filter(student__name__iregex=r"{}".format(my_regex))
                .order_by("-created_at")
            )
            return render(
                request,
                "control_panel/admin_adding_points_log.html",
                {"a_msgs": add_messages, "val": q},
            )

    return render(
        request,
        "control_panel/admin_adding_points_log.html",
        {"a_msgs": add_messages},
    )


@user_passes_test(check_admin)
@login_required
def admin_specializations(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        edits = list(request.POST)[1:]

        apply_edit_changes(edits)

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    specializations = Specialization.objects.all()
    parts = (
        Part.objects
        .select_related("subject__specialization")
        .prefetch_related(
            Prefetch(
                "studentspecializationpartrelation_set",
                queryset=StudentSpecializationPartRelation.objects.select_related("student"),
            )
        )
        .all()
        .order_by("subject__specialization", "subject", "part_number")
    )   
    
    students = Student.objects.exclude(studentspecializationpartrelation__isnull=True).prefetch_related("studentspecializationpartrelation_set").order_by("id")

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
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
            "student", "master__user", "part__subject__specialization"
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
def admin_test_certificates(request: HttpRequest) -> HttpResponse:

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    students = [s for s in Student.objects.all().order_by("id") if s.q_test_certificate != "لا يوجد"]

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
            students = [s for s in Student.objects.filter(
                name__iregex=r"{}".format(my_regex)
            ).order_by("id") if s.q_test_certificate != "لا يوجد"]
        else:
            students = [s for s in Student.objects.filter(pk=int(q)).order_by("id") if s.q_test_certificate != "لا يوجد"]

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
def admin_statistics(request: HttpRequest) -> HttpResponse:
    students = Student.objects.prefetch_related("coming_set").all()

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
    number_of_active_students = students.exclude(coming__isnull=True).count()

    return render(
        request,
        "control_panel/admin_statistics.html",
        {
            "number_of_pages": int(number_of_pages),
            "number_of_parts": int(number_of_parts),
            "number_of_parts_awqaf_normal": number_of_parts_awqaf_normal,
            "number_of_parts_awqaf_looking": number_of_parts_awqaf_looking,
            "number_of_parts_awqaf_explaining": number_of_parts_awqaf_explaining,
            "number_of_active_students": number_of_active_students,
        },
    )



# adding points
@user_passes_test(check_adding_points)
@login_required
def adding_points(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        adding_causes = PointsAddingCause.objects.all()
        return render(
            request,
            "adding_points.html",
            {"adding_causes": adding_causes},
        )

    elif request.method == "POST":
        master = Master.objects.get(user=request.user)
        sid = int(request.POST.get("student-id"))
        value = int(request.POST.get("value"))
        cid = int(request.POST.get("cause-id"))
        
        PointsAdding.objects.create(
            master=master, cause_id=cid, student_id=sid, value=value
        )

        return redirect(request.META.get("HTTP_REFERER"))

    else:
        return HttpResponseNotAllowed("")


@user_passes_test(check_adding_points)
@login_required
def adding_points_log(request: HttpRequest) -> HttpResponse:
    master = Master.objects.get(user=request.user)

    points_adding_msgs = (
        PointsAdding.objects.select_related("student", "cause")
        .filter(master=master)
        .order_by("-created_at")
    )

    return render(
        request,
        "adding_points_log.html",
        {
            "adding_msgs": points_adding_msgs,
        },
    )


@user_passes_test(check_adding_points)
@login_required
def deleting_adding_points(request: HttpRequest, aid: int) -> HttpResponse:
    if request.method == "POST":
        master = Master.objects.get(user=request.user)
        adding_id = int(request.POST.get("id"))
        adding = PointsAdding.objects.get(pk=adding_id)
        if request.user.is_superuser or adding.master == master:
            adding.delete()
        return redirect("adding_points_log")
    return render(request, "adding_points_delete.html", {"id": aid})


@user_passes_test(check_admin)
@login_required
def deleting_adding_points_admin(_, aid: int):
    adding = PointsAdding.objects.get(pk=aid)
    adding.delete()
    return redirect("admin_adding_points_log")


@user_passes_test(check_reports)
@login_required
def students_reports(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        sid = request.POST.get("student-id") or None
        reports_type = request.POST.get("type")
        start = request.POST.get("start").split("-")
        end = request.POST.get("end").split("-")

        start = datetime(year=int(start[0]), month=int(start[1]), day=int(start[2]), tzinfo=pytz.UTC)
        end = datetime(year=int(end[0]), month=int(end[1]), day=int(end[2]), tzinfo=pytz.UTC)

        if reports_type == "all":
            data = {}
            reports = []
            students = Student.objects.all()

            for student in students:
                data[student.id, student.name] = student.memorizemessage_set.filter(
                    sended_at__range=[start, end], message_type__in=[MessageTypeChoice.MEMO, MessageTypeChoice.TEST]
                )

            for personal_info, messages in data.items():
                sum_pages = 0
                for message in messages:
                    sum_pages += give_num_pages(message)
                reports.append({
                    "student_id": personal_info[0],
                    "student": personal_info[1],
                    "sum_pages": sum_pages,
                })

            reports.sort(key=lambda x: x["sum_pages"], reverse=True)

            return render(
                request,
                "reports/reports_results.html",
                {
                    "reports": reports,
                    "start": request.POST.get("start"),
                    "end": request.POST.get("end"),
                    "type": reports_type,
                },
            )

        elif reports_type == "groups":
            reports = []
            students_groups = StudentGroup.objects.all()

            for group in students_groups:
                students = []
                sum_pages = 0
                for student in group.student_set.all():
                    student_sum = 0
                    for message in student.memorizemessage_set.filter(sended_at__range=[start, end], message_type__in=[MessageTypeChoice.MEMO, MessageTypeChoice.TEST]):
                        student_sum += give_num_pages(message)
                        sum_pages += give_num_pages(message)
                    students.append({"id": student.id, "name": student.name, "sum_pages": student_sum})
                reports.append({"group": group, "sum_pages": sum_pages, "students": students})

            reports.sort(key=lambda x: x["sum_pages"], reverse=True)

            return render(
                request,
                "reports/reports_results.html",
                {
                    "reports": reports,
                    "start": request.POST.get("start"),
                    "end": request.POST.get("end"),
                    "type": reports_type,
                }
            )

        elif reports_type == "categories":
            reports = []
            students_categories = Category.objects.all()

            for category in students_categories:
                students = []
                sum_pages = 0
                for student in category.student_set.all():
                    student_sum = 0
                    for message in student.memorizemessage_set.filter(sended_at__range=[start, end], message_type__in=[MessageTypeChoice.MEMO, MessageTypeChoice.TEST]):
                        student_sum += give_num_pages(message)
                        sum_pages += give_num_pages(message)
                    students.append({"id": student.id, "name": student.name, "sum_pages": student_sum})
                reports.append({"category": category, "sum_pages": sum_pages, "students": students})

            reports.sort(key=lambda x: x["sum_pages"], reverse=True)

            return render(
                request,
                "reports/reports_results.html",
                {
                    "reports": reports,
                    "start": request.POST.get("start"),
                    "end": request.POST.get("end"),
                    "type": reports_type,
                }
            )

        else:
            result = {}
            student = Student.objects.get(pk=sid)
            result["student"] = student
            messages = student.memorizemessage_set.filter(
                sended_at__range=[start, end], message_type__in=[MessageTypeChoice.MEMO, MessageTypeChoice.TEST]
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
                    "type": reports_type,
                },
            )

    else:
        return render(request, "reports/students_reports.html")


@user_passes_test(check_admin)
@login_required
def deleting_money(request: HttpRequest) -> HttpResponse:
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
def deleting_money_category(request: HttpRequest) -> HttpResponse:
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
def deleting_money_table(request: HttpRequest) -> HttpResponse:

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    point_value = ControlSettings.objects.first().point_value

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
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
def deleting_money_total_table(request: HttpRequest) -> HttpResponse:

    q = request.GET.get("text-search-table") or None
    search_type = request.GET.get("type-search-table-admin-p") or None

    if (q is not None) and (search_type is not None):
        if search_type == "by-text":
            my_regex = r""
            for word in re.split(r"\s+", q.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
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


@user_passes_test(check_adding_hadeeth)
@login_required
def add_hadeeth(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        student_id = request.POST.get("student-id")
        hadeeth_number = int(request.POST.get("hadeeth-number"))
        add_hadeeth_type = request.POST.get("add-hadeeth-type")

        student = get_object_or_404(Student, id=student_id)

        master = Master.objects.get(user=request.user)

        control_settings = ControlSettings.objects.first()

        if add_hadeeth_type == "allah_names":
            if not (student.allah_names_old or student.allah_names_new):
                student.allah_names_new = True
                student.save()

                memorize_message = MemorizeMessage.objects.create(
                    master=master,
                    student=student,
                    student_string=student.name,
                    first_info=None,
                    second_info=None,
                    message_type=MessageTypeChoice.ALLAH_NAMES,
                )

                if control_settings.double_points:
                    DoublePointMessage.objects.create(
                        student=student,
                        points=50,
                        content=None,
                        memorize_message=memorize_message,
                        message_type=DoubleMessageTypeChoice.ALLAH_NAMES,
                    )

        elif add_hadeeth_type == "alarbaein_alnawawia":
            if student.alarbaein_alnawawia_old + student.alarbaein_alnawawia_new < hadeeth_number <= 50:
                memorize_message = MemorizeMessage.objects.create(
                    master=master,
                    student=student,
                    student_string=student.name,
                    first_info=[f"الحديث {i}" for i in range(student.alarbaein_alnawawia_old + student.alarbaein_alnawawia_new + 1, hadeeth_number + 1)],
                    second_info={"old": student.alarbaein_alnawawia_old, "new": student.alarbaein_alnawawia_new},
                    message_type=MessageTypeChoice.ALNAWAWIA,
                )

                if control_settings.double_points:
                    DoublePointMessage.objects.create(
                        student=student,
                        points=(hadeeth_number - student.alarbaein_alnawawia_old - student.alarbaein_alnawawia_new) * 2,
                        content=[f"الحديث {i}" for i in range(student.alarbaein_alnawawia_old + student.alarbaein_alnawawia_new + 1, hadeeth_number + 1)],
                        memorize_message=memorize_message,
                        message_type=DoubleMessageTypeChoice.ALNAWAWIA,
                    )

                student.alarbaein_alnawawia_new = hadeeth_number - student.alarbaein_alnawawia_old
                student.save()


            
        elif add_hadeeth_type == "riad_alsaalihin":
            if student.riad_alsaalihin_old + student.riad_alsaalihin_new < hadeeth_number:
                memorize_message = MemorizeMessage.objects.create(
                    master=master,
                    student=student,
                    student_string=student.name,
                    first_info=[f"الحديث {i}" for i in range(student.riad_alsaalihin_old + student.riad_alsaalihin_new + 1, hadeeth_number + 1)],
                    second_info={"old": student.riad_alsaalihin_old, "new": student.riad_alsaalihin_new},
                    message_type=MessageTypeChoice.ALSAALIHIN,
                )

                if control_settings.double_points:
                    DoublePointMessage.objects.create(
                        student=student,
                        points=(hadeeth_number - student.riad_alsaalihin_old - student.riad_alsaalihin_new) * 2,
                        content=[f"الحديث {i}" for i in range(student.riad_alsaalihin_old + student.riad_alsaalihin_new + 1, hadeeth_number + 1)],
                        memorize_message=memorize_message,
                        message_type=DoubleMessageTypeChoice.ALSAALIHIN,
                    )

                student.riad_alsaalihin_new = hadeeth_number - student.riad_alsaalihin_old
                student.save()



    return redirect(request.META.get("HTTP_REFERER"))


@login_required
def edit_parts_received(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        content = request.POST.get("content")
        student_id = request.POST.get("student-id")

        student = get_object_or_404(Student, pk=student_id)

        student.parts_received = content

        student.save()

    return redirect(request.META.get("HTTP_REFERER"))


def assets_files(request: HttpRequest) -> HttpResponse:
    return render(request, "assets_files.html", {"assets_categories": AssetsCategory.objects.prefetch_related("assetfile_set").all()})


def register(request: HttpRequest) -> HttpResponse:
    return render(request, "register/index.html")

def register_search_results(request: HttpRequest) -> HttpResponse:
    query_text = request.GET.get("q_text")
    query_id = request.GET.get("q_search_id")

    all_tests = AwqafTestNoQ.objects.all()

    if query_id:
        student = Student.objects.filter(pk=query_id)

        return render(request, "register/search_results.html", { "students": student, "all_tests": all_tests })

    if query_text:
        my_regex = ""

        for word in re.split(r"\s+", query_text.strip()):
            my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"

        students = (
            Student.objects.filter(name__iregex="{}".format(my_regex))
            .select_related("category", "student_group")
            .order_by("id")
        )

        return render(request, "register/search_results.html", { "students": students, "all_tests": all_tests })

    return HttpResponseBadRequest("<h1>You must provide an id or text</h1>")


def register_student(request: HttpRequest, id: int) -> HttpResponse:
    student = get_object_or_404(Student, pk=id)

    student.registered = True
    student.save()

    request.session["has_registered"] = True
    messages.success(request, "تم التسجيل بنجاح")
    return redirect("home")


def create_new_stduent(request: HttpRequest) -> HttpResponse:
    form = NewStudentForm(request.POST or None)

    if form.is_valid():
        form.save()
        request.session["has_registered"] = True
        messages.success(request, "تم التسجيل بنجاح")
        return redirect("home")

    return render(request, "register/create_new_student.html", {"form": form})

# ajax views
def students_ajax(request: HttpRequest) -> JsonResponse | HttpResponse:
    if request.method == "POST":
        query = json.loads(request.body)["content"]
        if query is not None:
            my_regex = r""
            for word in re.split(r"\s+", query.strip()):
                my_regex += re.escape(word).replace("\u0627", "(\u0623|\u0625|\u0627)").replace("أ", "(\u0623|\u0625|\u0627)").replace("إ", "(\u0623|\u0625|\u0627)") + r".*"
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
def switch_deleting_active_to_points_state(request: HttpRequest) -> JsonResponse | HttpResponse:
    if request.method == "POST":

        data = json.loads(request.body)["delete_id"] or None

        delete_id = int(data)

        delete_money = MoneyDeleting.objects.get(pk=delete_id)

        delete_money.active_to_points = not delete_money.active_to_points

        delete_money.save()

        return JsonResponse({"message": delete_money.active_to_points}, status=200)

    return HttpResponseNotAllowed("")


@user_passes_test(check_admin)
@login_required
def adding_hidden_id(request: HttpRequest) -> JsonResponse:
    id = json.loads(request.body).get("id")

    if id is None:
        return JsonResponse({
            "message": "Invalid payload"
        }, status=400)
    
    control_settings = ControlSettings.objects.first()

    if int(id) in control_settings.hidden_ids:
        return JsonResponse({
            "message": "duplicated id"
        }, status=400)

    control_settings.hidden_ids.append(int(id))
    control_settings.save()

    return JsonResponse({
        "message": "success",
    })


@user_passes_test(check_admin)
@login_required
def removing_hidden_id(request: HttpRequest) -> JsonResponse:
    id = json.loads(request.body).get("id")

    if id is None:
        return JsonResponse({
            "message": "Invalid payload"
        }, status=400)
    
    control_settings = ControlSettings.objects.first()

    try:
        control_settings.hidden_ids.remove(int(id))
        control_settings.save()
    except ValueError:
        return JsonResponse({
            "message": "id doesn't exist",
        }, status=404)

    return JsonResponse({
        "message": "success",
    })