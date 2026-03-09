import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from tourister.models import Package_Booking, Package_Details
from .serializers import BookingSerializer
from django.db import transaction as db_transaction

# Razorpay Client Setup
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreateOrderView(APIView):
    def post(self, request):
        try:
            package_id = request.data.get('package_id')
            adults = request.data.get('adults', 1)
            children = request.data.get('children', 0)
            boarding_point = request.data.get('boarding_point')
            phone_number = request.data.get('phone_number')
            total_price = request.data.get('total_price')

            # 1. Create the Package Booking
            package_instance = Package_Details.objects.get(id=package_id)
            booking = Package_Booking.objects.create(
                user=request.user, 
                package=package_instance,
                adults=adults,
                children=children,
                boarding_point=boarding_point,
                phone_number=phone_number,
                total_price=total_price
            )

            # 2. Create Razorpay Order
            razor_order_data = {
                "amount": int(float(total_price) * 100),  # Amount in paise
                "currency": "INR",
                "payment_capture": 1
            }
            razorpay_order = client.order.create(data=razor_order_data)

            # 3. Create Transaction with explicit amount
            # The 'amount' field is now stored directly in the Transaction model
            Transaction.objects.create(
                booking=booking,
                amount=total_price, # Storing the amount here
                razorpay_order_id=razorpay_order['id'],
                status="Pending"
            )

            data = {
                "booking_id": booking.id,
                "razorpay_order_id": razorpay_order['id'],
                "amount": total_price,
                "currency": "INR",
                "key": settings.RAZORPAY_KEY_ID
            }
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VerifyPaymentView(APIView):
    def post(self, request):
        res_data = request.data
    
        params_dict = {
            'razorpay_order_id': res_data.get('razorpay_order_id'),
            'razorpay_payment_id': res_data.get('razorpay_payment_id'),
            'razorpay_signature': res_data.get('razorpay_signature')
        }

        try:
            
            client.utility.verify_payment_signature(params_dict)

            # 2. Database atomic transaction
            with db_transaction.atomic():
                # Transaction விவரங்களை எடுத்தல்
                try:
                    transaction_obj = Transaction.objects.select_for_update().get(
                        razorpay_order_id=res_data.get('razorpay_order_id')
                    )
                except Transaction.DoesNotExist:
                    return Response({"message": "Transaction record not found"}, status=status.HTTP_404_NOT_FOUND)

                # ஸ்டேட்டஸை அப்டேட் செய்தல்
                transaction_obj.razorpay_payment_id = res_data.get('razorpay_payment_id')
                transaction_obj.razorpay_signature = res_data.get('razorpay_signature')
                transaction_obj.status = "Success"
                transaction_obj.save()

                # 3. Serializer-ஐ இயக்குதல்
                # ஜாவாஸ்கிரிப்ட்டில் இருந்து வரும் டேட்டாவைப் பயன்படுத்துகிறோம்
                serializer = BookingSerializer(data=request.data, context={'request': request})
                
                if serializer.is_valid():
                    # Serializer-ன் create() மெத்தட் இயங்கி சீட்டைக் குறைக்கும்
                    booking = serializer.save() 
                    
                    # F() எக்ஸ்பிரஷனுக்குப் பிறகு சரியான எண்ணிக்கையை எடுக்க
                    booking.package.bus.refresh_from_db()
                    
                    return Response({
                        "message": "Payment Successful and Booking Confirmed",
                        "booking_details": serializer.data,
                        "remaining_seats": booking.package.bus.total_seats
                    }, status=status.HTTP_200_OK)
                else:
                    # Serializer தவறாக இருந்தால் பிழையைத் தூக்கி எறியவும் (Rollback நடக்கும்)
                    raise Exception(serializer.errors)

        except Exception as e:
            # தோல்வியுற்றால் ஸ்டேட்டஸை 'Failure' என மாற்றுதல்
            try:
                transaction_obj = Transaction.objects.get(razorpay_order_id=res_data.get('razorpay_order_id'))
                if transaction_obj.status != "Success": # ஏற்கனவே சக்சஸ் ஆகவில்லை என்றால்
                    transaction_obj.status = "Failure"
                    transaction_obj.save()
            except:
                pass
            
            return Response({
                "message": "Verification or Booking Failed",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)