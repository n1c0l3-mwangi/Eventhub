from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('purchase/<int:event_id>/', views.purchase_ticket, name='purchase'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),
]