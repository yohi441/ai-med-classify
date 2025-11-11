# inventory/views.py

from django.views.generic import ListView, CreateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import Transaction
from inventory.forms import TransactionForm
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "inventory/transactions_list.html"
    context_object_name = "transactions"
    paginate_by = 10
    login_url = "login"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        queryset = (
            Transaction.objects.select_related("medicine", "user", "classification")
            .order_by("-transaction_date")  # newest first
        )
        if q:
            queryset = queryset.filter(
                Q(transaction_date__icontains=q) |
                Q(medicine__generic_name__icontains=q) |
                Q(quantity_dispensed__icontains=q) |
                Q(user__username__icontains=q)
            )

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = datetime.now()
        return context
    
class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "inventory/transaction_form.html"
    success_url = reverse_lazy("transaction-list")
    login_url = "login"

    def form_valid(self, form):
        form.instance.user = self.request.user  # assign logged-in pharmacist
        response = super().form_valid(form)
        self.object.status = "dispensed"  # automatic approval and dispense
        self.object.save() # automatic dispense upon creation
        self.object.dispense()  # this change was made by the advisor
                         

        return response
    
    def get_initial(self):
        initial = super().get_initial()
        medicine_id = self.request.GET.get("medicine")
        if medicine_id:
            initial["medicine"] = medicine_id
        return initial

    
class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = "inventory/transaction_detail.html"
    context_object_name = "transaction"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = self.get_object()
        context["transaction"] = transaction
        context["now"] = datetime.now()
        return context
    
class TransactionStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        transaction = get_object_or_404(Transaction, pk=pk)
        new_status = request.POST.get("status")

        allowed_transitions = {
            "pending": ["approved", "dispensed", "rejected"],
            "approved": ["dispensed", "rejected"],
            "dispensed": [],  # no further changes
            "rejected": [],   # no further changes
        }

        current_status = transaction.status
        if new_status not in allowed_transitions.get(current_status, []):
            messages.error(request, f"Invalid transition from {current_status} → {new_status}.")
            return redirect("transaction-detail", pk=pk)

        transaction.status = new_status
        transaction.save()

        # Auto deduct stock if dispensed
        if new_status == "dispensed":
            transaction.dispense()

        messages.success(request, f"Transaction updated to {new_status}.")
        return redirect("transaction-detail", pk=pk)
