from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from events.models import Event
from .models import Booking, Ticket


@login_required
def purchase_ticket(request, event_id):
    """Handle ticket purchase process"""
    event = get_object_or_404(Event, pk=event_id, status='approved')
    
    # Check if tickets are available
    if event.available_tickets <= 0:
        messages.error(request, 'Sorry, this event is sold out!')
        return redirect('events:event_detail', pk=event_id)
    
    # Check registration deadline
    if event.registration_deadline < timezone.now():
        messages.error(request, 'Registration deadline has passed')
        return redirect('events:event_detail', pk=event_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate quantity
        if quantity > event.available_tickets:
            messages.error(request, f'Only {event.available_tickets} tickets available')
            return redirect('tickets:purchase', event_id=event_id)
        
        if quantity < 1:
            messages.error(request, 'Please select at least 1 ticket')
            return redirect('tickets:purchase', event_id=event_id)
        
        # Calculate total
        total_amount = quantity * event.price
        
        # For FREE events, create tickets directly without payment
        if event.is_free or event.price == 0:
            # Create tickets directly
            tickets_created = []
            for _ in range(quantity):
                ticket = Ticket.objects.create(
                    event=event,
                    user=request.user,
                    quantity=1,
                    total_amount=0
                )
                tickets_created.append(ticket)
            
            # Update event tickets sold count
            event.tickets_sold += quantity
            event.save()
            
            # Send confirmation email for free tickets
            try:
                ticket_details = ""
                for t in tickets_created:
                    ticket_details += f"  - Ticket ID: {t.ticket_id}\n"
                
                email_subject = f'Free Ticket Confirmation - {event.title}'
                email_message = f"""
Hello {request.user.username},

Your FREE ticket(s) for {event.title} have been confirmed!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Event: {event.title}
Date: {event.start_date}
Venue: {event.venue}
Location: {event.city}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TICKET INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quantity: {quantity}
Price: FREE

{ticket_details}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You can view your tickets at: http://127.0.0.1:8000/tickets/my-tickets/

Thank you for using Eventify Kenya!
                    """
                
                send_mail(
                    subject=email_subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )
                print(f"✓ Free ticket email sent to {request.user.email}")
                
            except Exception as e:
                print(f"✗ Email failed: {e}")
            
            messages.success(request, f'Successfully booked {quantity} free ticket(s)!')
            return redirect('tickets:my_tickets')
        
        # For paid events, create booking and redirect to payment
        else:
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                event=event,
                quantity=quantity,
                total_amount=total_amount,
                expires_at=timezone.now() + timezone.timedelta(minutes=15)
            )
            
            # Redirect to payment
            return redirect('payments:process', booking_id=booking.id)
    
    context = {
        'event': event,
        'max_tickets': min(10, event.available_tickets)
    }
    return render(request, 'tickets/purchase.html', context)


@login_required
def my_tickets(request):
    """View user's tickets"""
    tickets = Ticket.objects.filter(user=request.user).select_related('event')
    
    upcoming_tickets = tickets.filter(
        event__start_date__gte=timezone.now(),
        status='active'
    )
    past_tickets = tickets.filter(
        event__start_date__lt=timezone.now()
    )
    
    context = {
        'upcoming_tickets': upcoming_tickets,
        'past_tickets': past_tickets,
    }
    return render(request, 'tickets/my_tickets.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """View ticket details with QR code"""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    
    context = {
        'ticket': ticket
    }
    return render(request, 'tickets/ticket_detail.html', context)