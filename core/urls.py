from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', include('django_prometheus.urls')),
    path('health/', include('health_check.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('admin/', admin.site.urls),
    path('users/', include(('user.urls', 'user'))),
    path('', include(('home.urls', 'home'))),
    path('menu/', include(('menu.urls', 'menu'))),
    path('media/soal/<str:image_file>', views.soal_media_protect),
    path('media/foto_profile/<str:image_file>', views.profile_foto),
    path('media/sertifikat/<str:image_file>', views.sertifikat_media_protect),
    path('media/pdf/<str:pdf_file>', views.pdf_protect_membership),
    path('media/vidio/<str:vidio_file>', views.vidio_protect_membership),
    path('favicon.ico', views.CachedRedirectView.as_view(url='/static/assets/img/favicon/favicon.ico'))
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

