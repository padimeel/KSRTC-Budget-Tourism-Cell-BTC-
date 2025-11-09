from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Package_Details,DayWiseItinerary

router = DefaultRouter()
router.register('packages', Package_Details)
router.register('itineraries', DayWiseItinerary)

urlpatterns = [
    path('', include(router.urls)),
]
