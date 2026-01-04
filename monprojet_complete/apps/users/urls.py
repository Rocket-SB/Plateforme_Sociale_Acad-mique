from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('follow/<int:pk>/', views.follow_user, name='follow'),
    path('unfollow/<int:pk>/', views.unfollow_user, name='unfollow'),
    path('save/<int:pk>/', views.save_profile, name='save_profile'),
    path('unsave/<int:pk>/', views.unsave_profile, name='unsave_profile'),
    path('saved/', views.saved_profiles, name='saved_profiles'),
]
