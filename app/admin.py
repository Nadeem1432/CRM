from django.contrib import admin
from app.models import *

# admin.site.register(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_admin',
        'is_super',
        'is_seller',
    )
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'customer_name',
        'pay_status',
        'created_at',
        'created_by',
    )
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )






@admin.register(Trns)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'designation',
        'train_no',
        'gateway',
        'pnr_time',
        'status',
        'created_at',
    )
    search_fields = (
        'train_no',
        'gateway',
        'pnr_time',
    )



@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = (
            'name',
            'user_id',
            'credit',
            'mode',
            'creater_name',
            'created_at',
            'updated_at',    )
    search_fields = (
        'name',
        'mode',
        'creater_name',
    )


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = (
            'message',
            'short_message',
            'news',
            'app_version',
            'dll_version',
            'created_at',
            'updated_at',    )
    search_fields = (
        'message',
        'app_version',
    )
