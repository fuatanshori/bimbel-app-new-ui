from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import ActiveSession
from django.utils.deprecation import MiddlewareMixin
from user.models import Profile
from django.conf import settings

User = get_user_model()

class PreventMultipleLoginsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            session_key = request.session.session_key
            if session_key:
                try:
                    active_session = ActiveSession.objects.get(user=request.user)
                    if active_session.session_key != session_key:
                        request.session.flush()
                        return redirect(reverse("user:masuk")+'?next='+request.path)  # Redirect to login or any other page
                
                except ActiveSession.DoesNotExist:
                    ActiveSession.objects.create(user=request.user, session_key=session_key)
    
    def process_response(self, request, response):
        if request.user.is_authenticated:
            session_key = request.session.session_key
            if session_key:
                ActiveSession.objects.update_or_create(user=request.user, defaults={'session_key': session_key})
        return response

class ValidateProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            excluded_paths = [reverse('user:add-profile'), 
                              reverse('user:keluar'),
                              settings.STATIC_URL,
                              '/media'
                              ]
            if request.path in excluded_paths:
                return None
            if any(request.path.startswith(path) for path in excluded_paths):
                return None
            try:
                profile = Profile.objects.get(user=request.user)
                if not profile.nama_lengkap or not any([
                    profile.jenis_kelamin, profile.tempat_tinggal, 
                    profile.nomor_telepon, profile.tanggal_lahir, profile.foto
                ]):
                    return redirect(reverse('user:add-profile')+'?next='+request.path)
            except Profile.DoesNotExist:
                return redirect('user:add-profile')
                    