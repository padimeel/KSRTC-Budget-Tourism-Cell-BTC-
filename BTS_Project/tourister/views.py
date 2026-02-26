from django.conf import settings
from django.contrib.auth import authenticate, get_user_model,login
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404,render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import permissions, status,renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import F
from django.db import transaction
from .models import RateReview, Package_Booking,RoomBooking
from hotel_management.models import Room
from admin_panel.models import Package_Details
from .serializers import SignupSerializer, RateReviewSerializer, BookingSerializer,RoomBookingSerializer
from admin_panel.serializers import PackageSerializer
from hotel_management.serializers import RoomSerializer
from django.views.decorators.csrf import csrf_exempt
import razorpay
from payment.models import Transaction
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
User = get_user_model()


class IndexTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "index.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class SignupTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "signup.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class LoginTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "login.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class HotelsTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "hotels.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class PackageListTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "packagelist.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class MyBookingTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "mybooking.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class HotelMyBookingsTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "hotel_mybookings.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class RoomBookingTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "roombooking.html"

    def get(self, request, pk):
        # Corrected the double braces to a single dictionary
        return Response({'room_id': pk}, template_name=self.template_name)
    
    
    
class PackageBookingTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "packagebooking.html"

    def get(self, request, pk):
        # We pass pk to context just in case, but JS will pull it from the URL path
        return Response({'package_id': pk}, template_name=self.template_name)

class PaymentTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "payment.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class PaymentSuccessTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "payment_success.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class Navbar(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "navbar.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)

class Footer(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "footer.html"

    def get(self, request):
        return Response({}, template_name=self.template_name)
    
class PackageDetailsTemplate(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "packagedetails.html"
    
    def get(self, request, pk):
        # Pass 'id' to the template so JS can pick it up if needed, 
        # though we will pull it from the URL path.
        return Response({'id': pk}, template_name=self.template_name)
    
    
class Signup(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            username = user.username
            email = user.email
            phone_number = request.data.get("phone_number", "Not provided")
            
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

            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Email failed: {e}")

            return Response(
                {"message": "User created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    permission_classes = [permissions.AllowAny]


    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=400)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"error": "Invalid username or password"}, status=401)

        if getattr(user, 'role', None) == "Tourister" or user.is_superuser:
            
            login(request, user) 
            
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "message": "Welcome Tourister!"
            }, status=200)
        else:
            return Response({
                "error": "Access Denied: Please use the staff or hotel portal to login."
            }, status=status.HTTP_403_FORBIDDEN)



class Index(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        packages = Package_Details.objects.all().order_by('-id')[:8]
        package_serializer = PackageSerializer(packages, many=True)
        
        reviews = RateReview.objects.all().order_by('-id')
        review_serializer = RateReviewSerializer(reviews, many=True)

        return Response({
            "packages": package_serializer.data,
            "reviews": review_serializer.data
        }, status=200)



class Packagelist(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
       
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


class PackageDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request, pk=None):
        if not pk:
            return Response({"message": "Package ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            package = Package_Details.objects.get(id=pk)
        except Package_Details.DoesNotExist:
            return Response({"message": "Package not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PackageSerializer(package)
        return Response({"package": serializer.data}, status=status.HTTP_200_OK)



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

    @transaction.atomic
    def delete(self, request, pk):
        try:
            booking = Package_Booking.objects.select_related('package__bus').get(pk=pk, user=request.user)
        
        
            passengers_to_return = booking.adults + booking.children
    
            if booking.package and booking.package.bus:
                bus = booking.package.bus
            
                bus.total_seats = F('total_seats') + passengers_to_return
                bus.save(update_fields=['total_seats']) 
            
                bus.refresh_from_db()

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
    renderer_classes = [JSONRenderer]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request):
        package_id = request.query_params.get('package_id')
        if not package_id:
            return Response({"error": "Package ID missing"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            pkg = Package_Details.objects.select_related('bus').get(id=package_id)
            data = {
                "id": pkg.id,
                "package_name": pkg.package_name,
                "price": pkg.price,
                "bus_id": pkg.bus.id if pkg.bus else None,
                "bus_seats": pkg.bus.total_seats if pkg.bus else 0
            }
            return Response(data, status=status.HTTP_200_OK)
        except Package_Details.DoesNotExist:
            return Response({"error": "Package not found"}, status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
    
        if serializer.is_valid():
            
            booking = serializer.save() 
        
            return Response({
                "message": "Booking Successful",
                "remaining_seats": booking.package.bus.total_seats,
                "details": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
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
    
    
    
class Hotels(APIView):

    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        location_query = request.query_params.get('location', '').strip()
        rooms = Room.objects.filter(is_available=True)
        if location_query:
            rooms = rooms.filter(hotel__address__icontains=location_query)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
        
class BookRoom(APIView):
    renderer_classes = [renderers.JSONRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        """Fetch room details for the booking page"""
        room = get_object_or_404(Room, id=room_id)
        
        return Response({
            "hotel_name": room.hotel.hotel_name,
            "room_type": room.room_type,
            "room_number": room.room_number,
            "price": str(room.price)
        })

    def post(self, request, room_id):
        """Initialize a room booking and Razorpay order"""
        room = get_object_or_404(Room, id=room_id)
        check_in = request.data.get('check_in_date')
        check_out = request.data.get('check_out_date')
        total_price = request.data.get('total_price')

       
        is_booked = RoomBooking.objects.filter(
            room=room,
            check_out_date__gt=check_in,
            check_in_date__lt=check_out  
        ).exists()

        if is_booked:
            return Response({"error": "This room is already booked for the selected dates."}, status=400)

        # 2. Save Booking Instance
        serializer = RoomBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking_instance = serializer.save(user=request.user, room=room)

            try:
                # 3. Create Razorpay Order
                # Amount must be in paise (total * 100)
                razor_order_data = {
                    "amount": int(float(total_price) * 100), 
                    "currency": "INR",
                    "payment_capture": 1
                }
                razorpay_order = client.order.create(data=razor_order_data)

                # 4. Create Transaction Record
                # CRITICAL: Added 'amount' field so it reflects in the Revenue Dashboard
                Transaction.objects.create(
                    room_booking=booking_instance,
                    amount=total_price,  # Storing the amount directly
                    razorpay_order_id=razorpay_order['id'],
                    status="Pending"     # Initial status is Pending until verification
                )

                return Response({
                    "razorpay_order_id": razorpay_order['id'],
                    "amount": total_price,
                    "key": settings.RAZORPAY_KEY_ID,
                    "booking_id": booking_instance.id
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                # If Razorpay fails, we should ideally handle the booking_instance 
                # (e.g., delete it or mark it as failed)
                return Response({"error": f"Razorpay Error: {str(e)}"}, status=400)
        
        return Response(serializer.errors, status=400)
    
    def delete(self, request, room_id):
        """Cancel a room booking"""
        # Note: Usually, room_id here should refer to the Booking ID, not the Room ID
        booking = RoomBooking.objects.filter(id=room_id, user=request.user).first()
    
        if booking:
            booking.delete()
            return Response({"message": "Booking cancelled successfully"}, status=status.HTTP_200_OK)
    
        return Response({"error": "No booking found to delete"}, status=status.HTTP_404_NOT_FOUND)
    
    

class HotelMyBooking(APIView):
    renderer_classes = [renderers.JSONRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookings = RoomBooking.objects.filter(user=request.user).order_by('-id')
        
        data = [{
            "id": b.id,
            "hotel_name": b.room.hotel.hotel_name,
            "room_no": b.room.room_number,
            "room_type": b.room.room_type,
            "check_in": b.check_in_date.strftime('%d %b %Y'),
            "check_out": b.check_out_date.strftime('%d %b %Y'),
            "total_price": str(b.total_price),
        } for b in bookings]
        
        return Response(data)


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
