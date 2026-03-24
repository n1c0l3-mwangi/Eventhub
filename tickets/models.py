from django.db import models
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
import uuid

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_reference = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return self.booking_reference
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"BK{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('used', 'Used'),
        ('cancelled', 'Cancelled'),
    )
    
    ticket_id = models.CharField(max_length=50, unique=True)
    # THIS LINE IS NOW FIXED - added related_name='tickets'
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-purchased_at']
    
    def __str__(self):
        return self.ticket_id
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = f"TKT{uuid.uuid4().hex[:8].upper()}"
        
        if not self.qr_code:
            self.generate_qr_code()
        
        super().save(*args, **kwargs)
    
    def generate_qr_code(self):
        """Generate QR code for ticket"""
        qr_data = f"{self.ticket_id}\n{self.event.title}\n{self.user.email}"
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'ticket_{self.ticket_id}.png'
        
        # Save to ImageField
        self.qr_code.save(filename, File(buffer), save=False)