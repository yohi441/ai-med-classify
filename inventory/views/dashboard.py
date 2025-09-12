# inventory/views/dashboard.py

from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Count
from inventory.models import Medicine, Inventory, Classification, Transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/dashboard.html"
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Inventory stats
        context['total_medicines'] = Medicine.objects.count()
        context['total_stock'] = Inventory.objects.aggregate(total=Count('quantity'))['total']

        # Low stock medicines (threshold = 10)
        context['low_stock'] = Inventory.objects.filter(quantity__lt=10)

        # Expired or near-expiry medicines (within 30 days)
        today = timezone.now().date()
        context['near_expiry'] = Inventory.objects.filter(expiration_date__lte=today + timezone.timedelta(days=30))

        # Pending classifications (new medicine requests waiting for pharmacist)
        context['pending_classifications'] = Classification.objects.filter(approved=False)

        # Recent transactions
        context['recent_transactions'] = Transaction.objects.order_by('-transaction_date')[:5]
        context['now'] = datetime.now()


        return context
