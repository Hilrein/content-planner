from django.contrib import admin
from .models import ContentPlan, ContentItem, ContentCategory

@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(ContentPlan)
class ContentPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at', 'updated_at')
    list_filter = ('owner',)
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_plan', 'category', 'status', 'scheduled_date')
    list_filter = ('status', 'category', 'content_plan')
    search_fields = ('title', 'content')
    date_hierarchy = 'scheduled_date'
    readonly_fields = ('created_at', 'updated_at')
