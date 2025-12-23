from rest_framework import serializers
from .models import SecurityEvent, Alert

class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    event_details = SecurityEventSerializer(source='event', read_only=True)
    
    class Meta:
        model = Alert
        fields = ('id', 'event', 'event_details', 'status', 'created_at')
        read_only_fields = ('created_at', 'event')
