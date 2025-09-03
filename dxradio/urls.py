"""
URL configuration for dxradio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from station import views as station_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', station_views.menu_view, name='menu'),
    path('queries/', station_views.queries_view, name='queries'),
    path('queries/analog/', station_views.analog_entries, name='analog_entries'),
    path('queries/digital/', station_views.digital_entries, name='digital_entries'),
    path('queries/bands/', station_views.bands_list, name='bands_list'),
    path('queries/band_entries/', station_views.band_entries, name='band_entries'),
    path('queries/modulation_entries/', station_views.modulation_entries, name='modulation_entries'),
    path('queries/decoding_entries/', station_views.decoding_entries, name='decoding_entries'),
    path('queries/callsign_entries/', station_views.callsign_entries, name='callsign_entries'),
    path('queries/date_entries/', station_views.date_entries, name='date_entries'),
    path('auto_logout/', station_views.auto_logout, name='auto_logout'),
    
    # Simple Password Reset
    path('password_reset/', station_views.simple_password_reset, name='simple_password_reset'),
    
    # OTP Password Reset
    path('otp_password_reset/', station_views.otp_password_reset, name='otp_password_reset'),
    path('otp_verify/<int:user_id>/', station_views.otp_verify, name='otp_verify'),
    
    # Password Reset URLs
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('admin/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('admin/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Database Backup/Restore URLs
    path('database/backup/', station_views.database_backup, name='database_backup'),
    path('database/restore/', station_views.database_restore, name='database_restore'),
    path('database/backup-files/', station_views.get_backup_files, name='get_backup_files'),
]
