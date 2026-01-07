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
           
            user_role = getattr(user, 'role', None) 
            
            if user_role == 'Hotel':
                login(request, user)  
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Access Denied: Not a Hotel Partner account."}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({"error": "Invalid Hotel ID or Password."}, status=status.HTTP_401_UNAUTHORIZED)
    
class Home(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'home.html'

    def get(self, request):
        return Response({}, template_name=self.template_name)
    
class HotelInfo(APIView):
   
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated] 
    
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'hotelprofile.html'

    def get(self, request):
        hotel = HotelProfile.objects.filter(user=request.user).first()
        
        if request.accepted_renderer.format == 'html':
            return Response({'hotel': hotel})
        
        serializer = HotelProfileSerializer(hotel)
        return Response(serializer.data)

    def post(self, request):
        if HotelProfile.objects.filter(user=request.user).exists():
            return Response({"error": "Hotel already exists"}, status=400)
        serializer = HotelProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request):
        hotel = get_object_or_404(HotelProfile, user=request.user)
        serializer = HotelProfileSerializer(hotel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        hotel = get_object_or_404(HotelProfile, user=request.user)
        hotel.delete()
        return Response(status=204)
    

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
    
    
    
     
    
class HotelLogout(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        logout(request)
       
        return redirect('hotel:hotellogin') 

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=204)
    
