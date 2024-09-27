import midtransclient
from django.conf import settings

MIDTRANS_CORE = midtransclient.CoreApi(
    is_production = settings.MIDTRANS['IS_PRODUCTION'],
    server_key=settings.MIDTRANS['SERVER_KEY'],
    client_key=settings.MIDTRANS['CLIENT_KEY'],
)

PAYMENT_STATUS = {
'pending': 'Belum Dibayar',
'settlement': 'Telah Dibayar',
'expire': 'Pembayaran Melebihi Batas Waktu',
'cancel': 'Pesanan Anda Batalkan',
'deny': 'Pembayaran Ditolak'
}