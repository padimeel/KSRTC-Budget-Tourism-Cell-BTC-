from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, RateReviewSerializer, BookingSerializer
from admin_panel.serializers import PackageSerializer
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.views.generic import TemplateView
from .models import RateReview, Package_Booking
from admin_panel.models import Package_Details
from rest_framework.authtoken.models import Token
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings


print("SMTP HOST:", settings.EMAIL_HOST)
print("SMTP USER:", settings.EMAIL_HOST_USER)


class Signup(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "signup.html"

    def get(self, request):
        return Response({})

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            username = user.username
            email = user.email
            phone_number = request.data.get("phone_number")

            subject = "Your KSRTC Budget Tourism Account is Successfully Created"

            text_message = f"""
Hi {username},

Your KSRTC Budget Tourism account has been created successfully.

Username: {username}
Phone: {phone_number}
Email: {email}

Regards,
KSRTC Budget Tourism Team
"""

            html_message = f"""
            <html><body>
            <h2>KSRTC Budget Tourism</h2>
            <p>Hi <strong>{username}</strong>,</p>
            <p>Your account has been created successfully.</p>

            <div>
                <p><strong>Username:</strong> {username}</p>
                <p><strong>Phone Number:</strong> {phone_number}</p>
                <p><strong>Email:</strong> {email}</p>
            </div>

            <p>Regards,<br>KSRTC Budget Tourism Team</p>
            </body></html>
            """

            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response(
                {"message": "User created successfully & Email sent"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
class Login(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'login.html'

    def get(self, request):
        if request.accepted_renderer.format == 'html':
            return Response({})
        return Response({"detail": "Not allowed"}, status=405)

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=400)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid username or password"}, status=401)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        }, status=200)


# ---------------------------------------------------------
# INDEX PAGE
# ---------------------------------------------------------
class Index(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'index.html'

    def get(self, request):
        if request.accepted_renderer.format == 'html':
            return Response({})

        package_list = Package_Details.objects.all()[:8]
        package_serializer = PackageSerializer(package_list, many=True)

        review_list = RateReview.objects.all()
        review_serializer = RateReviewSerializer(review_list, many=True)

        return Response({
            "packages": package_serializer.data,
            "reviews": review_serializer.data
        }, status=200)


# ---------------------------------------------------------
# PACKAGE LIST
# ---------------------------------------------------------
class Packagelist(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'packagelist.html'

    def get(self, request, pk=None):

        if request.accepted_renderer.format == 'html':
            return Response({})

        if pk:
            try:
                package = Package_Details.objects.get(id=pk)
            except Package_Details.DoesNotExist:
                return Response({"message": "Package not found"}, status=404)

            serializer = PackageSerializer(package)
            return Response(serializer.data)

        destination = request.GET.get('destination', '')
        date = request.GET.get('date', '')
        price = request.GET.get('price', '')

        packages = Package_Details.objects.all()

        if destination:
            packages = packages.filter(places__icontains=destination)

        if date:
            packages = packages.filter(start_date__lte=date, end_date__gte=date)

        if price:
            try:
                price = int(price)
                if price > 50000:
                    packages = packages.filter(price__gt=50000)
                else:
                    packages = packages.filter(price__lte=price)
            except ValueError:
                pass

        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data, status=200)

class PackageDetails(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'packagedetails.html'

    def get(self, request, pk=None):
        if request.accepted_renderer.format == 'html':
            return Response({})

        if not pk:
            return Response({"message": "Package ID required"}, status=400)

        try:
            package = Package_Details.objects.get(id=pk)
        except Package_Details.DoesNotExist:
            return Response({"message": "Package not found"}, status=404)

        serializer = PackageSerializer(package)
        return Response({"package": serializer.data})


# ---------------------------------------------------------
# STATIC PAGES
# ---------------------------------------------------------
class Navbar(TemplateView):
    template_name = "navbar.html"

class Footer(TemplateView):
    template_name = "footer.html"

class Payment(TemplateView):
    template_name = "payment.html"

class Payment_Success(TemplateView):
    template_name = "payment_success.html"


# ---------------------------------------------------------
# MY BOOKING (AUTH REQUIRED)
# ---------------------------------------------------------
class MyBooking(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "mybooking.html"

    def get(self, request, pk=None):

        if request.accepted_renderer.format == 'html' and pk is None:
            return Response({})

        if pk is None:
            bookings = Package_Booking.objects.filter(user=request.user)
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data)

        try:
            booking = Package_Booking.objects.get(pk=pk, user=request.user)
        except Package_Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            booking = Package_Booking.objects.get(pk=pk)
        except Package_Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            booking = Package_Booking.objects.get(pk=pk)
        except Package_Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        booking.delete()
        return Response({"message": "Booking deleted successfully"}, status=200)

    def post(self, request):
        serializer = RateReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Rate Review created successfully", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)


# ---------------------------------------------------------
# PACKAGE BOOKING (AUTH REQUIRED)
# ---------------------------------------------------------
class PackageBooking(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "packagebooking.html"

    def get(self, request, pk=None):

        if request.accepted_renderer.format == 'html':
            return Response({})

        if not pk:
            return Response({"message": "Package ID required"}, status=400)

        try:
            package = Package_Details.objects.get(id=pk)
        except Package_Details.DoesNotExist:
            return Response({"message": "Package not found"}, status=404)

        serializer = PackageSerializer(package)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            booking = serializer.save()
            return Response({"message": "Booking Successful", "booking": serializer.data}, status=201)
        return Response(serializer.errors, status=400)


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
class Logout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=200)
        except Exception:

            return Response({"error": "Invalid refresh token"}, status=400)

