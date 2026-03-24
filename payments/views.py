from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from tickets.models import Booking, Ticket
from .models import Payment
from .mobile_money import InternalMobilePaymentModule


@login_required
def process_payment(request, booking_id):
    """Process payment for a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if booking expired
    if booking.expires_at < timezone.now():
        messages.error(request, 'Booking expired. Please try again.')
        return redirect('tickets:purchase', event_id=booking.event.id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'mobile')
        phone_number = request.POST.get('phone_number', '')
        
        # Process payment with Internal Mobile Payment Module
        success, transaction_id, message = InternalMobilePaymentModule.process_payment(
            phone_number, booking.total_amount
        )
        
        if success:
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                booking=booking,
                amount=booking.total_amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                phone_number=phone_number,
                status='completed',
                completed_at=timezone.now()
            )
            
            # Create tickets
            tickets_created = []
            for _ in range(booking.quantity):
                ticket = Ticket.objects.create(
                    event=booking.event,
                    user=request.user,
                    quantity=1,
                    total_amount=booking.total_amount / booking.quantity
                )
                tickets_created.append(ticket)
            
            # Update event tickets sold count
            booking.event.tickets_sold += booking.quantity
            booking.event.save()
            
            # Send email confirmation
            try:
                ticket_details = ""
                for t in tickets_created:
                    ticket_details += f"  - Ticket ID: {t.ticket_id}\n"
                
                email_subject = f'Ticket Confirmation - {booking.event.title}'
                email_message = f"""
Hello {request.user.username},

Your ticket purchase for {booking.event.title} has been confirmed!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Event: {booking.event.title}
Date: {booking.event.start_date}
Venue: {booking.event.venue}
Location: {booking.event.city}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TICKET INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quantity: {booking.quantity}
Amount Paid: KES {booking.total_amount}
Transaction ID: {transaction_id}

{ticket_details}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You can view your tickets at: http://127.0.0.1:8000/tickets/my-tickets/

Thank you for using Eventhub Kenya!
                    """
                
                send_mail(
                    subject=email_subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )
                print(f"✓ Email sent to {request.user.email}")
                
            except Exception as e:
                print(f"✗ Email failed: {e}")
            
            messages.success(request, f'Payment successful! Transaction ID: {transaction_id}')
            return redirect('tickets:my_tickets')
        else:
            messages.error(request, f'Payment failed: {message}')
            return redirect('payments:process', booking_id=booking.id)
    
    context = {
        'booking': booking
    }
    return render(request, 'payments/process.html', context)


@login_required
def payment_history(request):
    """View user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/history.html', {'payments': payments})


@login_required
def payment_receipt(request, transaction_id):
    """View payment receipt"""
    payment = get_object_or_404(Payment, transaction_id=transaction_id, user=request.user)
    return render(request, 'payments/receipt.html', {'payment': payment})