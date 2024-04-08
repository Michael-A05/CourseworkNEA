from django.urls import path

from . import views
from .views import SignUpView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('home/', views.profile, name='user_page'),
    path('choose_allergens/', views.choose_allergens, name='choose_allergens'),
    path('remove_allergen/<int:choice_id>/', views.remove_allergen, name='remove_allergen'),
]
