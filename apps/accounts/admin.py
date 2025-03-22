from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib import admin
from django import forms

import re

from .models import AdminUser, Customer, User


class UserAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="Mật khẩu",
        required=False,
        widget=forms.PasswordInput,
        help_text="Để trống để giữ mật khẩu hiện tại. Nhập giá trị mới để thay đổi."
    )

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return make_password(password)

        if self.instance.pk:
            return self.instance.password

        return make_password(None)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_per_page = 15

    ordering = ('-created_at',)
    list_filter = ('type', 'status', 'gender', 'is_delete')
    autocomplete_fields = ('updated_by', 'created_by')
    search_fields = ('full_name', 'phone_number', 'code', 'email')
    list_display = ('id', 'code', 'masked_phone_number', 'full_name', 'email', 'type', 'gender', 'status', 'is_delete')
    readonly_fields = ('updated_at', 'created_at', 'deleted_at', 'is_delete', 'deleted_by', 'code')

    form = UserAdminForm
    
    def get_exclude(self, request, obj = None):
        exclude = super().get_exclude(request, obj)
        if obj and obj.is_delete:
            obj.phone_number = re.sub(f'__deleted__{obj.pk}', '', obj.phone_number)
            obj.password = None
        return exclude
    
    def masked_phone_number(self, obj):
        if not obj.is_delete:
            return obj.phone_number
        return re.sub(f'__deleted__{obj.pk}', '', obj.phone_number)
    
    masked_phone_number.short_description = 'Số điện thoại'

    def get_queryset(self, request):
        path_info = request.path_info
        is_detail_view = '/change/' in path_info
        queryset = super().get_queryset(request).select_related('updated_by', 'created_by')
        
        if is_detail_view or "is_delete__exact" in request.GET:
            return queryset

        return queryset.filter(is_delete=False)
    
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
    
    def delete_model(self, request, obj):
        obj.delete()
    
    def has_change_permission(self, request, obj=None):
        if obj and obj.is_delete:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_delete:
            return False
        return super().has_delete_permission(request, obj)


class CustomerAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="Mật khẩu",
        required=False,
        widget=forms.PasswordInput,
        help_text="Để trống để giữ mật khẩu hiện tại. Nhập giá trị mới để thay đổi."
    )

    class Meta:
        model = Customer
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return make_password(password)

        if self.instance.pk:
            return self.instance.password

        return make_password(None)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_per_page = 15

    ordering = ('-created_at',)
    autocomplete_fields = ('representative',)
    list_filter = ('status', 'gender', 'is_delete')
    search_fields = ('full_name', 'phone_number', 'code', 'email')
    list_display = ('id', 'code', 'masked_phone_number', 'full_name', 'email', 'gender', 'status', 'is_delete')
    readonly_fields = ('updated_at', 'created_at', 'deleted_at', 'is_delete', 'code')

    form = CustomerAdminForm
    
    def get_exclude(self, request, obj = None):
        exclude = super().get_exclude(request, obj)
        if obj and obj.is_delete:
            obj.phone_number = re.sub(f'__deleted__{obj.pk}', '', obj.phone_number)
            obj.password = None
        return exclude
    
    def masked_phone_number(self, obj):
        if not obj.is_delete:
            return obj.phone_number
        return re.sub(f'__deleted__{obj.pk}', '', obj.phone_number)
    
    masked_phone_number.short_description = 'Số điện thoại'

    def get_queryset(self, request):
        path_info = request.path_info
        is_detail_view = '/change/' in path_info
        queryset = super().get_queryset(request)
        
        if is_detail_view or  "is_delete__exact" in request.GET:
            return queryset

        return queryset.filter(is_delete=False)
    
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
    
    def delete_model(self, request, obj):
        obj.delete()
    
    def has_change_permission(self, request, obj=None):
        if obj and obj.is_delete:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_delete:
            return False
        return super().has_delete_permission(request, obj)
    

class AdminUserAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="Mật khẩu",
        required=False,
        widget=forms.PasswordInput,
        help_text="Để trống để giữ mật khẩu hiện tại. Nhập giá trị mới để thay đổi."
    )

    class Meta:
        model = AdminUser
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return make_password(password)

        if self.instance.pk:
            return self.instance.password

        return make_password(None)


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_per_page = 15

    ordering = ('-id',)
    search_fields = ('full_name', 'username')
    list_display = ('id', 'username', 'full_name')

    form = AdminUserAdminForm

    def has_delete_permission(self, request, obj=None):
        if obj:
            master_user = AdminUser.objects.only("id").last()
            if master_user:
                return master_user.id != obj.id
        return False


admin.site.unregister(Group)
