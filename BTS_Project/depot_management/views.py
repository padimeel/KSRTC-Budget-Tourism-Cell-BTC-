from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.contrib.auth import authenticate,login, logout
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from .serializers import BusDetailsSerializer, BusRouteSerializer
from .models import BusDetails, BusRoute
from admin_panel.models import Package_Details




class AddBusTemplate(APIView): 
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "addbus.html"
    
    def get(self, request, pk):
        return Response({'package_id': pk})
    
    
class AssignPackageTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer] 
    template_name = "assignpackage.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})
    
class DepotDashboardTemplate(APIView): 
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "depotdashboard.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})
    
class DepotLoginTemplate(APIView): 
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "depotlogin.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})
    
class UpdateBusTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "updatebus.html"

    def get(self, request, pk):
        return Response({'bus_id': pk})


# ---------------------- LOGIN API ----------------------

class Login(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'role') and (user.role == "depot_manager" or user.is_superuser):
                # Generate JWT Tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "username": user.username,
                    "depot_name": getattr(user, 'depot_name', 'Default Depot')
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Unauthorized: Access restricted to Depot Managers."
                }, status=status.HTTP_403_FORBIDDEN)
        
        return Response({"error": "Invalid Username or Password"}, status=status.HTTP_401_UNAUTHORIZED)

class DepotLogout(APIView):
    
    permission_classes = [permissions.IsAuthenticated] 
    def get(self, request):
        logout(request)
    
    
class BusAPI(APIView):
    permission_classes = [permissions.IsAuthenticated] 

    def get(self, request, pk=None):
        if pk:
            try:
                bus = BusDetails.objects.get(id=pk)
                serializer = BusDetailsSerializer(bus)
                return Response(serializer.data)
            except BusDetails.DoesNotExist:
                return Response({"error": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)

        buses = BusDetails.objects.all()
        serializer = BusDetailsSerializer(buses, many=True)
        return Response(serializer.data)

    def post(self, request):
        package_id = request.data.get('package')
        
       
        if BusDetails.objects.filter(package_id=package_id).exists():
            return Response(
                {"error": "This package already has a bus assigned. You cannot assign another one."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BusDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            bus = BusDetails.objects.get(id=pk)
        except BusDetails.DoesNotExist:
            return Response({"error": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)

       
        serializer = BusDetailsSerializer(bus, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            bus = BusDetails.objects.get(id=pk)
            bus.delete()
            return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except BusDetails.DoesNotExist:
            return Response({"error": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
class RouteAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                route = BusRoute.objects.get(id=pk)
                serializer = BusRouteSerializer(route)
                return Response(serializer.data)
            except BusRoute.DoesNotExist:
                return Response({"error": "Route not found"}, status=404)

        bus_id = request.query_params.get('bus_id')
        
        if bus_id:
            routes = BusRoute.objects.filter(bus_id=bus_id)
        else:
            routes = BusRoute.objects.all()

        serializer = BusRouteSerializer(routes, many=True)
        return Response(serializer.data)

    def post(self, request):
        bus_id = request.data.get("bus")
        
        if not BusDetails.objects.filter(id=bus_id).exists():
            return Response({"error": "Invalid bus ID"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BusRouteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            route = BusRoute.objects.get(id=pk)
        except BusRoute.DoesNotExist:
            return Response({"error": "Route not found"}, status=404)

        serializer = BusRouteSerializer(route, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            route = BusRoute.objects.get(id=pk)
            route.delete()
            return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except BusRoute.DoesNotExist:
            return Response({"error": "Route not found"}, status=404)
    
class AssignPackage(APIView):
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [JSONRenderer]

    def get(self, request, pk=None):
        # Fetch packages for the authenticated manager
        packages = Package_Details.objects.filter(
            assigned_depot_manager=request.user
        ).order_by('-id')
        
        data = []
        for pkg in packages:
            # Check if a bus is assigned to this package
            bus_obj = BusDetails.objects.filter(package=pkg).first()
            
            data.append({
                "id": pkg.id,
                "package_name": pkg.package_name,
                "duration": pkg.duration,
                "price": pkg.price,
                "start_date": pkg.start_date.isoformat() if pkg.start_date else None,
                "end_date": pkg.end_date.isoformat() if pkg.end_date else None,
                "places": pkg.places,
                "has_bus": bool(bus_obj),
                "bus_number": bus_obj.bus_number if bus_obj else None
            })
            
        return Response(data, status=status.HTTP_200_OK)

# class DepotDashboard(APIView):
    
    
#     renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
#     template_name = "depotdashboard.html"

#     def get(self, request, pk=None):
#         if request.accepted_renderer.format == 'html':
#             return Response({})
        
        


class UpdateBus(APIView):
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [JSONRenderer] # Only return JSON

    def get(self, request, pk):
        bus = get_object_or_404(BusDetails, id=pk)
        serializer = BusDetailsSerializer(bus)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            bus = BusDetails.objects.get(id=pk)
            bus_serializer = BusDetailsSerializer(bus, data=request.data, partial=True)
            
            if bus_serializer.is_valid():
                bus_serializer.save()
                
                # Logic for route update
                if hasattr(bus, 'route') and bus.route:
                    route_serializer = BusRouteSerializer(bus.route, data=request.data, partial=True)
                    if route_serializer.is_valid():
                        route_serializer.save()
                
                return Response({
                    "message": "Bus and Route details updated successfully",
                    "data": bus_serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response(bus_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BusDetails.DoesNotExist:
            return Response({"error": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)