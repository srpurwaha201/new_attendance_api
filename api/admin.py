from django.contrib import admin

# Register your models here.
from .models import Student, Teacher, Subject, Section, Timetable, Attendance 


admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Section)
admin.site.register(Timetable)
admin.site.register(Attendance)