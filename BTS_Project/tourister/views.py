from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import F
from django.db import transaction

from .models import RateReview, Package_Booking
from admin_panel.models import Package_Details
from .serializers import SignupSerializer, RateReviewSerializer, BookingSerializer
from admin_panel.serializers import PackageSerializer

User = get_user_model()


# ------------------------------
# SIGNUP
# ------------------------------
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
            return Response ({'Response':serializer.data})

            # Email notification
#             username = user.username
#             email = user.email
#             phone_number = request.data.get("phone_number", "")

#             subject = "Your KSRTC Budget Tourism Account is Successfully Created"
#             text_message = f"""
# Hi {username},

# Your KSRTC Budget Tourism account has been created successfully.

# Username: {username}
# Phone: {phone_number}
# Email: {email}

# Regards,
# KSRTC Budget Tourism Team
# """
#             html_message = f"""
# <html><body>
# <h2>KSRTC Budget Tourism</h2>
# <p>Hi <strong>{username}</strong>,</p>
# <p>Your account has been created successfully.</p>

# <div>
#     <p><strong>Username:</strong> {username}</p>
#     <p><strong>Phone Number:</strong> {phone_number}</p>
#     <p><strong>Email:</strong> {email}</p>
# </div>

# <p>Regards,<br>KSRTC Budget Tourism Team</p>
# </body></html>
# """

#             send_mail(
#                 subject,
#                 text_message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [email],
#                 html_message=html_message,
#                 fail_silently=False,
#             )

#             return Response(
#                 {"message": "User created successfully & Email sent"},
#                 status=status.HTTP_201_CREATED
#             )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------
# LOGIN
# ------------------------------
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



class Index(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'index.html'

    def get(self, request):
        # 1. HTML கோரிக்கை வந்தால் வெறும் பக்கத்தை மட்டும் அனுப்பவும்
        if request.accepted_renderer.format == 'html':
            return Response({})

        # 2. JSON கோரிக்கை வந்தால் (Axios மூலம்) தரவுகளை அனுப்பவும்
        # பேக்கேஜ்களை எடுக்கிறோம்
        packages = Package_Details.objects.all().order_by('-id')[:8]
        package_serializer = PackageSerializer(packages, many=True)
        
        # ரிவியூக்களை எடுக்கிறோம்
        reviews = RateReview.objects.all().order_by('-id')
        review_serializer = RateReviewSerializer(reviews, many=True)

        # 3. ஒரே ரெஸ்பான்ஸில் இரண்டையும் சேர்த்து அனுப்ப வேண்டும்
        return Response({
            "packages": package_serializer.data,
            "reviews": review_serializer.data
        }, status=200)



class Packagelist(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "packagelist.html"

    def get(self, request):
       
        if request.accepted_renderer.format == "html":
            return Response({})

        destination = request.GET.get("destination", "")
        date = request.GET.get("date", "")
        price = request.GET.get("price", "")

        packages = Package_Details.objects.all()

        if destination:
            packages = packages.filter(places__icontains=destination)

        if date:
            packages = packages.filter(
                start_date__lte=date,
                end_date__gte=date
            )

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


# ------------------------------
# PACKAGE DETAILS
# ------------------------------
class PackageDetails(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "packagedetails.html"

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


# ------------------------------
# TEMPLATE PAGES
# ------------------------------
class Navbar(TemplateView):
    template_name = "navbar.html"


class Footer(TemplateView):
    template_name = "footer.html"


class Payment(TemplateView):
    template_name = "payment.html"


class Payment_Success(TemplateView):
    template_name = "payment_success.html"


# ------------------------------
# MY BOOKINGS
# ------------------------------
class MyBooking(APIView):
    authentication_classes = [JWTAuthentication]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "mybooking.html"

    def get_permissions(self):
        if self.request.accepted_renderer.format == 'html':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request, pk=None):
        if request.accepted_renderer.format == "html":
            return Response({})
            
        bookings = Package_Booking.objects.filter(user=request.user).select_related('package', 'package__bus').order_by('-booking_date')
        
        data = []
        for b in bookings:
            # பிரண்ட்-எண்ட் எதிர்பார்க்கும் அதே ஸ்ட்ரக்சரில் தரவை அனுப்புதல்
            data.append({
                "id": b.id,
                "adults": b.adults,
                "children": b.children,
                "boarding_point": b.boarding_point,
                "total_price": b.total_price,
                "booking_date": b.booking_date.isoformat(), # ஜாவாஸ்கிரிப்ட் டேட் பார்மெட்டிற்கு
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

    @transaction.atomic
    def delete(self, request, pk):
        try:
        # புக்கிங்கை எடுக்கிறோம் (பயனருக்கு உரியதா என சரிபார்க்கிறோம்)
            booking = Package_Booking.objects.select_related('package__bus').get(pk=pk, user=request.user)
        
        # ரத்து செய்யப்படும் பயணிகளின் எண்ணிக்கை
            passengers_to_return = booking.adults + booking.children
        
        # அந்த பேருந்தின் சீட்களை அதிகரித்தல்
            if booking.package and booking.package.bus:
                bus = booking.package.bus
            
            # இதோ இங்கே தான் மாற்றம்: 
            # F expression மூலம் டேட்டாபேஸில் நேரடியாக கூட்டுகிறோம்
            # இது 'Race condition' வராமல் தடுக்கும்
                bus.total_seats = F('total_seats') + passengers_to_return
                bus.save(update_fields=['total_seats']) # குறிப்பிட்ட ஃபீல்டை மட்டும் சேமிக்கவும்
            
            # டேட்டாபேஸில் இருந்து புதிய மதிப்பை மீண்டும் இன்ஸ்டன்ஸிற்கு கொண்டு வர (Optional but good)
                bus.refresh_from_db()

        # புக்கிங்கை நீக்குதல்
            booking.delete()
        
            return Response({"message": "Booking cancelled and seats restored."}, status=200)
        
        except Package_Booking.DoesNotExist:
            return Response({"error": "Booking not found or not authorized"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# ------------------------------
# PACKAGE BOOKING
# ------------------------------
class PackageBooking(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "packagebooking.html"

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request):
        package_id = request.GET.get('package_id')
        
        if request.accepted_renderer.format == 'html':
            return Response({'package_id': package_id}, template_name=self.template_name)
        
        if not package_id:
            return Response({"error": "Package ID missing"}, status=400)
            
        try:
            # சீரியலைசரை மாற்றாமல் முழு விவரங்களையும் கையால் அனுப்பும் முறை
            pkg = Package_Details.objects.select_related('bus').get(id=package_id)
            data = {
                "id": pkg.id,
                "package_name": pkg.package_name,
                "price": pkg.price,
                "bus_id": pkg.bus.id if pkg.bus else None,
                "bus_seats": pkg.bus.total_seats if pkg.bus else 0
            }
            return Response(data)
        except Package_Details.DoesNotExist:
            return Response({"error": "Package not found"}, status=404)

    @transaction.atomic
    def post(self, request):
    # Serializer-ஐ இனிஷியலைஸ் செய்கிறோம்
        serializer = BookingSerializer(data=request.data, context={'request': request})
    
        if serializer.is_valid():
        # சீட்களைக் குறைக்கும் லாஜிக் ஏற்கனவே Serializer-இன் create() மெத்தடில் உள்ளது.
        # எனவே இங்கே மீண்டும் செய்யத் தேவையில்லை.
            serializer.save() 
        
            return Response({
            "message": "Booking Successful",
            "details": serializer.data
        }, status=201)
    
        return Response(serializer.errors, status=400)
    
    
class RateReviewAPI(APIView):
    authentication_classes = [JWTAuthentication]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    

    def post(self, request):
        data = request.data.copy()
        data['user_id'] = request.user.id 
        
        serializer = RateReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Review submitted successfully!"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ------------------------------
# LOGOUT
# ------------------------------
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
