from django.contrib import admin
from inventory.models import Classification, Medicine, Inventory, Transaction, AuditLog


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    pass

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    pass

@admin.register(Inventory)
class InvetoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    pass
