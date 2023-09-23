from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.conf.global_settings import AUTH_USER_MODEL
from django.core.validators import MinValueValidator
from main_app import default_json
from main_app.point_map import q_map
from datetime import date



# * Models
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="الفئة", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "الفئة"
        verbose_name_plural = "الفئات"


class StudentGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="الاسم", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مجموعة الطلاب"
        verbose_name_plural = "مجموعات الطلاب"


class Master(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="اسم المستخدم")
    permissions = models.JSONField(default=default_json.json_default_value_four, verbose_name="الصلاحيات")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "أستاذ"
        verbose_name_plural = "أساتذة"


class Student(models.Model):
    name = models.CharField(max_length=511, verbose_name="الاسم الثلاثي")
    mother_name = models.CharField(max_length=255, verbose_name="اسم الأم", null=True, blank=True)
    birthdate = models.DateField(verbose_name="تاريخ الميلاد", null=True, blank=True)
    address = models.CharField(max_length=511, verbose_name="العنوان تفصيلاً", null=True, blank=True)
    static_phone = models.CharField(max_length=20, verbose_name="الهاتف الأرضي", blank=True, null=True)
    cell_phone = models.CharField(max_length=20, verbose_name="الجوال", blank=True, null=True)
    father_phone = models.CharField(max_length=20, verbose_name="جوال الأب", blank=True, null=True)
    mother_phone = models.CharField(max_length=20, verbose_name="جوال الأم", null=True, blank=True)
    registered_at = models.DateField(verbose_name="تاريخ التسجيل", auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name="الفئة", null=True, blank=True)
    father_work = models.CharField(max_length=255, null=True, blank=True, verbose_name="عمل الأب")
    notes = models.CharField(max_length=511, null=True, blank=True, verbose_name="ملاحظات")
    bring_him = models.CharField(max_length=511, verbose_name="أحضره", null=True, blank=True)
    q_memorizing = models.JSONField(default=default_json.json_default_value, verbose_name="حفظ القرآن")
    q_test = models.JSONField(default=default_json.json_default_value_two, verbose_name="السبر في المسجد")
    q_awqaf_test = models.JSONField(default=default_json.json_default_value_three, verbose_name="سبر القرآن في الأوقاف")
    q_awqaf_test_looking = models.JSONField(default=default_json.json_default_value_three, verbose_name="سبر القرآن نظراً في الأوقاف")
    q_awqaf_test_explaining = models.JSONField(default=default_json.json_default_value_three, verbose_name="سبر القرآن تفسيراً في الأوقاف")
    alarbaein_alnawawia_old = models.IntegerField(verbose_name="الأربعين النووية قديم", default=0, validators=[MinValueValidator(0)])
    alarbaein_alnawawia_new = models.IntegerField(verbose_name="الأربعين النووية جديد", default=0, validators=[MinValueValidator(0)])
    riad_alsaalihin_old = models.IntegerField(verbose_name="رياض الصالحين قديم", default=0, validators=[MinValueValidator(0)])
    riad_alsaalihin_new = models.IntegerField(verbose_name="رياض الصالحين جديد", default=0, validators=[MinValueValidator(0)])
    allah_names_old = models.BooleanField(verbose_name="أسماء الله الحسنى قديم", default=False)
    allah_names_new = models.BooleanField(verbose_name="أسماء الله الحسنى جديد", default=False)
    student_group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, verbose_name="مجموعة الطالب", null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def age(self):
        if self.birthdate:
            delta = date.today() - self.birthdate
            return delta.days // 365
        else:
            return "تاريخ الميلاد غير محدد"
    age.fget.short_description = "العمر"

    @property
    def q_test_certificate(self):
        result = {}
        test_cer = check_for_cer(self.q_test)
        for i in test_cer:
            if test_cer[i] == "NEW":
                result[i] = "تم"
        if not result:
            return "لا يوجد"
        else:
            return result
    q_test_certificate.fget.short_description = "شهادات السبر"

    @property
    def points_of_coming(self):
        list_of_point = [p.points for p in self.coming_set.all()]
        return sum(list_of_point)
    points_of_coming.fget.short_description = "كلي نقاط الحضور"

    @property
    def points_of_q_memo(self):
        list_of_point = []
        for key, value in self.q_memorizing.items():
            if value == "NEW":
                list_of_point.append(q_map[key])

        # * message_type_1 here is created at .\views.py, the goal of it is to make prefetch related valid also inside @property method, check it in main_admin view in .\views.py
        for double in self.message_type_1:
            list_of_point.append(double.points)
        return sum(list_of_point)
    points_of_q_memo.fget.short_description = "كلي نقاط التسميع"

    @property
    def points_of_q_test(self):
        list_of_point = []
        for __, value in self.q_test.items():
            for ___, value2 in value.items():
                for ____, value3 in value2.items():
                    if value3 == "NEW":
                        list_of_point.append(13)

        # * message_type_2 here is created at .\views.py, the goal of it is to make prefetch related valid also inside @property method, check it in main_admin view in .\views.py
        for double in self.message_type_2:
            list_of_point.append(double.points)
        return sum(list_of_point)
    points_of_q_test.fget.short_description = "كلي نقاط السبر العادي"

    @property
    def number_of_q_memo(self):
        list_of_pages_num = []
        for key, value in self.q_memorizing.items():
            if len(key) <= 3 and value == "NEW":
                list_of_pages_num.append(1)

            elif len(key) > 3 and value == "NEW":
                list_of_pages_num.append(q_map[key] / 5)

        return sum(list_of_pages_num)
    number_of_q_memo.fget.short_description = "عدد الصفحات المسمعة"

    @property
    def number_of_q_test(self):
        list_of_chapters_num = []
        for __, value in self.q_test.items():
            for ___, value2 in value.items():
                for ____, value3 in value2.items():
                    if value3 == "NEW":
                        list_of_chapters_num.append(0.25)
        return sum(list_of_chapters_num)
    number_of_q_test.fget.short_description = "عدد الأجزاء المسبورة"

    @property
    def added_points(self):
        result = 0
        for process in self.pointsadding_set.all():
            result += process.value
        return result
    added_points.fget.short_description = "نقاط مضافة متفرقة"

    @property
    def deleted_points_for_money_deleting(self):
        result = [0, 0]
        for money_deleting in self.money_deleting_info:
            if money_deleting.is_money_main_value:
                result[1] += money_deleting.value
            else:
                result[0] += money_deleting.value
        return result

    @property
    def number_of_parts_awqaf_normal_tests(self):
        list_of_awqaf_normal_test_num = []
        for __, value in self.q_awqaf_test.items():
            if value == "NEW":
                list_of_awqaf_normal_test_num.append(1)
        return sum(list_of_awqaf_normal_test_num)
    number_of_parts_awqaf_normal_tests.fget.short_description = "عدد الأجزاء المسبورة غيباً في الأوقاف"
    

    @property
    def awqaf_points_normal_test(self):
        return self.number_of_parts_awqaf_normal_tests * 50

    awqaf_points_normal_test.fget.short_description = "نقاط الأجزاء المسبورة غيباً في الأوقاف"    

    @property
    def number_of_parts_awqaf_looking_tests(self):
        list_of_awqaf_looking_test_num = []
        for __, value in self.q_awqaf_test_looking.items():
            if value == "NEW":
                list_of_awqaf_looking_test_num.append(1)
        return sum(list_of_awqaf_looking_test_num)
    number_of_parts_awqaf_looking_tests.fget.short_description =  "عدد الأجزاء المسبورة نظراً في الأوقاف"
    

    @property
    def awqaf_points_looking_test(self):
        return self.number_of_parts_awqaf_looking_tests * 13
    awqaf_points_looking_test.fget.short_description = "نقاط الأجزاء المسبورة نظراً في الأوقاف"
    

    @property
    def number_of_parts_awqaf_explaining_tests(self):
        list_of_awqaf_explaining_test_num = []
        for __, value in self.q_awqaf_test_explaining.items():
            if value == "NEW":
                list_of_awqaf_explaining_test_num.append(1)
        return sum(list_of_awqaf_explaining_test_num)
    number_of_parts_awqaf_explaining_tests.fget.short_description = "عدد الأجزاء المسبورة تفسيراً في الأوقاف"

    @property
    def awqaf_points_explaining_test(self):
        return self.number_of_parts_awqaf_explaining_tests * 100
    awqaf_points_explaining_test.fget.short_description = "نقاط الأجزاء المسبورة تفسيراً في الأوقاف"
    
    @property
    def alarbaein_alnawawia_points(self):
        result = self.alarbaein_alnawawia_new * 2

        for double in self.message_type_3:
            result += double.points

        return result
    alarbaein_alnawawia_points.fget.short_description = "نقاط الأربعين النووية"

    @property
    def riad_alsaalihin_points(self):
        result = self.riad_alsaalihin_new * 2

        for double in self.message_type_4:
            result += double.points

        return result
    riad_alsaalihin_points.fget.short_description = "نقاط رياض الصالحين"

    @property
    def allah_names_points(self):
        result = 50 if self.allah_names_new else 0

        for double in self.message_type_5:
            result += double.points

        return result
    allah_names_points.fget.short_description = "نقاط أسماء الله الحسنى"
    

    @property
    def all_points_sum(self):
        all_added_points = (
            self.points_of_coming
            + self.points_of_q_memo
            + self.points_of_q_test
            + self.awqaf_points_normal_test
            + self.awqaf_points_looking_test
            + self.awqaf_points_explaining_test
            + self.added_points
            + self.alarbaein_alnawawia_points
            + self.riad_alsaalihin_points
            + self.allah_names_points
        )
        all_deleted_points = self.deleted_points_for_money_deleting[0]        
        money_for_deleting = self.deleted_points_for_money_deleting[1]
        sum_of_added_and_deleted = all_added_points - all_deleted_points
        return [sum_of_added_and_deleted, money_for_deleting]
    all_points_sum.fget.short_description = "مجموع النقاط الكلي"

    class Meta:
        verbose_name = "الطالب"
        verbose_name_plural = "الطلاب"


class MemorizeNotes(models.Model):
    master_name = models.ForeignKey(Master, verbose_name="اسم الأستاذ", on_delete=models.CASCADE, null=True)
    content = models.CharField(verbose_name="المحتوى", max_length=511)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="اسم الطالب")
    student_string = models.CharField(max_length=511, verbose_name="اسم الطالب", null=True, blank=True)
    sended_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")

    def __str__(self):
        return f"ملاحظة  ({self.id})"

    class Meta:
        verbose_name = "ملاحظة تسميع"
        verbose_name_plural = "ملاحظات التسميع"


class MessageTypeChoice(models.IntegerChoices):
    MEMO = 1, "تسميع"
    TEST = 2, "سبر"
    ALNAWAWIA = 3, "أربعين نووية"
    ALSAALIHIN = 4, "رياض الصالحين"
    ALLAH_NAMES = 5, "أسماء الله الحسنى"


class DoubleMessageTypeChoice(models.IntegerChoices):
    MEMO = 1, "تسميع"
    TEST = 2, "سبر"
    ALNAWAWIA = 3, "أربعين نووية"
    ALSAALIHIN = 4, "رياض الصالحين"
    ALLAH_NAMES = 5, "أسماء الله الحسنى"


class MemorizeMessage(models.Model):
    master_name = models.ForeignKey(Master, verbose_name="اسم الأستاذ", on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="اسم الطالب")
    student_string = models.CharField(max_length=511, verbose_name="اسم الطالب", null=True, blank=True)
    sended_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    first_info = models.JSONField(default=dict, verbose_name="الحفظ", null=True)
    second_info = models.JSONField(default=dict, verbose_name="الحفظ قبل التعديل", null=True)
    message_type = models.IntegerField(verbose_name="نوع الرسالة", choices=MessageTypeChoice.choices, default=MessageTypeChoice.MEMO)

    def __str__(self):
        return f"رسالة التسميع {self.id}"

    class Meta:
        verbose_name = "رسالة تسميع"
        verbose_name_plural = "رسائل التسميع"


class ComingCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name="الفئة")
    points = models.IntegerField(verbose_name="قيمة النقاط", default=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "سبب الحضور"
        verbose_name_plural = "أسباب الحضور"


class Coming(models.Model):
    master_name = models.ForeignKey(Master, verbose_name="اسم الأستاذ", on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, verbose_name="اسم الطالب", on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    category = models.ForeignKey(ComingCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="سبب الحضور")
    is_doubled = models.BooleanField(verbose_name="القيمة مضاعفة", default=False)

    def __str__(self):
        return f"تسجيل حضور {self.id}"

    class Meta:
        verbose_name = "تسجيل حضور"
        verbose_name_plural = "تسجيلات الحضور"


class ControlSettings(models.Model):
    double_points = models.BooleanField(default=False, verbose_name="مضاعفة النقاط")
    point_value = models.IntegerField(verbose_name="قيمة النقطة")
    hidden_ids = models.JSONField(verbose_name="المعرفات المخفية", default=list)


class DoublePointMessage(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    sended_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    points = models.IntegerField(verbose_name="النقاط")
    content = models.JSONField(default=dict, verbose_name="التسميع الذي تم مضاعفته", null=True)
    memorize_message = models.OneToOneField(MemorizeMessage, on_delete=models.CASCADE, null=True, blank=True, verbose_name="رسالة التسميع")
    message_type = models.IntegerField(choices=DoubleMessageTypeChoice.choices, default=DoubleMessageTypeChoice.MEMO, verbose_name="نوع التسميع")

    def __str__(self):
        return f"رسالة مضاعفة {self.id}"

    class Meta:
        verbose_name = "رسالة مضاعفة"
        verbose_name_plural = "رسائل مضاعفة"


class PointsAddingCause(models.Model):
    name = models.CharField(max_length=255, verbose_name="الاسم")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "سبب إضافة"
        verbose_name_plural = "أسباب إضافة"


class PointsAdding(models.Model):
    master_name = models.ForeignKey(Master, verbose_name="اسم الأستاذ", on_delete=models.CASCADE, null=True)
    value = models.IntegerField(verbose_name="القيمة")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    cause = models.ForeignKey(PointsAddingCause, verbose_name="السبب", on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"إضافة نقاط {self.id}"

    class Meta:
        verbose_name = "إضافة نقاط"
        verbose_name_plural = "إضافات النقاط"


class MoneyDeletingCause(models.Model):
    name = models.CharField(max_length=511, verbose_name="الاسم")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "سبب غرامة"
        verbose_name_plural = "أسباب الغرامات"


class MoneyDeleting(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الاسم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    cause = models.ForeignKey(MoneyDeletingCause, on_delete=models.PROTECT, verbose_name="سبب الغرامة", null=True)
    active_to_points = models.BooleanField(verbose_name="مخصومة من النقاط", default=True)
    value = models.IntegerField(verbose_name="القيمة", null=True)
    is_money_main_value = models.BooleanField(default=True)

    def __str__(self):
        return f"غرامة {self.id}"

    class Meta:
        verbose_name = "غرامة"
        verbose_name_plural = "الغرامات"


class AwqafTestNoQ(models.Model):
    name = models.CharField(max_length=511, verbose_name="الاسم")
    points = models.IntegerField(verbose_name="النقاط")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "سبر أوقاف بغير القرآن"
        verbose_name_plural = "سبر الأوقاف بغير القرآن"


class AwqafNoQStudentRelation(models.Model):
    test = models.ForeignKey(AwqafTestNoQ, on_delete=models.CASCADE, verbose_name="سبر الأوقاف")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    is_old = models.BooleanField(default=False, verbose_name="هل السبر قديم")



# * Signals Section
User = get_user_model()

@receiver(post_save, sender=User)
def create_master(sender, instance, created, **kwargs):
    if created:
        Master.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_master(sender, instance, **kwargs):
    instance.master.save()



# helpers
def check_for_cer(dictionary):
    result = {}
    for i in dictionary:
        non = 0
        old = 0
        new = 0
        error = 0
        for j in dictionary[i]:
            for k in dictionary[i][j]:
                if dictionary[i][j][k] == "NON":
                    non += 1
                elif dictionary[i][j][k] == "OLD":
                    old += 1
                elif dictionary[i][j][k] == "NEW":
                    new += 1
                else:
                    error += 1
        if error != 0:
            result[i] = "ERROR"
        elif non != 0:
            result[i] = "NON"
        elif new != 0:
            result[i] = "NEW"
        else:
            result[i] = "OLD"

    return result