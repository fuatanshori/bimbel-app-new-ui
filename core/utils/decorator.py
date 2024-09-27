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
