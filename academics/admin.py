from django.contrib import admin

from .models import (
    Department,
    Semester,
    Professor,
    Student,
    Subject,
    Room,
    Exam,
    Grade
)


admin.site.register(Department)
admin.site.register(Semester)
admin.site.register(Professor)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Room)
admin.site.register(Exam)
admin.site.register(Grade)

