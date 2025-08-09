# inventory/urls.py

from django.urls import path
from inventory.views.classification import MedicineClassificationView

app_name = 'inventory'

urlpatterns = [
    path('classify/', MedicineClassificationView.as_view(), name='classify'),
]