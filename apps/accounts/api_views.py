from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .models import User

class APILoginView(APIView):
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
