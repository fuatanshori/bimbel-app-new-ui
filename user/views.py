from django.shortcuts import render, redirect
from django.http.response import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Users,Profile
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from http import HTTPStatus
from django.urls import reverse,reverse_lazy
from django.utils.translation import gettext as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .utils.kirim_email import kirim_email_activate, kirim_email_reset_password
from .token import account_activation_token
from django.utils import timezone
import requests
from .forms import ChangePasswordForm,AddProfileForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.core.cache import cache

# Create your views here.
def daftar(request):
    # jika request adalah post
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if not full_name.strip() or len(full_name) != len(full_name.strip()):
            messages.error(request, _("Full name is invalid"))
            return render(request, 'user/daftar.html', status=HTTPStatus.BAD_REQUEST)

        cleaned_full_name = str(full_name).split()
        cleaned_full_name = ' '.join(cleaned_full_name)
        if len(full_name) != len(cleaned_full_name):
            messages.error(request, _("The full name has too many spaces"))
            return render(request, 'user/daftar.html', status=HTTPStatus.BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, _('Invalid email address'))
            return render(request, 'user/daftar.html', status=HTTPStatus.BAD_REQUEST)

        if password1 != password2:
            messages.error(request, _('Different Passwords'))
            return render(request, 'user/daftar.html', status=HTTPStatus.BAD_REQUEST)

        
        if str(password1).isspace() or len(password1) < 1 and str(password2).isspace() or len(password2) < 1:
            messages.error(request, _(
                "Password cannot contain spaces or be empty"))
            return render(request, 'user/daftar.html', status=HTTPStatus.BAD_REQUEST)

        # validasi password
        try:
            validate_password(password1)
        except ValidationError as e:
            messages.error(request, '\n '.join(e))
            return render(request, 'user/daftar.html', status=HTTPStatus.BAD_REQUEST)

        # validasi apakah email telah digunakan

        if Users.objects.filter(email=email.lower()).exists():
            messages.error(request, _("User with email already exists"))
            return render(request, 'user/daftar.html', status=HTTPStatus.BAD_REQUEST)

        # kalau semua validasi lolos maka user dibuat
        user_obj = Users.objects.create_user(
            full_name=cleaned_full_name,
            email=email.lower(),
            password=password1
        )

        uid = urlsafe_base64_encode(force_bytes(user_obj.pk))
        token = account_activation_token.make_token(user_obj)        
        domain = get_current_site(request).domain
        protocol = request.is_secure() and "https" or "http"
        # Kirim email secara asinkronus dengan domain dan protocol sebagai argumen
        kirim_email_activate.delay(uid, token, user_obj.email.lower(), domain, protocol)
        url = reverse("user:masuk")
        return redirect(url+f"?command=verification&email={email}")

    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("home:home")
        return render(request, 'user/daftar.html', status=HTTPStatus.OK)


def aktifasi(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect("home:home")
    # decode uidb64 lalu dijadikan pk atau id asli
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user_obj = Users._default_manager.get(pk=uid)
    except Exception:
        messages.error(request, 'Link Token tidak valid.')
        return redirect("user:daftar")

    if account_activation_token.check_token(user_obj, token):
        # Pastikan token belum digunakan sebelumnya
        user_obj.is_active = True
        user_obj.waktu_aktifasi = timezone.now()
        user_obj.save()
        messages.success(
            request, f"Selamat {user_obj.full_name}, akunmu telah aktif.")
        return redirect('user:masuk')
    else:
        messages.error(request, 'Link Token tidak valid.')
        return redirect("user:masuk")


def masuk(request):
    if request.user.is_authenticated:
        return redirect("home:home")  # response 302

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user_obj = Users.objects.get(email=email.lower(), is_active=False)
            if user_obj:
                messages.error(request, 'Silahkan aktivasi akun melalui email. hubungi admin jika belum mendapatkan token')
                return render(request, 'user/masuk.html', status=HTTPStatus.UNAUTHORIZED)
        except Users.DoesNotExist:
            pass

        user = authenticate(request, email=email.lower(), password=password)
        # jika email dan password benar atau ada
        if user is not None:
            login(request, user)
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(
                    x.split("=") for x in query.split("&")
                )
                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect("home:home")  # response 302
        # jika email salah ataupun password salah
        else:
            try:
                url = request.META.get("HTTP_REFERER")
                query = requests.utils.urlparse(url).query
                params =dict(
                    x.split("=") for x in query.split("&")
                )
                if "next" in params:
                    nextPage = params["next"]
                    messages.error(request, 'Email Atau Password Salah')
                    return redirect(nextPage)
            except:
                messages.error(request, 'Email Atau Password Salah')
                return render(request, 'user/masuk.html', status=HTTPStatus.UNAUTHORIZED)
    else:
        return render(request, 'user/masuk.html', status=HTTPStatus.OK)


def keluar(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("user:masuk")
    raise Http404()


def lupaPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            user_obj = Users.objects.get(email=email.lower())
            if user_obj:
                now = timezone.now()
                if user_obj.last_password_reset_request:
                    time_since_last_request = now - user_obj.last_password_reset_request
                    remaining_time = timedelta(minutes=2) - time_since_last_request

                    if remaining_time > timedelta(0):
                        # Jika waktu tunda belum berlalu
                        seconds_remaining = int(remaining_time.total_seconds())
                        minutes_remaining, seconds_remaining = divmod(seconds_remaining, 60)
                        messages.error(request, f"kamu harus menunggu {minutes_remaining} menit dan {seconds_remaining} detik sebelum melakukan request kembali.")
                        return render(request, 'user/lupapassword.html')

                user_obj.last_password_reset_request = now
                user_obj.save()

                uid = urlsafe_base64_encode(force_bytes(user_obj.id_user))
                token = default_token_generator.make_token(user_obj)
                kirim_email_reset_password.delay(
                    uid=uid,
                    token=token,
                    user_obj_email=email,
                    domain=request.get_host(),
                    protocol=request.scheme
                )
                url = reverse("user:lupapassword")
                return redirect(url+f"?command=verification&email={email}")

        except Users.DoesNotExist:
            messages.error(request, 'Akun Tidak Ditemukan')
            return render(request, 'user/lupapassword.html', status=HTTPStatus.UNAUTHORIZED)
    else:
        if request.user.is_authenticated:
            return redirect("home:home")
        return render(request, 'user/lupapassword.html')

def resetPassword(request, uidb64, token):
    if request.method == "GET":
        if request.user.is_authenticated:
            logout(request)
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user_obj = Users._default_manager.get(pk=uid)
        except Exception:
            messages.error(request, 'Link Token tidak valid')
            return redirect("user:masuk")

        if default_token_generator.check_token(user_obj, token):
            return render(request, 'user/resetpassword.html', {"uid": uidb64, "token": token})
        else:
            messages.error(request, 'Link Token tidak valid')
            return redirect("user:masuk")

    if request.method == "POST":
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, _('Different Passwords'))
            return redirect("user:resetpassword", uidb64=uidb64, token=token)

        if str(password1).isspace() or len(password1) < 1 and str(password2).isspace() or len(password2) < 1:
            messages.error(request, _(
                "Password cannot contain spaces or be empty"))
            return redirect("user:resetpassword", uidb64=uidb64, token=token)

        try:
            validate_password(password1)
        except ValidationError as e:
            messages.error(request, '\n '.join(e))
            return redirect("user:resetpassword", uidb64=uidb64, token=token)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user_obj = Users._default_manager.get(pk=uid)
        except Exception:
            messages.error(request, 'Link Token tidak valid')
            return redirect("user:resetpassword", uidb64=uidb64, token=token)

        if default_token_generator.check_token(user_obj, token):
            user_obj.set_password(password1)
            user_obj.save()
            messages.success(request, "selamat password berhasil di reset")
            return redirect("user:masuk")
        else:
            messages.error(request, 'Link token tidak valid')
            return redirect("user:masuk")



class UbahPasswordView(PasswordChangeView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('menu:menu')
    template_name = 'user/ubah_password.html'


@login_required(login_url="user:masuk")
def add_profile(request):
    try:
        profile_obj = Profile.objects.get(user=request.user)
        if not any([profile_obj.foto, profile_obj.jenis_kelamin, profile_obj.tempat_tinggal, profile_obj.nomor_telepon, profile_obj.tanggal_lahir]):
            if not request.session.get('profile_message_displayed', False):
                if request.user.role == "pelajar":
                    messages.info(request, "Saat ini anda tidak diizinkan untuk mengakses beberapa halaman, anda harus melengkapi profil.")
                request.session['profile_message_displayed'] = True
    except Profile.DoesNotExist:
        profile_obj = None

    if request.method == "POST":
        forms = AddProfileForm(request.POST, request.FILES, instance=profile_obj)
        if forms.is_valid():
            profile = forms.save(commit=False)
            if not profile_obj:
                profile.user = request.user
            profile.save()
            cache_key = f'foto_profile_{request.user.pk}'
            cache.delete(cache_key)
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(
                    x.split("=") for x in query.split("&")
                )
                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect("menu:menu")  # response 302
        else:
            for field, errors in forms.errors.items():
                for error in errors:
                    messages.error(request, f"Error pada {field}: {error}")
    
    else:
        forms = AddProfileForm(instance=profile_obj)
    
    context = {
        "forms": forms,
    }
    return render(request, "user/addprofile.html", context)