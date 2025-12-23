from django.contrib import admin
from .models import SecurityEvent, Alert

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('source', 'event_type', 'severity', 'timestamp')
    list_filter = ('severity', 'timestamp')
    search_fields = ('source', 'event_type')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('event', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('status', 'event__source')
