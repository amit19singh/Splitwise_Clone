from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='splitwise_home'),
    path('add-expense/', AddExpenseView.as_view(), name='add_expense'),
    path('expense/edit/<int:pk>/', EditExpenseView.as_view(), name='edit_expense'),
    path('group/<int:pk>/', GroupDetailView.as_view(), name='group_details'),
    path('settle-up/<int:user_id>/', SettleUpView.as_view(), name='settle_up'),
    # Authentication URLs
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]


