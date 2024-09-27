from .models import Transaksi
from .views import PAYMENT_STATUS
def transaksi(request):
    if request.user.is_anonymous:
        return {}

    try:
        transaksi_obj = Transaksi.objects.get(user=request.user, transaksi_status="settlement")
        status_transaksi = [PAYMENT_STATUS.get(transaksi_obj.transaksi_status)]
    except Transaksi.DoesNotExist:
        if request.user.role == "admin" or request.user.role == "pemateri":
            status_transaksi = [None]
        else:
            status_transaksi = []  

    return {
        'status_transaksi': status_transaksi[0] if status_transaksi else None
    }


        