import datetime
from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='splitwise_groups')

    def __str__(self):
        return self.name


class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField(default=datetime.datetime.now)
    paid_by = models.ForeignKey(User, related_name='paid_expenses', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='expenses', on_delete=models.CASCADE, null=True, blank=True)
    split_among = models.ManyToManyField(User, related_name='shared_expenses')
    split_type = models.CharField(max_length=10, choices=[('equal', 'Equal'), ('unequal', 'Unequal'), ('percentage', 'Percentage')], default='equal')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_balances()

    def update_balances(self):
        if self.split_type == 'equal':
            # split_amount = self.amount / self.split_among.count()
            split_amount = self.amount
            for user in self.split_among.all():
                self.update_balance(user, split_amount)
        elif self.split_type == 'unequal':
            for share in self.shares.all():
                self.update_balance(share.user, share.amount)
        elif self.split_type == 'percentage':
            for share in self.shares.all():
                amount = self.amount * (share.percentage / 100)
                self.update_balance(share.user, amount)

    def update_balance(self, user, amount):
        if user != self.paid_by:
            balance, created = Balance.objects.get_or_create(
                user_from=user, 
                user_to=self.paid_by
            )
            balance.amount += amount
            balance.save()
    
    def __str__(self):
        return f"{self.description} - {self.amount}"


class ExpenseShare(models.Model):
    expense = models.ForeignKey(Expense, related_name='shares', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='expense_shares', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # For unequal splits
    percentage = models.FloatField(null=True, blank=True)  # For percentage splits


class Balance(models.Model):
    user_from = models.ForeignKey(User, related_name='balances_owed', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='balances_due', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user_from} owes {self.user_to}: {self.amount}"

