from django.contrib import admin

from .models import Workspace, WorkspaceUser, WorkspaceCustomer, Position, Action


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    list_per_page = 15


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    list_per_page = 15


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    list_per_page = 15


@admin.register(WorkspaceUser)
class WorkspaceUserAdmin(admin.ModelAdmin):
    list_filter = ('workspace',)
    list_display = ('user', 'workspace', 'joined_at', 'left_at')
    search_fields = ('user__phone_number', 'workspace__name')
    list_per_page = 15


@admin.register(WorkspaceCustomer)
class WorkspaceCustomerAdmin(admin.ModelAdmin):
    list_filter = ('workspace',)
    list_display = ('customer', 'workspace', 'joined_at', 'left_at')
    search_fields = ('customer__phone_number', 'workspace__name')
    list_per_page = 15