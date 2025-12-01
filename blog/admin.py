from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'category', 'location', 'status', 'author', 'date_posted')
    list_filter = ('item_type', 'category', 'status', 'date_posted', 'author')
    search_fields = ('title', 'content', 'location')
    date_hierarchy = 'date_posted'
    ordering = ('-date_posted',)
    
    fieldsets = (
        ('Item Information', {
            'fields': ('title', 'content', 'item_type', 'category', 'status', 'image')
        }),
        ('Location & Date', {
            'fields': ('location', 'date_item_lost_found')
        }),
        ('Author', {
            'fields': ('author',)
        }),
        ('Timestamps', {
            'fields': ('date_posted',)
        }),
    )
