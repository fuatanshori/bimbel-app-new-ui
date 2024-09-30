from django.http import Http404
from functools import wraps
from django.shortcuts import redirect
from menu.pembayaran.models import Transaksi

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



def transaksi_settlement_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            Transaksi.objects.get(user=request.user, transaksi_status="settlement")
        except Transaksi.DoesNotExist:
            if request.user.role not in ["pemateri", "admin"]:
                return redirect("menu:pembayaran")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
