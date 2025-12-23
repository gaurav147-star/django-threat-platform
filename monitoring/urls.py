from django.urls import path
from .views import EventIngestView, AlertListView, AlertDetailView, AlertStatusUpdateView

urlpatterns = [
    path('events/', EventIngestView.as_view(), name='event_ingest'),
    path('alerts/', AlertListView.as_view(), name='alert_list'),
    path('alerts/<int:pk>/', AlertDetailView.as_view(), name='alert_detail'),
    path('alerts/<int:pk>/status/', AlertStatusUpdateView.as_view(), name='alert_status'),
]
