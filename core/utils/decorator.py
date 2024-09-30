# myapp/decorators.py

from django.http import Http404
from functools import wraps

def admin_pemateri_required(function):
    """
    Decorator untuk memastikan pengguna adalah admin dan pemateri
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.role not in ["pemateri","admin"]:
            raise Http404
        return function(request, *args, **kwargs)
    return wrap


def admin_required(function):
    """
    Decorator untuk memastikan pengguna adalah admin dan pemateri
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.role not in ["admin"]:
            raise Http404
        return function(request, *args, **kwargs)
    return wrap

from functools import wraps
from django.shortcuts import redirect
from menu.pembayaran.models import Transaksi

def transaksi_settlement_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            # Cek apakah ada transaksi dengan status "settlement"
            Transaksi.objects.get(user=request.user, transaksi_status="settlement")
        except Transaksi.DoesNotExist:
            # Jika tidak ada dan pengguna bukan pemateri atau admin, redirect ke halaman pembayaran
            if request.user.role not in ["pemateri", "admin"]:
                return redirect("menu:pembayaran")
        # Lanjutkan ke view jika syarat terpenuhi
        return view_func(request, *args, **kwargs)

    return _wrapped_view
