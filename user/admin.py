from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm,CustomUserChangeForm
from .models import Users,Token,Profile

class TokenAdminTabInline(admin.TabularInline):
    model = Token
    extra = 0
    readonly_fields =('token',)

@admin.register(Users)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Users
    list_display = ("email", "full_name", "is_active", "role")
    inlines=[TokenAdminTabInline]
    filter_horizontal=[]
    list_filter=[]
    readonly_fields = ["last_login", "date_joined", "waktu_aktifasi","last_password_reset_request"]
    fieldsets = [ ]
    fieldsets = (
        ("Informasi", {
         "fields": ("email", "full_name", "password", "last_login", "date_joined", "waktu_aktifasi","last_password_reset_request")}),

        ("Permissions", {"fields": ("is_active", "role","groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email","full_name","role","password1","password2", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

@admin.register(Profile)    
class ProfileAdmin(admin.ModelAdmin):
    pass