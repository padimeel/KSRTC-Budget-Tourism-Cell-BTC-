from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions,renderers
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import HotelProfile,Room
from tourister.models import RoomBooking
from .serializers import HotelProfileSerializer,RoomSerializer




class DisplayRoomBookingsTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer] 
    template_name = "Displayroombookings.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})
    
class HomeTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]  
    template_name = "home.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})
    
class HotelLoginTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]  
    template_name = "hotellogin.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})
    
class HotelProfileTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]  
    template_name = "hotelprofile.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})
    
class RoomManagementTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]  
    template_name = "roommanagement.html"
    
    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response({})
    
    

class HotelLogin(APIView):
    # Allow anyone to access the login endpoint
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # 1. Validation
        if not username or not password:
            return Response(
                {"error": "Please provide both username and password."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Authentication
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 3. Role Authorization check
            if getattr(user, 'role', None) == 'Hotel' or user.is_superuser:
                
                # 4. Generate JWT Tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "message": "Hotel login successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "role": getattr(user, 'role', 'Admin')
                }, status=status.HTTP_200_OK)
            
            return Response(
                {"error": "Access Denied: This is not a Hotel account."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(
            {"error": "Invalid Hotel ID or Password."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    
    
    
class HotelInfo(APIView):
    # This automatically replaces 'if not request.user.is_authenticated'
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hotel = HotelProfile.objects.filter(user=request.user).first()
        if not hotel:
            return Response({"error": "Hotel profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = HotelProfileSerializer(hotel)
        return Response(serializer.data)

    def post(self, request):
        if HotelProfile.objects.filter(user=request.user).exists():
            return Response({"error": "Hotel profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = HotelProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        hotel = get_object_or_404(HotelProfile, user=request.user)
        serializer = HotelProfileSerializer(hotel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        hotel = get_object_or_404(HotelProfile, user=request.user)
        hotel.delete()
        return Response({"message": "Profile deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    
class RoomManagementView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hotel = get_object_or_404(HotelProfile, user=request.user)
        rooms = Room.objects.filter(hotel=hotel)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        hotel = get_object_or_404(HotelProfile, user=request.user)
        serializer = RoomSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(hotel=hotel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        room = get_object_or_404(Room, pk=pk, hotel__user=request.user)
        serializer = RoomSerializer(room, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        room = get_object_or_404(Room, pk=pk, hotel__user=request.user)
        room.delete()
        return Response({"message": "Room deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    


class DisplayRoomBookings(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hotel_profile = get_object_or_404(HotelProfile, user=request.user)

        bookings = RoomBooking.objects.filter(
            room__hotel=hotel_profile
        ).select_related('room', 'room__hotel', 'user').order_by('-created_at')

        data = [{
            "id": b.id,
            "hotel_name": b.room.hotel.hotel_name,
            "guest_name": b.guest_name,  
            "guest_phone": b.phone_number,
            "guest_email": b.user.email if b.user else "N/A",
            "room_no": b.room.room_number,
            "room_type": b.room.room_type,
            "check_in": b.check_in_date.strftime('%Y-%m-%d'), 
            "display_check_in": b.check_in_date.strftime('%d %b %Y'),
            "display_check_out": b.check_out_date.strftime('%d %b %Y'),
            "total_price": str(b.total_price),
            "booking_date": b.created_at.strftime('%d %b %Y'),
            "members": f"{b.adults} Adults, {b.children} Children"
        } for b in bookings]
        
        return Response(data, status=status.HTTP_200_OK)
    
        
class HotelLogout(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        logout(request)
       
        return redirect('hotel:hotellogin') 

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=204)
    
