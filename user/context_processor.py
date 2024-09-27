from .models import Profile


def get_foto_profile(request):
    if request.user.is_authenticated:
        try:
            profile_obj = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return {}
        return {
            'foto_profile': profile_obj if profile_obj.foto else None
        }
    else:
        return {}