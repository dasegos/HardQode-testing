from django.contrib import admin
from .models import *

admin.site.register(Group)

@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('title', )}
    
@admin.register(Lesson)
class AdminLesson(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('title', )}