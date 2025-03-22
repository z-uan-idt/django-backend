from django.contrib import admin

from .models import Logs


class LogsAdmin(admin.ModelAdmin):
    model = Logs
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Logs, LogsAdmin)