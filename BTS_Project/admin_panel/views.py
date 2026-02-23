from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404,redirect,render
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from tourister.models import Package_Booking
from django.db.models import Sum
from .models import Package_Details, DayWiseItinerary
from .serializers import (
    PackageSerializer,
    DayWiseItinerarySerializer,
    DepotSignupSerializer,
    HotelSignupSerializer
)
from payment.models import Transaction

User = get_user_model()


class AddHotelTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "addhotel.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})

class AddPackageTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "addpackage.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})

class AdminLoginTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "adminlogin.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})

class BookingListTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "bookinglist.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})

class DashboardTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "dashboard.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})

class DepotManagersTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "depotmanagers.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})

class DepotSignupTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "depotsignup.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})

class HotelListTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "hotellist.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})

    
    
class AdminLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            return Response(
                {"error": "Both username and password are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        
        if user.is_staff:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "username": user.username,
                    "email": user.email
                },
                "message": "Welcome Admin!"
            }, status=status.HTTP_200_OK)
            
        
        return Response({
            "error": "Access Denied: Invalid credentials or insufficient permissions."
        }, status=status.HTTP_403_FORBIDDEN)


class AdminLogout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {'message': 'Successfully logged out'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': 'Invalid token or token already blacklisted'},
                status=status.HTTP_400_BAD_REQUEST
            )

class Dashboard(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Summary Statistics
        total_packages = Package_Details.objects.count()
        total_bookings = Package_Booking.objects.count()
        
        # 2. Revenue from stored 'amount' field in Transaction
        total_revenue = Transaction.objects.filter(
            status="Success"
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # 3. Role Statistics
        role_stats = {
            "tourists": User.objects.filter(role__icontains="Tourister").count(),
            "admins": User.objects.filter(is_superuser=True).count(),
            "managers": User.objects.filter(role__icontains="depot_manager").count(),
            "hotels": User.objects.filter(role__icontains="Hotel").count(),
        }

        recent_qs = Package_Booking.objects.select_related('package', 'user').order_by('-booking_date')[:5]
        
        recent_bookings = []
        for b in recent_qs:
            recent_bookings.append({
                "id": f"BTC{b.id}",
                "pkg": b.package.package_name if b.package else "N/A", 
                "user": b.user.username if b.user else "Anonymous",
                "amount": b.total_price or 0 
            })

        data = {
            "summary": {
                "packages": total_packages,
                "bookings": total_bookings,
                "tourists": role_stats["tourists"],
                "revenue": total_revenue 
            },
            "roles": role_stats,
            "recentBookings": recent_bookings
        }
        return Response(data)
    
    

class DepotSignup(APIView):
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [JSONRenderer]

    def get(self, request):
        managers = User.objects.filter(role="depot_manager")
        
      
        if request.accepted_renderer.format == 'html':
            return Response({'managers': managers}, template_name=self.template_name)
        
        
        data = [
            {
                "id": m.id,
                "username": m.username,
                "email": m.email,
                "depot_name": m.depot_name,
                "role": m.role,
                "date_joined": m.date_joined.isoformat() if m.date_joined else ""
            } for m in managers
        ]
        return Response(data)

    def post(self, request):
        """Create a new Depot Manager"""
        serializer = DepotSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Depot Manager created", "data": serializer.data}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        manager = get_object_or_404(User, id=pk, role="depot_manager")
        manager.delete()
        return Response({"message": "Manager deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

   
    
    

@method_decorator(csrf_exempt, name='dispatch')
class PackageAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request, pk=None):
        if pk:
            package = get_object_or_404(Package_Details, id=pk)
            serializer = PackageSerializer(package)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        packages = Package_Details.objects.all().order_by('-id')
        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        package = get_object_or_404(Package_Details, id=pk)
        serializer = PackageSerializer(package, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        package = get_object_or_404(Package_Details, id=pk)
        package_name = package.package_name 
        try:
            package.delete()
            return Response({"message": f"Package '{package_name}' deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class DayWiseItineraryAPI(APIView):
    permission_classes = [permissions.IsAuthenticated] 

    def get(self, request, pk=None):
        if pk:
            itinerary = get_object_or_404(DayWiseItinerary, id=pk)
            serializer = DayWiseItinerarySerializer(itinerary)
            return Response(serializer.data)
        itineraries = DayWiseItinerary.objects.all()
        serializer = DayWiseItinerarySerializer(itineraries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DayWiseItinerarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        itinerary = get_object_or_404(DayWiseItinerary, id=pk)
        serializer = DayWiseItinerarySerializer(itinerary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        DayWiseItinerary.objects.filter(id=pk).delete()
        return Response({"message": "Deleted"}, status=204)

class UpdatePackage(APIView):

    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "update_package.html"

    def get(self, request, pk):
        # 1. Fetch the object
        package = get_object_or_404(Package_Details, id=pk)

        # 2. Check if the request is for the HTML page or JSON data
        if request.accepted_renderer.format == 'html':
            # Returns the context needed for the Django Template
            return Response({'package': package, 'pk': pk}, template_name=self.template_name)
        
        # 3. If Axios/AJAX requests JSON, return serialized data
        serializer = PackageSerializer(package)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        # 1. Fetch the object
        package = get_object_or_404(Package_Details, id=pk)
        
        # 2. Use partial=True to allow updating specific fields (like price or name) 
        # without requiring all image fields to be re-uploaded.
        serializer = PackageSerializer(package, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # 3. Return errors if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    
class BookingList(APIView):
    # Only authenticated users can access this data
    permission_classes = [permissions.IsAuthenticated] 
    
    # We only need JSONRenderer now
    renderer_classes = [JSONRenderer]
    
    def get(self, request, pk=None):
        # Fetch data with select_related to optimize database queries (joins)
        bookings = Package_Booking.objects.select_related(
            'package', 
            'package__bus'
        ).order_by('-booking_date')
        
        data = []
        for b in bookings:
            data.append({
                "id": b.id,
                "adults": b.adults,
                "children": b.children,
                "boarding_point": b.boarding_point,
                "total_price": b.total_price,
                "booking_date": b.booking_date.isoformat() if b.booking_date else None, 
                "package": {
                    "package_name": b.package.package_name if b.package else "N/A",
                    "start_date": b.package.start_date if b.package else "-",
                    "end_date": b.package.end_date if b.package else "-",
                    "bus": {
                        "bus_name": b.package.bus.bus_name if b.package and b.package.bus else "KSRTC BTC",
                        "bus_number": b.package.bus.bus_number if b.package and b.package.bus else "KL-15-XXXX",
                    }
                }
            })
            
        return Response(data, status=status.HTTP_200_OK)
    
class HotelSignup(APIView):
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [JSONRenderer]

    def get(self, request):
        # Fetch only the users with the 'Hotel' role
        hotels = User.objects.filter(role="Hotel")
        
        # Simple list comprehension for data serialization
        data = [
            {
                "id": h.id, 
                "username": h.username, 
                "location": getattr(h, 'location', 'N/A') # Safe check if location exists
            } 
            for h in hotels
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HotelSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Hotel Partner created successfully"}, 
                status=status.HTTP_201_CREATED
            )
        
        # If validation fails, return the errors as JSON
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HotelList(APIView):
    # Pure JSON API - No Session or Basic Auth to interfere with Bearer tokens
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [JSONRenderer]

    def get(self, request, pk=None):
        # Fetch users with 'Hotel' role
        hotels = User.objects.filter(role='Hotel').order_by('-id')
        
        # Use your existing serializer for a clean JSON output
        serializer = HotelSignupSerializer(hotels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # Ensure we only delete users that actually have the Hotel role
        hotel = get_object_or_404(User, pk=pk, role='Hotel')
        hotel.delete()
        
        # Return 204 No Content for a successful deletion
        return Response(
            {"message": "Hotel deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    