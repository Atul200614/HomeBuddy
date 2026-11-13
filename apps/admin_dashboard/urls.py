from django.urls import path

from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('users/', views.users_list, name='users'),
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('verifications/', views.verifications_list, name='verifications'),
    path('verifications/<int:doc_id>/<str:action>/', views.process_verification, name='process_verification'),
    path('bookings/', views.bookings_list, name='bookings'),
    path('payments/', views.payments_list, name='payments'),
    path('payments/<int:payment_id>/refund/', views.refund_payment, name='refund_payment'),
    path('payouts/', views.payouts_list, name='payouts'),
    path('payouts/<int:payout_id>/<str:action>/', views.process_payout, name='process_payout'),
    path('complaints/', views.complaints_list, name='complaints'),
    path('complaints/<int:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
]
