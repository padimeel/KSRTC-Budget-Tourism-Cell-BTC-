from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, RateReviewSerializer, BookingSerializer
from django.views.generic import TemplateView
from .models import RateReview, Booking
from rest_framework.authtoken.models import Token
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings


print("SMTP HOST:", settings.EMAIL_HOST)
print("SMTP USER:", settings.EMAIL_HOST_USER)


# -------------------- SIGNUP API --------------------
class Signup(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Get values
            username = request.data.get("username")
            email = request.data.get("email")
            password = request.data.get("password")
            phone_number = request.data.get("phone_number")

            # ---------------- EMAIL CONTENT ----------------
            subject = "Your KSRTC Budget Tourism Account is Successfully Created"

            # Plain Text Fallback
            message = (
                f"Hi {username},\n\n"
                f"Your KSRTC Budget Tourism account has been created.\n"
                f"Username: {username}\n"
                f"Password: {password}\n"
                f"Phone: {phone_number}\n"
                f"Email: {email}\n\n"
                f"Regards,\n"
                f"KSRTC Budget Tourism Team"
            )

            # HTML Email (Styled)
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; background:#f6f7f9; padding:20px;">

                <div style="max-width:600px; margin:auto; background:white; padding:25px;
                            border-radius:8px; border:1px solid #e0e0e0;">

                    <h2 style="color:#d62828; text-align:center; margin-top:0;">
                        KSRTC Budget Tourism
                    </h2>

                    <p style="font-size:15px; color:#333;">Hi <strong>{username}</strong>,</p>

                    <p style="font-size:15px; color:#333;">
                        Welcome to KSRTC Budget Tourism. Your account has been created successfully.
                    </p>

                    <h3 style="color:#333; margin-bottom:8px;">Account Information</h3>

                    <div style="background:#f2f2f2; padding:15px; border-radius:6px;">
                        <p><strong>Username:</strong> {username}</p>
                        <p><strong>Password:</strong> {password}</p>
                        <p><strong>Phone Number:</strong> {phone_number}</p>
                        <p><strong>Email:</strong> {email}</p>
                    </div>

                    <h3 style="margin-top:20px;">Next Steps</h3>
                    <ul style="line-height:1.6; color:#333; font-size:15px;">
                        <li>Login using your username and password.</li>
                        <li>Explore tourism packages and available services.</li>
                        <li>Keep your account credentials safe.</li>
                    </ul>

                    <p style="font-size:14px; color:#555;">
                        If you did not create this account, please contact our support team immediately.
                    </p>

                    <p style="font-size:15px; margin-top:25px;">
                        Thank you for choosing KSRTC Budget Tourism.<br>
                        We wish you a pleasant and safe travel experience.
                    </p>

                    <p style="font-weight:bold; margin-top:10px;">
                        Regards,<br> KSRTC Budget Tourism Team
                    </p>

                </div>

            </body>
            </html>
            """

            # ---------------- SEND EMAIL ----------------
            send_mail(
                subject,
                message,
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

    def get(self, request):
        users = User.objects.all()
        serializer = SignupSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------- LOGIN API --------------------
class Login(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': user.username,
                    'email': user.email,
                },
                status=status.HTTP_200_OK
            )
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# class Logout (APIView):
    
# -------------------- RATE & REVIEW --------------------
class RateReviewAPI(APIView):
    permission_classes = [permissions.AllowAny]  

    def post(self, request):
        serializer = RateReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  
            return Response(
                {"message": "Rate Review created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        reviews = RateReview.objects.all()
        serializer = RateReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class Package_BookingAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk=None):
        if pk:
            try:
                booking = Booking.objects.get(pk=pk)
            except Booking.DoesNotExist:
                return Response({"error": "Booking not found"}, status=404)

            serializer = BookingSerializer(booking)
            return Response(serializer.data)

        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        serializer = BookingSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        booking.delete()
        return Response({"message": "Booking deleted successfully"}, status=200)


# -------------------- FRONTEND PAGES --------------------
class Package_details(TemplateView):
    template_name = "package_details.html"

class Index(TemplateView):
    template_name = "index.html"

class Navbar(TemplateView):
    template_name = "navbar.html"

class Footer(TemplateView):
    template_name = "footer.html"

class Payment(TemplateView):
    template_name = "payment.html"

class Payment_Success(TemplateView):
    template_name = "payment_success.html"

class front_end_signup(TemplateView):
    template_name = "signup.html"

class front_end_login(TemplateView):
    template_name = "login.html"
    
class Package_list(TemplateView):
    template_name="package_list.html"
    
class My_Booking(TemplateView):
    template_name="my_booking.html"
    
class Package_Booking_Frontend(TemplateView):
    template_name="packagebooking.html"
    
    
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass 
        return HttpResponseRedirect('/login/')
