from django.db import models
from datetime import date
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.conf.global_settings import AUTH_USER_MODEL
from .default_dictionary import DEFAULT_DICT, DEFAULT_DICT_FOR_q_test, DEFAULT_DICT_FOR_q_candidate_test, DEFAULT_DICT_FOR_PERMISSIONS, check_for_cer
from .point_map import apply_q_map, q_map
import json


#* Default json
def json_default_value():
    return DEFAULT_DICT

def json_default_value_two():
    return DEFAULT_DICT_FOR_q_test

def json_default_value_three():
    return DEFAULT_DICT_FOR_q_candidate_test

def json_default_value_four():
    return DEFAULT_DICT_FOR_PERMISSIONS


#* Models
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='الفئة')

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'الفئة'
        verbose_name_plural = 'الفئات'


class Master(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="اسم المستخدم")
    permissions = models.JSONField(default=json_default_value_four, verbose_name="الصلاحيات")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'أستاذ'
        verbose_name_plural = 'أساتذة'


class Student(models.Model):
    name = models.CharField(max_length=511, verbose_name='الاسم الثلاثي')
    mother_name = models.CharField(max_length=255, verbose_name='اسم الأم')
    birthdate = models.DateField(verbose_name='تاريخ الميلاد', null=True, blank=True)
    address = models.CharField(max_length=511, verbose_name='العنوان تفصيلاً', null=True, blank=True)
    static_phone = models.CharField(max_length=20, verbose_name='الهاتف الأرضي', blank=True, null=True)
    cell_phone = models.CharField(max_length=20, verbose_name='الجوال', blank=True, null=True)
    father_phone = models.CharField(max_length=20, verbose_name='جوال الأب', blank=True, null=True)
    mother_phone = models.CharField(max_length=20, verbose_name='جوال الأم', null=True, blank=True)
    registered_at = models.DateField(verbose_name='تاريخ التسجيل', auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name='الفئة', null=True, blank=True)
    father_work = models.CharField(max_length=255, null=True, blank=True, verbose_name='عمل الأب')
    notes = models.CharField(max_length=511, null=True, blank=True, verbose_name='ملاحظات')
    bring_him = models.CharField(max_length=511, verbose_name='أحضره', null=True, blank=True)
    q_memorizing = models.JSONField(default=json_default_value, verbose_name='حفظ القرآن')
    q_test = models.JSONField(default=json_default_value_two, verbose_name='السبر في المسجد')
    q_test_candidate = models.JSONField(default=json_default_value_three, verbose_name='السبر الترشيحي')
    q_awqaf_test = models.JSONField(default=json_default_value_three, verbose_name='سبر القرآن في الأوقاف')
    is_q_test_certificate = models.BooleanField(default=True, verbose_name='هل يوجد شهادة سبر')

    def __str__(self):
        return self.name

    @property
    def age(self):
        if self.birthdate:
            delta = date.today() - self.birthdate
            return delta.days // 365
        else:
            return 'تاريخ الميلاد غير محدد'
    age.fget.short_description = 'العمر'

    def __str__(self):
        return self.name

    @property
    def q_test_certificate(self):
        result = {}
        test_cer = check_for_cer(self.q_test)
        for i in test_cer:
            if test_cer[i] == 'NEW':
                result[i] = 'تم'
        if not result:
            return 'لا يوجد'
        else:
            return json.dumps(result, ensure_ascii=False)
    q_test_certificate.fget.short_description = 'شهادات السبر'

    @property
    def points_of_coming(self):
        list_of_point = [p.points for p in self.coming_set.all()]
        return sum(list_of_point)
    points_of_coming.fget.short_description = 'كلي نقاط الحضور'

    @property
    def points_of_q_memo(self):
        list_of_point = []
        for key, value in self.q_memorizing.items():
            if value == "NEW":
                list_of_point.append(q_map[key])

        #* message_type_1 here is created at .\views.py, the goal of it is to make prefetch related valid also inside @property method, check it in main_admin view in .\views.py
        for double in self.message_type_1:
            list_of_point.append(double.points)
        return sum(list_of_point)
    points_of_q_memo.fget.short_description = 'كلي نقاط التسميع'

    @property
    def points_of_q_test(self):
        list_of_point = []
        for __, value in self.q_test.items():
            for ___, value2 in value.items():
                for ____, value3 in value2.items():
                    if value3 == "NEW":
                        list_of_point.append(13)
        
        #* message_type_2 here is created at .\views.py, the goal of it is to make prefetch related valid also inside @property method, check it in main_admin view in .\views.py
        for double in self.message_type_2:
            list_of_point.append(double.points)
        return sum(list_of_point)
    points_of_q_test.fget.short_description = 'كلي نقاط السبر العادي'

    @property
    def points_of_q_candidate_test(self):
        list_of_point = []
        for __, value in self.q_test_candidate.items():
            if value == "NEW":
                list_of_point.append(25)
        return sum(list_of_point)
    points_of_q_candidate_test.fget.short_description = 'كلي نقاط السبر الترشيحي'

    @property
    def number_of_q_memo(self):
        list_of_pages_num = []
        for key, value in self.q_memorizing.items():
            if len(key) <= 3 and value == "NEW":
                list_of_pages_num.append(1)

            elif len(key) > 3 and value == "NEW":
                list_of_pages_num.append(q_map[key] / 5)

        return sum(list_of_pages_num)
    number_of_q_memo.fget.short_description = 'عدد الصفحات المسمعة'

    @property
    def number_of_q_test(self):
        list_of_chapters_num = []
        for __, value in self.q_test.items():
            for ___, value2 in value.items():
                for ____, value3 in value2.items():
                    if value3 == "NEW":
                        list_of_chapters_num.append(0.25)
        return sum(list_of_chapters_num)
    number_of_q_test.fget.short_description = 'عدد الأجزاء المسبورة'

    @property
    def number_of_q_candidate_test(self):
        list_of_candidate_num = []
        for __, value in self.q_test_candidate.items():
            if value == "NEW":
                list_of_candidate_num.append(1)
        return sum(list_of_candidate_num)
    number_of_q_candidate_test.fget.short_description = 'عدد الأجزاء الترشيحية المسبورة'

    @property
    def added_points(self):
        result = 0
        for process in self.pointsadding_set.all():
            result += process.value
        return result
    added_points.fget.short_description = 'نقاط مضافة متفرقة'

    @property
    def deleted_points(self):
        result = 0
        for process in self.pointsdeleting_set.all():
            result += process.value
        return result
    deleted_points.fget.short_description = 'نقاط مخصومة متفرقة'

    class Meta:
        verbose_name = 'الطالب'
        verbose_name_plural = 'الطلاب'


class MemorizeNotes(models.Model):
    master_name = models.ForeignKey(Master, verbose_name='اسم الأستاذ', on_delete=models.CASCADE, null=True)
    content = models.CharField(verbose_name='المحتوى', max_length=511)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='اسم الطالب')
    student_string = models.CharField(max_length=511, verbose_name='اسم الطالب', null=True, blank=True)
    sended_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')

    def __str__(self):
        return f'ملاحظة  ({self.id})'


    class Meta:
        verbose_name = 'ملاحظة تسميع'
        verbose_name_plural = 'ملاحظات التسميع'


class MessageTypeChoice(models.IntegerChoices):
    MEMO = 1, "تسميع"
    TEST = 2, "سبر"
    CAND = 3, "سبر ترشيحي"


class DoubleMessageTypeChoice(models.IntegerChoices):
    MEMO = 1, "تسميع"
    TEST = 2, "سبر"


class MemorizeMessage(models.Model):
    master_name = models.ForeignKey(Master, verbose_name='اسم الأستاذ', on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='اسم الطالب')
    student_string = models.CharField(max_length=511, verbose_name='اسم الطالب', null=True, blank=True)
    sended_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')
    first_info = models.JSONField(default=dict, verbose_name='الحفظ')
    second_info = models.JSONField(default=dict, verbose_name='الحفظ قبل التعديل')
    message_type = models.IntegerField(verbose_name="نوع الرسالة", choices=MessageTypeChoice.choices, default=MessageTypeChoice.MEMO)

    def __str__(self):
        return f'رسالة التسميع {self.id}'

    
    class Meta:
        verbose_name = 'رسالة تسميع'
        verbose_name_plural = 'رسائل التسميع'


class ComingCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name='الفئة')

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'فئة الحضور'
        verbose_name_plural = 'فئات الحضور'


class Coming(models.Model):
    master_name = models.ForeignKey(Master, verbose_name='اسم الأستاذ', on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, verbose_name='اسم الطالب', on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')
    category = models.ForeignKey(ComingCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='نوع الحضور')
    points = models.IntegerField(verbose_name='نقاط الحضور', default=0)
    note = models.TextField(verbose_name='ملاحظة', null=True, blank=True)


    def __str__(self):
        return f"تسجيل حضور {self.id}"


    class Meta:
        verbose_name = 'تسجيل حضور'
        verbose_name_plural = 'تسجيلات الحضور'


class ControlSettings(models.Model):
    double_points = models.BooleanField(default=False, verbose_name='مضاعفة النقاط')
    point_value = models.IntegerField(verbose_name='قيمة النقطة')


class DoublePointMessage(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='الطالب')
    sended_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')
    points = models.IntegerField(verbose_name='النقاط')
    content = models.JSONField(default=dict, verbose_name='التسميع الذي تم مضاعفته')
    memorize_message = models.OneToOneField(MemorizeMessage, on_delete=models.CASCADE, null=True, blank=True, verbose_name='رسالة التسميع')
    message_type = models.IntegerField(choices=DoubleMessageTypeChoice.choices, default=DoubleMessageTypeChoice.MEMO, verbose_name='نوع التسميع')

    def __str__(self):
        return f"رسالة مضاعفة {self.id}"


    class Meta:
        verbose_name = 'رسالة مضاعفة'
        verbose_name_plural = 'رسائل مضاعفة'


class PointsAddingCause(models.Model):
    name = models.CharField(max_length=255, verbose_name='الاسم')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'سبب إضافة'
        verbose_name_plural = 'أسباب إضافة'


class PointsDeletingCause(models.Model):
    name = models.CharField(max_length=255, verbose_name='الاسم')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'سبب خصم'
        verbose_name_plural = 'أسباب خصم'


class PointsAdding(models.Model):
    master_name = models.ForeignKey(Master, verbose_name='اسم الأستاذ', on_delete=models.CASCADE, null=True)
    value = models.IntegerField(verbose_name="القيمة")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    cause = models.ForeignKey(PointsAddingCause, verbose_name='السبب', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"إضافة نقاط {self.id}"

    class Meta:
        verbose_name = 'إضافة نقاط'
        verbose_name_plural = 'إضافات النقاط'


class PointsDeleting(models.Model):
    master_name = models.ForeignKey(Master, verbose_name='اسم الأستاذ', on_delete=models.CASCADE, null=True)
    value = models.IntegerField(verbose_name="القيمة")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الخصم")
    cause = models.ForeignKey(PointsDeletingCause, verbose_name='السبب', on_delete=models.PROTECT, null=True, blank=True)


    def __str__(self):
        return f"خصم نقاط {self.id}"

    class Meta:
        verbose_name = 'خصم نقاط'
        verbose_name_plural = 'خصومات النقاط'


class MoneyDeletingCause(models.Model):
    name = models.CharField(max_length=511, verbose_name='الاسم')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'سبب غرامة'
        verbose_name_plural = 'أسباب الغرامات'


class MoneyDeleting(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='الاسم')
    value_in_points = models.IntegerField(verbose_name='القيمة مقدرة بالنقاط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')
    cause = models.ForeignKey(MoneyDeletingCause, on_delete=models.PROTECT, verbose_name='سبب الغرامة', null=True)

    def __str__(self):
        return f"غرامة {self.id}"

    class Meta:
        verbose_name = 'غرامة'
        verbose_name_plural = 'الغرامات'

    
    @property
    def value_in_money(self):
        return self.value_in_points * ControlSettings.objects.first().point_value







#* Signals Section
User = get_user_model()

@receiver(post_save, sender=User)
def create_master(sender, instance, created, **kwargs):
    if created:
        Master.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_master(sender, instance, **kwargs):
        instance.master.save()