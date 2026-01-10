from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions,renderers
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import HotelProfile,Room
from tourister.models import RoomBooking
from .serializers import HotelProfileSerializer,RoomSerializer

class HotelLogin(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'hotellogin.html'

    def get(self, request):
        return Response({}, template_name=self.template_name)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Please provide both username and password."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == 'Hotel' or user.is_superuser:
                login(request, user)  
                return Response({"message": "Hotel login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Access Denied: This is not a Hotel account."}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({"error": "Invalid Hotel ID or Password."}, status=status.HTTP_401_UNAUTHORIZED)
    
class Home(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'home.html'

    def get(self, request):
        return Response({}, template_name=self.template_name)
    
    
    
class HotelInfo(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    # இங்கே permission_classes-ஐத் தற்காலிகமாக நீக்கிவிட்டு, உள்ளே மேனுவலாக செக் செய்வோம்
    permission_classes = [permissions.AllowAny] 
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'hotelprofile.html'

    def get(self, request):
        # NORMAL METHOD: பயனர் லாகின் செய்யவில்லை என்றால் ரீடைரக்ட் செய்
        if not request.user.is_authenticated:
            return redirect('login') 
            
        hotel = HotelProfile.objects.filter(user=request.user).first()
        
        if request.accepted_renderer.format == 'html':
            return Response({'hotel': hotel})
        
        serializer = HotelProfileSerializer(hotel)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Login required"}, status=401)
            
        if HotelProfile.objects.filter(user=request.user).exists():
            return Response({"error": "Hotel already exists"}, status=400)
        
        serializer = HotelProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Login required"}, status=401)
            
        hotel = get_object_or_404(HotelProfile, user=request.user)
        serializer = HotelProfileSerializer(hotel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Login required"}, status=401)
            
        hotel = get_object_or_404(HotelProfile, user=request.user)
        hotel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class RoomManagementView(APIView):
    
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    
    renderer_classes = [renderers.TemplateHTMLRenderer, renderers.JSONRenderer]
    template_name = 'roommanagement.html'

    def get(self, request):
       
        hotel = get_object_or_404(HotelProfile, user=request.user)
        rooms = Room.objects.filter(hotel=hotel)
        
        return Response(
            {'hotel': hotel, 'rooms': rooms}, 
            template_name=self.template_name
        )

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
        return Response({"message": "Room deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    
    


class DisplayRoomBookings(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    renderer_classes = [renderers.TemplateHTMLRenderer, renderers.JSONRenderer]
    template_name = 'Displayroombookings.html'

    def get(self, request, hotel_id=None):
        if request.accepted_renderer.format == 'html':
            return Response({'hotel_id': hotel_id}, template_name=self.template_name)
    
        hotel_profile = get_object_or_404(HotelProfile, user=request.user)
        
        query = RoomBooking.objects.filter(room__hotel=hotel_profile)

        if hotel_id:
            query = query.filter(room__hotel_id=hotel_id)
            
        bookings = query.order_by('-created_at') 
        
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
        
        return Response(data)
    
        
class HotelLogout(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        logout(request)
       
        return redirect('hotel:hotellogin') 

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=204)
    
