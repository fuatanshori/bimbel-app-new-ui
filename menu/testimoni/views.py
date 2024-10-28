from django.shortcuts import render
from .models import Testimoni
from core.utils.decorator import admin_pemateri_required,transaksi_settlement_required
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='user:masuk')
@transaksi_settlement_required
def testimoni(request):
    if request.user.role != "pelajar":
        testimoni_objs = Testimoni.objects.all()
        context = {
            "testimoni_objs":testimoni_objs,
            "star_range" : range(1, 6),
        }
        return render(request,"testimoni/testimoni_admin.html", context)
    try:
        testimoni_obj = Testimoni.objects.get(user=request.user)
    except Testimoni.DoesNotExist:
        testimoni_obj = None

    if request.method == "POST":
        rating = request.POST.get("rating")
        review = request.POST.get("review")
        
        if testimoni_obj:
            testimoni_obj.testimonial_review = review
            testimoni_obj.rating = rating
            testimoni_obj.save()
        else:
            testimoni_obj = Testimoni.objects.create(
                user=request.user,
                testimonial_review=review,
                rating=rating
            )

    context = {
        "review": testimoni_obj.testimonial_review if testimoni_obj else "",
        "rating": int(testimoni_obj.rating) if testimoni_obj else "",
    }
    
    return render(request, "testimoni/testimoni.html", context)