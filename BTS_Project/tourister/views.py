from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer,RateReviewSerializer
from django.views.generic import TemplateView
from .models import RateReview

class Signup(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class RateReview(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RateReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data,{"Rate is created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        reviews = RateReview.objects.all()
        serializer = RateReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
class Package_details(TemplateView):
    template_name="package_details.html"

class Index(TemplateView):
    template_name="index.html"

class Navbar(TemplateView):
    template_name="navbar.html"

class Footer(TemplateView):
    template_name="footer.html"

class Payment(TemplateView):
    template_name="payment.html"

class Payment_Success(TemplateView):
    template_name="payment_success.html"