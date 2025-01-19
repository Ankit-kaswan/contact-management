from django.urls import path
from .views import UserRegistrationView, UserProfileView, MarkSpamView, SearchPersonView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('mark_spam/', MarkSpamView.as_view(), name='mark_spam'),
    path('search/', SearchPersonView.as_view(), name='search_by_name'),
]
