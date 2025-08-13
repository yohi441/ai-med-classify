# inventory/urls.py

from django.urls import path
from inventory.views.classification import MedicineClassificationView
from inventory.views.dashboard import DashboardView
from inventory.views.medicine import MedicineDetailView, MedicineListView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('classify/', MedicineClassificationView.as_view(), name='classify'),
    path("medicines/", MedicineListView.as_view(), name="medicines-list"),
    path("medicines/<int:pk>/", MedicineDetailView.as_view(), name="medicine-detail"),
    path("login/", auth_views.LoginView.as_view(template_name="inventory/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
]