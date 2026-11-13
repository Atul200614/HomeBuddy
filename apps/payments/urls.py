from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:booking_id>/', views.checkout_view, name='checkout'),
    path('order/<int:booking_id>/', views.create_order_ajax, name='create_order'),
    path('callback/<int:booking_id>/', views.razorpay_callback, name='razorpay_callback'),
    path('cash-confirm/<int:booking_id>/', views.cash_confirm, name='cash_confirm'),
    path('invoice/<int:booking_id>/', views.invoice_detail, name='invoice_detail'),
    path('status/<int:booking_id>/', views.payment_status, name='status'),
    path('webhook/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
]
