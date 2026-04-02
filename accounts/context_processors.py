from .roles import user_is_admin, user_is_dealer, user_is_moderator


def user_roles(request):
    return {
        'is_admin': user_is_admin(request.user),
        'is_dealer': user_is_dealer(request.user),
        'is_moderator': user_is_moderator(request.user),
    }
