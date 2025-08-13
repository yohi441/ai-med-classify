# inventory/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from inventory.models import Medicine
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin

class MedicineListView(LoginRequiredMixin, ListView):
    model = Medicine
    template_name = "inventory/medicines_list.html"
    context_object_name = "medicines"
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        # Annotate each medicine with the sum of its inventory quantities
        return (
            Medicine.objects.all()
            .annotate(total_stock=Sum("inventory__quantity"))
            .select_related("classification")
        )

class MedicineDetailView(LoginRequiredMixin, DetailView):
    model = Medicine
    template_name = "inventory/medicine_detail.html"
    context_object_name = "medicine"
    login_url = 'login'
