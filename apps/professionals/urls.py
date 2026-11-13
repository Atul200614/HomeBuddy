from django.urls import path

from . import views

app_name = 'professionals'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.edit_profile, name='edit_profile'),
    path('verification/', views.verification_view, name='verification'),
    path('jobs/', views.jobs_view, name='jobs'),
    path('jobs/<int:booking_id>/accept/', views.accept_booking, name='accept_booking'),
    path('jobs/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
    path('jobs/<int:booking_id>/status/<str:new_status>/', views.update_job_status, name='update_job_status'),
    path('jobs/<int:booking_id>/work-proof/', views.work_proof_upload, name='work_proof_upload'),
    path('earnings/', views.earnings_view, name='earnings'),
    path('<int:provider_id>/', views.public_profile_view, name='public_profile'),
]
