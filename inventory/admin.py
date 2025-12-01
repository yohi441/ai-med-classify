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


admin.site.site_title = "AI Med Classify Admin"
admin.site.site_header = "AI Med Classify Admin"
admin.site.index_title = "Admin Dashboard"


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("label", "ai_confidence_score", "approved")
    search_fields = ("label",)
    list_filter = ("approved",)

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("generic_name", "brand_name", "manufacturer", "get_classifications")
    search_fields = ("generic_name", "brand_name", "manufacturer")
    list_filter = ("classification",)

    def get_classifications(self, obj):
        return ", ".join([c.label for c in obj.classification.all()])
    get_classifications.short_description = "Classifications"

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

from django.contrib.auth.models import Group

admin.site.unregister(Group)
