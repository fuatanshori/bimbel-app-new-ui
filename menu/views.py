from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .pembayaran.models import Transaksi
from config import midtrans

@login_required(login_url="user:masuk")
def menu(request):
    try:
        transaksi_obj = Transaksi.objects.get(user=request.user)
        status_transaksi = midtrans.PAYMENT_STATUS[transaksi_obj.transaksi_status]
    except Transaksi.DoesNotExist:
        status_transaksi = None

    context = {
        'status_transaksi': status_transaksi
    }
    return render(request, "menu/menu.html",context)
