from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth import authenticate,login, logout
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from .serializers import BusDetailsSerializer, BusRouteSerializer
from .models import BusDetails, BusRoute
from admin_panel.models import Package_Details


# ---------------------- LOGIN API ----------------------

class Login(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "depotlogin.html"

    def get(self, request, pk=None):
        if request.accepted_renderer.format == 'html':
            return Response({})

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.role == "Depot Manager" or user.is_superuser:
                login(request, user) 
                
                return Response({
                    "message": "Login successful",
                    "username": user.username,
                    "depot_name": getattr(user, 'depot_name', '')
                }, status=status.HTTP_200_OK)
            else:

                return Response({
                    "error": "Unauthorized: This account is not assigned to a Depot Manager."
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class DepotLogout(APIView):
    
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    def get(self, request):
        logout(request)
        return redirect('depot:login')  
    
    
class BusAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk=None):
        if pk:
            try:
                route = BusRoute.objects.get(id=pk)
            except BusRoute.DoesNotExist:
                return Response({"error": "Route not found"}, status=404)

            serializer = BusRouteSerializer(route)
            return Response(serializer.data)

        routes = BusRoute.objects.all()
        serializer = BusRouteSerializer(routes, many=True)
        return Response(serializer.data)


    def post(self, request):
        
        bus_id = request.data.get("bus")
        if not BusDetails.objects.filter(id=bus_id).exists():
            return Response({"error": "Invalid bus ID"}, status=400)

        serializer = BusRouteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


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
        except BusRoute.DoesNotExist:
            return Response({"error": "Route not found"}, status=404)

        route.delete()
        return Response({"message": "Deleted successfully"}, status=204)
    
class AssignPackage(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "assignpackage.html"

    def get(self, request, pk=None):
      
        packages = Package_Details.objects.filter(assigned_depot_manager=request.user).order_by('-id')
        
        if request.accepted_renderer.format == 'html':
            return Response({'packages': packages})

        data = []
        for pkg in packages:

            bus_obj = BusDetails.objects.filter(package=pkg).first()
            
            data.append({
                "id": pkg.id,
                "package_name": pkg.package_name,
                "duration": pkg.duration,
                "price": pkg.price,
                "start_date": pkg.start_date.isoformat() if pkg.start_date else None,
                "end_date": pkg.end_date.isoformat() if pkg.end_date else None,
                "places": pkg.places,
                "has_bus": True if bus_obj else False,
                "bus_number": bus_obj.bus_number if bus_obj else None
            })
        return Response(data, status=status.HTTP_200_OK)


class DepotDashboard(APIView):
    
    
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "depotdashboard.html"

    def get(self, request, pk=None):
        if request.accepted_renderer.format == 'html':
            return Response({})
        
class AddBus(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "addbus.html"
    def get(self, request, pk=None, *args, **kwargs):
        if request.accepted_renderer.format == 'html':
            return Response({'package_id': pk})
        return Response({"error": "HTML only"}, status=400)

    def post(self, request, pk=None, *args, **kwargs):
     
        pass


class UpdateBus(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "updatebus.html"
    
    def get(self, request, pk):
        
        bus = get_object_or_404(BusDetails, id=pk)
        return Response({'bus': bus})

    def put(self, request, pk):
        try:
           
            bus = BusDetails.objects.get(id=pk)
            bus_serializer = BusDetailsSerializer(bus, data=request.data, partial=True)
            
            if bus_serializer.is_valid():
                bus_serializer.save()
                
                
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