from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404,redirect
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from tourister.models import Package_Booking
from .models import Package_Details, DayWiseItinerary
from .serializers import (
    PackageSerializer,
    DayWiseItinerarySerializer,
    DepotSignupSerializer
)

User = get_user_model()

# --- Authentication & User Management ---

class AdminLogin(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "adminlogin.html"

    def get(self, request):
       
        return Response({}, template_name=self.template_name)

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)
        
        if user and user.is_staff:
            login(request, user)
            return Response({"message": "Admin logged in"}, status=status.HTTP_200_OK)
        
        if request.accepted_renderer.format == 'html':
            return Response({"error": "Invalid credentials"}, template_name=self.template_name, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class AdminLogout(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    def get(self, request):
        logout(request)
        return redirect('admin_site:adminlogin')


class DepotSignup(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "depotsignup.html"

    def post(self, request):
        serializer = DepotSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Depot Manager created"}, status=201)
        return Response(serializer.errors, status=400)
    
    def get(self, request):
        # Fetch the managers from the database
        managers = User.objects.filter(role="depot_manager")
        
        # FIX 2: If the request is for HTML, pass the managers list to the template
        if request.accepted_renderer.format == 'html':
            return Response({'managers': managers}, template_name=self.template_name)
        
        data = [{"id": m.id, "username": m.username, "depot_name": m.depot_name} for m in managers]
        return Response(data)


class DepotManagerList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "depotmanagers.html"

    def get(self, request):
        managers = User.objects.filter(role="depot_manager")
        
        # Handle HTML request (rendering the page)
        if request.accepted_renderer.format == 'html':
            return Response({'managers': managers}, template_name=self.template_name)
        
        # Handle JSON request (Axios call)
        # ADDED: role and date_joined to match frontend expectations
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
    
    def delete(self, request, pk):
        manager = get_object_or_404(User, id=pk, role="depot_manager")
        manager.delete()
        return Response({"message": "Manager deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@method_decorator(csrf_exempt, name='dispatch')
class PackageAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "addpackage.html"

    def get(self, request, pk=None):
        if pk:
            package = get_object_or_404(Package_Details, id=pk)
            serializer = PackageSerializer(package)
            return Response(serializer.data)

        if request.accepted_renderer.format == 'html':
            return Response({}, template_name=self.template_name)

        packages = Package_Details.objects.all().order_by('-id')
        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Image upload-க்கு request.data-வை அப்படியே அனுப்பலாம்
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        
        print(serializer.errors) # பிழையை டெர்மினலில் பார்க்க
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        package = get_object_or_404(Package_Details, id=pk)
        serializer = PackageSerializer(package, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        package = get_object_or_404(Package_Details, id=pk)
        
        try:

            package.delete()
            return Response({
                "message": f"Package '{package.package_name}' deleted successfully."
            }, status=204) 
            
        except Exception as e:
            return Response({
                "error": "Something went wrong while deleting the package."
            }, status=500)

# --- Itinerary Management ---
@method_decorator(csrf_exempt, name='dispatch')
class DayWiseItineraryAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
        # partial=True handles 400 errors when updating title/desc without the full object
        serializer = DayWiseItinerarySerializer(itinerary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        DayWiseItinerary.objects.filter(id=pk).delete()
        return Response({"message": "Deleted"}, status=204)

class UpdatePackage(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "update_package.html"
    
    def get(self, request, pk):
        package = get_object_or_404(Package_Details, id=pk)
        return Response({'package': package, 'pk': pk}, template_name=self.template_name)

    def put(self, request, pk):
        package = get_object_or_404(Package_Details, id=pk)
        serializer = PackageSerializer(package, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
class BookingList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "bookinglist.html"
    
    def get(self, request, pk=None):
        if request.accepted_renderer.format == "html":
            return Response({})
            
        bookings = Package_Booking.objects.select_related('package', 'package__bus').order_by('-booking_date')
        
        data = []
        for b in bookings:
            data.append({
                "id": b.id,
                "adults": b.adults,
                "children": b.children,
                "boarding_point": b.boarding_point,
                "total_price": b.total_price,
                "booking_date": b.booking_date.isoformat(), 
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
        return Response(data)
    