from django.contrib import admin
from inventory.models import (
    Classification, 
    Medicine, 
    Inventory, 
    Transaction, 
    AuditLog, 
    TransactionBatch,
    DosageInstruction
)
from django.utils import timezone


admin.site.site_title = "AI Med Classify Admin"
admin.site.site_header = "AI Med Classify Admin"
admin.site.index_title = "Admin Dashboard"

# proxy model
class ExpiredInventory(Inventory):
    class Meta:
        proxy = True
        verbose_name = "Expired stock"
        verbose_name_plural = "Expired stocks"


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("label", "ai_confidence_score", "approved")
    search_fields = ("label",)
    list_filter = ("approved",)

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("generic_name", "brand_name", "manufacturer",)
    search_fields = ("generic_name", "brand_name", "manufacturer")
    list_filter = ("classification",)


@admin.register(Inventory)
class InvetoryAdmin(admin.ModelAdmin):
    list_display = ("medicine", "batch_number", "quantity", "expiration_date", "date_added")
    search_fields = ("medicine__generic_name", "batch_number")
    list_filter = ("expiration_date",)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("medicine", "user", "quantity_dispensed", "status", "transaction_date")
    search_fields = ("medicine__generic_name", "user__username")
    list_filter = ("status", "transaction_date")

@admin.register(TransactionBatch)
class TransactionBatchAdmin(admin.ModelAdmin):
    pass

@admin.register(DosageInstruction)
class DosageInstructionAdmin(admin.ModelAdmin):
    pass

@admin.register(ExpiredInventory)
class ExpiredInventoryAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.objects.expired()

    def has_add_permission(self, request):
        return False  # optional: prevent adding here

    def has_change_permission(self, request, obj=None):
        return True

from django.contrib.auth.models import Group

admin.site.unregister(Group)
