# inventory/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from inventory.models import Medicine
from django.db.models import Sum, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime

class MedicineListView(LoginRequiredMixin, ListView):
    model = Medicine
    template_name = "inventory/medicines_list.html"
    context_object_name = "medicines"
    paginate_by = 10
    login_url = 'login'

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()

        queryset = (
            Medicine.objects.all()
            .annotate(total_stock=Sum("inventory__quantity")).order_by('generic_name')
        )

        if q:
            queryset = queryset.filter(
                Q(generic_name__icontains=q) |
                Q(brand_name__icontains=q) |
                Q(manufacturer__icontains=q)
            )

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = datetime.now()

        return context

class MedicineDetailView(LoginRequiredMixin, DetailView):
    model = Medicine
    template_name = "inventory/medicine_detail.html"
    context_object_name = "medicine"
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = datetime.now()

        return context
