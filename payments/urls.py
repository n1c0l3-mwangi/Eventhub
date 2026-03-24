from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:booking_id>/', views.process_payment, name='process'),
    path('history/', views.payment_history, name='history'),
    path('receipt/<str:transaction_id>/', views.payment_receipt, name='receipt'),
]