from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('event/<int:event_id>/analytics/', views.event_analytics, name='event_analytics'),
    path('approve-event/<int:event_id>/', views.approve_event, name='approve_event'),
]