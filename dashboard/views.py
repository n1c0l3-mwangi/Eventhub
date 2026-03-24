from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from events.models import Event
from tickets.models import Ticket
from payments.models import Payment
from accounts.models import User

@login_required
def organizer_dashboard(request):
    """Dashboard for event organizers only"""
    # Check if user is an organizer
    if request.user.user_type != 'organizer':
        messages.error(request, 'Access denied. Organizer privileges required.')
        return redirect('home')
    
    # Get organizer's events
    events = Event.objects.filter(organizer=request.user)
    
    # Statistics
    total_events = events.count()
    total_tickets_sold = events.aggregate(total=Sum('tickets_sold'))['total'] or 0
    
    # Calculate revenue
    total_revenue = 0
    for event in events:
        total_revenue += event.tickets_sold * event.price
    
    # Upcoming events
    upcoming_events = events.filter(
        start_date__gte=timezone.now(),
        status='approved'
    ).order_by('start_date')
    
    # Recent ticket sales
    recent_tickets = Ticket.objects.filter(
        event__organizer=request.user
    ).select_related('event', 'user').order_by('-purchased_at')[:10]
    
    context = {
        'events': events,
        'total_events': total_events,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
        'upcoming_events': upcoming_events,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'dashboard/organizer.html', context)


@login_required
def admin_dashboard(request):
    """Dashboard for system administrators only"""
    # Check if user is admin or superuser
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # System statistics
    total_users = User.objects.count()
    total_organizers = User.objects.filter(user_type='organizer').count()
    total_event_goers = User.objects.filter(user_type='event_goer').count()
    
    total_events = Event.objects.count()
    pending_events = Event.objects.filter(status='pending').count()
    approved_events = Event.objects.filter(status='approved').count()
    
    total_tickets = Ticket.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    # Events pending approval
    pending_approval = Event.objects.filter(status='pending').order_by('created_at')
    
    # Recent users
    recent_users = User.objects.all().order_by('-date_joined')[:10]
    
    context = {
        'total_users': total_users,
        'total_organizers': total_organizers,
        'total_event_goers': total_event_goers,
        'total_events': total_events,
        'pending_events': pending_events,
        'approved_events': approved_events,
        'total_tickets': total_tickets,
        'total_revenue': total_revenue,
        'pending_approval': pending_approval,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard/admin.html', context)


@login_required
def event_analytics(request, event_id):
    """View analytics for a specific event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is the organizer or admin
    if request.user != event.organizer and not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, 'Access denied. You cannot view analytics for this event.')
        return redirect('home')
    
    # Get ticket sales data
    tickets_sold = Ticket.objects.filter(event=event).count()
    total_revenue = tickets_sold * event.price
    
    context = {
        'event': event,
        'tickets_sold': tickets_sold,
        'total_revenue': total_revenue,
        'available_tickets': event.available_tickets,
    }
    return render(request, 'dashboard/event_analytics.html', context)


@login_required
def approve_event(request, event_id):
    """Approve a pending event (admin only)"""
    # Check if user is admin or superuser
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    event = get_object_or_404(Event, id=event_id)
    
    # Only allow approving pending events
    if event.status == 'pending':
        event.status = 'approved'
        event.save()
        messages.success(request, f'Event "{event.title}" has been approved successfully.')
    else:
        messages.warning(request, f'Event "{event.title}" is already {event.status}.')
    
    return redirect('dashboard:admin_dashboard')


@login_required
def reject_event(request, event_id):
    """Reject a pending event (admin only)"""
    # Check if user is admin or superuser
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    event = get_object_or_404(Event, id=event_id)
    
    if event.status == 'pending':
        event.status = 'rejected'
        event.save()
        messages.success(request, f'Event "{event.title}" has been rejected.')
    else:
        messages.warning(request, f'Event "{event.title}" is already {event.status}.')
    
    return redirect('dashboard:admin_dashboard')