from django.contrib.auth.models import Group, Permission


DEALERS_GROUP_NAME = 'Dealers'
MODERATORS_GROUP_NAME = 'Moderators'

DEALER_PERMISSIONS = (
    ('cars', 'add_car'),
    ('cars', 'change_car'),
    ('cars', 'delete_car'),
    ('cars', 'view_car'),
    ('inquiries', 'add_inquiry'),
    ('inquiries', 'view_inquiry'),
    ('accounts', 'view_profile'),
    ('accounts', 'change_profile'),
    ('accounts', 'view_favorite'),
    ('accounts', 'add_favorite'),
    ('accounts', 'delete_favorite'),
)

MODERATOR_PERMISSIONS = (
    ('cars', 'view_car'),
    ('cars', 'change_car'),
    ('catalog', 'view_brand'),
    ('catalog', 'add_brand'),
    ('catalog', 'change_brand'),
    ('catalog', 'delete_brand'),
    ('catalog', 'view_feature'),
    ('catalog', 'add_feature'),
    ('catalog', 'change_feature'),
    ('catalog', 'delete_feature'),
    ('inquiries', 'view_inquiry'),
)


def user_is_admin(user):
    return user.is_authenticated and user.is_superuser


def user_is_moderator(user):
    return (
        user.is_authenticated
        and (user_is_admin(user) or user.groups.filter(name=MODERATORS_GROUP_NAME).exists())
    )


def user_is_dealer(user):
    return (
        user.is_authenticated
        and not user_is_moderator(user)
        and user.groups.filter(name=DEALERS_GROUP_NAME).exists()
    )


def ensure_role_groups():
    dealers_group, _ = Group.objects.get_or_create(name=DEALERS_GROUP_NAME)
    moderators_group, _ = Group.objects.get_or_create(name=MODERATORS_GROUP_NAME)

    dealers_group.permissions.set(_get_permissions(DEALER_PERMISSIONS))
    moderators_group.permissions.set(_get_permissions(MODERATOR_PERMISSIONS))

    sync_regular_users_to_dealers()


def assign_user_to_default_group(user):
    if user.is_staff or user.is_superuser:
        return

    dealers_group, _ = Group.objects.get_or_create(name=DEALERS_GROUP_NAME)
    user.groups.add(dealers_group)


def sync_regular_users_to_dealers():
    dealers_group, _ = Group.objects.get_or_create(name=DEALERS_GROUP_NAME)
    regular_users = (
        dealers_group.user_set.model.objects
        .filter(is_staff=False, is_superuser=False)
        .exclude(groups__name=MODERATORS_GROUP_NAME)
    )

    for user in regular_users.iterator():
        user.groups.add(dealers_group)


def _get_permissions(permission_specs):
    permissions = []

    for app_label, codename in permission_specs:
        permission = Permission.objects.filter(
            content_type__app_label=app_label,
            codename=codename,
        ).first()
        if permission is not None:
            permissions.append(permission)

    return permissions
