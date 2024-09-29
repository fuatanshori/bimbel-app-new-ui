from django.urls import path,re_path
from . import views as views_menu
from .pembayaran import views as views_pembayaran
from .modul import views as views_modul
from .ujian import views as views_ujian
from .nilai import views as views_nilai
from .mapel import views as views_mapel
from .levelstudy import views as views_levelstudy

# menu
urlpatterns = [
    path('', views_menu.menu, name='menu'),
]
# pembayaran
urlpatterns += [
    path('pembayaran/', views_pembayaran.pembayaran, name='pembayaran'),
    path('pembayaran/menu/', views_pembayaran.menu_pembayaran, name='pembayaran-menu'),
    path('pembayaran-admin-list/', views_pembayaran.pembayaran_admin_list, name='pembayaran-admin-list'),
    path('buatpesanan/', views_pembayaran.buat_pesanan, name='buat_pesanan'),
    path('batalkanpesanan/<str:id_transaksi>/',
         views_pembayaran.batalkan_pesanan, name="batalkan_pesanan"),
    path('pembayaran/invoice/<str:id_transaksi>/', views_pembayaran.invoice, name='invoice'),
    path('notifikasi-midtrans/', views_pembayaran.notifikasi_midtrans_handler,
         name="notifikasi_midtrans_handler"),
    path('laporan-transaksi/',views_pembayaran.laporan_excel,name='laporan-transaksi'),
    path("laporan-invoice/",views_pembayaran.laporan_invoice,name="laporan-invoice"),
    path("pembayaran/invoice-gopay/<str:id_transaksi>/",views_pembayaran.invoice_gopay,name="invoice-gopay"),
    re_path(r'^pembayaran/[^/]+/$', views_pembayaran.pembayaran, name='pembayaran-gopay-redirect'),
    path("tarif/",views_pembayaran.tarif,name="tarif"),
    path("tarif/delete/<id_tarif>/",views_pembayaran.delete_tarif,name="delete-tarif"),
    path("tarif/add/",views_pembayaran.add_tarif,name="add-tarif"),
    path("tarif/edit/<id_tarif>/",views_pembayaran.edit_tarif,name="edit-tarif"),
    path("diskon/<id_tarif>/",views_pembayaran.diskon,name="diskon"),
    path("diskon/add/<id_tarif>/",views_pembayaran.add_diskon,name="add-diskon"),
    path("diskon/delete/<id_tarif>/<id_diskon>/",views_pembayaran.delete_diskon,name="delete-diskon"),
    path("diskon/edit/<id_tarif>/<id_diskon>/",views_pembayaran.edit_diskon,name="edit-diskon"),
]

# modul
urlpatterns += [
    path("modul/levelstudy/", views_modul.modul_levelstudy, name='levelstudy-modul'),
    path("modul/mapel/<id_levelstudy>/", views_modul.modul_mapel, name='mapel-modul'),
    path("modul/daftar-modul/<id_levelstudy>/<id_mapel>/", views_modul.daftar_modul, name='daftar-modul'),
    path('modul/delete-modul/<id_levelstudy>/<id_mapel>/<id_modul>/',views_modul.hapusModul, name='hapus-modul'),
    path('modul/tambah/<id_levelstudy>/<id_mapel>/', views_modul.tambah_modul, name='tambah-modul'),
    path('modul/edit/<id_mapel>/<id_modul>/', views_modul.edit_modul, name='edit-modul'),
    
    path('modul/detail/<id_levelstudy>/<id_mapel>/<id_modul>/', views_modul.detailmodul, name='detail-modul'),
]


# ujian
urlpatterns+=[
    path("ujian/mapel/levelstudy/", views_ujian.levelstudy_ujian, name='levelstudy-ujian'),
    path("ujian/mapel/<id_levelstudy>/", views_ujian.ujian_mapel, name='mapel-ujian'),
    path("ujian/daftar-ujian-admin-pemateri/<id_mapel>/", views_ujian.daftar_ujian_admin_pemateri, name='daftar-ujian-admin-pemateri'),
    path('ujian/delete-ujian/<id_mapel>/<id_soal_ujian>/',views_ujian.hapusSoalUjian, name='hapus-soal-ujian'),
    path('ujian/tambah/<id_mapel>/', views_ujian.tambah_ujian, name='tambah-ujian'),
    path('ujian/edit/<id_mapel>/<id_soal_ujian>/', views_ujian.edit_ujian, name='edit-ujian'),

    path('ujian/<id_mapel>/', views_ujian.ujian, name='ujian'),
    path('ujian/nilai/<id_mapel>/<id_nilai>/', views_ujian.nilai_setelah_ujian, name='nilai-setelah-ujian'),
]

# nilai
urlpatterns+=[
    path("nilai/", views_nilai.daftar_nilai, name='daftar-nilai'),
    path("nilai-permapel/<id_mapel>/", views_nilai.daftar_nilai_permapel, name='daftar-nilai-permapel'),
    path("nilai/ujian_ulang/<id_mapel>/<id_nilai>/",views_nilai.lakukan_ujian_ulang,name='ujian-ulang')
]

# mapel
urlpatterns+=[
    path('mapel/levelstudy/',views_mapel.levelstudy_mapel,name="mapel-levelstudy"),
    path('mapel/<id_levelstudy>/',views_mapel.mapel,name="mapel"),
    path('mapel/tambah/<id_levelstudy>/',views_mapel.tambah_mapel,name="tambah-mapel"),
    path('mapel/hapus/<id_levelstudy>/<id_mapel>/',views_mapel.hapus_mapel,name="hapus-mapel"),
    path('mapel/edit/<id_levelstudy>/<id_mapel>/',views_mapel.edit_mapel,name="edit-mapel"),
]


# levelstudy
urlpatterns+=[
    path('levelstudy/',views_levelstudy.levelstudy,name="levelstudy"),
    path('levelstudy/tambah-levelstudy/',views_levelstudy.tambah_levelstudy,name="tambah-levelstudy"),
    path('levelstudy/hapus-levelstudy/<id_levelstudy>/',views_levelstudy.hapus_levelstudy,name="hapus-levelstudy"),
    path('levelstudy/edit-levelstudy/<id_levelstudy>/',views_levelstudy.edit_levelstudy,name="edit-levelstudy"),
]