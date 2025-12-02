# inventory/urls.py

from django.urls import path
from inventory.views.classification import MedicineClassificationView, inventory_search_view
from inventory.views.dashboard import (
    DashboardView,
    low_stock_pagination,
    near_expiry_pagination,
    recent_transactions_pagination,
    expired_pagination,
)    
from inventory.views.medicine import MedicineDetailView, MedicineListView
from inventory.views.inventory import InventoryListView, InventoryDetailView
from inventory.views.transaction import (
    TransactionListView, 
    TransactionCreateView, 
    TransactionDetailView, 
    TransactionStatusUpdateView, 
    TransactionCreateMultipleView,
    TransactionSuccessView,
    TransactionSuccessMultipleView, 
    TransactionItemsListView
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('classify/', MedicineClassificationView.as_view(), name='classify'),
    path("medicines/", MedicineListView.as_view(), name="medicines-list"),
    path("medicines/<int:pk>/", MedicineDetailView.as_view(), name="medicine-detail"),
    path("inventory/", InventoryListView.as_view(), name="inventory-list"),
    path("inventory/<int:pk>/", InventoryDetailView.as_view(), name="inventory-detail"),
    path("transaction/", TransactionListView.as_view(), name="transaction-list"),
    path("transaction/new/", TransactionCreateView.as_view(), name="transaction-create"),
    path("transaction/<int:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("transactions/<int:pk>/status/", TransactionStatusUpdateView.as_view(), name="transaction-status-update"),
    path("transaction/create/multiple/", TransactionCreateMultipleView.as_view(), name='transaction-create-multiple'),
    path("transaction/success/single/<int:pk>/", TransactionSuccessView.as_view(), name='transaction-success'),
    path("transaction/success/multiple/<str:pk>/", TransactionSuccessMultipleView.as_view(), name='transaction-success-multiple'),
    path('ai/search/', inventory_search_view, name='inventory-search-view'),
    path('transactions/list/', TransactionItemsListView.as_view(), name='transaction-list-forms'),


    # HTMX
    path("low-stock-pagination/", low_stock_pagination, name="low-stock-pagination"),
    path("near-expiry-pagination/", near_expiry_pagination, name="near-expiry-pagination"),
    path("tx-pagination/", recent_transactions_pagination, name="recent-transactions-pagination"),
    path("expired-pagination/", expired_pagination, name='expired-pagination'),


    # authentication
    path("login/", auth_views.LoginView.as_view(template_name="inventory/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
]