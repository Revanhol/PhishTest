from django.contrib import admin
from .models import Course, Test, Question, Answer, TestResult, UserProfile

class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'completed_at')
    list_filter = ('test', 'completed_at')
    search_fields = ('user__username', 'test__title')

admin.site.register(Course)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(TestResult, TestResultAdmin)
admin.site.register(UserProfile)
