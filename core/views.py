from django.conf import settings
from django.shortcuts import HttpResponse,render
from django.http.response import FileResponse,Http404
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from menu.pembayaran.models import Transaksi
from django.shortcuts import redirect
import os
import io
from datetime import datetime, timedelta
import hashlib
from django.http import StreamingHttpResponse

# hanya pelajar yang sukses melakukan pembayaran akan diizinkan melihat pdf. admin/pemateri
@login_required(login_url="user:masuk")
def pdf_protect_membership(request, pdf_file):
    cache_key = f"pdf_{request.user.id}_{pdf_file}"
    pdf_content = cache.get(cache_key)
    if pdf_content is None:
        try:
            transaksi_obj = Transaksi.objects.get(
                user=request.user, transaksi_status="settlement")
            if transaksi_obj:
                file_path = os.path.join(settings.MEDIA_ROOT, 'pdf', pdf_file)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        pdf_content = file.read()
                    cache.set(cache_key, pdf_content, timeout=60*15)
                else:
                    raise Http404("File tidak ditemukan")
            else:
                return redirect("menu:pembayaran")
                
        except Transaksi.DoesNotExist:
            if request.user.role in ["admin", "pemateri"]:
                file_path = os.path.join(settings.MEDIA_ROOT, 'pdf', pdf_file)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        pdf_content = file.read()
                    cache.set(cache_key, pdf_content, timeout=60*15)  # Cache selama 15 menit
                else:
                    raise Http404("File tidak ditemukan")
            if request.user.role == "pelajar":
                return redirect("menu:pembayaran")
    
    response = FileResponse(io.BytesIO(pdf_content), content_type='application/pdf')
    response['Cache-Control'] = 'public, max-age=86400'  # Cache selama 1 hari (24 * 60 * 60)
    response['Expires'] = (datetime.utcnow() + timedelta(days=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

# hanya pelajar yang sukses melakukan pembayaran akan diizinkan melihat vidio. admin/pemateri
@login_required(login_url="user:masuk")
def vidio_protect_membership(request, vidio_file):
    media_path = os.path.join(settings.MEDIA_ROOT, 'vidio')
    video_path = os.path.join(media_path, vidio_file)

    # Cek apakah file ada
    if not os.path.exists(video_path):
        raise Http404("File tidak ditemukan")

    try:
        transaksi_obj = Transaksi.objects.get(user=request.user, transaksi_status="settlement")

        with open(video_path, 'rb') as video_file:
            response = HttpResponse(video_file, content_type='video/mp4')
            response['Content-Disposition'] = f'inline; filename="{vidio_file}"'
            response['Accept-Ranges'] = 'bytes'
            
            # Mendukung permintaan range
            range_header = request.META.get('HTTP_RANGE', None)
            if range_header:
                # Parse the range header
                range_value = range_header.split('=')[1]
                start, end = map(int, range_value.split('-'))
                video_file.seek(start)
                length = end - start + 1
                response = HttpResponse(video_file.read(length), status=206)
                response['Content-Range'] = f'bytes {start}-{end}/{os.path.getsize(video_path)}'
                response['Content-Length'] = length
            else:
                response['Content-Length'] = os.path.getsize(video_path)
                
            return response

    except Transaksi.DoesNotExist:
        # Cek role pengguna
        if request.user.role in ["admin", "pemateri"]:
            with open(video_path, 'rb') as video_file:
                response = HttpResponse(video_file, content_type='video/mp4')
                response['Content-Disposition'] = f'inline; filename="{vidio_file}"'
                response['Accept-Ranges'] = 'bytes'
                return response
        else:
            # Pengguna tidak memiliki akses, redirect ke halaman pembayaran
            return redirect("menu:pembayaran")


@login_required(login_url="user:masuk")
def soal_media_protect(request, image_file):
    media_root = os.path.join(settings.MEDIA_ROOT)
    img = open(F'{media_root}/soal/{image_file}', 'rb')
    response = FileResponse(img)
    return response


def sertifikat_media_protect(request, image_file):
    cache_key = f"sertifikat_{image_file}"
    img_content = cache.get(cache_key)
    if img_content is None:
        media_root = os.path.join(settings.MEDIA_ROOT, 'sertifikat')
        file_path = os.path.join(media_root, image_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as img_file:
                    img_content = img_file.read()
                cache.set(cache_key, img_content, timeout=60*1)  # Cache selama 15 menit
                return FileResponse(io.BytesIO(img_content), content_type='image/jpeg')
            except Exception as e:
                return HttpResponse(f"Terjadi kesalahan saat mengakses file: {e}", status=500)
        else:
            raise Http404("Sertifikat tidak ditemukan")
    else:
        return FileResponse(io.BytesIO(img_content), content_type='image/jpeg')


@login_required(login_url="user:masuk")
def profile_foto(request, image_file):
    # Membuat cache key yang unik berdasarkan nama file
    cache_key = f"profile_foto_{hashlib.md5(image_file.encode()).hexdigest()}"
    
    image_content = cache.get(cache_key)
    
    if image_content is None:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, 'foto_profile', image_file)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as img_file:
                    image_content = img_file.read()
                cache.set(cache_key, image_content, timeout=60*60*24)
            else:
                raise Http404("File tidak ditemukan")
        except Exception as e:
            raise Http404("Terjadi kesalahan saat membaca file: " + str(e))
    response = FileResponse(io.BytesIO(image_content))
    response['Cache-Control'] = 'public, max-age=86400'
    return response

def custom_404_handler(request):
    context = {}
    return render(request,"404.html",context,status=404)

def custom_500_handler(request):
    context = {}
    return render(request,"500.html",context,status=500)

def csrf_failure(request, reason=""):
    return render(
        request,
        "403_csrf.html",
        {"reason": reason},
        status=403,
    )