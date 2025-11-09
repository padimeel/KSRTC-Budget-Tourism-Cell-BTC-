from django.db import models

class Package_Details(models.Model):
    package_name = models.CharField(max_length=200)
    # image = models.ImageField(upload_to='packages/')
    package_overview = models.TextField()
    duration = models.CharField(max_length=100)  # Example: 1 Night & 2 Days
    places = models.JSONField(default=list)  # Store multiple places
    start_date = models.DateField()
    end_date = models.DateField()
    package_includes = models.JSONField(default=list)  # Store icons like ['fa-hotel', 'fa-bus']
    price = models.DecimalField(max_digits=10, decimal_places=2)

class DayWiseItinerary(models.Model):
    package = models.ForeignKey(Package_Details, related_name='itineraries', on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.package.package_name} - Day {self.day_number}: {self.title}"

