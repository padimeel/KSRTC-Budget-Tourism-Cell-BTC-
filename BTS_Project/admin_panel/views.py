from rest_framework import viewsets, permissions
from .models import Package_Details, DayWiseItinerary
from .serializers import PackageSerializer, DayWiseItinerarySerializer

class Package_Details(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Package_Details.objects.all()
    serializer_class = PackageSerializer


class DayWiseItinerary(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = DayWiseItinerary.objects.all()
    serializer_class = DayWiseItinerarySerializer
