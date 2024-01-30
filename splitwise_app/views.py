from django.views import View
from .forms import ExpenseForm
from django.db.models import F
from .forms import UserRegisterForm
from django.urls import reverse_lazy
from .models import Expense, Group, Balance
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView


class UserRegisterView(FormView):
    template_name = 'register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
class UserLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('splitwise_home')
        
    
class HomeView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'home.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        return Expense.objects.filter(paid_by=self.request.user)


class AddExpenseView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'add_expense.html'
    success_url = reverse_lazy('splitwise_home')

    def form_valid(self, form):
        form.instance.paid_by = self.request.user
        return super().form_valid(form)

class EditExpenseView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'edit_expense.html'
    success_url = reverse_lazy('splitwise_home')
    
    
class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'group_details.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expenses'] = Expense.objects.filter(group=self.object)
        return context


class SettleUpView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        payment_amount = kwargs.get('payment_amount', 0)  # Default to 0 if not provided
        payment_amount = float(payment_amount)  # Convert to float, handle exceptions as needed

        user_to_pay = get_object_or_404(User, id=user_id)
        balance = get_object_or_404(Balance, user_from=request.user, user_to=user_to_pay)

        if payment_amount <= 0 or payment_amount > balance.amount:
            return HttpResponseBadRequest("Invalid payment amount")

        balance.amount = F('amount') - payment_amount
        balance.save()

        return redirect('splitwise_home')
    


