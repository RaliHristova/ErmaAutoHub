from django.contrib.auth import views as auth_views
from django.urls import path

from .views import RegisterView, ProfileDetailView, ProfileUpdateView, FavoriteCarsListView, AddFavoriteView, \
    RemoveFavoriteView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',auth_views.LoginView.as_view(template_name='accounts/login.html'),name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', ProfileDetailView.as_view(), name='profile-details'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile-edit'),
    path('favorites/', FavoriteCarsListView.as_view(), name='favorite-cars'),
    path('favorites/add/<int:car_id>/', AddFavoriteView.as_view(), name='add-favorite'),
    path('favorites/remove/<int:car_id>/', RemoveFavoriteView.as_view(), name='remove-favorite'),
]