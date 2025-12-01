# inventory/views.py

from django.views.generic import ListView, CreateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import Transaction, TransactionBatch, DosageInstruction
from inventory.forms import TransactionForm
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render
from inventory.models import Medicine
from inventory.forms import TransactionForm, TransactionFormSet
from django.forms import modelformset_factory
from django.db import transaction as db_transaction
from django.urls import reverse



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
                Q(user__username__icontains=q) |
                Q(batch__batch_id__icontains=q),
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
    
    def get_success_url(self):
        return reverse("transaction-detail", kwargs={"pk": self.object.pk})

    
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


class TransactionCreateMultipleView(LoginRequiredMixin, View):
    template_name = "inventory/transaction_form_multiple.html"

    def get(self, request):
        medicines = Medicine.objects.all()
        dosage = DosageInstruction.objects.all()
        return render(request, self.template_name, {'medicines': medicines, "dosage": dosage})

    def post(self, request):
        medicines = Medicine.objects.all()
        dosage = DosageInstruction.objects.all()
        total_forms = int(request.POST.get('form-TOTAL_FORMS', 0))
        if not total_forms:
            return render(request, self.template_name, {
                'errors': ['No forms added']
            })
        errors = []

        try:
            with db_transaction.atomic():
                transactions_to_create = []
                tb = TransactionBatch.objects.create(
                    user=request.user,
                    batch_id=TransactionBatch.generate_batch_id()
                )
                for i in range(total_forms):
                    med_id = request.POST.get(f'form-{i}-medicine')
                    qty = request.POST.get(f'form-{i}-quantity_dispensed')
                    dos_id = request.POST.get(f'form-{i}-dosage')
                    remarks = request.POST.get(f'form-{i}-remarks')

                    if not med_id or not qty or not dos_id:
                        errors.append(f"Row {i+1}: Medicine and quantity and dosage are required")
                        continue

                    try:
                        med = Medicine.objects.get(id=med_id)
                    except Medicine.DoesNotExist:
                        errors.append(f"Row {i+1}: Medicine with ID {med_id} does not exist")
                        continue
                    
                    try:
                        dos = DosageInstruction.objects.get(id=dos_id)
                    except DosageInstruction.DoesNotExist:
                        errors.append(f"Row {i+1}: Medicine with ID {med_id} does not exist")
                        continue

                    qty = int(qty)
                    total_stock = med.inventory.aggregate(total=Sum("quantity"))["total"] or 0
                    if qty > total_stock:
                        errors.append(f"Row {i+1}: Not enough stock for {med.generic_name}. Available: {total_stock}, requested: {qty}")
                        continue

                    transactions_to_create.append((med, qty, remarks))

                if errors:
                    # If there are any errors, rollback by not creating anything
                    raise ValueError("Validation failed")

                # If all rows are valid, save transactions
                for med, qty, remarks in transactions_to_create:
                    tx = Transaction.objects.create(
                        batch=tb,
                        user=request.user,
                        dosage=dos,
                        medicine=med,
                        quantity_dispensed=qty,
                        remarks=remarks,
                        status='dispensed'
                    )
                    tx.dispense()

        except ValueError:
            # Render template with errors, nothing is saved
            return render(request, self.template_name, {
                'medicines': medicines,
                'dosage': dosage,
                'errors': errors,
                'initial_form': total_forms
            })

        return redirect('transaction-success-multiple', pk=tb.pk)
    
class TransactionSuccessView(LoginRequiredMixin, View):
    template_name = 'inventory/transaction_success.html'
    def get(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)
        context = {
            "transaction": transaction
        }
        return render(request, self.template_name, context)
    
class TransactionSuccessMultipleView(LoginRequiredMixin, View):
    template_name = 'inventory/transaction_success_multiple.html'
    def get(self, request, pk):
        batch = TransactionBatch.objects.get(pk=pk)
        transaction_items = Transaction.objects.filter(batch=batch)
        context = {
            "transaction_items": transaction_items
        }
        print(transaction_items)
        return render(request, self.template_name, context)