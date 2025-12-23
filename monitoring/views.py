from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import SecurityEvent, Alert
from .serializers import SecurityEventSerializer, AlertSerializer
from .permissions import IsAdminOrReadOnly

class EventIngestView(generics.CreateAPIView):
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
    permission_classes = (permissions.IsAuthenticated,)

class AlertListView(generics.ListAPIView):
    queryset = Alert.objects.select_related('event').all()
    serializer_class = AlertSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'event__severity']
    ordering_fields = ['created_at', 'status']
    search_fields = ['event__source', 'event__description', 'event__event_type']

class AlertDetailView(generics.RetrieveAPIView):
    queryset = Alert.objects.select_related('event').all()
    serializer_class = AlertSerializer
    permission_classes = (permissions.IsAuthenticated,)

class AlertStatusUpdateView(generics.UpdateAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = (permissions.IsAdminUser,)
    http_method_names = ['patch']

    def perform_update(self, serializer):
        # Only allow updating status
        serializer.save()
