import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from tourister.models import Package_Booking, Package_Details

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
            # Verify the signature
            client.utility.verify_payment_signature(params_dict)

            # Update Transaction status
            transaction = Transaction.objects.get(razorpay_order_id=res_data.get('razorpay_order_id'))
            transaction.razorpay_payment_id = res_data.get('razorpay_payment_id')
            transaction.razorpay_signature = res_data.get('razorpay_signature')
            transaction.status = "Success"
            transaction.save()

            # Optional: If your Package_Booking has a payment_status field, update it here:
            # if transaction.booking:
            #     transaction.booking.payment_status = "Paid"
            #     transaction.booking.save()

            return Response({"message": "Payment Successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            # Update status to Failure if verification fails
            try:
                transaction = Transaction.objects.get(razorpay_order_id=res_data.get('razorpay_order_id'))
                transaction.status = "Failure"
                transaction.save()
            except:
                pass
            return Response({"message": "Payment Verification Failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)