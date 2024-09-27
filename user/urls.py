from django.urls import path
from . import views

urlpatterns = [
    path('masuk/',views.masuk,name='masuk'),
    path('keluar/',views.keluar,name='keluar'),
    path('daftar/',views.daftar,name='daftar'),
    path('aktifasi/<str:uidb64>/<str:token>/',views.aktifasi,name='aktifasi'),
    path('lupa-password/', views.lupaPassword, name='lupapassword'),
    path('resetpassword/<str:uidb64>/<str:token>/', views.resetPassword, name='resetpassword'),
    path('ubah-password/', views.UbahPasswordView.as_view(), name='ubah_password'),
    path('add-profile/', views.add_profile, name='add-profile'),
]
