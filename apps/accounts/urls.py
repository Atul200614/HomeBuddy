from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_customer, name='register_customer'),
    path('register/provider/', views.register_provider, name='register_provider'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    path('password-change/', views.password_change_view, name='password_change'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
]
