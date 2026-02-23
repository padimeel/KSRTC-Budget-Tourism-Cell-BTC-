from django.db import models
from django.db.models import Sum
from tourister.models import Package_Booking

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failure', 'Failure'),
        ('Refunded', 'Refunded'),
    )
    
    # Relationships
    booking = models.OneToOneField(
        Package_Booking, 
        on_delete=models.CASCADE, 
        related_name="payment_details",
        null=True, 
        blank=True
    )
    room_booking = models.OneToOneField(
        'tourister.RoomBooking', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Success")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically set the amount from the booking if not already set
        if not self.amount or self.amount == 0:
            if self.booking:
                self.amount = self.booking.total_price
            elif self.room_booking:
                self.amount = self.room_booking.total_price
        super().save(*args, **kwargs)

    def __str__(self):
        booking_id = "N/A"
        if self.booking:
            booking_id = f"PKG-{self.booking.id}"
        elif self.room_booking:
            booking_id = f"RM-{self.room_booking.id}"
            
        return f"Booking {booking_id} - {self.status} (₹{self.amount})"