from django.contrib import admin
from django.db import models
from .models import Student, Category, MemorizeMessage, MemorizeNotes, Coming, ComingCategory, DoublePointMessage, Master, PointsAddingCause, PointsDeletingCause
from django_json_widget.widgets import JSONEditorWidget


admin.site.site_title = 'لوحة إدارة مسجد الحسنين'
admin.site.site_header = 'إدارة مسجد الحسنين'


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['name']

# Here we add an action besides to delete action, visit (https://docs.djangoproject.com/en/4.1/ref/contrib/admin/actions/) for more information
@admin.action(description='تحديث حالة السبر')
def update_q_test_certifcate(modeladmin, requset, queryset):
    students =Student.objects.all()
    for st in students:
        if st.q_test_certificate == 'لا يوجد':
            st.is_q_test_certificate = False
        else:
            st.is_q_test_certificate = True
        st.save()




@admin.register(Student)
class AdminStudent(admin.ModelAdmin):
    list_display = ['name', 'age', 'category', 'mother_name', 'q_test_certificate', 'is_q_test_certificate']
    search_fields = ['name']
    list_select_related = ['category']
    list_filter = ['category', 'is_q_test_certificate']
    exclude = ['is_q_test_certificate']
    actions = [update_q_test_certifcate]

    # here changed the widget of JSONField into another widget, this widget is imported from django_json_widget.widgets
    # we should firstly install the module 'django-json-widget' by using 'pip install django-json-widget', then we should go INSTALLED_APPS in settings.py and add 'django_json_widget'
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(mode='code', options={
            'modes': ['code', 'form'],
            'mode': 'code',
            'search': True,
        })}
    }

    # here we will define method that make us to edit 'add object' and 'change object' separatly
    def get_form(self, request, obj=None,**kwargs):
        # here the property kwargs (which we used below) has these keys: form, fields, exclude, formfield_callback
        
        # here when the object has already been added (change object case) 
        if obj:
            kwargs['exclude'] = ('is_q_test_certificate',)

        # here when the object doesn't exisit (add object case) 
        else:
            kwargs['exclude'] = ('q_memorizing', 'q_test', 'q_test_candidate', 'q_awqaf_test', 'is_q_test_certificate')
        return super().get_form(request, obj, **kwargs)


    # this is another method for doing what did in get_form() method
    # def add_view(self,request,extra_content=None):
    #     self.exclude = ('q_memorizing',)
    #     return super().add_view(request)
    
    # def change_view(self,request,object_id,extra_content=None):
    #     self.exclude = ()
    #     return super().change_view(request,object_id)


@admin.register(MemorizeMessage)
class AdminMemorizeMessage(admin.ModelAdmin):
    list_display = ['id', 'master_name', 'student', 'message_type', 'sended_at']
    list_select_related = ['master_name__user', 'student']
    readonly_fields = ['master_name', 'student',  'message_type', 'sended_at', 'first_info']
    list_filter = ['master_name', 'message_type']
    search_fields = ['student_string']
    exclude = ['student_string', 'second_info']
    

    # this method prevent admin from deleting objects in this model
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    ormfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(mode='code', options={
            'modes': ['code', 'form'],
            'mode': 'code',
            'search': True,
        })}
    }

    # def time_seconds(self, obj):
    #     return obj.sended_at.strftime("%I:%M:%S || %Y-%m-%d")
    # time_seconds.short_description = 'تاريخ الإرسال' 


@admin.register(MemorizeNotes)
class AdminMemorizeNote(admin.ModelAdmin):
    list_display = ['master_name', 'student', 'sended_at']
    list_select_related = ['master_name__user', 'student']
    readonly_fields = ['master_name', 'student', 'content', 'sended_at']
    list_filter = ['master_name']
    search_fields = ['student_string']
    exclude = ['student_string']

    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_add_permission(self, request, obj=None) -> bool:
        return False

@admin.register(ComingCategory)
class ComingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Coming)
class ComingAdmin(admin.ModelAdmin):
    list_display = ['student', 'master_name', 'category', 'registered_at', 'note']
    list_filter = ['registered_at', 'category', 'note']
    list_select_related = ['student', 'master_name__user', 'category']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(DoublePointMessage)
class DoublePointMessageAdmin(admin.ModelAdmin):
    list_display = ['student', 'points', 'sended_at']
    list_select_related = ['student']
    readonly_fields = ['student', 'points', 'content']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PointsAddingCause)
class PointsAddingCauseAdmin(admin.ModelAdmin):
    pass


@admin.register(PointsDeletingCause)
class PointsDeletingCauseAdmin(admin.ModelAdmin):
    pass