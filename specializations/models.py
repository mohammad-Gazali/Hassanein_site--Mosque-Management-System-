from django.db import models
from main_app.models import Student, Master


class Specialization(models.Model):
    name = models.CharField(max_length=511, verbose_name="الاسم")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "اختصاص"
        verbose_name_plural = "الاختصاصات"


class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name="الاسم")
    specialization = models.ForeignKey(Specialization, verbose_name="الاختصاص", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"اختصاص {self.specialization} مقرر {self.name}"

    class Meta:
        verbose_name = "مقرر"
        verbose_name_plural = "المقررات"


class Part(models.Model):
    subject = models.ForeignKey(Subject, verbose_name="المقرر", on_delete=models.CASCADE)
    part_content = models.CharField(max_length=255, verbose_name="محتوى القسم")
    part_number = models.IntegerField(default=1, verbose_name="ترتيب القسم")
    points = models.IntegerField(verbose_name="النقاط")
    

    def __str__(self) -> str:
        return f"اختصاص {self.subject.specialization} مقرر {self.subject.name} {self.part_content}"

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "أقسام"


class StudentSpecializationPartRelation(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_old = models.BooleanField(default=False)

    class Meta:
        unique_together = ["part", "student"]


class SpecializationMessage(models.Model):
    student = models.ForeignKey(Student, verbose_name="الطالب", on_delete=models.CASCADE)
    master = models.ForeignKey(Master, verbose_name="الأستاذ", on_delete=models.CASCADE)
    part = models.ForeignKey(Part, verbose_name="القسم", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "رسالة اختصاص"
        verbose_name_plural = "رسائل اختصاص"
