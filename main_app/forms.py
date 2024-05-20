from django import forms
from main_app.models import ControlSettings, NewStudent, StudentClass


class SettingForm(forms.ModelForm):
    class Meta:
        model = ControlSettings
        fields = ["double_points", "event_title", "point_value"]
        widgets = {
            "double_points": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "event_title": forms.Textarea(
                attrs={"class": "form-control w-50 d-inline-block", "rows": 3}
            ),
            "point_value": forms.NumberInput(
                attrs={"class": "form-control w-50 d-inline-block"}
            ),
        }


class NewStudentForm(forms.ModelForm):
    first_name = forms.CharField(
        label="الاسم",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="الكنية",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    father_name = forms.CharField(
        label="اسم الأب",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    mother_name = forms.CharField(
        label="اسم الأم",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    birthdate = forms.CharField(
        label="تاريخ الميلاد",
        widget=forms.DateInput(attrs={
            "class": "form-control", 
            "type": "date",
            "min": "2005-01-01",
            "max": "20017-01-01",
        })
    )
    student_class = forms.CharField(
        label="الصف الدراسي",
        widget=forms.Select(
            choices=StudentClass.choices,
            attrs={"class": "form-control"},
        )
    )
    static_phone = forms.CharField(
        label="الهاتف الأرضي",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 20, "type": "tel"})
    )
    cell_phone = forms.CharField(
        label="الجوال",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 20, "type": "tel"})
    )
    father_phone = forms.CharField(
        label="جوال الأب",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 20, "type": "tel"})
    )
    mother_phone = forms.CharField(
        label="جوال الأم",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 20, "type": "tel"})
    )
    father_work = forms.CharField(
        label="عمل الأب",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    notes = forms.CharField(
        label="ملاحظات إضافية",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control"})
    )

    class Meta:
        model = NewStudent
        fields = "__all__"