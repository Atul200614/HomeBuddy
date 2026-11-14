from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.urls import reverse
from .models import User
from .forms import CustomerRegistrationForm
from apps.customers.models import CustomerProfile
from apps.notifications.services import notify


class APIRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        # If confirm_password was omitted, default it to password for API convenience
        if 'password' in data and 'confirm_password' not in data:
            data['confirm_password'] = data['password']

        form = CustomerRegistrationForm(data)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.get_or_create(user=user)
            try:
                notify(
                    user,
                    "Welcome to HomeBuddy",
                    "Your customer account is ready. Add an address, then book your first service.",
                    'SYSTEM',
                    reverse('customers:dashboard'),
                )
            except Exception:
                pass

            login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
            return Response({
                'success': True,
                'message': f"Welcome to HomeBuddy, {user.first_name or user.username}! Your customer account is ready.",
                'user': {
                    'id': user.id,
                    'name': user.get_full_name() or user.username,
                    'email': user.email,
                    'role': user.role,
                }
            }, status=status.HTTP_201_CREATED)

        first_err = "Registration failed."
        for field, errors in form.errors.items():
            if errors:
                first_err = f"{field}: {errors[0]}" if field != '__all__' else str(errors[0])
                break

        return Response({
            'success': False,
            'message': first_err,
            'errors': form.errors.get_json_data(),
        }, status=status.HTTP_400_BAD_REQUEST)


class APILoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user and user.is_active:
            login(request, user)
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'name': user.get_full_name() or user.username,
                    'email': user.email,
                    'role': user.role
                }
            })
        return Response({'success': False, 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class APILogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'success': True, 'message': 'Signed out successfully'})

class APICurrentUserView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'id': request.user.id,
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'role': request.user.role
            })
        return Response({'authenticated': False})
