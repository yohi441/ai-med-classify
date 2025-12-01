from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db import transaction

class Classification(models.Model):
    label = models.CharField(max_length=100)
    ai_confidence_score = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.label} ({'Approved' if self.approved else 'Pending'})"

class Medicine(models.Model):
    generic_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255, blank=True)
    dosage_form = models.CharField(max_length=100)
    strength = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=255, blank=True)
    classification = models.ManyToManyField(Classification, related_name="medicines", blank=True)

    intended_for = models.CharField(
        max_length=20,
        choices=[("adult", "Adult"), ("pediatric", "Pediatric"), ("both", "Both")],
        default="both"
    )

    def __str__(self):
        return f"{self.generic_name} ({self.brand_name})"

class Inventory(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="inventory")
    batch_number = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    expiration_date = models.DateField()
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine.generic_name} - Batch {self.batch_number}"
    
    class Meta:
        verbose_name_plural = "Inventories"


class TransactionBatch(models.Model):
    batch_id = models.CharField(max_length=30, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Batch {self.batch_id}"

    @staticmethod
    def generate_batch_id():
        from django.utils import timezone
        return "TX" + timezone.now().strftime("%Y%m%d%H%M%S")

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    batch = models.ForeignKey(
        TransactionBatch,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True
    )
    dosage = models.ForeignKey(
        'DosageInstruction',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transactions"
    )
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="transactions")
    quantity_dispensed = models.PositiveIntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("dispensed", "Dispensed"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )
    classification = models.ForeignKey(
        "Classification",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    request_id = models.CharField(max_length=100, blank=True, null=True) #NOSONAR
    stock_before = models.PositiveIntegerField(null=True, blank=True)
    stock_after = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity_dispensed} of {self.medicine} by {self.user}"
    
    def dispense(self):
        """
        Deducts stock using FIFO when transaction is marked dispensed.
        """
        if self.status != "dispensed":
            return  # only deduct when status is dispensed

        qty_needed = self.quantity_dispensed
        inventories = Inventory.objects.filter(
            medicine=self.medicine,
            quantity__gt=0
        ).order_by("expiration_date", "date_added")  # FIFO

        total_available = inventories.aggregate(total=Sum("quantity"))["total"] or 0
        self.stock_before = total_available

        if total_available < qty_needed:
            raise ValueError("Not enough stock available!")

        with transaction.atomic():
            for inv in inventories:
                if qty_needed <= 0:
                    break
                if inv.quantity <= qty_needed:
                    qty_needed -= inv.quantity
                    inv.quantity = 0
                else:
                    inv.quantity -= qty_needed
                    qty_needed = 0
                inv.save()

        # Save final stock_after
        remaining = inventories.aggregate(total=Sum("quantity"))["total"] or 0
        self.stock_after = remaining
        self.save()


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_log")
    action_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_type} @ {self.timestamp}"
    
class DosageInstruction(models.Model):
    key = models.CharField(max_length=50, unique=True)  # e.g., 'once_daily', 'twice_daily', 'three_times_daily'
    label = models.CharField(max_length=100)            # e.g., 'Once a day', 'Twice a day', 'Three times a day'

    def __str__(self):
        return self.label
