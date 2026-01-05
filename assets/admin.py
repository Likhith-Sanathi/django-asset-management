from django.contrib import admin
from .models import Asset, AssetDocument, ActivityLog


class AssetDocumentInline(admin.TabularInline):
    model = AssetDocument
    extra = 1


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'value', 'owner', 'start_date', 'created_at']
    list_filter = ['category', 'owner', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    inlines = [AssetDocumentInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AssetDocument)
class AssetDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['name', 'asset__name']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'asset_name', 'timestamp']
    list_filter = ['action', 'timestamp', 'user']
    search_fields = ['asset_name', 'user__username', 'details']
    readonly_fields = ['user', 'action', 'asset_name', 'asset_category', 'details', 'ip_address', 'timestamp']
