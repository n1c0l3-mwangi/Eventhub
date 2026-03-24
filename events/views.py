from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Event, Category
from notifications.models import Notification


def home(request):
    """Home page with featured events"""
    featured_events = Event.objects.filter(
        status='approved',
        start_date__gte=timezone.now()
    ).order_by('start_date')[:6]
    
    categories = Category.objects.all()
    
    context = {
        'featured_events': featured_events,
        'categories': categories,
    }
    return render(request, 'events/home.html', context)


def event_list(request):
    """List all events with search and filters"""
    events = Event.objects.filter(status='approved', start_date__gte=timezone.now())
    categories = Category.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(venue__icontains=query) |
            Q(city__icontains=query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        events = events.filter(category_id=category_id)
    
    # Date filter
    date_filter = request.GET.get('date')
    if date_filter == 'today':
        events = events.filter(start_date__date=timezone.now().date())
    elif date_filter == 'tomorrow':
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        events = events.filter(start_date__date=tomorrow)
    elif date_filter == 'this_week':
        end_week = timezone.now() + timezone.timedelta(days=7)
        events = events.filter(start_date__lte=end_week)
    elif date_filter == 'this_month':
        end_month = timezone.now() + timezone.timedelta(days=30)
        events = events.filter(start_date__lte=end_month)
    
    context = {
        'events': events,
        'categories': categories,
        'search_query': query,
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, pk):
    """Display event details - Admins can see pending events"""
    # Allow admins and superusers to see pending events for approval
    if request.user.is_authenticated and (request.user.is_superuser or request.user.user_type == 'admin'):
        event = get_object_or_404(Event, pk=pk)
    else:
        event = get_object_or_404(Event, pk=pk, status='approved')
    
    context = {
        'event': event,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def create_event(request):
    """Create a new event (organizers only)"""
    if request.user.user_type != 'organizer':
        messages.error(request, 'Only organizers can create events')
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        venue = request.POST.get('venue')
        address = request.POST.get('address')
        city = request.POST.get('city')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        registration_deadline = request.POST.get('registration_deadline')
        total_capacity = request.POST.get('total_capacity')
        price = request.POST.get('price')
        featured_image = request.FILES.get('featured_image')
        
        event = Event.objects.create(
            title=title,
            description=description,
            category_id=category_id,
            organizer=request.user,
            venue=venue,
            address=address,
            city=city,
            start_date=start_date,
            end_date=end_date,
            registration_deadline=registration_deadline,
            total_capacity=total_capacity,
            price=price,
            featured_image=featured_image,
            status='pending'
        )
        
        messages.success(request, 'Event created successfully! Pending approval.')
        return redirect('dashboard:organizer_dashboard')
    
    categories = Category.objects.all()
    return render(request, 'events/create_event.html', {'categories': categories})


@login_required
def edit_event(request, pk):
    """Edit an existing event"""
    event = get_object_or_404(Event, pk=pk)
    
    # Check if user is the organizer
    if event.organizer != request.user:
        messages.error(request, 'You cannot edit this event')
        return redirect('events:event_detail', pk=pk)
    
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.category_id = request.POST.get('category')
        event.venue = request.POST.get('venue')
        event.address = request.POST.get('address')
        event.city = request.POST.get('city')
        event.start_date = request.POST.get('start_date')
        event.end_date = request.POST.get('end_date')
        event.registration_deadline = request.POST.get('registration_deadline')
        event.total_capacity = request.POST.get('total_capacity')
        event.price = request.POST.get('price')
        
        if request.FILES.get('featured_image'):
            event.featured_image = request.FILES.get('featured_image')
        
        event.save()
        messages.success(request, 'Event updated successfully!')
        return redirect('events:event_detail', pk=pk)
    
    categories = Category.objects.all()
    context = {
        'event': event,
        'categories': categories,
    }
    return render(request, 'events/edit_event.html', context)