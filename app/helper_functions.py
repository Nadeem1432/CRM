from app.models import *


def all_under_user(username):
    users = []
    super_data = list(User.objects.filter(created_by= username).values_list('username', flat=True))
    users += super_data
    seller_data = list(User.objects.filter(created_by__in= super_data).values_list('username', flat=True))
    users += seller_data
    # users.append(username)
    return users