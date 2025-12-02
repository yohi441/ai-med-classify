# inventory/views/dashboard.py

from django.views import View
from django.utils import timezone
from django.db.models import Count
from inventory.models import Medicine, Inventory, Classification, Transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.core.paginator import Paginator
from django.shortcuts import render
from urllib.parse import urlencode, urlparse, parse_qs
import time

class DashboardView(LoginRequiredMixin, View):
    template_name = "inventory/dashboard.html"
    login_url = 'login'

    def get(self, request):
        
        total_medicines = Medicine.objects.count()
        total_stock = Inventory.objects.aggregate(total=Count('quantity'))['total']
      
        # Querysets
        low_stock_qs = Inventory.objects.filter(quantity__lte=10).order_by('quantity')
        near_expiry_qs = Inventory.objects.filter(expiration_date__lte=timezone.now().date() + timezone.timedelta(days=30)).order_by('expiration_date')
        transactions_qs = Transaction.objects.order_by('-transaction_date')
        expired_qs = Inventory.objects.expired()

        # Pagination setup
        low_stock_paginator = Paginator(low_stock_qs, 5)
        near_expiry_paginator = Paginator(near_expiry_qs, 5)
        tx_paginator = Paginator(transactions_qs, 5)
        expired_paginator = Paginator(expired_qs, 5)

        context = {
            'total_medicines': total_medicines,
            'total_stock': total_stock,
            'low_stock': low_stock_paginator.get_page(self.request.GET.get('low_page', 1)),  # Show only first 5 items
            'low_stock_paginator': low_stock_paginator,
            'near_expiry': near_expiry_paginator.get_page(self.request.GET.get('exp_page', 1)),  # Show only first 5 items\
            'near_expiry_paginator': near_expiry_paginator,
            'recent_transactions': tx_paginator.get_page(self.request.GET.get('tx_page', 1)),  # Show only first 5 items
            'tx_paginator': tx_paginator,
            'expired': expired_paginator.get_page(self.request.GET.get('ex_page', 1)),
            'expired_paginator': expired_paginator,
            'pending_classifications': Classification.objects.filter(approved=False),
            'now': datetime.now(),
        }

        return render(request, self.template_name, context)
    
def low_stock_pagination(request):
    low_stock_qs = Inventory.objects.filter(quantity__lte=10).order_by('quantity')
    low_stock_paginator = Paginator(low_stock_qs, 5)
    low_stock_page = low_stock_paginator.get_page(request.GET.get('low_page', 1))

    context = {
        'low_stock': low_stock_page,
        'low_stock_paginator': low_stock_paginator,
    }
    time.sleep(1)
    return render(request, 'inventory/partials/dashboard/low_stock_partials.html', context)

def near_expiry_pagination(request):

    near_expiry_qs = Inventory.objects.filter(expiration_date__lte=timezone.now().date() + timezone.timedelta(days=30)).order_by('expiration_date')
    near_expiry_paginator = Paginator(near_expiry_qs, 5)
    near_expiry_page = near_expiry_paginator.get_page(request.GET.get('exp_page', 1))
   
    context = {
        'near_expiry': near_expiry_page,
        'near_expiry_paginator': near_expiry_paginator,
    }
    time.sleep(1)
 
    return render(request, 'inventory/partials/dashboard/near_expiry_partials.html', context)

def expired_pagination(request):

    expired_qs = Inventory.objects.expired().order_by('expiration_date')
    expired_paginator = Paginator(expired_qs, 5)
    expired_page = expired_paginator.get_page(request.GET.get('exp_page', 1))
   
    context = {
        'expired': expired_page,
        'expired_paginator': expired_paginator,
    }
    time.sleep(1)
 
    return render(request, 'inventory/partials/dashboard/expired_partials.html', context)

def recent_transactions_pagination(request):
   
    transactions_qs = Transaction.objects.order_by('-transaction_date')
    tx_paginator = Paginator(transactions_qs, 5)
    tx_page = tx_paginator.get_page(request.GET.get('tx_page', 1))
    context = {
        'recent_transactions': tx_page,
        'tx_paginator': tx_paginator,
    }
    time.sleep(1)
    return render(request, 'inventory/partials/dashboard/recent_transaction_partials.html', context)
    

    
