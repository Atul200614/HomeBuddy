"""Read-only REST endpoints used by the React frontend."""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Booking


class APIMyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_customer:
            bookings = Booking.objects.filter(customer__user=request.user)
        elif request.user.is_provider:
            bookings = Booking.objects.filter(provider__user=request.user)
        elif request.user.is_admin_user or request.user.is_staff:
            bookings = Booking.objects.all()
        else:
            return Response({'error': 'No booking scope for this role'},
                            status=status.HTTP_403_FORBIDDEN)

        bookings = bookings.select_related('service').order_by('-created_at')[:100]

        return Response([{
            'id': b.id,
            'booking_number': b.booking_number,
            'service_name': b.service.name,
            'status': b.status,
            'status_display': b.get_status_display(),
            'scheduled_date': str(b.scheduled_date),
            'time_slot': b.time_slot,
            'total_amount': str(b.total_amount),
            'is_emergency': b.is_emergency,
        } for b in bookings])
