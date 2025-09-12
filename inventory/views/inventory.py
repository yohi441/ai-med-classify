# inventory/views.py

from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from inventory.models import Inventory, Transaction
from datetime import datetime
from django.db.models import Q


class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = "inventory/inventory_list.html"
    context_object_name = "inventories"
    paginate_by = 10
    login_url = "login"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        # Prefetch related medicine so queries are efficient
        queryset = (
            Inventory.objects.select_related("medicine")
            .order_by("expiration_date")  # default sort: nearest to expire
        )
        if q:
            queryset = queryset.filter(
                Q(medicine__generic_name__icontains=q) |
                Q(batch_number__icontains=q)
            )

        return queryset

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = datetime.now()
        return context
    
class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = Inventory
    template_name = "inventory/inventory_detail.html"
    context_object_name = "inventory"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch = self.object

        # Get transactions linked to this medicine (later can track by batch)
        context["transactions"] = (
            Transaction.objects.filter(medicine=batch.medicine)
            .order_by("-transaction_date")[:20]
        )
        context["now"] = datetime.now()
        return context


