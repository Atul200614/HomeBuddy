"""Read-only payment API used by the React frontend."""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Booking
from .models import Payment


class APIMyPaymentsView(APIView):
    """Lists the signed-in user's payments (never somebody else's)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_customer:
            payments = Payment.objects.filter(booking__customer__user=request.user)
        elif request.user.is_provider:
            payments = Payment.objects.filter(booking__provider__user=request.user)
        elif request.user.is_admin_user or request.user.is_staff:
            payments = Payment.objects.all()
        else:
            return Response({'error': 'No payment scope for this role.'}, status=status.HTTP_403_FORBIDDEN)

        data = [{
            'booking_number': p.booking.booking_number,
            'amount': str(p.amount),
            'method': p.payment_method,
            'status': p.status,
            'is_demo': p.is_demo,
            'settled': p.is_settled,
            'created_at': p.created_at.isoformat(),
        } for p in payments.select_related('booking')[:100]]

        return Response(data)


class APIPaymentDetailView(APIView):
    """Single booking payment, ownership enforced."""

    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        booking = Booking.objects.filter(id=booking_id).first()
        if booking is None:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

        owns = (
            (hasattr(request.user, 'customer_profile') and booking.customer_id == request.user.customer_profile.id)
            or (hasattr(request.user, 'provider_profile') and booking.provider_id == request.user.provider_profile.id)
            or request.user.is_admin_user
        )
        if not owns:
            return Response({'error': 'Not authorised for this booking'}, status=status.HTTP_403_FORBIDDEN)

        payment = getattr(booking, 'payment', None)
        if payment is None:
            return Response({'status': 'NONE'})

        return Response({
            'amount': str(payment.amount),
            'method': payment.payment_method,
            'status': payment.status,
            'is_demo': payment.is_demo,
            'settled': payment.is_settled,
        })
