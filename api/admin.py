from django.contrib import admin
# from imagekit.admin import AdminThumbnail

# Register your models here.
from .models import Student, Teacher, Subject, Section, Timetable, Attendance, Lab


# admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Section)
admin.site.register(Timetable)
admin.site.register(Attendance)
admin.site.register(Lab)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    # list_display = ['name', 'image_display']
    # image_display = AdminThumbnail(image_field='image')
    # image_display.short_description = 'Image'

    fields = ( "rollno", "user","image",'image_tag', )
    readonly_fields = ('image_tag',)

    # def student_image(self, obj):
    #     return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
    #         url = obj.image.url,
    #         width=obj.image.width,
    #         height=obj.image.height,
    #         )
    # )