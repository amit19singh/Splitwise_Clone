from django import forms
from .models import Expense
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'paid_by', 'split_among', 'group', 'date']
        # Define other fields and widgets as necessary
        
    def save(self, commit=True):
        expense = super().save(commit=False)
        if commit:
            expense.save()
            self.save_shares(expense)
        return expense
    
    def save_shares(self, expense):
        # Get the split type
        split_type = self.cleaned_data.get('split_type')

        if split_type == 'equal':
            split_amount = expense.amount / expense.split_among.count()
            for user in expense.split_among.all():
                ExpenseShare.objects.update_or_create(
                    expense=expense, 
                    user=user,
                    defaults={'amount': split_amount, 'percentage': None}
                )
        elif split_type == 'unequal':
            # Assume you have a dictionary of amounts passed in the form
            amounts = self.cleaned_data.get('unequal_amounts', {})
            for user_id, amount in amounts.items():
                user = User.objects.get(id=user_id)
                ExpenseShare.objects.update_or_create(
                    expense=expense, 
                    user=user,
                    defaults={'amount': amount, 'percentage': None}
                )

        elif split_type == 'percentage':
            # Assume you have a dictionary of percentages passed in the form
            percentages = self.cleaned_data.get('percentage_shares', {})
            for user_id, percentage in percentages.items():
                user = User.objects.get(id=user_id)
                calculated_amount = (expense.amount * percentage) / 100
                ExpenseShare.objects.update_or_create(
                    expense=expense, 
                    user=user,
                    defaults={'amount': calculated_amount, 'percentage': percentage}
                )
    
    def clean(self):
        cleaned_data = super().clean()
        split_type = cleaned_data.get('split_type')

        if split_type == 'unequal' or split_type == 'percentage':
            shares = self.instance.shares.all()
            total_share = sum(share.amount for share in shares) if split_type == 'unequal' else sum(share.percentage for share in shares)

            if split_type == 'unequal' and total_share != cleaned_data.get('amount'):
                raise forms.ValidationError("The total of all shares must equal the expense amount.")
            elif split_type == 'percentage' and total_share != 100:
                raise forms.ValidationError("The total of all percentages must equal 100%.")

        return cleaned_data



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        

